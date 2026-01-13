"""Unit tests for PostgreSQL storage adapters.

These tests mock the asyncpg pool to test adapter logic
without requiring a real database.
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from mind.adapters.standard.postgres_storage import (
    PostgresMemoryStorage,
    PostgresDecisionStorage,
)
from mind.core.memory.models import Memory, TemporalLevel
from mind.core.decision.models import DecisionTrace, Outcome, SalienceUpdate


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_pool():
    """Create a mock asyncpg pool."""
    pool = AsyncMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock()
    pool.execute = AsyncMock()
    pool.fetchval = AsyncMock()
    return pool


@pytest.fixture
def memory_storage(mock_pool):
    """Create a PostgresMemoryStorage with mocked pool."""
    return PostgresMemoryStorage(pool=mock_pool)


@pytest.fixture
def decision_storage(mock_pool):
    """Create a PostgresDecisionStorage with mocked pool."""
    return PostgresDecisionStorage(pool=mock_pool)


@pytest.fixture
def sample_memory():
    """Create a sample memory for testing."""
    return Memory(
        memory_id=uuid4(),
        user_id=uuid4(),
        content="Test memory content",
        content_type="observation",
        temporal_level=TemporalLevel.SITUATIONAL,
        valid_from=datetime.now(UTC),
        valid_until=None,
        base_salience=0.8,
        outcome_adjustment=0.0,
        retrieval_count=0,
        decision_count=0,
        positive_outcomes=0,
        negative_outcomes=0,
        promoted_from_level=None,
        promotion_timestamp=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_trace():
    """Create a sample decision trace for testing."""
    return DecisionTrace(
        trace_id=uuid4(),
        user_id=uuid4(),
        session_id="session-123",
        memory_ids=[uuid4(), uuid4()],
        memory_scores={"mem1": 0.9, "mem2": 0.7},
        decision_type="recommendation",
        decision_summary="Test decision",
        confidence=0.85,
        alternatives_count=3,
        created_at=datetime.now(UTC),
        outcome_observed=False,
        outcome_quality=None,
        outcome_timestamp=None,
        outcome_signal=None,
    )


def create_mock_memory_row(memory: Memory) -> MagicMock:
    """Create a mock database row from a Memory object."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: getattr(self, key)
    row.memory_id = memory.memory_id
    row.user_id = memory.user_id
    row.content = memory.content
    row.content_type = memory.content_type
    row.temporal_level = memory.temporal_level.value
    row.valid_from = memory.valid_from
    row.valid_until = memory.valid_until
    row.base_salience = memory.base_salience
    row.outcome_adjustment = memory.outcome_adjustment
    row.retrieval_count = memory.retrieval_count
    row.decision_count = memory.decision_count
    row.positive_outcomes = memory.positive_outcomes
    row.negative_outcomes = memory.negative_outcomes
    row.promoted_from_level = (
        memory.promoted_from_level.value if memory.promoted_from_level else None
    )
    row.promotion_timestamp = memory.promotion_timestamp
    row.created_at = memory.created_at
    row.updated_at = memory.updated_at
    return row


def create_mock_trace_row(trace: DecisionTrace) -> MagicMock:
    """Create a mock database row from a DecisionTrace object."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: getattr(self, key)
    row.trace_id = trace.trace_id
    row.user_id = trace.user_id
    row.session_id = trace.session_id
    row.memory_ids = [str(m) for m in trace.memory_ids]
    row.memory_scores = json.dumps(trace.memory_scores)
    row.decision_type = trace.decision_type
    row.decision_summary = trace.decision_summary
    row.confidence = trace.confidence
    row.alternatives_count = trace.alternatives_count
    row.created_at = trace.created_at
    row.outcome_observed = trace.outcome_observed
    row.outcome_quality = trace.outcome_quality
    row.outcome_timestamp = trace.outcome_timestamp
    row.outcome_signal = trace.outcome_signal
    return row


# =============================================================================
# PostgresMemoryStorage Tests
# =============================================================================


class TestPostgresMemoryStorage:
    """Tests for PostgresMemoryStorage."""

    @pytest.mark.asyncio
    async def test_store_memory(self, memory_storage, mock_pool, sample_memory):
        """Test storing a new memory."""
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetchrow.return_value = mock_row

        result = await memory_storage.store(sample_memory)

        assert result.user_id == sample_memory.user_id
        assert result.content == sample_memory.content
        assert result.temporal_level == sample_memory.temporal_level
        mock_pool.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_memory_found(self, memory_storage, mock_pool, sample_memory):
        """Test retrieving an existing memory."""
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetchrow.return_value = mock_row

        result = await memory_storage.get(sample_memory.memory_id)

        assert result is not None
        assert result.memory_id == sample_memory.memory_id
        assert result.content == sample_memory.content

    @pytest.mark.asyncio
    async def test_get_memory_not_found(self, memory_storage, mock_pool):
        """Test retrieving a non-existent memory."""
        mock_pool.fetchrow.return_value = None

        result = await memory_storage.get(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user(self, memory_storage, mock_pool, sample_memory):
        """Test retrieving memories for a user."""
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetch.return_value = [mock_row, mock_row]

        result = await memory_storage.get_by_user(
            sample_memory.user_id,
            limit=10,
            offset=0,
        )

        assert len(result) == 2
        mock_pool.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_user_with_filters(
        self, memory_storage, mock_pool, sample_memory
    ):
        """Test retrieving memories with temporal level and salience filters."""
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetch.return_value = [mock_row]

        result = await memory_storage.get_by_user(
            sample_memory.user_id,
            temporal_level=TemporalLevel.SITUATIONAL,
            min_salience=0.5,
            valid_only=True,
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_update_salience(self, memory_storage, mock_pool, sample_memory):
        """Test adjusting memory salience."""
        updated = Memory(
            memory_id=sample_memory.memory_id,
            user_id=sample_memory.user_id,
            content=sample_memory.content,
            content_type=sample_memory.content_type,
            temporal_level=sample_memory.temporal_level,
            valid_from=sample_memory.valid_from,
            valid_until=sample_memory.valid_until,
            base_salience=sample_memory.base_salience,
            outcome_adjustment=0.1,  # Changed
            retrieval_count=sample_memory.retrieval_count,
            decision_count=sample_memory.decision_count,
            positive_outcomes=sample_memory.positive_outcomes,
            negative_outcomes=sample_memory.negative_outcomes,
            promoted_from_level=sample_memory.promoted_from_level,
            promotion_timestamp=sample_memory.promotion_timestamp,
            created_at=sample_memory.created_at,
            updated_at=sample_memory.updated_at,
        )
        mock_row = create_mock_memory_row(updated)
        mock_pool.fetchrow.return_value = mock_row

        result = await memory_storage.update_salience(
            sample_memory.memory_id,
            adjustment=0.1,
        )

        assert result.outcome_adjustment == 0.1

    @pytest.mark.asyncio
    async def test_update_salience_not_found(self, memory_storage, mock_pool):
        """Test adjusting salience for non-existent memory."""
        mock_pool.fetchrow.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await memory_storage.update_salience(uuid4(), adjustment=0.1)

    @pytest.mark.asyncio
    async def test_increment_retrieval_count(self, memory_storage, mock_pool):
        """Test incrementing retrieval count."""
        mock_pool.execute.return_value = None

        await memory_storage.increment_retrieval_count(uuid4())

        mock_pool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_increment_decision_count_positive(self, memory_storage, mock_pool):
        """Test incrementing decision count with positive outcome."""
        mock_pool.execute.return_value = None

        await memory_storage.increment_decision_count(uuid4(), positive=True)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0][0]
        assert "positive_outcomes = positive_outcomes + 1" in call_args

    @pytest.mark.asyncio
    async def test_increment_decision_count_negative(self, memory_storage, mock_pool):
        """Test incrementing decision count with negative outcome."""
        mock_pool.execute.return_value = None

        await memory_storage.increment_decision_count(uuid4(), positive=False)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0][0]
        assert "negative_outcomes = negative_outcomes + 1" in call_args

    @pytest.mark.asyncio
    async def test_expire_memory(self, memory_storage, mock_pool):
        """Test expiring a memory."""
        mock_pool.execute.return_value = None

        await memory_storage.expire(uuid4())

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0][0]
        assert "valid_until = NOW()" in call_args

    @pytest.mark.asyncio
    async def test_promote_memory(self, memory_storage, mock_pool, sample_memory):
        """Test promoting a memory to higher temporal level."""
        # First get returns current memory
        mock_row = create_mock_memory_row(sample_memory)

        # Create promoted version
        promoted = Memory(
            memory_id=sample_memory.memory_id,
            user_id=sample_memory.user_id,
            content=sample_memory.content,
            content_type=sample_memory.content_type,
            temporal_level=TemporalLevel.SEASONAL,  # Promoted
            valid_from=sample_memory.valid_from,
            valid_until=sample_memory.valid_until,
            base_salience=sample_memory.base_salience,
            outcome_adjustment=sample_memory.outcome_adjustment,
            retrieval_count=sample_memory.retrieval_count,
            decision_count=sample_memory.decision_count,
            positive_outcomes=sample_memory.positive_outcomes,
            negative_outcomes=sample_memory.negative_outcomes,
            promoted_from_level=TemporalLevel.SITUATIONAL,
            promotion_timestamp=datetime.now(UTC),
            created_at=sample_memory.created_at,
            updated_at=sample_memory.updated_at,
        )
        promoted_row = create_mock_memory_row(promoted)

        # First call returns current, second returns promoted
        mock_pool.fetchrow.side_effect = [mock_row, promoted_row]

        result = await memory_storage.promote(
            sample_memory.memory_id,
            TemporalLevel.SEASONAL,
        )

        assert result.temporal_level == TemporalLevel.SEASONAL
        assert result.promoted_from_level == TemporalLevel.SITUATIONAL

    @pytest.mark.asyncio
    async def test_promote_to_lower_level_fails(
        self, memory_storage, mock_pool, sample_memory
    ):
        """Test that promoting to lower level raises error."""
        # Current memory is at SEASONAL level
        sample_memory = Memory(
            memory_id=sample_memory.memory_id,
            user_id=sample_memory.user_id,
            content=sample_memory.content,
            content_type=sample_memory.content_type,
            temporal_level=TemporalLevel.SEASONAL,
            valid_from=sample_memory.valid_from,
            valid_until=sample_memory.valid_until,
            base_salience=sample_memory.base_salience,
            outcome_adjustment=sample_memory.outcome_adjustment,
            retrieval_count=sample_memory.retrieval_count,
            decision_count=sample_memory.decision_count,
            positive_outcomes=sample_memory.positive_outcomes,
            negative_outcomes=sample_memory.negative_outcomes,
            promoted_from_level=sample_memory.promoted_from_level,
            promotion_timestamp=sample_memory.promotion_timestamp,
            created_at=sample_memory.created_at,
            updated_at=sample_memory.updated_at,
        )
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetchrow.return_value = mock_row

        with pytest.raises(ValueError, match="Cannot promote"):
            await memory_storage.promote(
                sample_memory.memory_id,
                TemporalLevel.SITUATIONAL,  # Lower than current
            )

    @pytest.mark.asyncio
    async def test_get_candidates_for_promotion(
        self, memory_storage, mock_pool, sample_memory
    ):
        """Test getting memories that are candidates for promotion."""
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetch.return_value = [mock_row]

        result = await memory_storage.get_candidates_for_promotion(
            sample_memory.user_id,
            level=TemporalLevel.SITUATIONAL,
            min_salience=0.7,
            min_positive_ratio=0.6,
        )

        assert len(result) == 1
        mock_pool.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_expired_candidates(
        self, memory_storage, mock_pool, sample_memory
    ):
        """Test getting memories that should be expired."""
        mock_row = create_mock_memory_row(sample_memory)
        mock_pool.fetch.return_value = [mock_row]

        result = await memory_storage.get_expired_candidates(
            sample_memory.user_id,
            level=TemporalLevel.IMMEDIATE,
            older_than_days=1,
        )

        assert len(result) == 1


# =============================================================================
# PostgresDecisionStorage Tests
# =============================================================================


class TestPostgresDecisionStorage:
    """Tests for PostgresDecisionStorage."""

    @pytest.mark.asyncio
    async def test_store_trace(self, decision_storage, mock_pool, sample_trace):
        """Test storing a decision trace."""
        mock_row = create_mock_trace_row(sample_trace)
        mock_pool.fetchrow.return_value = mock_row

        result = await decision_storage.store_trace(sample_trace)

        assert result.trace_id == sample_trace.trace_id
        assert result.decision_summary == sample_trace.decision_summary
        mock_pool.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_trace_found(self, decision_storage, mock_pool, sample_trace):
        """Test retrieving an existing trace."""
        mock_row = create_mock_trace_row(sample_trace)
        mock_pool.fetchrow.return_value = mock_row

        result = await decision_storage.get_trace(sample_trace.trace_id)

        assert result is not None
        assert result.trace_id == sample_trace.trace_id

    @pytest.mark.asyncio
    async def test_get_trace_not_found(self, decision_storage, mock_pool):
        """Test retrieving a non-existent trace."""
        mock_pool.fetchrow.return_value = None

        result = await decision_storage.get_trace(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_record_outcome(self, decision_storage, mock_pool, sample_trace):
        """Test recording an outcome for a trace."""
        outcome = Outcome(
            quality=0.9,
            signal="user_accepted",
            observed_at=datetime.now(UTC),
        )

        # Create updated trace with outcome
        updated_trace = DecisionTrace(
            trace_id=sample_trace.trace_id,
            user_id=sample_trace.user_id,
            session_id=sample_trace.session_id,
            memory_ids=sample_trace.memory_ids,
            memory_scores=sample_trace.memory_scores,
            decision_type=sample_trace.decision_type,
            decision_summary=sample_trace.decision_summary,
            confidence=sample_trace.confidence,
            alternatives_count=sample_trace.alternatives_count,
            created_at=sample_trace.created_at,
            outcome_observed=True,
            outcome_quality=outcome.quality,
            outcome_timestamp=outcome.observed_at,
            outcome_signal=outcome.signal,
        )
        mock_row = create_mock_trace_row(updated_trace)
        mock_pool.fetchrow.return_value = mock_row

        result = await decision_storage.record_outcome(
            sample_trace.trace_id,
            outcome,
        )

        assert result.outcome_observed is True
        assert result.outcome_quality == 0.9
        assert result.outcome_signal == "user_accepted"

    @pytest.mark.asyncio
    async def test_record_outcome_not_found(self, decision_storage, mock_pool):
        """Test recording outcome for non-existent trace."""
        mock_pool.fetchrow.return_value = None
        outcome = Outcome(
            quality=0.9,
            signal="user_accepted",
            observed_at=datetime.now(UTC),
        )

        with pytest.raises(ValueError, match="not found"):
            await decision_storage.record_outcome(uuid4(), outcome)

    @pytest.mark.asyncio
    async def test_get_traces_by_user(
        self, decision_storage, mock_pool, sample_trace
    ):
        """Test retrieving traces for a user."""
        mock_row = create_mock_trace_row(sample_trace)
        mock_pool.fetch.return_value = [mock_row]

        result = await decision_storage.get_traces_by_user(
            sample_trace.user_id,
            limit=10,
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_traces_by_user_with_outcomes_only(
        self, decision_storage, mock_pool, sample_trace
    ):
        """Test retrieving only traces with outcomes."""
        mock_pool.fetch.return_value = []

        result = await decision_storage.get_traces_by_user(
            sample_trace.user_id,
            with_outcomes_only=True,
        )

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_traces_for_memory(
        self, decision_storage, mock_pool, sample_trace
    ):
        """Test retrieving traces that used a specific memory."""
        mock_row = create_mock_trace_row(sample_trace)
        mock_pool.fetch.return_value = [mock_row]

        memory_id = sample_trace.memory_ids[0]
        result = await decision_storage.get_traces_for_memory(memory_id)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_pending_outcomes(
        self, decision_storage, mock_pool, sample_trace
    ):
        """Test retrieving traces without outcomes."""
        mock_row = create_mock_trace_row(sample_trace)
        mock_pool.fetch.return_value = [mock_row]

        result = await decision_storage.get_pending_outcomes(
            sample_trace.user_id,
            older_than_hours=24,
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_store_salience_update(self, decision_storage, mock_pool):
        """Test storing a salience update record."""
        update = SalienceUpdate(
            memory_id=uuid4(),
            trace_id=uuid4(),
            delta=0.05,
            reason="positive_outcome",
        )
        mock_pool.execute.return_value = None

        await decision_storage.store_salience_update(update)

        mock_pool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_salience_updates_for_memory(self, decision_storage, mock_pool):
        """Test retrieving salience update history for a memory."""
        memory_id = uuid4()
        trace_id = uuid4()

        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: getattr(self, key)
        mock_row.memory_id = memory_id
        mock_row.trace_id = trace_id
        mock_row.delta = 0.05
        mock_row.reason = "positive_outcome"
        mock_pool.fetch.return_value = [mock_row]

        result = await decision_storage.get_salience_updates_for_memory(
            memory_id,
            limit=50,
        )

        assert len(result) == 1
        assert result[0].delta == 0.05
        assert result[0].reason == "positive_outcome"
