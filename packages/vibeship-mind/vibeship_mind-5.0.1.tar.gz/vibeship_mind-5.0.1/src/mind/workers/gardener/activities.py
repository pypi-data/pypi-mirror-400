"""Temporal activities for memory management.

Activities are the individual tasks that workflows orchestrate.
They should be idempotent and handle their own retries for
transient failures.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from temporalio import activity

from mind.core.events.memory import MemoryExpired, MemoryPromoted
from mind.core.memory.models import Memory, TemporalLevel
from mind.core.memory.retrieval import RetrievalRequest
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import MemoryRepository
from mind.services.events import get_event_service


@dataclass
class PromotionCandidate:
    """A memory that may be eligible for promotion."""

    memory_id: UUID
    user_id: UUID
    current_level: TemporalLevel
    target_level: TemporalLevel
    score: float  # Confidence in promotion decision
    reason: str


@dataclass
class PromotionResult:
    """Result of a memory promotion attempt."""

    memory_id: UUID
    success: bool
    from_level: TemporalLevel | None = None
    to_level: TemporalLevel | None = None
    error: str | None = None


# Promotion criteria thresholds
PROMOTION_THRESHOLDS = {
    # From IMMEDIATE to SITUATIONAL
    (TemporalLevel.IMMEDIATE, TemporalLevel.SITUATIONAL): {
        "min_age_hours": 24,  # At least 1 day old
        "min_retrieval_count": 3,  # Retrieved at least 3 times
        "min_positive_ratio": 0.6,  # 60% positive outcomes
        "min_salience": 0.5,  # Above average salience
    },
    # From SITUATIONAL to SEASONAL
    (TemporalLevel.SITUATIONAL, TemporalLevel.SEASONAL): {
        "min_age_hours": 24 * 7,  # At least 1 week old
        "min_retrieval_count": 10,
        "min_positive_ratio": 0.7,
        "min_salience": 0.6,
    },
    # From SEASONAL to IDENTITY
    (TemporalLevel.SEASONAL, TemporalLevel.IDENTITY): {
        "min_age_hours": 24 * 30,  # At least 1 month old
        "min_retrieval_count": 25,
        "min_positive_ratio": 0.8,
        "min_salience": 0.7,
    },
}


@activity.defn
async def find_promotion_candidates(
    user_id: UUID,
    batch_size: int = 100,
) -> list[PromotionCandidate]:
    """Find memories eligible for promotion.

    This activity scans a user's memories and identifies those that
    meet the criteria for promotion to the next temporal level.

    Criteria include:
    - Age (time since creation)
    - Retrieval frequency
    - Outcome ratio (positive vs negative)
    - Current salience

    Args:
        user_id: User whose memories to evaluate
        batch_size: Maximum candidates to return

    Returns:
        List of promotion candidates ordered by score
    """
    activity.logger.info(f"Finding promotion candidates for user {user_id}")

    candidates = []
    db = get_database()

    async with db.session() as session:
        repo = MemoryRepository(session)

        # Check each level for promotion opportunities
        for from_level in [
            TemporalLevel.IMMEDIATE,
            TemporalLevel.SITUATIONAL,
            TemporalLevel.SEASONAL,
        ]:
            to_level = TemporalLevel(from_level.value + 1)
            thresholds = PROMOTION_THRESHOLDS.get((from_level, to_level))

            if not thresholds:
                continue

            # Query memories at this level
            result = await repo.retrieve(
                RetrievalRequest(
                    user_id=user_id,
                    query="",  # Empty query for listing
                    temporal_levels=[from_level],
                    limit=batch_size,
                )
            )

            if not result.is_ok:
                activity.logger.warning(f"Failed to query level {from_level}: {result.error}")
                continue

            for scored_memory in result.value.memories:
                memory = scored_memory.memory

                # Check age
                age_hours = (datetime.now(UTC) - memory.created_at).total_seconds() / 3600
                if age_hours < thresholds["min_age_hours"]:
                    continue

                # Check retrieval count
                if memory.retrieval_count < thresholds["min_retrieval_count"]:
                    continue

                # Check outcome ratio
                total_outcomes = memory.positive_outcomes + memory.negative_outcomes
                if total_outcomes > 0:
                    positive_ratio = memory.positive_outcomes / total_outcomes
                    if positive_ratio < thresholds["min_positive_ratio"]:
                        continue

                # Check salience
                if memory.effective_salience < thresholds["min_salience"]:
                    continue

                # Calculate promotion score (higher is better)
                score = _calculate_promotion_score(memory, thresholds)

                candidates.append(
                    PromotionCandidate(
                        memory_id=memory.memory_id,
                        user_id=memory.user_id,
                        current_level=from_level,
                        target_level=to_level,
                        score=score,
                        reason=f"Met all criteria: age={age_hours:.0f}h, retrievals={memory.retrieval_count}, "
                        f"salience={memory.effective_salience:.2f}",
                    )
                )

    # Sort by score and limit
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:batch_size]


def _calculate_promotion_score(memory: Memory, thresholds: dict) -> float:
    """Calculate a promotion confidence score for a memory.

    Higher scores indicate stronger candidates for promotion.
    """
    # Factors that increase score
    age_factor = min(
        1.0,
        (datetime.now(UTC) - memory.created_at).total_seconds()
        / 3600
        / thresholds["min_age_hours"],
    )
    retrieval_factor = min(1.0, memory.retrieval_count / (thresholds["min_retrieval_count"] * 2))
    salience_factor = memory.effective_salience

    # Outcome factor (heavily weighted)
    total_outcomes = memory.positive_outcomes + memory.negative_outcomes
    if total_outcomes > 0:
        outcome_factor = memory.positive_outcomes / total_outcomes
    else:
        outcome_factor = 0.5  # Neutral if no outcomes

    # Weighted average
    score = (
        age_factor * 0.15 + retrieval_factor * 0.25 + salience_factor * 0.25 + outcome_factor * 0.35
    )

    return min(1.0, max(0.0, score))


@activity.defn
async def promote_memory(
    candidate: PromotionCandidate,
) -> PromotionResult:
    """Promote a single memory to the next temporal level.

    This is an idempotent operation - if the memory has already
    been promoted, it returns success without modifying.

    Args:
        candidate: The promotion candidate

    Returns:
        Result of the promotion attempt
    """
    activity.logger.info(
        f"Promoting memory {candidate.memory_id} from "
        f"{candidate.current_level.name} to {candidate.target_level.name}"
    )

    db = get_database()

    async with db.session() as session:
        repo = MemoryRepository(session)

        # Get current memory state
        result = await repo.get(candidate.memory_id)
        if not result.is_ok:
            return PromotionResult(
                memory_id=candidate.memory_id,
                success=False,
                error=f"Memory not found: {result.error.message}",
            )

        memory = result.value

        # Check if already promoted (idempotency)
        if memory.temporal_level.value >= candidate.target_level.value:
            activity.logger.info(
                f"Memory {candidate.memory_id} already at level {memory.temporal_level.name}"
            )
            return PromotionResult(
                memory_id=candidate.memory_id,
                success=True,
                from_level=candidate.current_level,
                to_level=memory.temporal_level,
            )

        # Perform promotion by updating the memory
        # Note: In a full implementation, we'd create a new memory version
        # Here we update in place for simplicity
        Memory(
            memory_id=memory.memory_id,
            user_id=memory.user_id,
            content=memory.content,
            content_type=memory.content_type,
            temporal_level=candidate.target_level,
            valid_from=memory.valid_from,
            valid_until=memory.valid_until,
            base_salience=memory.base_salience,
            outcome_adjustment=memory.outcome_adjustment,
            retrieval_count=memory.retrieval_count,
            decision_count=memory.decision_count,
            positive_outcomes=memory.positive_outcomes,
            negative_outcomes=memory.negative_outcomes,
            promoted_from_level=memory.temporal_level,
            promotion_timestamp=datetime.now(UTC),
            created_at=memory.created_at,
        )

        # Update in database (would use a dedicated update method in production)
        # For now, we'll use a direct SQL update
        from sqlalchemy import update

        from mind.infrastructure.postgres.models import MemoryModel

        await session.execute(
            update(MemoryModel)
            .where(MemoryModel.memory_id == candidate.memory_id)
            .values(
                temporal_level=candidate.target_level.value,
                promoted_from_level=candidate.current_level.value,
                promotion_timestamp=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
        await session.commit()

    return PromotionResult(
        memory_id=candidate.memory_id,
        success=True,
        from_level=candidate.current_level,
        to_level=candidate.target_level,
    )


@activity.defn
async def notify_promotion(
    result: PromotionResult,
    user_id: UUID,
) -> bool:
    """Publish event for a successful memory promotion.

    This activity handles the event publishing for promoted memories.
    It's separated from the promotion itself to allow for retry
    without re-promoting.

    Args:
        result: The promotion result
        user_id: User ID for the event

    Returns:
        True if notification succeeded
    """
    if not result.success or not result.from_level or not result.to_level:
        return False

    activity.logger.info(f"Publishing promotion event for {result.memory_id}")

    try:
        get_event_service()

        event = MemoryPromoted(
            memory_id=result.memory_id,
            from_level=result.from_level,
            to_level=result.to_level,
            reason="Met promotion criteria",
        )

        from mind.infrastructure.nats.client import get_nats_client
        from mind.infrastructure.nats.publisher import EventPublisher

        client = await get_nats_client()
        publisher = EventPublisher(client)

        await publisher.publish_event(
            event=event,
            user_id=user_id,
        )

        return True

    except Exception as e:
        activity.logger.warning(f"Failed to publish promotion event: {e}")
        return False


@dataclass
class ExpirationCandidate:
    """A memory that has expired and should be archived."""

    memory_id: UUID
    user_id: UUID
    temporal_level: TemporalLevel
    valid_until: datetime
    reason: str  # "valid_until_passed", "low_salience"


@dataclass
class ExpirationResult:
    """Result of a memory expiration attempt."""

    memory_id: UUID
    success: bool
    archived: bool = False
    error: str | None = None


# Expiration thresholds
EXPIRATION_THRESHOLDS = {
    # Low salience threshold by temporal level
    TemporalLevel.IMMEDIATE: 0.1,  # Very aggressive for short-term
    TemporalLevel.SITUATIONAL: 0.15,
    TemporalLevel.SEASONAL: 0.2,
    TemporalLevel.IDENTITY: 0.1,  # Identity memories almost never expire by salience
}


@activity.defn
async def find_expired_memories(
    user_id: UUID,
    batch_size: int = 100,
) -> list[ExpirationCandidate]:
    """Find memories that have expired and should be archived.

    Memories expire when:
    1. Their valid_until timestamp has passed
    2. Their effective salience has dropped below threshold

    Args:
        user_id: User whose memories to evaluate
        batch_size: Maximum candidates to return

    Returns:
        List of expiration candidates
    """
    activity.logger.info(f"Finding expired memories for user {user_id}")

    candidates = []
    now = datetime.now(UTC)
    db = get_database()

    async with db.session() as session:
        repo = MemoryRepository(session)

        # Check each temporal level
        for level in TemporalLevel:
            result = await repo.retrieve(
                RetrievalRequest(
                    user_id=user_id,
                    query="",  # Empty query for listing
                    temporal_levels=[level],
                    limit=batch_size,
                )
            )

            if not result.is_ok:
                activity.logger.warning(f"Failed to query level {level}: {result.error}")
                continue

            for scored_memory in result.value.memories:
                memory = scored_memory.memory

                # Check valid_until expiration
                if memory.valid_until and memory.valid_until < now:
                    candidates.append(
                        ExpirationCandidate(
                            memory_id=memory.memory_id,
                            user_id=memory.user_id,
                            temporal_level=memory.temporal_level,
                            valid_until=memory.valid_until,
                            reason="valid_until_passed",
                        )
                    )
                    continue

                # Check salience-based expiration (except IDENTITY level)
                if level != TemporalLevel.IDENTITY:
                    threshold = EXPIRATION_THRESHOLDS.get(level, 0.1)
                    if memory.effective_salience < threshold:
                        candidates.append(
                            ExpirationCandidate(
                                memory_id=memory.memory_id,
                                user_id=memory.user_id,
                                temporal_level=memory.temporal_level,
                                valid_until=memory.valid_until or now,
                                reason="low_salience",
                            )
                        )

    return candidates[:batch_size]


@activity.defn
async def archive_memory(
    candidate: ExpirationCandidate,
) -> ExpirationResult:
    """Archive an expired memory.

    This is an idempotent operation - if the memory has already
    been archived, it returns success without modifying.

    In production, archiving would move to cold storage.
    For now, we mark as expired and set valid_until.

    Args:
        candidate: The expiration candidate

    Returns:
        Result of the archival attempt
    """
    activity.logger.info(f"Archiving memory {candidate.memory_id} (reason: {candidate.reason})")

    db = get_database()

    async with db.session() as session:
        repo = MemoryRepository(session)

        # Get current memory state
        result = await repo.get(candidate.memory_id)
        if not result.is_ok:
            return ExpirationResult(
                memory_id=candidate.memory_id,
                success=False,
                error=f"Memory not found: {result.error.message}",
            )

        memory = result.value

        # Check if already archived (idempotency)
        if memory.valid_until and memory.valid_until < datetime.now(UTC):
            activity.logger.info(f"Memory {candidate.memory_id} already archived")
            return ExpirationResult(
                memory_id=candidate.memory_id,
                success=True,
                archived=True,
            )

        # Archive by setting valid_until to now
        from sqlalchemy import update

        from mind.infrastructure.postgres.models import MemoryModel

        now = datetime.now(UTC)
        await session.execute(
            update(MemoryModel)
            .where(MemoryModel.memory_id == candidate.memory_id)
            .values(
                valid_until=now,
                updated_at=now,
            )
        )
        await session.commit()

    return ExpirationResult(
        memory_id=candidate.memory_id,
        success=True,
        archived=True,
    )


@activity.defn
async def notify_expiration(
    result: ExpirationResult,
    candidate: ExpirationCandidate,
) -> bool:
    """Publish event for a memory expiration.

    This activity handles the event publishing for expired memories.
    It's separated from the archival to allow for retry without
    re-archiving.

    Args:
        result: The expiration result
        candidate: The expiration candidate (for metadata)

    Returns:
        True if notification succeeded
    """
    if not result.success or not result.archived:
        return False

    activity.logger.info(f"Publishing expiration event for {result.memory_id}")

    try:
        event = MemoryExpired(
            memory_id=result.memory_id,
            temporal_level=candidate.temporal_level,
            expired_at=datetime.now(UTC),
            valid_until=candidate.valid_until,
            reason=candidate.reason,
        )

        from mind.infrastructure.nats.client import get_nats_client
        from mind.infrastructure.nats.publisher import EventPublisher

        client = await get_nats_client()
        publisher = EventPublisher(client)

        await publisher.publish_event(
            event=event,
            user_id=candidate.user_id,
        )

        return True

    except Exception as e:
        activity.logger.warning(f"Failed to publish expiration event: {e}")
        return False


# =============================================================================
# Memory Consolidation Activities
# =============================================================================


@dataclass
class ConsolidationCandidate:
    """A group of similar memories that can be consolidated."""

    primary_memory_id: UUID
    similar_memory_ids: list[UUID]
    user_id: UUID
    temporal_level: TemporalLevel
    similarity_scores: list[float]  # Similarity of each similar memory to primary
    reason: str  # Description of why these are candidates


@dataclass
class ConsolidationResult:
    """Result of a memory consolidation attempt."""

    consolidated_memory_id: UUID | None
    source_memory_ids: list[UUID]
    success: bool
    memories_merged: int = 0
    error: str | None = None


# Consolidation thresholds
CONSOLIDATION_THRESHOLDS = {
    # Minimum similarity score to consider merging
    "min_similarity": 0.85,
    # Minimum age in hours before considering consolidation
    "min_age_hours": 48,
    # Maximum memories to merge at once
    "max_merge_size": 5,
    # Minimum memories needed to trigger consolidation
    "min_group_size": 2,
}


@activity.defn
async def find_consolidation_candidates(
    user_id: UUID,
    batch_size: int = 50,
) -> list[ConsolidationCandidate]:
    """Find groups of similar memories that can be consolidated.

    This activity identifies memories with high semantic similarity that
    could be merged to reduce redundancy while preserving information.

    The algorithm:
    1. Fetch memories with embeddings
    2. Find clusters of similar memories using cosine similarity
    3. Return groups that exceed similarity threshold

    Args:
        user_id: User whose memories to evaluate
        batch_size: Maximum candidate groups to return

    Returns:
        List of consolidation candidate groups
    """
    activity.logger.info(f"Finding consolidation candidates for user {user_id}")

    candidates = []
    db = get_database()

    async with db.session() as session:
        # Query memories with embeddings, grouped by temporal level
        from sqlalchemy import text

        stmt = text("""
            SELECT
                memory_id, user_id, content, content_type, temporal_level,
                valid_from, valid_until, base_salience, outcome_adjustment,
                retrieval_count, decision_count, positive_outcomes, negative_outcomes,
                promoted_from_level, promotion_timestamp, created_at, updated_at,
                embedding
            FROM memories
            WHERE user_id = :user_id
                AND embedding IS NOT NULL
                AND (valid_until IS NULL OR valid_until > :now)
                AND created_at < :min_age
            ORDER BY temporal_level, created_at DESC
            LIMIT :limit
        """)

        now = datetime.now(UTC)
        min_age = now - timedelta(hours=CONSOLIDATION_THRESHOLDS["min_age_hours"])

        result = await session.execute(
            stmt,
            {
                "user_id": str(user_id),
                "now": now,
                "min_age": min_age,
                "limit": batch_size * 10,  # Over-fetch for clustering
            },
        )

        rows = result.fetchall()
        if len(rows) < CONSOLIDATION_THRESHOLDS["min_group_size"]:
            activity.logger.info("Not enough memories for consolidation")
            return []

        # Group memories by temporal level for fair comparison
        level_groups: dict[int, list] = {}
        for row in rows:
            level = row.temporal_level
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(row)

        # Find similar memory clusters within each level
        for level, memories in level_groups.items():
            if len(memories) < CONSOLIDATION_THRESHOLDS["min_group_size"]:
                continue

            # Track which memories have been assigned to a group
            assigned = set()

            for i, primary in enumerate(memories):
                if primary.memory_id in assigned:
                    continue

                similar_ids = []
                similarity_scores = []

                # Compare with other memories in same level
                for j, candidate in enumerate(memories):
                    if i == j or candidate.memory_id in assigned:
                        continue

                    # Calculate cosine similarity between embeddings
                    if primary.embedding and candidate.embedding:
                        similarity = _cosine_similarity(primary.embedding, candidate.embedding)
                        if similarity >= CONSOLIDATION_THRESHOLDS["min_similarity"]:
                            similar_ids.append(candidate.memory_id)
                            similarity_scores.append(similarity)

                            if len(similar_ids) >= CONSOLIDATION_THRESHOLDS["max_merge_size"] - 1:
                                break

                # Only create candidate if we found similar memories
                if len(similar_ids) >= CONSOLIDATION_THRESHOLDS["min_group_size"] - 1:
                    assigned.add(primary.memory_id)
                    assigned.update(similar_ids)

                    candidates.append(
                        ConsolidationCandidate(
                            primary_memory_id=primary.memory_id,
                            similar_memory_ids=similar_ids,
                            user_id=user_id,
                            temporal_level=TemporalLevel(level),
                            similarity_scores=similarity_scores,
                            reason=f"Found {len(similar_ids)} similar memories "
                            f"(avg similarity: {sum(similarity_scores) / len(similarity_scores):.2f})",
                        )
                    )

                    if len(candidates) >= batch_size:
                        break

            if len(candidates) >= batch_size:
                break

    activity.logger.info(f"Found {len(candidates)} consolidation candidates")
    return candidates


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


@activity.defn
async def consolidate_memories(
    candidate: ConsolidationCandidate,
) -> ConsolidationResult:
    """Consolidate a group of similar memories into one.

    This is an idempotent operation - if the primary memory has already
    absorbed the similar memories, it returns success.

    The consolidation strategy:
    1. Keep the primary memory's content as the base
    2. Append unique information from similar memories
    3. Combine salience (average with boost for agreement)
    4. Sum retrieval/decision counts
    5. Archive the merged memories

    Args:
        candidate: The consolidation candidate

    Returns:
        Result of the consolidation attempt
    """
    activity.logger.info(
        f"Consolidating {len(candidate.similar_memory_ids) + 1} memories "
        f"for primary {candidate.primary_memory_id}"
    )

    db = get_database()
    all_memory_ids = [candidate.primary_memory_id] + candidate.similar_memory_ids

    async with db.session() as session:
        repo = MemoryRepository(session)

        # Fetch all memories to consolidate
        memories = []
        for memory_id in all_memory_ids:
            result = await repo.get(memory_id)
            if result.is_ok:
                memories.append(result.value)
            else:
                activity.logger.warning(f"Memory {memory_id} not found")

        if len(memories) < 2:
            return ConsolidationResult(
                consolidated_memory_id=None,
                source_memory_ids=all_memory_ids,
                success=False,
                error="Not enough valid memories to consolidate",
            )

        primary = memories[0]
        similar = memories[1:]

        # Build consolidated content
        consolidated_content = _merge_content(primary.content, [m.content for m in similar])

        # Calculate combined metrics
        total_retrieval_count = sum(m.retrieval_count for m in memories)
        total_decision_count = sum(m.decision_count for m in memories)
        total_positive = sum(m.positive_outcomes for m in memories)
        total_negative = sum(m.negative_outcomes for m in memories)

        # Average salience with boost for agreement
        avg_salience = sum(m.base_salience for m in memories) / len(memories)
        avg_outcome_adj = sum(m.outcome_adjustment for m in memories) / len(memories)

        # Agreement boost: if all memories have positive outcomes, boost salience
        all_positive = all(
            m.positive_outcomes > m.negative_outcomes
            for m in memories
            if m.positive_outcomes + m.negative_outcomes > 0
        )
        salience_boost = 0.05 if all_positive else 0.0

        # Create consolidated memory
        from sqlalchemy import update

        from mind.infrastructure.postgres.models import MemoryModel

        now = datetime.now(UTC)
        new_memory_id = uuid4()

        # Insert new consolidated memory
        new_memory = MemoryModel(
            memory_id=new_memory_id,
            user_id=candidate.user_id,
            content=consolidated_content,
            content_type=primary.content_type,
            temporal_level=candidate.temporal_level.value,
            valid_from=min(m.valid_from for m in memories),
            valid_until=None,  # Consolidated memories don't expire by default
            base_salience=min(1.0, avg_salience + salience_boost),
            outcome_adjustment=avg_outcome_adj,
            retrieval_count=total_retrieval_count,
            decision_count=total_decision_count,
            positive_outcomes=total_positive,
            negative_outcomes=total_negative,
            created_at=now,
            updated_at=now,
        )

        session.add(new_memory)

        # Archive source memories (set valid_until to now)
        for memory_id in all_memory_ids:
            await session.execute(
                update(MemoryModel)
                .where(MemoryModel.memory_id == memory_id)
                .values(
                    valid_until=now,
                    updated_at=now,
                )
            )

        await session.commit()

    activity.logger.info(
        f"Created consolidated memory {new_memory_id} from {len(memories)} sources"
    )

    return ConsolidationResult(
        consolidated_memory_id=new_memory_id,
        source_memory_ids=all_memory_ids,
        success=True,
        memories_merged=len(memories),
    )


def _merge_content(primary_content: str, similar_contents: list[str]) -> str:
    """Merge multiple memory contents into one.

    Strategy:
    - Keep primary content as the base
    - Extract unique sentences from similar contents
    - Append unique information (limited to avoid bloat)
    """
    # Simple sentence-based deduplication
    primary_sentences = {s.strip() for s in primary_content.split(".") if s.strip()}

    unique_additions = []
    for content in similar_contents:
        for sentence in content.split("."):
            sentence = sentence.strip()
            if sentence and sentence not in primary_sentences:
                # Check if it's substantially different (not just minor rewording)
                if not any(_sentence_similar(sentence, p) for p in primary_sentences):
                    unique_additions.append(sentence)
                    primary_sentences.add(sentence)

    # Limit additions to avoid content explosion
    max_additions = 3
    if unique_additions:
        additions = ". ".join(unique_additions[:max_additions])
        return f"{primary_content.rstrip('.')}. {additions}."

    return primary_content


def _sentence_similar(s1: str, s2: str, threshold: float = 0.7) -> bool:
    """Check if two sentences are similar using simple word overlap."""
    words1 = set(s1.lower().split())
    words2 = set(s2.lower().split())

    if not words1 or not words2:
        return False

    overlap = len(words1 & words2)
    min_len = min(len(words1), len(words2))

    return overlap / min_len >= threshold


@activity.defn
async def notify_consolidation(
    result: ConsolidationResult,
    user_id: UUID,
) -> bool:
    """Publish event for a successful memory consolidation.

    This activity handles the event publishing for consolidated memories.

    Args:
        result: The consolidation result
        user_id: User ID for the event

    Returns:
        True if notification succeeded
    """
    if not result.success or not result.consolidated_memory_id:
        return False

    activity.logger.info(f"Publishing consolidation event for {result.consolidated_memory_id}")

    try:
        from mind.core.events.memory import MemoryConsolidated
        from mind.infrastructure.nats.client import get_nats_client
        from mind.infrastructure.nats.publisher import EventPublisher

        client = await get_nats_client()
        publisher = EventPublisher(client)

        event = MemoryConsolidated(
            consolidated_memory_id=result.consolidated_memory_id,
            source_memory_ids=result.source_memory_ids,
            memories_merged=result.memories_merged,
        )

        await publisher.publish_event(
            event=event,
            user_id=user_id,
        )

        return True

    except Exception as e:
        activity.logger.warning(f"Failed to publish consolidation event: {e}")
        return False


# =============================================================================
# Outcome Analysis Activities
# =============================================================================


@dataclass
class OutcomeAnalysis:
    """Analysis of decision outcomes for a time period."""

    user_id: UUID
    period_start: datetime
    period_end: datetime
    total_decisions: int
    positive_outcomes: int
    negative_outcomes: int
    neutral_outcomes: int
    success_rate: float
    top_performing_memories: list[tuple[UUID, float]]  # memory_id, contribution
    underperforming_memories: list[tuple[UUID, float]]
    decision_type_breakdown: dict[str, dict]  # type -> {total, positive, negative}


@dataclass
class OutcomeAnalysisResult:
    """Result of outcome analysis activity."""

    success: bool
    analysis: OutcomeAnalysis | None = None
    error: str | None = None


@activity.defn
async def analyze_user_outcomes(
    user_id: UUID,
    days_back: int = 7,
) -> OutcomeAnalysisResult:
    """Analyze decision outcomes for a user over a time period.

    This activity aggregates outcome data to identify:
    - Overall success rate
    - Top contributing memories
    - Underperforming memories
    - Decision type patterns

    Args:
        user_id: User to analyze
        days_back: Number of days to look back

    Returns:
        OutcomeAnalysisResult with analysis data
    """
    activity.logger.info(f"Analyzing outcomes for user {user_id}, last {days_back} days")

    db = get_database()
    now = datetime.now(UTC)
    period_start = now - timedelta(days=days_back)

    async with db.session() as session:
        from sqlalchemy import text

        # Query decision traces with outcomes
        stmt = text("""
            SELECT
                trace_id, decision_type, outcome_quality, outcome_signal,
                memory_ids, memory_scores, created_at
            FROM decision_traces
            WHERE user_id = :user_id
                AND created_at >= :period_start
                AND outcome_observed = true
            ORDER BY created_at DESC
        """)

        result = await session.execute(
            stmt,
            {
                "user_id": str(user_id),
                "period_start": period_start,
            },
        )

        rows = result.fetchall()

        if not rows:
            return OutcomeAnalysisResult(
                success=True,
                analysis=OutcomeAnalysis(
                    user_id=user_id,
                    period_start=period_start,
                    period_end=now,
                    total_decisions=0,
                    positive_outcomes=0,
                    negative_outcomes=0,
                    neutral_outcomes=0,
                    success_rate=0.0,
                    top_performing_memories=[],
                    underperforming_memories=[],
                    decision_type_breakdown={},
                ),
            )

        # Aggregate outcomes
        total = len(rows)
        positive = 0
        negative = 0
        neutral = 0
        memory_contributions: dict[str, list[float]] = {}
        type_breakdown: dict[str, dict] = {}

        for row in rows:
            quality = row.outcome_quality
            if quality > 0.6:
                positive += 1
            elif quality < 0.4:
                negative += 1
            else:
                neutral += 1

            # Track decision type breakdown
            dt = row.decision_type or "unknown"
            if dt not in type_breakdown:
                type_breakdown[dt] = {"total": 0, "positive": 0, "negative": 0}
            type_breakdown[dt]["total"] += 1
            if quality > 0.6:
                type_breakdown[dt]["positive"] += 1
            elif quality < 0.4:
                type_breakdown[dt]["negative"] += 1

            # Track memory contributions
            if row.memory_scores:
                for mid, score in row.memory_scores.items():
                    if mid not in memory_contributions:
                        memory_contributions[mid] = []
                    # Weight contribution by outcome quality
                    memory_contributions[mid].append(quality * score)

        # Calculate memory performance
        memory_perf = [
            (UUID(mid), sum(scores) / len(scores))
            for mid, scores in memory_contributions.items()
            if len(scores) >= 2  # Require at least 2 data points
        ]
        memory_perf.sort(key=lambda x: x[1], reverse=True)

        success_rate = positive / total if total > 0 else 0.0

        analysis = OutcomeAnalysis(
            user_id=user_id,
            period_start=period_start,
            period_end=now,
            total_decisions=total,
            positive_outcomes=positive,
            negative_outcomes=negative,
            neutral_outcomes=neutral,
            success_rate=success_rate,
            top_performing_memories=memory_perf[:5],
            underperforming_memories=memory_perf[-5:][::-1] if len(memory_perf) > 5 else [],
            decision_type_breakdown=type_breakdown,
        )

    activity.logger.info(f"Analysis complete: {total} decisions, {success_rate:.1%} success rate")

    return OutcomeAnalysisResult(success=True, analysis=analysis)


@dataclass
class SalienceAdjustmentBatch:
    """Batch of salience adjustments to apply."""

    memory_id: UUID
    adjustment: float
    reason: str


@activity.defn
async def apply_salience_adjustments(
    adjustments: list[SalienceAdjustmentBatch],
) -> int:
    """Apply batch salience adjustments to memories.

    This activity efficiently updates multiple memory saliences
    based on outcome analysis.

    Args:
        adjustments: List of adjustments to apply

    Returns:
        Number of successfully updated memories
    """
    if not adjustments:
        return 0

    activity.logger.info(f"Applying {len(adjustments)} salience adjustments")

    db = get_database()
    updated = 0

    async with db.session() as session:
        from sqlalchemy import update

        from mind.infrastructure.postgres.models import MemoryModel

        for adj in adjustments:
            try:
                await session.execute(
                    update(MemoryModel)
                    .where(MemoryModel.memory_id == adj.memory_id)
                    .values(
                        outcome_adjustment=MemoryModel.outcome_adjustment + adj.adjustment,
                        updated_at=datetime.now(UTC),
                    )
                )
                updated += 1
            except Exception as e:
                activity.logger.warning(f"Failed to adjust {adj.memory_id}: {e}")

        await session.commit()

    activity.logger.info(f"Applied {updated}/{len(adjustments)} adjustments")
    return updated


# =============================================================================
# Confidence Calibration Activities
# =============================================================================


@dataclass
class CalibrationBucket:
    """A bucket of predictions grouped by confidence level."""

    confidence_min: float
    confidence_max: float
    total_predictions: int
    correct_predictions: int
    expected_accuracy: float  # midpoint of bucket
    actual_accuracy: float  # observed accuracy


@dataclass
class CalibrationResult:
    """Result of confidence calibration analysis."""

    success: bool
    buckets: list[CalibrationBucket] = field(default_factory=list)
    overall_calibration_error: float = 0.0  # ECE
    adjustment_factor: float = 1.0  # Factor to multiply confidence by
    error: str | None = None


@activity.defn
async def analyze_confidence_calibration(
    user_id: UUID,
    days_back: int = 30,
    bucket_count: int = 10,
) -> CalibrationResult:
    """Analyze confidence calibration for a user's predictions.

    This activity computes the Expected Calibration Error (ECE) by:
    1. Grouping predictions into confidence buckets
    2. Comparing expected vs actual accuracy for each bucket
    3. Computing weighted calibration error

    Args:
        user_id: User to analyze
        days_back: Number of days to look back
        bucket_count: Number of confidence buckets

    Returns:
        CalibrationResult with bucket analysis and adjustment factor
    """
    activity.logger.info(f"Analyzing confidence calibration for user {user_id}")

    db = get_database()
    now = datetime.now(UTC)
    period_start = now - timedelta(days=days_back)

    async with db.session() as session:
        from sqlalchemy import text

        # Query predictions with outcomes
        stmt = text("""
            SELECT
                confidence_score, outcome_quality
            FROM decision_traces
            WHERE user_id = :user_id
                AND created_at >= :period_start
                AND outcome_observed = true
                AND confidence_score IS NOT NULL
        """)

        result = await session.execute(
            stmt,
            {
                "user_id": str(user_id),
                "period_start": period_start,
            },
        )

        rows = result.fetchall()

        if not rows:
            return CalibrationResult(
                success=True,
                buckets=[],
                overall_calibration_error=0.0,
                adjustment_factor=1.0,
            )

        # Create calibration buckets
        bucket_size = 1.0 / bucket_count
        buckets: dict[int, list[tuple[float, float]]] = {i: [] for i in range(bucket_count)}

        for row in rows:
            confidence = row.confidence_score
            outcome = row.outcome_quality

            # Determine bucket (0-9 for 10 buckets)
            bucket_idx = min(int(confidence / bucket_size), bucket_count - 1)
            buckets[bucket_idx].append((confidence, outcome))

        # Compute metrics for each bucket
        calibration_buckets = []
        total_samples = len(rows)
        ece = 0.0

        for i in range(bucket_count):
            bucket_data = buckets[i]
            if not bucket_data:
                continue

            conf_min = i * bucket_size
            conf_max = (i + 1) * bucket_size
            expected = (conf_min + conf_max) / 2

            # A prediction is "correct" if outcome > 0.5
            correct = sum(1 for _, outcome in bucket_data if outcome > 0.5)
            total = len(bucket_data)
            actual = correct / total if total > 0 else 0.0

            calibration_buckets.append(
                CalibrationBucket(
                    confidence_min=conf_min,
                    confidence_max=conf_max,
                    total_predictions=total,
                    correct_predictions=correct,
                    expected_accuracy=expected,
                    actual_accuracy=actual,
                )
            )

            # ECE contribution: weighted absolute difference
            bucket_weight = total / total_samples
            ece += bucket_weight * abs(actual - expected)

        # Calculate adjustment factor
        # If actual < expected, we're overconfident (factor < 1)
        # If actual > expected, we're underconfident (factor > 1)
        total_expected = sum(b.expected_accuracy * b.total_predictions for b in calibration_buckets)
        total_actual = sum(b.actual_accuracy * b.total_predictions for b in calibration_buckets)

        if total_expected > 0:
            adjustment_factor = total_actual / total_expected
            adjustment_factor = max(0.5, min(1.5, adjustment_factor))  # Clamp
        else:
            adjustment_factor = 1.0

    activity.logger.info(
        f"Calibration analysis complete: ECE={ece:.3f}, adjustment={adjustment_factor:.3f}"
    )

    return CalibrationResult(
        success=True,
        buckets=calibration_buckets,
        overall_calibration_error=ece,
        adjustment_factor=adjustment_factor,
    )


@dataclass
class CalibrationSettings:
    """Calibration settings for a user."""

    user_id: UUID
    adjustment_factor: float
    last_calibrated: datetime
    sample_count: int
    calibration_error: float


@activity.defn
async def update_calibration_settings(
    user_id: UUID,
    adjustment_factor: float,
    sample_count: int,
    calibration_error: float,
) -> bool:
    """Update calibration settings for a user.

    In production, this would store calibration data in a user settings table.
    For now, we log and return success.

    Args:
        user_id: User to update
        adjustment_factor: New confidence adjustment factor
        sample_count: Number of samples used
        calibration_error: Computed ECE

    Returns:
        True if successful
    """
    activity.logger.info(
        f"Updating calibration for user {user_id}: "
        f"factor={adjustment_factor:.3f}, ECE={calibration_error:.3f}, samples={sample_count}"
    )

    # In production, store in database
    # For now, just log and return success
    return True


# =============================================================================
# Pattern Extraction Activities
# =============================================================================


@dataclass
class DecisionPatternData:
    """Data extracted from a decision for pattern analysis."""

    trace_id: UUID
    user_id: UUID
    decision_type: str
    outcome_quality: float
    memory_contents: list[str]  # Used for categorization
    memory_ids: list[UUID]
    created_at: datetime


@dataclass
class ExtractedPattern:
    """A pattern extracted from decision outcomes."""

    pattern_key: str
    pattern_type: str
    trigger_category: str
    response_strategy: str
    observation_count: int
    user_count: int
    average_outcome: float
    first_observed: datetime
    last_observed: datetime


@dataclass
class PatternExtractionResult:
    """Result of pattern extraction activity."""

    success: bool
    patterns_found: int = 0
    patterns: list[ExtractedPattern] = field(default_factory=list)
    error: str | None = None


@activity.defn
async def find_successful_decisions(
    user_id: UUID,
    days_back: int = 30,
    min_outcome_quality: float = 0.6,
) -> list[DecisionPatternData]:
    """Find successful decisions for pattern extraction.

    This activity queries decision traces with positive outcomes
    to identify potential patterns.

    Args:
        user_id: User to analyze (or None for all users)
        days_back: Number of days to look back
        min_outcome_quality: Minimum outcome quality threshold

    Returns:
        List of decision data for pattern extraction
    """
    activity.logger.info(f"Finding successful decisions for user {user_id}")

    db = get_database()
    now = datetime.now(UTC)
    period_start = now - timedelta(days=days_back)

    async with db.session() as session:
        from sqlalchemy import text

        stmt = text("""
            SELECT
                trace_id, user_id, decision_type, outcome_quality,
                memory_ids, created_at
            FROM decision_traces
            WHERE user_id = :user_id
                AND created_at >= :period_start
                AND outcome_observed = true
                AND outcome_quality >= :min_quality
            ORDER BY outcome_quality DESC
            LIMIT 500
        """)

        result = await session.execute(
            stmt,
            {
                "user_id": str(user_id),
                "period_start": period_start,
                "min_quality": min_outcome_quality,
            },
        )

        rows = result.fetchall()

        if not rows:
            activity.logger.info("No successful decisions found")
            return []

        # Fetch memory contents for categorization
        decisions = []
        for row in rows:
            memory_ids = row.memory_ids or []
            memory_contents = []

            # Fetch memory contents for this decision
            if memory_ids:
                from mind.infrastructure.postgres.repositories import MemoryRepository

                repo = MemoryRepository(session)
                for mid in memory_ids[:10]:  # Limit to avoid excessive queries
                    mem_result = await repo.get(UUID(mid) if isinstance(mid, str) else mid)
                    if mem_result.is_ok:
                        memory_contents.append(mem_result.value.content)

            decisions.append(
                DecisionPatternData(
                    trace_id=row.trace_id if isinstance(row.trace_id, UUID) else UUID(row.trace_id),
                    user_id=row.user_id if isinstance(row.user_id, UUID) else UUID(row.user_id),
                    decision_type=row.decision_type or "unknown",
                    outcome_quality=row.outcome_quality,
                    memory_contents=memory_contents,
                    memory_ids=[UUID(m) if isinstance(m, str) else m for m in memory_ids],
                    created_at=row.created_at,
                )
            )

    activity.logger.info(f"Found {len(decisions)} successful decisions")
    return decisions


@activity.defn
async def extract_patterns_from_decisions(
    decisions: list[DecisionPatternData],
) -> PatternExtractionResult:
    """Extract patterns from successful decisions.

    Uses the PatternExtractor to identify recurring patterns
    that lead to positive outcomes.

    Args:
        decisions: List of decision data to analyze

    Returns:
        PatternExtractionResult with extracted patterns
    """
    if not decisions:
        return PatternExtractionResult(
            success=True,
            patterns_found=0,
            patterns=[],
        )

    activity.logger.info(f"Extracting patterns from {len(decisions)} decisions")

    try:
        from mind.core.decision.models import DecisionTrace, Outcome
        from mind.core.federation.extractor import (
            CategoryMapper,
            ExtractionContext,
            PatternExtractor,
        )
        from mind.core.federation.models import PrivacyBudget

        # Create extractor with relaxed thresholds for single-user analysis
        # (Patterns will be validated again before federation)
        budget = PrivacyBudget(
            min_users=1,  # Allow single user patterns locally
            min_observations=5,
        )
        extractor = PatternExtractor(privacy_budget=budget)
        category_mapper = CategoryMapper()

        for decision in decisions:
            # Create minimal trace for extraction
            trace = DecisionTrace(
                trace_id=decision.trace_id,
                user_id=decision.user_id,
                query="",  # Not needed for pattern extraction
                decision_type=decision.decision_type,
                memory_ids=decision.memory_ids,
            )

            outcome = Outcome(
                quality=decision.outcome_quality,
                signal=1.0 if decision.outcome_quality > 0.6 else 0.0,
            )

            # Categorize memory contents
            categories = category_mapper.categorize_memories(decision.memory_contents)

            context = ExtractionContext(
                trace=trace,
                outcome=outcome,
                memory_categories=categories,
            )

            extractor.extract_from_outcome(context)

        # Get patterns that meet thresholds
        ready_patterns = extractor.get_ready_patterns()

        extracted = []
        for pattern in ready_patterns:
            extracted.append(
                ExtractedPattern(
                    pattern_key=f"{pattern.trigger_category}:{pattern.response_strategy}",
                    pattern_type=pattern.pattern_type.value,
                    trigger_category=pattern.trigger_category,
                    response_strategy=pattern.response_strategy,
                    observation_count=pattern.observation_count,
                    user_count=pattern.user_count,
                    average_outcome=pattern.average_outcome,
                    first_observed=pattern.created_at,
                    last_observed=pattern.created_at,
                )
            )

        activity.logger.info(f"Extracted {len(extracted)} patterns")

        return PatternExtractionResult(
            success=True,
            patterns_found=len(extracted),
            patterns=extracted,
        )

    except Exception as e:
        activity.logger.error(f"Pattern extraction failed: {e}")
        return PatternExtractionResult(
            success=False,
            error=str(e),
        )


@dataclass
class SanitizedPatternData:
    """A sanitized pattern safe for federation."""

    pattern_id: UUID
    pattern_type: str
    trigger_category: str
    response_strategy: str
    outcome_improvement: float
    confidence: float
    source_count: int
    user_count: int
    epsilon: float


@dataclass
class SanitizationResult:
    """Result of pattern sanitization activity."""

    success: bool
    patterns_sanitized: int = 0
    patterns: list[SanitizedPatternData] = field(default_factory=list)
    patterns_rejected: int = 0
    error: str | None = None


@activity.defn
async def sanitize_patterns(
    patterns: list[ExtractedPattern],
    min_users: int = 10,
    min_observations: int = 100,
) -> SanitizationResult:
    """Sanitize patterns for cross-user federation.

    Applies differential privacy to patterns that meet
    privacy thresholds.

    Args:
        patterns: List of extracted patterns to sanitize
        min_users: Minimum unique users required
        min_observations: Minimum observations required

    Returns:
        SanitizationResult with sanitized patterns
    """
    if not patterns:
        return SanitizationResult(
            success=True,
            patterns_sanitized=0,
        )

    activity.logger.info(f"Sanitizing {len(patterns)} patterns")

    try:
        from mind.core.federation.models import Pattern, PatternType, PrivacyBudget
        from mind.core.federation.sanitizer import DifferentialPrivacySanitizer

        budget = PrivacyBudget(
            min_users=min_users,
            min_observations=min_observations,
        )
        sanitizer = DifferentialPrivacySanitizer(privacy_budget=budget)

        sanitized = []
        rejected = 0

        for ext_pattern in patterns:
            # Convert to Pattern for sanitization
            pattern = Pattern(
                pattern_id=uuid4(),
                pattern_type=PatternType(ext_pattern.pattern_type),
                trigger_category=ext_pattern.trigger_category,
                response_strategy=ext_pattern.response_strategy,
                average_outcome=ext_pattern.average_outcome,
                observation_count=ext_pattern.observation_count,
                user_count=ext_pattern.user_count,
            )

            # Check if meets thresholds
            if not budget.is_satisfied(pattern.user_count, pattern.observation_count):
                activity.logger.debug(
                    f"Pattern {ext_pattern.pattern_key} rejected: "
                    f"users={pattern.user_count}, obs={pattern.observation_count}"
                )
                rejected += 1
                continue

            # Sanitize
            result = sanitizer.sanitize(pattern)
            if result.is_ok:
                san = result.value
                sanitized.append(
                    SanitizedPatternData(
                        pattern_id=san.pattern_id,
                        pattern_type=san.pattern_type.value,
                        trigger_category=san.trigger_category,
                        response_strategy=san.response_strategy,
                        outcome_improvement=san.outcome_improvement,
                        confidence=san.confidence,
                        source_count=san.source_count,
                        user_count=san.user_count,
                        epsilon=san.epsilon,
                    )
                )
            else:
                rejected += 1

        activity.logger.info(
            f"Sanitization complete: {len(sanitized)} sanitized, {rejected} rejected"
        )

        return SanitizationResult(
            success=True,
            patterns_sanitized=len(sanitized),
            patterns=sanitized,
            patterns_rejected=rejected,
        )

    except Exception as e:
        activity.logger.error(f"Pattern sanitization failed: {e}")
        return SanitizationResult(
            success=False,
            error=str(e),
        )


@activity.defn
async def store_federated_patterns(
    patterns: list[SanitizedPatternData],
) -> int:
    """Store sanitized patterns for federation.

    In production, this would store patterns in a shared
    pattern database accessible to all users.

    Args:
        patterns: List of sanitized patterns to store

    Returns:
        Number of patterns successfully stored
    """
    if not patterns:
        return 0

    activity.logger.info(f"Storing {len(patterns)} federated patterns")

    # In production, store in database
    # For now, log and return success count
    stored = 0
    for pattern in patterns:
        activity.logger.info(
            f"Stored pattern: {pattern.trigger_category} -> {pattern.response_strategy} "
            f"(confidence={pattern.confidence:.2f}, improvement={pattern.outcome_improvement:.2f})"
        )
        stored += 1

    return stored


# =============================================================================
# Reindex Embeddings Activities
# =============================================================================


@dataclass
class ReindexCandidate:
    """A memory that needs embedding reindexing."""

    memory_id: UUID
    user_id: UUID
    content: str
    has_embedding: bool


@dataclass
class ReindexBatch:
    """A batch of memories with their new embeddings."""

    memory_ids: list[UUID]
    embeddings: list[list[float]]
    errors: list[str] = field(default_factory=list)


@dataclass
class ReindexResult:
    """Result of a reindex operation."""

    success: bool
    memories_updated: int = 0
    memories_failed: int = 0
    error: str | None = None


@dataclass
class ReindexProgress:
    """Progress of the reindex workflow."""

    total_memories: int
    processed: int
    succeeded: int
    failed: int
    batches_completed: int


@activity.defn
async def count_memories_for_reindex(
    user_id: UUID | None = None,
    include_existing: bool = False,
) -> int:
    """Count memories that need embedding reindexing.

    Args:
        user_id: Optional user ID to filter by (None = all users)
        include_existing: If True, also count memories that already have embeddings

    Returns:
        Count of memories needing reindex
    """
    activity.logger.info(
        f"Counting memories for reindex (user={user_id}, include_existing={include_existing})"
    )

    db = get_database()

    async with db.session() as session:
        repo = MemoryRepository(session)

        if include_existing:
            # Count all active memories
            from datetime import UTC, datetime

            from sqlalchemy import func, select

            from mind.infrastructure.postgres.models import MemoryModel

            stmt = select(func.count(MemoryModel.memory_id))

            if user_id is not None:
                stmt = stmt.where(MemoryModel.user_id == user_id)

            now = datetime.now(UTC)
            stmt = stmt.where((MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > now))

            result = await session.execute(stmt)
            count = result.scalar() or 0
        else:
            # Count only memories without embeddings
            count = await repo.count_memories_needing_embeddings(user_id)

    activity.logger.info(f"Found {count} memories for reindex")
    return count


@activity.defn
async def find_memories_for_reindex(
    user_id: UUID | None = None,
    include_existing: bool = False,
    batch_size: int = 100,
    offset: int = 0,
) -> list[ReindexCandidate]:
    """Find memories that need embedding reindexing.

    Args:
        user_id: Optional user ID to filter by
        include_existing: If True, include memories that already have embeddings
        batch_size: Maximum memories to return
        offset: Offset for pagination

    Returns:
        List of reindex candidates
    """
    activity.logger.info(
        f"Finding memories for reindex (user={user_id}, batch={batch_size}, offset={offset})"
    )

    db = get_database()
    candidates = []

    async with db.session() as session:
        repo = MemoryRepository(session)
        result = await repo.find_memories_for_reindex(
            user_id=user_id,
            include_with_embeddings=include_existing,
            limit=batch_size,
            offset=offset,
        )

        if result.is_ok:
            for memory in result.value:
                candidates.append(
                    ReindexCandidate(
                        memory_id=memory.memory_id,
                        user_id=memory.user_id,
                        content=memory.content,
                        has_embedding=False,  # We're only getting ones without embeddings
                    )
                )

    activity.logger.info(f"Found {len(candidates)} memories for reindex")
    return candidates


@activity.defn
async def generate_embeddings_for_batch(
    candidates: list[ReindexCandidate],
) -> ReindexBatch:
    """Generate embeddings for a batch of memories.

    Args:
        candidates: List of reindex candidates

    Returns:
        ReindexBatch with memory IDs and their embeddings
    """
    if not candidates:
        return ReindexBatch(memory_ids=[], embeddings=[])

    activity.logger.info(f"Generating embeddings for {len(candidates)} memories")

    from mind.observability.metrics import metrics
    from mind.services.embedding import get_embedding_service

    embedding_service = get_embedding_service()

    # Extract content and generate embeddings
    contents = [c.content for c in candidates]
    memory_ids = [c.memory_id for c in candidates]
    embeddings = []
    errors = []

    # Process in sub-batches for API limits
    sub_batch_size = 50
    for i in range(0, len(contents), sub_batch_size):
        sub_contents = contents[i : i + sub_batch_size]
        memory_ids[i : i + sub_batch_size]

        result = await embedding_service.embed_batch(sub_contents)

        if result.is_ok:
            embeddings.extend(result.value)
            # Record metrics
            for _ in sub_contents:
                metrics.record_embedding_cache_miss()  # New embeddings
        else:
            # Log error but continue with other batches
            error_msg = (
                f"Failed to generate embeddings for batch {i // sub_batch_size}: {result.error}"
            )
            activity.logger.error(error_msg)
            errors.append(error_msg)
            # Add None placeholders for failed embeddings
            embeddings.extend([None] * len(sub_contents))

    # Filter out failed embeddings
    valid_ids = []
    valid_embeddings = []
    for mid, emb in zip(memory_ids, embeddings, strict=False):
        if emb is not None:
            valid_ids.append(mid)
            valid_embeddings.append(emb)

    activity.logger.info(
        f"Generated {len(valid_embeddings)} embeddings, {len(memory_ids) - len(valid_ids)} failed"
    )

    return ReindexBatch(
        memory_ids=valid_ids,
        embeddings=valid_embeddings,
        errors=errors,
    )


@activity.defn
async def update_memory_embeddings(
    batch: ReindexBatch,
) -> ReindexResult:
    """Update memory embeddings in the database.

    Args:
        batch: Batch of memory IDs and embeddings to update

    Returns:
        ReindexResult with success/failure counts
    """
    if not batch.memory_ids:
        return ReindexResult(success=True, memories_updated=0)

    activity.logger.info(f"Updating embeddings for {len(batch.memory_ids)} memories")

    db = get_database()
    updated = 0
    failed = 0
    errors = list(batch.errors)  # Copy existing errors

    async with db.session() as session:
        repo = MemoryRepository(session)

        for memory_id, embedding in zip(batch.memory_ids, batch.embeddings, strict=False):
            try:
                result = await repo.update_embedding(memory_id, embedding)
                if result.is_ok:
                    updated += 1
                else:
                    failed += 1
                    errors.append(f"Memory {memory_id}: {result.error.message}")
            except Exception as e:
                failed += 1
                errors.append(f"Memory {memory_id}: {str(e)}")

        await session.commit()

    activity.logger.info(f"Updated {updated} embeddings, {failed} failed")

    return ReindexResult(
        success=failed == 0,
        memories_updated=updated,
        memories_failed=failed,
        error="; ".join(errors) if errors else None,
    )


# =============================================================================
# USER DISCOVERY ACTIVITIES
# =============================================================================


@activity.defn
async def get_active_user_ids(
    days_active: int = 30,
    limit: int = 1000,
) -> list[UUID]:
    """Get user IDs that have been active recently.

    This is used by the ScheduledGardenerWorkflow to determine which
    users need gardening tasks run.

    Args:
        days_active: Consider users active if they have activity in this window
        limit: Maximum number of users to return

    Returns:
        List of active user IDs
    """
    activity.logger.info(f"Finding active users (last {days_active} days, limit {limit})")

    from sqlalchemy import select

    from mind.infrastructure.postgres.models import DecisionTraceModel, MemoryModel

    db = get_database()

    async with db.session() as session:
        # Find users with recent memories or decisions
        cutoff_date = datetime.now(UTC) - timedelta(days=days_active)

        # Get users with recent memories
        memory_query = (
            select(MemoryModel.user_id).where(MemoryModel.created_at >= cutoff_date).distinct()
        )

        # Get users with recent decisions
        decision_query = (
            select(DecisionTraceModel.user_id)
            .where(DecisionTraceModel.created_at >= cutoff_date)
            .distinct()
        )

        # Combine and deduplicate
        memory_result = await session.execute(memory_query)
        decision_result = await session.execute(decision_query)

        memory_users = {row[0] for row in memory_result.fetchall()}
        decision_users = {row[0] for row in decision_result.fetchall()}

        all_users = list(memory_users | decision_users)[:limit]

    activity.logger.info(f"Found {len(all_users)} active users")
    return all_users
