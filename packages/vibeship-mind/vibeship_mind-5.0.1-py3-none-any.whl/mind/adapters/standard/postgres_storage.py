"""PostgreSQL storage adapters for memories and decisions.

These adapters implement IMemoryStorage and IDecisionStorage using
PostgreSQL with asyncpg for async database access.
"""

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

import asyncpg

from ...core.memory.models import Memory, TemporalLevel
from ...core.decision.models import DecisionTrace, Outcome, SalienceUpdate
from ...ports.storage import IMemoryStorage, IDecisionStorage


class PostgresMemoryStorage(IMemoryStorage):
    """PostgreSQL implementation of memory storage.

    Uses asyncpg connection pool for efficient async database access.
    Supports pgvector for embedding storage (indexed separately).
    """

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with a connection pool.

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool

    async def store(self, memory: Memory) -> Memory:
        """Store a memory, returning it with server-assigned fields."""
        # Generate ID if not provided
        memory_id = memory.memory_id or uuid4()
        now = datetime.now(UTC)

        query = """
            INSERT INTO memories (
                memory_id, user_id, content, content_type,
                temporal_level, valid_from, valid_until,
                base_salience, outcome_adjustment,
                retrieval_count, decision_count,
                positive_outcomes, negative_outcomes,
                promoted_from_level, promotion_timestamp,
                created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9,
                $10, $11, $12, $13, $14, $15, $16, $17
            )
            RETURNING *
        """

        row = await self.pool.fetchrow(
            query,
            memory_id,
            memory.user_id,
            memory.content,
            memory.content_type,
            memory.temporal_level.name.lower(),  # Store as 'immediate', 'situational', etc.
            memory.valid_from,
            memory.valid_until,
            memory.base_salience,
            memory.outcome_adjustment,
            memory.retrieval_count,
            memory.decision_count,
            memory.positive_outcomes,
            memory.negative_outcomes,
            memory.promoted_from_level.name.lower() if memory.promoted_from_level else None,
            memory.promotion_timestamp,
            now,
            now,
        )

        return self._row_to_memory(row)

    async def get(self, memory_id: UUID) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        query = "SELECT * FROM memories WHERE memory_id = $1"
        row = await self.pool.fetchrow(query, memory_id)

        if row is None:
            return None

        return self._row_to_memory(row)

    async def get_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
        temporal_level: Optional[TemporalLevel] = None,
        min_salience: float = 0.0,
        valid_only: bool = True,
    ) -> list[Memory]:
        """Get memories for a user with filtering."""
        conditions = ["user_id = $1"]
        params: list = [user_id]
        param_idx = 2

        if temporal_level is not None:
            conditions.append(f"temporal_level = ${param_idx}")
            params.append(temporal_level.name.lower())
            param_idx += 1

        if min_salience > 0:
            conditions.append(
                f"(base_salience + outcome_adjustment) >= ${param_idx}"
            )
            params.append(min_salience)
            param_idx += 1

        if valid_only:
            conditions.append(
                "(valid_until IS NULL OR valid_until > NOW())"
            )

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        query = f"""
            SELECT * FROM memories
            WHERE {where_clause}
            ORDER BY (base_salience + outcome_adjustment) DESC, created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """

        rows = await self.pool.fetch(query, *params)
        return [self._row_to_memory(row) for row in rows]

    async def update_salience(
        self,
        memory_id: UUID,
        adjustment: float,
    ) -> Memory:
        """Adjust a memory's outcome_adjustment."""
        query = """
            UPDATE memories
            SET outcome_adjustment = LEAST(1.0, GREATEST(-1.0,
                    outcome_adjustment + $2)),
                updated_at = NOW()
            WHERE memory_id = $1
            RETURNING *
        """

        row = await self.pool.fetchrow(query, memory_id, adjustment)

        if row is None:
            raise ValueError(f"Memory {memory_id} not found")

        return self._row_to_memory(row)

    async def increment_retrieval_count(self, memory_id: UUID) -> None:
        """Increment a memory's retrieval count."""
        query = """
            UPDATE memories
            SET retrieval_count = retrieval_count + 1,
                updated_at = NOW()
            WHERE memory_id = $1
        """
        await self.pool.execute(query, memory_id)

    async def increment_decision_count(
        self,
        memory_id: UUID,
        positive: bool,
    ) -> None:
        """Increment a memory's decision and outcome counts."""
        if positive:
            query = """
                UPDATE memories
                SET decision_count = decision_count + 1,
                    positive_outcomes = positive_outcomes + 1,
                    updated_at = NOW()
                WHERE memory_id = $1
            """
        else:
            query = """
                UPDATE memories
                SET decision_count = decision_count + 1,
                    negative_outcomes = negative_outcomes + 1,
                    updated_at = NOW()
                WHERE memory_id = $1
            """
        await self.pool.execute(query, memory_id)

    async def expire(self, memory_id: UUID) -> None:
        """Mark a memory as expired."""
        query = """
            UPDATE memories
            SET valid_until = NOW(),
                updated_at = NOW()
            WHERE memory_id = $1
        """
        await self.pool.execute(query, memory_id)

    async def promote(
        self,
        memory_id: UUID,
        new_level: TemporalLevel,
    ) -> Memory:
        """Promote a memory to a higher temporal level."""
        # First check current level
        current = await self.get(memory_id)
        if current is None:
            raise ValueError(f"Memory {memory_id} not found")

        if new_level.value <= current.temporal_level.value:
            raise ValueError(
                f"Cannot promote from {current.temporal_level} to {new_level}"
            )

        query = """
            UPDATE memories
            SET temporal_level = $2,
                promoted_from_level = $3,
                promotion_timestamp = NOW(),
                updated_at = NOW()
            WHERE memory_id = $1
            RETURNING *
        """

        row = await self.pool.fetchrow(
            query,
            memory_id,
            new_level.name.lower(),
            current.temporal_level.name.lower(),
        )

        return self._row_to_memory(row)

    async def get_candidates_for_promotion(
        self,
        user_id: UUID,
        level: TemporalLevel,
        min_salience: float = 0.7,
        min_positive_ratio: float = 0.6,
        limit: int = 50,
    ) -> list[Memory]:
        """Get memories that are candidates for promotion."""
        query = """
            SELECT * FROM memories
            WHERE user_id = $1
              AND temporal_level = $2
              AND (valid_until IS NULL OR valid_until > NOW())
              AND (base_salience + outcome_adjustment) >= $3
              AND decision_count > 0
              AND (positive_outcomes::float / NULLIF(positive_outcomes + negative_outcomes, 0)) >= $4
            ORDER BY (base_salience + outcome_adjustment) DESC
            LIMIT $5
        """

        rows = await self.pool.fetch(
            query,
            user_id,
            level.name.lower(),
            min_salience,
            min_positive_ratio,
            limit,
        )

        return [self._row_to_memory(row) for row in rows]

    async def get_expired_candidates(
        self,
        user_id: UUID,
        level: TemporalLevel,
        older_than_days: int,
        limit: int = 100,
    ) -> list[Memory]:
        """Get memories that should be expired based on age."""
        query = """
            SELECT * FROM memories
            WHERE user_id = $1
              AND temporal_level = $2
              AND (valid_until IS NULL OR valid_until > NOW())
              AND created_at < NOW() - INTERVAL '1 day' * $3
            ORDER BY created_at ASC
            LIMIT $4
        """

        rows = await self.pool.fetch(
            query,
            user_id,
            level.name.lower(),
            older_than_days,
            limit,
        )

        return [self._row_to_memory(row) for row in rows]

    def _row_to_memory(self, row: asyncpg.Record) -> Memory:
        """Convert a database row to a Memory object."""
        # Parse temporal_level from string (e.g., 'immediate' -> TemporalLevel.IMMEDIATE)
        temporal_level = self._parse_temporal_level(row["temporal_level"])

        promoted_from = None
        if row["promoted_from_level"] is not None:
            promoted_from = self._parse_temporal_level(row["promoted_from_level"])

        return Memory(
            memory_id=row["memory_id"],
            user_id=row["user_id"],
            content=row["content"],
            content_type=row["content_type"],
            temporal_level=temporal_level,
            valid_from=row["valid_from"],
            valid_until=row["valid_until"],
            base_salience=row["base_salience"],
            outcome_adjustment=row["outcome_adjustment"],
            retrieval_count=row["retrieval_count"],
            decision_count=row["decision_count"],
            positive_outcomes=row["positive_outcomes"],
            negative_outcomes=row["negative_outcomes"],
            promoted_from_level=promoted_from,
            promotion_timestamp=row["promotion_timestamp"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _parse_temporal_level(self, value: str | int) -> TemporalLevel:
        """Parse temporal level from database value.

        Handles both string names ('immediate') and int values (1).
        """
        if isinstance(value, int):
            return TemporalLevel(value)
        # String name - convert to enum
        return TemporalLevel[value.upper()]


class PostgresDecisionStorage(IDecisionStorage):
    """PostgreSQL implementation of decision trace storage."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with a connection pool.

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool

    async def store_trace(self, trace: DecisionTrace) -> DecisionTrace:
        """Store a new decision trace."""
        query = """
            INSERT INTO decision_traces (
                trace_id, user_id, session_id,
                memory_ids, memory_scores,
                decision_type, decision_summary, confidence,
                alternatives_count, created_at,
                outcome_observed, outcome_quality,
                outcome_timestamp, outcome_signal
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                $11, $12, $13, $14
            )
            RETURNING *
        """

        import json

        row = await self.pool.fetchrow(
            query,
            trace.trace_id,
            trace.user_id,
            trace.session_id,
            [str(m) for m in trace.memory_ids],
            json.dumps(trace.memory_scores),
            trace.decision_type,
            trace.decision_summary,
            trace.confidence,
            trace.alternatives_count,
            trace.created_at,
            trace.outcome_observed,
            trace.outcome_quality,
            trace.outcome_timestamp,
            trace.outcome_signal,
        )

        return self._row_to_trace(row)

    async def get_trace(self, trace_id: UUID) -> Optional[DecisionTrace]:
        """Retrieve a decision trace by ID."""
        query = "SELECT * FROM decision_traces WHERE trace_id = $1"
        row = await self.pool.fetchrow(query, trace_id)

        if row is None:
            return None

        return self._row_to_trace(row)

    async def record_outcome(
        self,
        trace_id: UUID,
        outcome: Outcome,
    ) -> DecisionTrace:
        """Record an outcome for a decision trace."""
        query = """
            UPDATE decision_traces
            SET outcome_observed = TRUE,
                outcome_quality = $2,
                outcome_timestamp = $3,
                outcome_signal = $4
            WHERE trace_id = $1
            RETURNING *
        """

        row = await self.pool.fetchrow(
            query,
            trace_id,
            outcome.quality,
            outcome.observed_at,
            outcome.signal,
        )

        if row is None:
            raise ValueError(f"Trace {trace_id} not found")

        return self._row_to_trace(row)

    async def get_traces_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
        with_outcomes_only: bool = False,
        decision_type: Optional[str] = None,
    ) -> list[DecisionTrace]:
        """Get decision traces for a user."""
        conditions = ["user_id = $1"]
        params: list = [user_id]
        param_idx = 2

        if with_outcomes_only:
            conditions.append("outcome_observed = TRUE")

        if decision_type is not None:
            conditions.append(f"decision_type = ${param_idx}")
            params.append(decision_type)
            param_idx += 1

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        query = f"""
            SELECT * FROM decision_traces
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """

        rows = await self.pool.fetch(query, *params)
        return [self._row_to_trace(row) for row in rows]

    async def get_traces_for_memory(
        self,
        memory_id: UUID,
        *,
        limit: int = 50,
        with_outcomes_only: bool = True,
    ) -> list[DecisionTrace]:
        """Get decision traces that used a specific memory."""
        memory_id_str = str(memory_id)

        if with_outcomes_only:
            query = """
                SELECT * FROM decision_traces
                WHERE $1 = ANY(memory_ids)
                  AND outcome_observed = TRUE
                ORDER BY created_at DESC
                LIMIT $2
            """
        else:
            query = """
                SELECT * FROM decision_traces
                WHERE $1 = ANY(memory_ids)
                ORDER BY created_at DESC
                LIMIT $2
            """

        rows = await self.pool.fetch(query, memory_id_str, limit)
        return [self._row_to_trace(row) for row in rows]

    async def get_pending_outcomes(
        self,
        user_id: UUID,
        older_than_hours: int = 24,
        limit: int = 50,
    ) -> list[DecisionTrace]:
        """Get traces that don't have outcomes yet."""
        query = """
            SELECT * FROM decision_traces
            WHERE user_id = $1
              AND outcome_observed = FALSE
              AND created_at < NOW() - INTERVAL '1 hour' * $2
            ORDER BY created_at ASC
            LIMIT $3
        """

        rows = await self.pool.fetch(query, user_id, older_than_hours, limit)
        return [self._row_to_trace(row) for row in rows]

    async def store_salience_update(self, update: SalienceUpdate) -> None:
        """Store a salience update record."""
        query = """
            INSERT INTO salience_updates (
                memory_id, trace_id, delta, reason, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """

        await self.pool.execute(
            query,
            update.memory_id,
            update.trace_id,
            update.delta,
            update.reason,
        )

    async def get_salience_updates_for_memory(
        self,
        memory_id: UUID,
        limit: int = 50,
    ) -> list[SalienceUpdate]:
        """Get salience update history for a memory."""
        query = """
            SELECT * FROM salience_updates
            WHERE memory_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """

        rows = await self.pool.fetch(query, memory_id, limit)

        return [
            SalienceUpdate(
                memory_id=row["memory_id"],
                trace_id=row["trace_id"],
                delta=row["delta"],
                reason=row["reason"],
            )
            for row in rows
        ]

    def _row_to_trace(self, row: asyncpg.Record) -> DecisionTrace:
        """Convert a database row to a DecisionTrace object."""
        import json

        return DecisionTrace(
            trace_id=row["trace_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            memory_ids=[UUID(m) for m in row["memory_ids"]],
            memory_scores=json.loads(row["memory_scores"]),
            decision_type=row["decision_type"],
            decision_summary=row["decision_summary"],
            confidence=row["confidence"],
            alternatives_count=row["alternatives_count"],
            created_at=row["created_at"],
            outcome_observed=row["outcome_observed"],
            outcome_quality=row["outcome_quality"],
            outcome_timestamp=row["outcome_timestamp"],
            outcome_signal=row["outcome_signal"],
        )
