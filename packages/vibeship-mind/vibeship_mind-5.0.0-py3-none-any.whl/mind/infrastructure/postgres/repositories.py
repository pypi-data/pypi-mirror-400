"""Repository pattern for database operations."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mind.core.decision.models import DecisionTrace, Outcome, SalienceUpdate
from mind.core.errors import ErrorCode, MindError, Result
from mind.core.federation.models import PatternType, SanitizedPattern
from mind.core.memory.models import Memory, TemporalLevel
from mind.core.memory.retrieval import RetrievalRequest, RetrievalResult, ScoredMemory
from mind.infrastructure.postgres.models import (
    DecisionTraceModel,
    EventModel,
    MemoryModel,
    SalienceAdjustmentModel,
    SanitizedPatternModel,
    UserModel,
)


async def ensure_user_exists(session: AsyncSession, user_id: UUID) -> None:
    """Ensure a user exists, creating if needed (upsert pattern for dev)."""
    stmt = select(UserModel).where(UserModel.user_id == user_id)
    result = await session.execute(stmt)
    if result.scalar_one_or_none() is None:
        user = UserModel(user_id=user_id)
        session.add(user)
        await session.flush()


class MemoryRepository:
    """Repository for memory operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, memory: Memory, embedding: list[float] | None = None) -> Result[Memory]:
        """Create a new memory."""
        # Ensure user exists (auto-create for dev convenience)
        await ensure_user_exists(self._session, memory.user_id)

        model = MemoryModel(
            memory_id=memory.memory_id,
            user_id=memory.user_id,
            content=memory.content,
            content_type=memory.content_type,
            embedding=embedding,
            temporal_level=memory.temporal_level.value,
            valid_from=memory.valid_from,
            valid_until=memory.valid_until,
            base_salience=memory.base_salience,
            outcome_adjustment=memory.outcome_adjustment,
            retrieval_count=memory.retrieval_count,
            decision_count=memory.decision_count,
            positive_outcomes=memory.positive_outcomes,
            negative_outcomes=memory.negative_outcomes,
            promoted_from_level=memory.promoted_from_level.value
            if memory.promoted_from_level
            else None,
            promotion_timestamp=memory.promotion_timestamp,
        )
        self._session.add(model)
        await self._session.flush()
        return Result.ok(memory)

    async def get(self, memory_id: UUID) -> Result[Memory]:
        """Get a memory by ID."""
        stmt = select(MemoryModel).where(MemoryModel.memory_id == memory_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.MEMORY_NOT_FOUND,
                    message=f"Memory {memory_id} not found",
                    context={"memory_id": str(memory_id)},
                )
            )

        return Result.ok(self._to_domain(model))

    async def retrieve(self, request: RetrievalRequest) -> Result[RetrievalResult]:
        """Retrieve memories using multi-source fusion."""
        start_time = datetime.now(UTC)

        # Build base query
        stmt = select(MemoryModel).where(MemoryModel.user_id == request.user_id)

        # Filter by temporal levels
        if request.temporal_levels:
            levels = [level.value for level in request.temporal_levels]
            stmt = stmt.where(MemoryModel.temporal_level.in_(levels))

        # Filter by salience
        if request.min_salience > 0:
            stmt = stmt.where(
                (MemoryModel.base_salience + MemoryModel.outcome_adjustment) >= request.min_salience
            )

        # Filter expired
        if not request.include_expired:
            now = datetime.now(UTC)
            stmt = stmt.where((MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > now))
            stmt = stmt.where(MemoryModel.valid_from <= now)

        # Order by effective salience and limit
        stmt = stmt.order_by(
            (MemoryModel.base_salience + MemoryModel.outcome_adjustment).desc()
        ).limit(request.limit * 3)  # Over-fetch for reranking

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        # Convert to scored memories
        scored_memories = []
        for i, model in enumerate(models[: request.limit]):
            memory = self._to_domain(model)
            scored = ScoredMemory(
                memory=memory,
                salience_score=memory.effective_salience,
                final_score=memory.effective_salience,  # Simple for now
                rank=i + 1,
            )
            scored_memories.append(scored)

        latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return Result.ok(
            RetrievalResult(
                memories=scored_memories,
                query=request.query,
                latency_ms=latency_ms,
            )
        )

    async def vector_search(
        self,
        user_id: UUID,
        query_embedding: list[float],
        limit: int = 10,
    ) -> list[tuple[MemoryModel, float]]:
        """Search memories by vector similarity."""
        # Use pgvector cosine distance
        stmt = (
            select(
                MemoryModel,
                (1 - MemoryModel.embedding.cosine_distance(query_embedding)).label("similarity"),
            )
            .where(MemoryModel.user_id == user_id)
            .where(MemoryModel.embedding.isnot(None))
            .order_by(MemoryModel.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def update_salience(
        self,
        memory_id: UUID,
        adjustment: SalienceUpdate,
    ) -> Result[Memory]:
        """Update memory salience based on outcome."""
        stmt = select(MemoryModel).where(MemoryModel.memory_id == memory_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.MEMORY_NOT_FOUND,
                    message=f"Memory {memory_id} not found",
                )
            )

        # Log the adjustment
        log = SalienceAdjustmentModel(
            memory_id=memory_id,
            trace_id=adjustment.trace_id,
            previous_adjustment=model.outcome_adjustment,
            new_adjustment=model.outcome_adjustment + adjustment.delta,
            delta=adjustment.delta,
            reason=adjustment.reason,
        )
        self._session.add(log)

        # Update the memory
        model.outcome_adjustment += adjustment.delta
        if adjustment.delta > 0:
            model.positive_outcomes += 1
        else:
            model.negative_outcomes += 1

        await self._session.flush()
        return Result.ok(self._to_domain(model))

    async def get_recent(
        self,
        user_id: UUID,
        limit: int = 50,
    ) -> Result[list[Memory]]:
        """Get recent memories for a user.

        Returns memories ordered by creation time, most recent first.
        """
        stmt = (
            select(MemoryModel)
            .where(MemoryModel.user_id == user_id)
            .order_by(MemoryModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        memories = [self._to_domain(m) for m in result.scalars().all()]
        return Result.ok(memories)

    async def update_embedding(
        self,
        memory_id: UUID,
        embedding: list[float],
    ) -> Result[Memory]:
        """Update the embedding for a memory.

        Used for reindexing with newer embedding models.

        Args:
            memory_id: Memory ID to update
            embedding: New embedding vector

        Returns:
            Result with updated Memory
        """
        stmt = select(MemoryModel).where(MemoryModel.memory_id == memory_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.MEMORY_NOT_FOUND,
                    message=f"Memory {memory_id} not found",
                    context={"memory_id": str(memory_id)},
                )
            )

        model.embedding = embedding
        model.updated_at = datetime.now(UTC)
        await self._session.flush()
        return Result.ok(self._to_domain(model))

    async def find_memories_for_reindex(
        self,
        user_id: UUID | None = None,
        include_with_embeddings: bool = False,
        limit: int = 1000,
        offset: int = 0,
    ) -> Result[list[Memory]]:
        """Find memories that need embedding reindexing.

        Args:
            user_id: Optional user filter (None = all users)
            include_with_embeddings: Include memories that already have embeddings
            limit: Maximum memories to return
            offset: Offset for pagination

        Returns:
            Result with list of memories needing reindex
        """
        stmt = select(MemoryModel)

        if user_id is not None:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        if not include_with_embeddings:
            stmt = stmt.where(MemoryModel.embedding.is_(None))

        # Filter out archived/expired memories
        now = datetime.now(UTC)
        stmt = stmt.where((MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > now))

        stmt = stmt.order_by(MemoryModel.created_at.desc()).offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        memories = [self._to_domain(m) for m in result.scalars().all()]
        return Result.ok(memories)

    async def count_memories_needing_embeddings(
        self,
        user_id: UUID | None = None,
    ) -> int:
        """Count memories without embeddings.

        Args:
            user_id: Optional user filter

        Returns:
            Count of memories without embeddings
        """
        stmt = select(func.count(MemoryModel.memory_id)).where(MemoryModel.embedding.is_(None))

        if user_id is not None:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        # Filter out archived/expired memories
        now = datetime.now(UTC)
        stmt = stmt.where((MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > now))

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def delete(self, memory_id: UUID, user_id: UUID) -> Result[bool]:
        """Delete a memory by ID (soft delete by setting valid_until)."""
        stmt = select(MemoryModel).where(
            MemoryModel.memory_id == memory_id,
            MemoryModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.MEMORY_NOT_FOUND,
                    message=f"Memory {memory_id} not found",
                    context={"memory_id": str(memory_id)},
                )
            )

        # Hard delete for now - can change to soft delete later
        await self._session.delete(model)
        await self._session.flush()
        return Result.ok(True)

    def _to_domain(self, model: MemoryModel) -> Memory:
        """Convert SQLAlchemy model to domain object."""
        return Memory(
            memory_id=model.memory_id,
            user_id=model.user_id,
            content=model.content,
            content_type=model.content_type,
            temporal_level=TemporalLevel(model.temporal_level),
            valid_from=model.valid_from,
            valid_until=model.valid_until,
            base_salience=model.base_salience,
            outcome_adjustment=model.outcome_adjustment,
            retrieval_count=model.retrieval_count,
            decision_count=model.decision_count,
            positive_outcomes=model.positive_outcomes,
            negative_outcomes=model.negative_outcomes,
            promoted_from_level=TemporalLevel(model.promoted_from_level)
            if model.promoted_from_level
            else None,
            promotion_timestamp=model.promotion_timestamp,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class DecisionRepository:
    """Repository for decision tracking."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_trace(self, trace: DecisionTrace) -> Result[DecisionTrace]:
        """Create a new decision trace."""
        # Ensure user exists (auto-create for dev convenience)
        await ensure_user_exists(self._session, trace.user_id)

        model = DecisionTraceModel(
            trace_id=trace.trace_id,
            user_id=trace.user_id,
            session_id=trace.session_id,
            context_memory_ids=[str(mid) for mid in trace.memory_ids],
            memory_scores=trace.memory_scores,
            decision_type=trace.decision_type,
            decision_summary=trace.decision_summary,
            confidence=trace.confidence,
            alternatives_count=trace.alternatives_count,
        )
        self._session.add(model)
        await self._session.flush()
        return Result.ok(trace)

    async def get_trace(self, trace_id: UUID) -> Result[DecisionTrace]:
        """Get a decision trace by ID."""
        stmt = select(DecisionTraceModel).where(DecisionTraceModel.trace_id == trace_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.DECISION_NOT_FOUND,
                    message=f"Decision trace {trace_id} not found",
                )
            )

        return Result.ok(self._to_domain(model))

    async def record_outcome(
        self,
        trace_id: UUID,
        outcome: Outcome,
        attributions: dict[str, float],
    ) -> Result[DecisionTrace]:
        """Record an outcome for a decision trace."""
        stmt = select(DecisionTraceModel).where(DecisionTraceModel.trace_id == trace_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.DECISION_NOT_FOUND,
                    message=f"Decision trace {trace_id} not found",
                )
            )

        if model.outcome_observed:
            return Result.err(
                MindError(
                    code=ErrorCode.DECISION_ALREADY_OBSERVED,
                    message=f"Outcome already recorded for trace {trace_id}",
                )
            )

        model.outcome_observed = True
        model.outcome_quality = outcome.quality
        model.outcome_timestamp = outcome.observed_at
        model.outcome_signal = outcome.signal
        model.memory_attribution = attributions

        await self._session.flush()
        return Result.ok(self._to_domain(model))

    async def get_pending_traces(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[DecisionTrace]:
        """Get traces without observed outcomes."""
        stmt = (
            select(DecisionTraceModel)
            .where(DecisionTraceModel.user_id == user_id)
            .where(not DecisionTraceModel.outcome_observed)
            .order_by(DecisionTraceModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_user(
        self,
        user_id: UUID,
        session_id: UUID | None = None,
        limit: int = 50,
    ) -> Result[list[DecisionTrace]]:
        """Get decision traces for a user.

        Args:
            user_id: User ID
            session_id: Optional session ID to filter by
            limit: Maximum traces to return
        """
        stmt = select(DecisionTraceModel).where(DecisionTraceModel.user_id == user_id)

        if session_id:
            stmt = stmt.where(DecisionTraceModel.session_id == session_id)

        stmt = stmt.order_by(DecisionTraceModel.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        traces = [self._to_domain(m) for m in result.scalars().all()]
        return Result.ok(traces)

    def _to_domain(self, model: DecisionTraceModel) -> DecisionTrace:
        """Convert SQLAlchemy model to domain object."""
        return DecisionTrace(
            trace_id=model.trace_id,
            user_id=model.user_id,
            session_id=model.session_id,
            memory_ids=[UUID(mid) for mid in model.context_memory_ids],
            memory_scores=model.memory_scores,
            decision_type=model.decision_type,
            decision_summary=model.decision_summary,
            confidence=model.confidence,
            alternatives_count=model.alternatives_count,
            created_at=model.created_at,
            outcome_observed=model.outcome_observed,
            outcome_quality=model.outcome_quality,
            outcome_timestamp=model.outcome_timestamp,
            outcome_signal=model.outcome_signal,
        )


class EventRepository:
    """Repository for event sourcing."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def append(self, event: EventModel) -> Result[EventModel]:
        """Append an event to the log."""
        self._session.add(event)
        await self._session.flush()
        return Result.ok(event)

    async def get_by_aggregate(
        self,
        aggregate_id: UUID,
        after_version: int = 0,
    ) -> list[EventModel]:
        """Get events for an aggregate."""
        stmt = (
            select(EventModel)
            .where(EventModel.aggregate_id == aggregate_id)
            .where(EventModel.version > after_version)
            .order_by(EventModel.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: UUID,
        event_types: list[str] | None = None,
        limit: int = 100,
    ) -> list[EventModel]:
        """Get events for a user."""
        stmt = select(EventModel).where(EventModel.user_id == user_id)

        if event_types:
            stmt = stmt.where(EventModel.event_type.in_(event_types))

        stmt = stmt.order_by(EventModel.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class PatternRepository:
    """Repository for federated pattern storage.

    Manages persistent storage of sanitized patterns that have been
    validated for cross-user sharing with differential privacy guarantees.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, pattern: SanitizedPattern) -> Result[SanitizedPattern]:
        """Save a sanitized pattern to persistent storage.

        Args:
            pattern: The sanitized pattern to store

        Returns:
            Result with the saved pattern
        """
        model = SanitizedPatternModel(
            pattern_id=pattern.pattern_id,
            pattern_type=pattern.pattern_type.value,
            trigger_category=pattern.trigger_category,
            response_strategy=pattern.response_strategy,
            outcome_improvement=pattern.outcome_improvement,
            confidence=pattern.confidence,
            source_count=pattern.source_count,
            user_count=pattern.user_count,
            epsilon=pattern.epsilon,
            created_at=pattern.created_at,
            expires_at=pattern.expires_at,
            is_active=True,
        )
        self._session.add(model)
        await self._session.flush()
        return Result.ok(pattern)

    async def get(self, pattern_id: UUID) -> Result[SanitizedPattern]:
        """Get a pattern by ID.

        Args:
            pattern_id: The pattern ID

        Returns:
            Result with the pattern or error if not found
        """
        stmt = select(SanitizedPatternModel).where(
            SanitizedPatternModel.pattern_id == pattern_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.PATTERN_NOT_FOUND,
                    message=f"Pattern {pattern_id} not found",
                    context={"pattern_id": str(pattern_id)},
                )
            )

        return Result.ok(self._to_domain(model))

    async def get_active(
        self,
        trigger_category: str | None = None,
        min_confidence: float = 0.5,
        limit: int = 100,
    ) -> Result[list[SanitizedPattern]]:
        """Get active patterns, optionally filtered by trigger category.

        Args:
            trigger_category: Optional filter by trigger category
            min_confidence: Minimum confidence threshold
            limit: Maximum patterns to return

        Returns:
            Result with list of active patterns
        """
        now = datetime.now(UTC)

        stmt = (
            select(SanitizedPatternModel)
            .where(SanitizedPatternModel.is_active == True)  # noqa: E712
            .where(SanitizedPatternModel.confidence >= min_confidence)
            .where(
                (SanitizedPatternModel.expires_at.is_(None))
                | (SanitizedPatternModel.expires_at > now)
            )
        )

        if trigger_category is not None:
            stmt = stmt.where(SanitizedPatternModel.trigger_category == trigger_category)

        stmt = stmt.order_by(SanitizedPatternModel.confidence.desc()).limit(limit)

        result = await self._session.execute(stmt)
        patterns = [self._to_domain(m) for m in result.scalars().all()]
        return Result.ok(patterns)

    async def get_all(
        self,
        include_expired: bool = False,
        include_inactive: bool = False,
        limit: int = 1000,
    ) -> Result[list[SanitizedPattern]]:
        """Get all patterns.

        Args:
            include_expired: Include expired patterns
            include_inactive: Include inactive patterns
            limit: Maximum patterns to return

        Returns:
            Result with list of patterns
        """
        stmt = select(SanitizedPatternModel)

        if not include_inactive:
            stmt = stmt.where(SanitizedPatternModel.is_active == True)  # noqa: E712

        if not include_expired:
            now = datetime.now(UTC)
            stmt = stmt.where(
                (SanitizedPatternModel.expires_at.is_(None))
                | (SanitizedPatternModel.expires_at > now)
            )

        stmt = stmt.order_by(SanitizedPatternModel.created_at.desc()).limit(limit)

        result = await self._session.execute(stmt)
        patterns = [self._to_domain(m) for m in result.scalars().all()]
        return Result.ok(patterns)

    async def deactivate(self, pattern_id: UUID) -> Result[bool]:
        """Deactivate a pattern (soft delete).

        Args:
            pattern_id: The pattern ID to deactivate

        Returns:
            Result with success status
        """
        stmt = select(SanitizedPatternModel).where(
            SanitizedPatternModel.pattern_id == pattern_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Result.err(
                MindError(
                    code=ErrorCode.PATTERN_NOT_FOUND,
                    message=f"Pattern {pattern_id} not found",
                )
            )

        model.is_active = False
        await self._session.flush()
        return Result.ok(True)

    async def count(
        self,
        active_only: bool = True,
        trigger_category: str | None = None,
    ) -> int:
        """Count patterns.

        Args:
            active_only: Count only active patterns
            trigger_category: Optional filter by category

        Returns:
            Count of patterns
        """
        stmt = select(func.count(SanitizedPatternModel.pattern_id))

        if active_only:
            stmt = stmt.where(SanitizedPatternModel.is_active == True)  # noqa: E712

        if trigger_category is not None:
            stmt = stmt.where(SanitizedPatternModel.trigger_category == trigger_category)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_stats(self) -> dict:
        """Get aggregated statistics about stored patterns.

        Returns:
            Dict with pattern statistics
        """
        now = datetime.now(UTC)

        # Total patterns
        total_stmt = select(func.count(SanitizedPatternModel.pattern_id))
        total_result = await self._session.execute(total_stmt)
        total = total_result.scalar() or 0

        # Active patterns
        active_stmt = select(func.count(SanitizedPatternModel.pattern_id)).where(
            SanitizedPatternModel.is_active == True  # noqa: E712
        )
        active_result = await self._session.execute(active_stmt)
        active = active_result.scalar() or 0

        # Expired patterns
        expired_stmt = select(func.count(SanitizedPatternModel.pattern_id)).where(
            SanitizedPatternModel.expires_at <= now
        )
        expired_result = await self._session.execute(expired_stmt)
        expired = expired_result.scalar() or 0

        # Average confidence and improvement
        stats_stmt = select(
            func.avg(SanitizedPatternModel.confidence),
            func.avg(SanitizedPatternModel.outcome_improvement),
        ).where(SanitizedPatternModel.is_active == True)  # noqa: E712
        stats_result = await self._session.execute(stats_stmt)
        stats_row = stats_result.one_or_none()

        avg_confidence = float(stats_row[0]) if stats_row and stats_row[0] else 0.0
        avg_improvement = float(stats_row[1]) if stats_row and stats_row[1] else 0.0

        return {
            "total_patterns": total,
            "active_patterns": active,
            "expired_patterns": expired,
            "average_confidence": avg_confidence,
            "average_improvement": avg_improvement,
        }

    def _to_domain(self, model: SanitizedPatternModel) -> SanitizedPattern:
        """Convert SQLAlchemy model to domain object."""
        return SanitizedPattern(
            pattern_id=model.pattern_id,
            pattern_type=PatternType(model.pattern_type),
            trigger_category=model.trigger_category,
            response_strategy=model.response_strategy,
            outcome_improvement=model.outcome_improvement,
            confidence=model.confidence,
            source_count=model.source_count,
            user_count=model.user_count,
            epsilon=model.epsilon,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )
