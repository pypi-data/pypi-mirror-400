"""Integration tests for PostgreSQL storage adapters (Embedded).

These tests verify PostgresMemoryStorage and PostgresDecisionStorage
work correctly against an embedded PostgreSQL database.

Note: pgvector is not available with embedded PostgreSQL, so vector-related
tests are in the standard integration tests.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.integration.embedded.conftest import requires_embedded_pg


pytestmark = [pytest.mark.integration, requires_embedded_pg]


# =============================================================================
# PostgresMemoryStorage Integration Tests (Embedded)
# =============================================================================


class TestPostgresMemoryStorageEmbedded:
    """Integration tests for PostgresMemoryStorage using embedded PostgreSQL."""

    @pytest_asyncio.fixture
    async def storage(self, clean_db):
        """Create a PostgresMemoryStorage instance."""
        from mind.adapters.standard.postgres_storage import PostgresMemoryStorage
        return PostgresMemoryStorage(pool=clean_db)

    @pytest.mark.asyncio
    async def test_store_and_retrieve_memory(self, storage, test_user):
        """Test storing and retrieving a memory."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="User prefers detailed technical explanations",
            content_type="preference",
            temporal_level=TemporalLevel.IDENTITY,
            base_salience=0.8,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )

        saved = await storage.store(memory)

        assert saved.memory_id == memory.memory_id
        assert saved.content == memory.content

        retrieved = await storage.get(memory.memory_id)

        assert retrieved is not None
        assert retrieved.memory_id == memory.memory_id
        assert retrieved.content == memory.content
        assert retrieved.base_salience == 0.8

    @pytest.mark.asyncio
    async def test_update_memory(self, storage, test_user):
        """Test updating a memory."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Original content",
            content_type="observation",
            temporal_level=TemporalLevel.SESSION,
            base_salience=0.5,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )

        await storage.store(memory)

        updated_memory = Memory(
            memory_id=memory.memory_id,
            user_id=test_user,
            content="Updated content",
            content_type="observation",
            temporal_level=TemporalLevel.SEASONAL,
            base_salience=0.7,
            outcome_adjustment=0.1,
            valid_from=memory.valid_from,
        )

        result = await storage.update(updated_memory)

        assert result.content == "Updated content"
        assert result.base_salience == 0.7
        assert result.outcome_adjustment == 0.1

    @pytest.mark.asyncio
    async def test_delete_memory(self, storage, test_user):
        """Test deleting a memory."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Memory to delete",
            content_type="observation",
            temporal_level=TemporalLevel.IMMEDIATE,
            base_salience=0.5,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )

        await storage.store(memory)

        result = await storage.delete(memory.memory_id)

        assert result is True

        retrieved = await storage.get(memory.memory_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_list_memories_by_user(self, storage, test_user):
        """Test listing memories for a user."""
        from mind.core.memory.models import Memory, TemporalLevel

        for i in range(5):
            memory = Memory(
                memory_id=uuid4(),
                user_id=test_user,
                content=f"Memory {i}",
                content_type="observation",
                temporal_level=TemporalLevel.SESSION,
                base_salience=0.5,
                outcome_adjustment=0.0,
                valid_from=datetime.now(UTC),
            )
            await storage.store(memory)

        memories = await storage.list_by_user(test_user, limit=10)

        assert len(memories) == 5

    @pytest.mark.asyncio
    async def test_list_memories_with_temporal_level_filter(self, storage, test_user):
        """Test listing memories filtered by temporal level."""
        from mind.core.memory.models import Memory, TemporalLevel

        for level in [TemporalLevel.IMMEDIATE, TemporalLevel.SESSION, TemporalLevel.IDENTITY]:
            memory = Memory(
                memory_id=uuid4(),
                user_id=test_user,
                content=f"Memory at {level.name}",
                content_type="observation",
                temporal_level=level,
                base_salience=0.5,
                outcome_adjustment=0.0,
                valid_from=datetime.now(UTC),
            )
            await storage.store(memory)

        identity_memories = await storage.list_by_user(
            test_user,
            temporal_level=TemporalLevel.IDENTITY,
        )

        assert len(identity_memories) == 1
        assert identity_memories[0].temporal_level == TemporalLevel.IDENTITY

    @pytest.mark.asyncio
    async def test_adjust_salience(self, storage, test_user):
        """Test adjusting memory salience."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Memory for salience test",
            content_type="preference",
            temporal_level=TemporalLevel.IDENTITY,
            base_salience=0.5,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )

        await storage.store(memory)

        result = await storage.adjust_salience(
            memory.memory_id,
            delta=0.15,
            reason="positive_outcome",
        )

        assert result.outcome_adjustment == 0.15

        # Verify persistence
        retrieved = await storage.get(memory.memory_id)
        assert retrieved.outcome_adjustment == 0.15

    @pytest.mark.asyncio
    async def test_record_retrieval(self, storage, test_user):
        """Test recording memory retrieval."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Memory for retrieval test",
            content_type="fact",
            temporal_level=TemporalLevel.SEASONAL,
            base_salience=0.6,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
            retrieval_count=0,
        )

        await storage.store(memory)

        result = await storage.record_retrieval(memory.memory_id)

        assert result.retrieval_count == 1

    @pytest.mark.asyncio
    async def test_health_check(self, storage):
        """Test storage health check."""
        result = await storage.health_check()
        assert result is True


# =============================================================================
# PostgresDecisionStorage Integration Tests (Embedded)
# =============================================================================


class TestPostgresDecisionStorageEmbedded:
    """Integration tests for PostgresDecisionStorage using embedded PostgreSQL."""

    @pytest_asyncio.fixture
    async def storage(self, clean_db):
        """Create a PostgresDecisionStorage instance."""
        from mind.adapters.standard.postgres_storage import PostgresDecisionStorage
        return PostgresDecisionStorage(pool=clean_db)

    @pytest.mark.asyncio
    async def test_store_and_retrieve_trace(self, storage, test_user):
        """Test storing and retrieving a decision trace."""
        from mind.core.decision.models import DecisionTrace

        trace = DecisionTrace(
            trace_id=uuid4(),
            user_id=test_user,
            session_id=uuid4(),
            memory_ids=[],
            memory_scores={},
            decision_type="recommendation",
            decision_summary="Test decision",
            confidence=0.8,
            alternatives_count=2,
        )

        saved = await storage.store(trace)

        assert saved.trace_id == trace.trace_id

        retrieved = await storage.get(trace.trace_id)

        assert retrieved is not None
        assert retrieved.trace_id == trace.trace_id
        assert retrieved.decision_type == "recommendation"
        assert retrieved.confidence == 0.8

    @pytest.mark.asyncio
    async def test_record_outcome(self, storage, test_user):
        """Test recording an outcome for a decision trace."""
        from mind.core.decision.models import DecisionTrace

        trace = DecisionTrace(
            trace_id=uuid4(),
            user_id=test_user,
            session_id=uuid4(),
            memory_ids=[],
            memory_scores={},
            decision_type="action",
            decision_summary="Test action",
            confidence=0.75,
        )

        await storage.store(trace)

        result = await storage.record_outcome(
            trace.trace_id,
            quality=0.9,
            signal="user_satisfied",
        )

        assert result.outcome_observed is True
        assert result.outcome_quality == 0.9
        assert result.outcome_signal == "user_satisfied"
        assert result.outcome_timestamp is not None

    @pytest.mark.asyncio
    async def test_list_traces_by_user(self, storage, test_user):
        """Test listing traces for a user."""
        from mind.core.decision.models import DecisionTrace

        for i in range(3):
            trace = DecisionTrace(
                trace_id=uuid4(),
                user_id=test_user,
                session_id=uuid4(),
                memory_ids=[],
                memory_scores={},
                decision_type="query",
                decision_summary=f"Query {i}",
                confidence=0.7,
            )
            await storage.store(trace)

        traces = await storage.list_by_user(test_user, limit=10)

        assert len(traces) == 3

    @pytest.mark.asyncio
    async def test_list_traces_with_outcome_filter(self, storage, test_user):
        """Test listing traces filtered by outcome status."""
        from mind.core.decision.models import DecisionTrace

        # Create trace with outcome
        trace1 = DecisionTrace(
            trace_id=uuid4(),
            user_id=test_user,
            session_id=uuid4(),
            memory_ids=[],
            memory_scores={},
            decision_type="action",
            confidence=0.8,
        )
        await storage.store(trace1)
        await storage.record_outcome(trace1.trace_id, quality=0.8, signal="positive")

        # Create trace without outcome
        trace2 = DecisionTrace(
            trace_id=uuid4(),
            user_id=test_user,
            session_id=uuid4(),
            memory_ids=[],
            memory_scores={},
            decision_type="action",
            confidence=0.7,
        )
        await storage.store(trace2)

        # Filter for traces with outcomes
        with_outcomes = await storage.list_by_user(
            test_user,
            outcome_observed=True,
        )

        assert len(with_outcomes) == 1
        assert with_outcomes[0].trace_id == trace1.trace_id

    @pytest.mark.asyncio
    async def test_get_pending_outcomes(self, storage, test_user):
        """Test getting traces awaiting outcomes."""
        from mind.core.decision.models import DecisionTrace

        # Create trace that should be in pending outcomes
        trace1 = DecisionTrace(
            trace_id=uuid4(),
            user_id=test_user,
            session_id=uuid4(),
            memory_ids=[],
            memory_scores={},
            decision_type="action",
            confidence=0.8,
        )
        await storage.store(trace1)

        # Create trace with outcome
        trace2 = DecisionTrace(
            trace_id=uuid4(),
            user_id=test_user,
            session_id=uuid4(),
            memory_ids=[],
            memory_scores={},
            decision_type="action",
            confidence=0.7,
        )
        await storage.store(trace2)
        await storage.record_outcome(trace2.trace_id, quality=0.9, signal="positive")

        pending = await storage.get_pending_outcomes(
            test_user,
            max_age=timedelta(hours=1),
        )

        assert len(pending) == 1
        assert pending[0].trace_id == trace1.trace_id

    @pytest.mark.asyncio
    async def test_health_check(self, storage):
        """Test storage health check."""
        result = await storage.health_check()
        assert result is True
