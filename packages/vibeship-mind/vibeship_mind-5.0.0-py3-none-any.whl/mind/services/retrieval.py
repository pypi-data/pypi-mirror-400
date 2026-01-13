"""Memory retrieval service with multi-source fusion."""

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import structlog
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from mind.core.errors import Result
from mind.core.memory.fusion import (
    RankedMemory,
    weighted_rrf,
)
from mind.core.memory.models import Memory, TemporalLevel
from mind.core.memory.retrieval import RetrievalRequest, RetrievalResult, ScoredMemory
from mind.infrastructure.embeddings.openai import OpenAIEmbedder
from mind.infrastructure.postgres.models import MemoryModel

if TYPE_CHECKING:
    from mind.infrastructure.falkordb.repository import CausalGraphRepository
    from mind.infrastructure.qdrant.repository import QdrantVectorRepository

logger = structlog.get_logger()
tracer = trace.get_tracer("mind.retrieval")


class RetrievalService:
    """Multi-source memory retrieval with RRF fusion.

    Combines:
    - Vector similarity (semantic search)
    - Keyword/BM25 (full-text search)
    - Salience ranking (outcome-weighted)
    - Recency decay (time-based)
    - Causal success (historical outcome quality from causal graph)
    """

    # Source weights for weighted RRF
    WEIGHTS = {
        "vector": 1.0,  # Semantic similarity
        "keyword": 0.8,  # Full-text match
        "salience": 0.6,  # Outcome-weighted importance
        "recency": 0.4,  # Time decay
        "causal": 0.7,  # Historical causal success rate
    }

    def __init__(
        self,
        session: AsyncSession,
        embedder: OpenAIEmbedder | None = None,
        causal_graph: "CausalGraphRepository | None" = None,
        qdrant_repo: "QdrantVectorRepository | None" = None,
    ):
        self._session = session
        self._embedder = embedder
        self._causal_graph = causal_graph
        self._qdrant_repo = qdrant_repo

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> Result[RetrievalResult]:
        """Retrieve memories using multi-source fusion.

        Args:
            request: Retrieval parameters

        Returns:
            Result with fused retrieval results
        """
        with tracer.start_as_current_span("retrieve_memories") as span:
            span.set_attribute("user_id", str(request.user_id))
            span.set_attribute("query_length", len(request.query))
            span.set_attribute("limit", request.limit)

            start_time = datetime.now(UTC)
            log = logger.bind(
                user_id=str(request.user_id),
                query_length=len(request.query),
                limit=request.limit,
            )

            # Run retrieval sources in parallel
            sources_to_run = []
            source_names = []

            # Vector search (if embedder available)
            if self._embedder:
                sources_to_run.append(self._vector_search(request))
                source_names.append("vector")

            # Keyword search (always available)
            sources_to_run.append(self._keyword_search(request))
            source_names.append("keyword")

            # Salience ranking (always available)
            sources_to_run.append(self._salience_search(request))
            source_names.append("salience")

            # Recency ranking (always available)
            sources_to_run.append(self._recency_search(request))
            source_names.append("recency")

            # Causal success (if causal graph available)
            if self._causal_graph:
                sources_to_run.append(self._causal_search(request))
                source_names.append("causal")

            span.set_attribute("sources_enabled", source_names)

            # Execute in parallel
            with tracer.start_as_current_span("parallel_search"):
                results = await asyncio.gather(*sources_to_run, return_exceptions=True)

            # Collect successful results
            ranked_lists: list[tuple[list[RankedMemory], float]] = []
            successful_sources = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    log.warning(
                        "retrieval_source_failed", source=source_names[i], error=str(result)
                    )
                    continue
                if result:
                    source_name = result[0].source if result else "unknown"
                    weight = self.WEIGHTS.get(source_name, 1.0)
                    ranked_lists.append((result, weight))
                    successful_sources.append(source_name)

            span.set_attribute("sources_succeeded", successful_sources)

            if not ranked_lists:
                log.warning("no_retrieval_results")
                span.set_attribute("result_count", 0)
                return Result.ok(
                    RetrievalResult(
                        retrieval_id=uuid4(),
                        memories=[],
                        query=request.query,
                        latency_ms=0,
                    )
                )

            # Fuse results
            with tracer.start_as_current_span("rrf_fusion") as fusion_span:
                fusion_span.set_attribute("ranked_lists_count", len(ranked_lists))
                fused = weighted_rrf(
                    ranked_lists=ranked_lists,
                    k=60,
                    limit=request.limit,
                )
                fusion_span.set_attribute("fused_count", len(fused))

            # Convert to ScoredMemory
            scored_memories = []
            for i, fm in enumerate(fused):
                scored = ScoredMemory(
                    memory=fm.memory,
                    vector_score=fm.raw_scores.get("vector"),
                    keyword_score=fm.raw_scores.get("keyword"),
                    recency_score=fm.raw_scores.get("recency"),
                    salience_score=fm.raw_scores.get("salience"),
                    causal_score=fm.raw_scores.get("causal"),
                    final_score=fm.rrf_score,
                    rank=i + 1,
                )
                scored_memories.append(scored)

            latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

            span.set_attribute("result_count", len(scored_memories))
            span.set_attribute("latency_ms", round(latency_ms, 2))
            span.set_status(Status(StatusCode.OK))

            log.info(
                "retrieval_complete",
                result_count=len(scored_memories),
                sources=len(ranked_lists),
                latency_ms=round(latency_ms, 2),
            )

            return Result.ok(
                RetrievalResult(
                    retrieval_id=uuid4(),
                    memories=scored_memories,
                    query=request.query,
                    latency_ms=latency_ms,
                )
            )

    async def _vector_search(
        self,
        request: RetrievalRequest,
    ) -> list[RankedMemory]:
        """Search by vector similarity.

        Uses Qdrant if configured, otherwise falls back to pgvector.
        """
        with tracer.start_as_current_span("vector_search") as span:
            if not self._embedder:
                span.set_attribute("skipped", True)
                return []

            # Generate query embedding
            with tracer.start_as_current_span("generate_embedding"):
                embed_result = await self._embedder.embed(request.query)
                if embed_result.is_err:
                    logger.warning("embedding_failed", error=str(embed_result.error))
                    span.set_attribute("embedding_failed", True)
                    return []

            query_embedding = embed_result.value
            span.set_attribute("embedding_dim", len(query_embedding))

            # Use Qdrant if available, otherwise pgvector
            if self._qdrant_repo:
                span.set_attribute("backend", "qdrant")
                return await self._vector_search_qdrant(request, query_embedding, span)
            else:
                span.set_attribute("backend", "pgvector")
                return await self._vector_search_pgvector(request, query_embedding, span)

    async def _vector_search_qdrant(
        self,
        request: RetrievalRequest,
        query_embedding: list[float],
        span,
    ) -> list[RankedMemory]:
        """Search using Qdrant vector database."""
        with tracer.start_as_current_span("qdrant_search"):
            search_result = await self._qdrant_repo.search(
                user_id=request.user_id,
                query_vector=query_embedding,
                limit=request.limit * 2,  # Over-fetch for fusion
                temporal_levels=request.temporal_levels,
                min_salience=request.min_salience,
            )

            if search_result.is_err:
                logger.warning(
                    "qdrant_search_failed",
                    error=str(search_result.error),
                )
                span.set_attribute("qdrant_failed", True)
                return []

            vector_results = search_result.value

        if not vector_results:
            span.set_attribute("result_count", 0)
            return []

        # Fetch full Memory objects from PostgreSQL by ID
        memory_ids = [r.memory_id for r in vector_results]
        score_map = {r.memory_id: r.score for r in vector_results}

        with tracer.start_as_current_span("fetch_memories_by_id"):
            stmt = select(MemoryModel).where(MemoryModel.memory_id.in_(memory_ids))
            result = await self._session.execute(stmt)
            models = {m.memory_id: m for m in result.scalars().all()}

        # Build ranked list preserving Qdrant's ordering
        ranked = []
        for i, vr in enumerate(vector_results):
            model = models.get(vr.memory_id)
            if model:
                memory = self._model_to_memory(model)
                ranked.append(
                    RankedMemory(
                        memory=memory,
                        rank=i + 1,
                        source="vector",
                        raw_score=score_map[vr.memory_id],
                    )
                )

        span.set_attribute("result_count", len(ranked))
        return ranked

    async def _vector_search_pgvector(
        self,
        request: RetrievalRequest,
        query_embedding: list[float],
        span,
    ) -> list[RankedMemory]:
        """Search using pgvector in PostgreSQL."""
        # Convert embedding to PostgreSQL vector format string
        # asyncpg doesn't support named params with ::vector cast
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        now = datetime.now(UTC)
        limit = request.limit * 2  # Over-fetch for fusion

        stmt = text(f"""
            SELECT
                memory_id, user_id, content, content_type, temporal_level,
                valid_from, valid_until, base_salience, outcome_adjustment,
                retrieval_count, decision_count, positive_outcomes, negative_outcomes,
                promoted_from_level, promotion_timestamp, created_at, updated_at,
                1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM memories
            WHERE user_id = :user_id
                AND embedding IS NOT NULL
                AND (valid_until IS NULL OR valid_until > :now)
                AND valid_from <= :now
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT :limit
        """)

        result = await self._session.execute(
            stmt,
            {
                "user_id": str(request.user_id),
                "now": now,
                "limit": limit,
            },
        )

        ranked = []
        for i, row in enumerate(result.fetchall()):
            memory = self._row_to_memory(row)
            ranked.append(
                RankedMemory(
                    memory=memory,
                    rank=i + 1,
                    source="vector",
                    raw_score=float(row.similarity),
                )
            )

        span.set_attribute("result_count", len(ranked))
        return ranked

    async def _keyword_search(
        self,
        request: RetrievalRequest,
    ) -> list[RankedMemory]:
        """Search by keyword/full-text."""
        # Build dynamic SQL with optional filters
        base_sql = """
            SELECT
                memory_id, user_id, content, content_type, temporal_level,
                valid_from, valid_until, base_salience, outcome_adjustment,
                retrieval_count, decision_count, positive_outcomes, negative_outcomes,
                promoted_from_level, promotion_timestamp, created_at, updated_at,
                ts_rank(to_tsvector('english', content), plainto_tsquery('english', :query)) as rank_score
            FROM memories
            WHERE user_id = :user_id
                AND to_tsvector('english', content) @@ plainto_tsquery('english', :query)
                AND (valid_until IS NULL OR valid_until > :now)
                AND valid_from <= :now
        """

        params = {
            "user_id": str(request.user_id),
            "query": request.query,
            "now": datetime.now(UTC),
            "limit": request.limit * 2,
        }

        # Add temporal level filter
        if request.temporal_levels:
            levels = [level.value for level in request.temporal_levels]
            base_sql += " AND temporal_level = ANY(:temporal_levels)"
            params["temporal_levels"] = levels

        # Add min salience filter
        if request.min_salience > 0:
            base_sql += " AND (base_salience + outcome_adjustment) >= :min_salience"
            params["min_salience"] = request.min_salience

        base_sql += " ORDER BY rank_score DESC LIMIT :limit"

        stmt = text(base_sql)
        result = await self._session.execute(stmt, params)

        ranked = []
        for i, row in enumerate(result.fetchall()):
            memory = self._row_to_memory(row)
            ranked.append(
                RankedMemory(
                    memory=memory,
                    rank=i + 1,
                    source="keyword",
                    raw_score=float(row.rank_score) if row.rank_score else 0.0,
                )
            )

        return ranked

    async def _salience_search(
        self,
        request: RetrievalRequest,
    ) -> list[RankedMemory]:
        """Search by outcome-weighted salience."""
        stmt = (
            select(MemoryModel)
            .where(MemoryModel.user_id == request.user_id)
            .where(
                (MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > datetime.now(UTC))
            )
            .where(MemoryModel.valid_from <= datetime.now(UTC))
            .order_by((MemoryModel.base_salience + MemoryModel.outcome_adjustment).desc())
            .limit(request.limit * 2)
        )

        if request.temporal_levels:
            levels = [level.value for level in request.temporal_levels]
            stmt = stmt.where(MemoryModel.temporal_level.in_(levels))

        if request.min_salience > 0:
            stmt = stmt.where(
                (MemoryModel.base_salience + MemoryModel.outcome_adjustment) >= request.min_salience
            )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        ranked = []
        for i, model in enumerate(models):
            memory = self._model_to_memory(model)
            ranked.append(
                RankedMemory(
                    memory=memory,
                    rank=i + 1,
                    source="salience",
                    raw_score=memory.effective_salience,
                )
            )

        return ranked

    async def _recency_search(
        self,
        request: RetrievalRequest,
    ) -> list[RankedMemory]:
        """Search by recency (most recent first)."""
        stmt = (
            select(MemoryModel)
            .where(MemoryModel.user_id == request.user_id)
            .where(
                (MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > datetime.now(UTC))
            )
            .where(MemoryModel.valid_from <= datetime.now(UTC))
            .order_by(MemoryModel.created_at.desc())
            .limit(request.limit * 2)
        )

        # Apply temporal level filter
        if request.temporal_levels:
            levels = [level.value for level in request.temporal_levels]
            stmt = stmt.where(MemoryModel.temporal_level.in_(levels))

        # Apply min salience filter
        if request.min_salience > 0:
            stmt = stmt.where(
                (MemoryModel.base_salience + MemoryModel.outcome_adjustment) >= request.min_salience
            )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        now = datetime.now(UTC)
        ranked = []
        for i, model in enumerate(models):
            memory = self._model_to_memory(model)
            # Recency score: exponential decay over 7 days
            age_hours = (now - memory.created_at).total_seconds() / 3600
            recency_score = 1.0 / (1.0 + age_hours / 168)  # 168 hours = 7 days
            ranked.append(
                RankedMemory(
                    memory=memory,
                    rank=i + 1,
                    source="recency",
                    raw_score=recency_score,
                )
            )

        return ranked

    async def _causal_search(
        self,
        request: RetrievalRequest,
    ) -> list[RankedMemory]:
        """Search by historical causal success rate.

        Ranks memories by how often they have led to positive outcomes
        in past decisions. Uses the causal graph to calculate success rates.
        """
        if not self._causal_graph:
            return []

        # First get all memories for the user (we need to check each one's success rate)
        stmt = (
            select(MemoryModel)
            .where(MemoryModel.user_id == request.user_id)
            .where(
                (MemoryModel.valid_until.is_(None)) | (MemoryModel.valid_until > datetime.now(UTC))
            )
            .where(MemoryModel.valid_from <= datetime.now(UTC))
            .limit(request.limit * 3)  # Over-fetch for filtering
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        # Get causal success rates for each memory
        memories_with_scores = []
        for model in models:
            memory = self._model_to_memory(model)
            try:
                rate_result = await self._causal_graph.get_memory_success_rate(memory.memory_id)
                if rate_result.is_ok:
                    rate_data = rate_result.value
                    # Only include memories with at least some outcome history
                    if rate_data["total_outcomes"] > 0:
                        # Combine success rate with outcome count for confidence
                        raw_score = rate_data["success_rate"]
                        # Boost score slightly for memories with more evidence
                        confidence_boost = min(0.2, rate_data["total_outcomes"] / 50.0)
                        memories_with_scores.append((memory, raw_score + confidence_boost))
            except Exception as e:
                logger.debug(
                    "causal_rate_lookup_failed",
                    memory_id=str(memory.memory_id),
                    error=str(e),
                )
                continue

        # Sort by success rate (descending)
        memories_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Convert to RankedMemory
        ranked = []
        for i, (memory, score) in enumerate(memories_with_scores[: request.limit * 2]):
            ranked.append(
                RankedMemory(
                    memory=memory,
                    rank=i + 1,
                    source="causal",
                    raw_score=score,
                )
            )

        return ranked

    def _model_to_memory(self, model: MemoryModel) -> Memory:
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
            promoted_from_level=(
                TemporalLevel(model.promoted_from_level) if model.promoted_from_level else None
            ),
            promotion_timestamp=model.promotion_timestamp,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _row_to_memory(self, row) -> Memory:
        """Convert raw SQL row to domain object."""
        return Memory(
            memory_id=row.memory_id,
            user_id=row.user_id,
            content=row.content,
            content_type=row.content_type,
            temporal_level=TemporalLevel(row.temporal_level),
            valid_from=row.valid_from,
            valid_until=row.valid_until,
            base_salience=row.base_salience,
            outcome_adjustment=row.outcome_adjustment,
            retrieval_count=row.retrieval_count,
            decision_count=row.decision_count,
            positive_outcomes=row.positive_outcomes,
            negative_outcomes=row.negative_outcomes,
            promoted_from_level=(
                TemporalLevel(row.promoted_from_level) if row.promoted_from_level else None
            ),
            promotion_timestamp=row.promotion_timestamp,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
