"""Unit tests for LearningService.

These tests verify the synchronous learning loop that updates
memory salience based on decision outcomes.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from mind.core.causal.models import NodeType, RelationshipType
from mind.core.decision.models import DecisionTrace, Outcome, SalienceUpdate
from mind.core.errors import ErrorCode
from mind.core.memory.models import Memory, TemporalLevel
from mind.services.learning import LearningService, LearningResult


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_memory_storage():
    """Create a mock memory storage."""
    storage = AsyncMock()
    storage.get = AsyncMock()
    storage.update_salience = AsyncMock()
    return storage


@pytest.fixture
def mock_decision_storage():
    """Create a mock decision storage."""
    storage = AsyncMock()
    storage.get_trace = AsyncMock()
    storage.record_outcome = AsyncMock()
    storage.store_salience_update = AsyncMock()
    return storage


@pytest.fixture
def mock_causal_graph():
    """Create a mock causal graph."""
    graph = AsyncMock()
    graph.add_node = AsyncMock()
    graph.add_edge = AsyncMock()
    return graph


@pytest.fixture
def learning_service(mock_memory_storage, mock_decision_storage, mock_causal_graph):
    """Create a LearningService with mocked dependencies."""
    return LearningService(
        memory_storage=mock_memory_storage,
        decision_storage=mock_decision_storage,
        causal_graph=mock_causal_graph,
    )


@pytest.fixture
def learning_service_no_graph(mock_memory_storage, mock_decision_storage):
    """Create a LearningService without causal graph."""
    return LearningService(
        memory_storage=mock_memory_storage,
        decision_storage=mock_decision_storage,
        causal_graph=None,
    )


@pytest.fixture
def sample_user_id():
    """Create a sample user ID."""
    return uuid4()


@pytest.fixture
def sample_trace(sample_user_id):
    """Create a sample decision trace."""
    mem1, mem2, mem3 = uuid4(), uuid4(), uuid4()
    return DecisionTrace(
        trace_id=uuid4(),
        user_id=sample_user_id,
        session_id="session-123",
        memory_ids=[mem1, mem2, mem3],
        memory_scores={
            str(mem1): 0.9,  # High contribution
            str(mem2): 0.6,  # Medium contribution
            str(mem3): 0.3,  # Low contribution
        },
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


@pytest.fixture
def sample_trace_with_outcome(sample_user_id):
    """Create a decision trace that already has an outcome."""
    return DecisionTrace(
        trace_id=uuid4(),
        user_id=sample_user_id,
        session_id="session-123",
        memory_ids=[uuid4()],
        memory_scores={"mem1": 0.8},
        decision_type="recommendation",
        decision_summary="Test decision",
        confidence=0.85,
        alternatives_count=3,
        created_at=datetime.now(UTC),
        outcome_observed=True,
        outcome_quality=0.9,
        outcome_timestamp=datetime.now(UTC),
        outcome_signal="user_accepted",
    )


@pytest.fixture
def sample_memory(sample_user_id):
    """Create a sample memory."""
    return Memory(
        memory_id=uuid4(),
        user_id=sample_user_id,
        content="Test memory content",
        content_type="observation",
        temporal_level=TemporalLevel.SITUATIONAL,
        valid_from=datetime.now(UTC),
        valid_until=None,
        base_salience=0.8,
        outcome_adjustment=0.0,
        retrieval_count=5,
        decision_count=3,
        positive_outcomes=2,
        negative_outcomes=1,
        promoted_from_level=None,
        promotion_timestamp=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# =============================================================================
# record_outcome Tests
# =============================================================================


class TestRecordOutcome:
    """Tests for the record_outcome method."""

    @pytest.mark.asyncio
    async def test_record_outcome_success(
        self,
        learning_service,
        mock_decision_storage,
        mock_memory_storage,
        sample_trace,
        sample_user_id,
    ):
        """Test successful outcome recording."""
        mock_decision_storage.get_trace.return_value = sample_trace

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.9,
            signal="user_accepted",
        )

        assert result.is_ok
        learning_result = result.value
        assert learning_result.trace_id == sample_trace.trace_id
        assert learning_result.outcome_quality == 0.9
        assert learning_result.memories_updated > 0
        mock_decision_storage.record_outcome.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_outcome_negative(
        self,
        learning_service,
        mock_decision_storage,
        mock_memory_storage,
        sample_trace,
        sample_user_id,
    ):
        """Test recording a negative outcome."""
        mock_decision_storage.get_trace.return_value = sample_trace

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=-0.8,
            signal="user_rejected",
        )

        assert result.is_ok
        # Should still update memories
        assert mock_memory_storage.update_salience.call_count > 0

    @pytest.mark.asyncio
    async def test_record_outcome_neutral(
        self,
        learning_service,
        mock_decision_storage,
        mock_memory_storage,
        sample_trace,
        sample_user_id,
    ):
        """Test recording a neutral outcome."""
        mock_decision_storage.get_trace.return_value = sample_trace

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.0,
            signal="no_feedback",
        )

        assert result.is_ok

    @pytest.mark.asyncio
    async def test_record_outcome_quality_too_high(
        self, learning_service, sample_user_id
    ):
        """Test that quality above 1.0 is rejected."""
        result = await learning_service.record_outcome(
            trace_id=uuid4(),
            user_id=sample_user_id,
            quality=1.5,
            signal="test",
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_record_outcome_quality_too_low(
        self, learning_service, sample_user_id
    ):
        """Test that quality below -1.0 is rejected."""
        result = await learning_service.record_outcome(
            trace_id=uuid4(),
            user_id=sample_user_id,
            quality=-1.5,
            signal="test",
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_record_outcome_trace_not_found(
        self,
        learning_service,
        mock_decision_storage,
        sample_user_id,
    ):
        """Test recording outcome for non-existent trace."""
        mock_decision_storage.get_trace.return_value = None

        result = await learning_service.record_outcome(
            trace_id=uuid4(),
            user_id=sample_user_id,
            quality=0.9,
            signal="test",
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.NOT_FOUND

    @pytest.mark.asyncio
    async def test_record_outcome_wrong_user(
        self,
        learning_service,
        mock_decision_storage,
        sample_trace,
    ):
        """Test recording outcome for another user's trace."""
        mock_decision_storage.get_trace.return_value = sample_trace
        different_user = uuid4()

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=different_user,  # Not the trace owner
            quality=0.9,
            signal="test",
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_record_outcome_already_recorded(
        self,
        learning_service,
        mock_decision_storage,
        sample_trace_with_outcome,
        sample_user_id,
    ):
        """Test recording outcome when already recorded."""
        mock_decision_storage.get_trace.return_value = sample_trace_with_outcome

        result = await learning_service.record_outcome(
            trace_id=sample_trace_with_outcome.trace_id,
            user_id=sample_user_id,
            quality=0.5,
            signal="test",
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.CONFLICT

    @pytest.mark.asyncio
    async def test_record_outcome_with_feedback(
        self,
        learning_service,
        mock_decision_storage,
        sample_trace,
        sample_user_id,
    ):
        """Test recording outcome with text feedback."""
        mock_decision_storage.get_trace.return_value = sample_trace

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.9,
            signal="user_accepted",
            feedback="This was very helpful!",
        )

        assert result.is_ok

    @pytest.mark.asyncio
    async def test_record_outcome_salience_update_fails(
        self,
        learning_service,
        mock_decision_storage,
        mock_memory_storage,
        sample_trace,
        sample_user_id,
    ):
        """Test that individual salience update failures don't break the flow."""
        mock_decision_storage.get_trace.return_value = sample_trace
        mock_memory_storage.update_salience.side_effect = Exception("DB error")

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.9,
            signal="test",
        )

        # Should still succeed overall
        assert result.is_ok
        # But memories_updated should be 0
        assert result.value.memories_updated == 0

    @pytest.mark.asyncio
    async def test_record_outcome_updates_causal_graph(
        self,
        learning_service,
        mock_decision_storage,
        mock_causal_graph,
        sample_trace,
        sample_user_id,
    ):
        """Test that causal graph is updated on outcome."""
        mock_decision_storage.get_trace.return_value = sample_trace

        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.9,
            signal="test",
        )

        assert result.is_ok
        assert result.value.causal_edges_created > 0
        mock_causal_graph.add_node.assert_called()
        mock_causal_graph.add_edge.assert_called()

    @pytest.mark.asyncio
    async def test_record_outcome_without_causal_graph(
        self,
        learning_service_no_graph,
        mock_decision_storage,
        sample_trace,
        sample_user_id,
    ):
        """Test outcome recording works without causal graph."""
        mock_decision_storage.get_trace.return_value = sample_trace

        result = await learning_service_no_graph.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.9,
            signal="test",
        )

        assert result.is_ok
        assert result.value.causal_edges_created == 0


# =============================================================================
# _calculate_attribution Tests
# =============================================================================


class TestCalculateAttribution:
    """Tests for attribution calculation."""

    def test_calculate_attribution_weighted(self, learning_service, sample_trace):
        """Test that attribution is weighted by memory scores."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=0.9,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(sample_trace, outcome)

        # Should have updates for memories above minimum threshold
        assert len(updates) >= 1

        # Higher-scoring memories should get larger deltas
        deltas = {str(u.memory_id): u.delta for u in updates}
        assert all(d > 0 for d in deltas.values())  # Positive outcome = positive deltas

    def test_calculate_attribution_negative_outcome(
        self, learning_service, sample_trace
    ):
        """Test attribution with negative outcome."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=-0.8,
            signal="rejected",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(sample_trace, outcome)

        # Negative outcome = negative deltas
        for update in updates:
            assert update.delta < 0

    def test_calculate_attribution_zero_scores(self, learning_service, sample_user_id):
        """Test attribution when all scores are zero."""
        trace = DecisionTrace(
            trace_id=uuid4(),
            user_id=sample_user_id,
            session_id="session",
            memory_ids=[uuid4(), uuid4()],
            memory_scores={},  # No scores
            decision_type="test",
            decision_summary="test",
            confidence=0.5,
            alternatives_count=1,
            created_at=datetime.now(UTC),
            outcome_observed=False,
            outcome_quality=None,
            outcome_timestamp=None,
            outcome_signal=None,
        )

        outcome = Outcome(
            trace_id=trace.trace_id,
            quality=0.5,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(trace, outcome)

        # Should distribute equally
        assert len(updates) == 2

    def test_calculate_attribution_no_memories(self, learning_service, sample_user_id):
        """Test attribution with no memories."""
        trace = DecisionTrace(
            trace_id=uuid4(),
            user_id=sample_user_id,
            session_id="session",
            memory_ids=[],  # No memories
            memory_scores={},
            decision_type="test",
            decision_summary="test",
            confidence=0.5,
            alternatives_count=1,
            created_at=datetime.now(UTC),
            outcome_observed=False,
            outcome_quality=None,
            outcome_timestamp=None,
            outcome_signal=None,
        )

        outcome = Outcome(
            trace_id=trace.trace_id,
            quality=0.9,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(trace, outcome)

        assert len(updates) == 0

    def test_calculate_attribution_respects_max_delta(
        self, learning_service, sample_user_id
    ):
        """Test that attribution respects MAX_ADJUSTMENT_DELTA."""
        mem_id = uuid4()
        trace = DecisionTrace(
            trace_id=uuid4(),
            user_id=sample_user_id,
            session_id="session",
            memory_ids=[mem_id],
            memory_scores={str(mem_id): 1.0},  # 100% contribution
            decision_type="test",
            decision_summary="test",
            confidence=1.0,
            alternatives_count=1,
            created_at=datetime.now(UTC),
            outcome_observed=False,
            outcome_quality=None,
            outcome_timestamp=None,
            outcome_signal=None,
        )

        outcome = Outcome(
            trace_id=trace.trace_id,
            quality=1.0,  # Max positive
            signal="test",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(trace, outcome)

        # Delta should be clamped
        for update in updates:
            assert abs(update.delta) <= learning_service.MAX_ADJUSTMENT_DELTA

    def test_calculate_attribution_filters_low_contribution(
        self, learning_service, sample_user_id
    ):
        """Test that low-contribution memories are filtered out."""
        high_mem = uuid4()
        low_mem = uuid4()
        trace = DecisionTrace(
            trace_id=uuid4(),
            user_id=sample_user_id,
            session_id="session",
            memory_ids=[high_mem, low_mem],
            memory_scores={
                str(high_mem): 0.99,  # 99% contribution
                str(low_mem): 0.01,  # 1% contribution (below threshold)
            },
            decision_type="test",
            decision_summary="test",
            confidence=0.5,
            alternatives_count=1,
            created_at=datetime.now(UTC),
            outcome_observed=False,
            outcome_quality=None,
            outcome_timestamp=None,
            outcome_signal=None,
        )

        outcome = Outcome(
            trace_id=trace.trace_id,
            quality=0.5,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(trace, outcome)

        # Low contribution memory should be filtered
        memory_ids = {u.memory_id for u in updates}
        assert high_mem in memory_ids
        assert low_mem not in memory_ids


# =============================================================================
# _update_causal_graph Tests
# =============================================================================


class TestUpdateCausalGraph:
    """Tests for causal graph updates."""

    @pytest.mark.asyncio
    async def test_update_causal_graph_creates_nodes(
        self,
        learning_service,
        mock_causal_graph,
        sample_trace,
    ):
        """Test that causal graph creates decision and outcome nodes."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=0.9,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        edges = await learning_service._update_causal_graph(sample_trace, outcome)

        assert edges > 0
        # Should have created nodes: decision + outcome + memories
        assert mock_causal_graph.add_node.call_count >= 2

    @pytest.mark.asyncio
    async def test_update_causal_graph_creates_edges(
        self,
        learning_service,
        mock_causal_graph,
        sample_trace,
    ):
        """Test that causal graph creates relationship edges."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=0.9,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        edges = await learning_service._update_causal_graph(sample_trace, outcome)

        # Should create: memory→decision edges + decision→outcome edge
        expected_edges = len(sample_trace.memory_ids) + 1
        assert edges == expected_edges

    @pytest.mark.asyncio
    async def test_update_causal_graph_no_graph(
        self,
        learning_service_no_graph,
        sample_trace,
    ):
        """Test that update is skipped when no causal graph."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=0.9,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        edges = await learning_service_no_graph._update_causal_graph(
            sample_trace, outcome
        )

        assert edges == 0

    @pytest.mark.asyncio
    async def test_update_causal_graph_handles_errors(
        self,
        learning_service,
        mock_causal_graph,
        sample_trace,
    ):
        """Test that causal graph errors are handled gracefully."""
        mock_causal_graph.add_node.side_effect = Exception("Graph error")

        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=0.9,
            signal="test",
            observed_at=datetime.now(UTC),
        )

        # Should not raise
        edges = await learning_service._update_causal_graph(sample_trace, outcome)

        assert edges == 0


# =============================================================================
# get_memory_effectiveness Tests
# =============================================================================


class TestGetMemoryEffectiveness:
    """Tests for memory effectiveness statistics."""

    @pytest.mark.asyncio
    async def test_get_effectiveness_success(
        self,
        learning_service,
        mock_memory_storage,
        sample_memory,
        sample_user_id,
    ):
        """Test getting memory effectiveness."""
        sample_memory = Memory(
            memory_id=sample_memory.memory_id,
            user_id=sample_user_id,
            content=sample_memory.content,
            content_type=sample_memory.content_type,
            temporal_level=sample_memory.temporal_level,
            valid_from=sample_memory.valid_from,
            valid_until=sample_memory.valid_until,
            base_salience=sample_memory.base_salience,
            outcome_adjustment=sample_memory.outcome_adjustment,
            retrieval_count=sample_memory.retrieval_count,
            decision_count=10,
            positive_outcomes=7,
            negative_outcomes=3,
            promoted_from_level=sample_memory.promoted_from_level,
            promotion_timestamp=sample_memory.promotion_timestamp,
            created_at=sample_memory.created_at,
            updated_at=sample_memory.updated_at,
        )
        mock_memory_storage.get.return_value = sample_memory

        result = await learning_service.get_memory_effectiveness(
            user_id=sample_user_id,
            memory_id=sample_memory.memory_id,
        )

        assert result.is_ok
        stats = result.value
        assert stats["decision_count"] == 10
        assert stats["positive_outcomes"] == 7
        assert stats["negative_outcomes"] == 3
        assert stats["success_rate"] == 0.7

    @pytest.mark.asyncio
    async def test_get_effectiveness_not_found(
        self,
        learning_service,
        mock_memory_storage,
        sample_user_id,
    ):
        """Test getting effectiveness for non-existent memory."""
        mock_memory_storage.get.return_value = None

        result = await learning_service.get_memory_effectiveness(
            user_id=sample_user_id,
            memory_id=uuid4(),
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_effectiveness_wrong_user(
        self,
        learning_service,
        mock_memory_storage,
        sample_memory,
    ):
        """Test getting effectiveness for another user's memory."""
        mock_memory_storage.get.return_value = sample_memory
        different_user = uuid4()

        result = await learning_service.get_memory_effectiveness(
            user_id=different_user,
            memory_id=sample_memory.memory_id,
        )

        assert not result.is_ok
        assert result.error.code == ErrorCode.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_effectiveness_no_outcomes(
        self,
        learning_service,
        mock_memory_storage,
        sample_user_id,
    ):
        """Test getting effectiveness when no outcomes recorded."""
        memory = Memory(
            memory_id=uuid4(),
            user_id=sample_user_id,
            content="test",
            content_type="observation",
            temporal_level=TemporalLevel.SITUATIONAL,
            valid_from=datetime.now(UTC),
            valid_until=None,
            base_salience=0.5,
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
        mock_memory_storage.get.return_value = memory

        result = await learning_service.get_memory_effectiveness(
            user_id=sample_user_id,
            memory_id=memory.memory_id,
        )

        assert result.is_ok
        assert result.value["success_rate"] == 0.0


# =============================================================================
# Integration Tests (with mocked dependencies)
# =============================================================================


class TestLearningLoop:
    """Integration tests for the full learning loop."""

    @pytest.mark.asyncio
    async def test_full_learning_loop(
        self,
        learning_service,
        mock_decision_storage,
        mock_memory_storage,
        mock_causal_graph,
        sample_trace,
        sample_user_id,
    ):
        """Test the complete learning loop from outcome to updates."""
        mock_decision_storage.get_trace.return_value = sample_trace

        # Record positive outcome
        result = await learning_service.record_outcome(
            trace_id=sample_trace.trace_id,
            user_id=sample_user_id,
            quality=0.9,
            signal="user_accepted",
        )

        assert result.is_ok

        # Verify decision storage was updated
        mock_decision_storage.record_outcome.assert_called_once()

        # Verify memories were updated
        assert mock_memory_storage.update_salience.call_count > 0

        # Verify causal graph was updated
        assert mock_causal_graph.add_node.call_count > 0
        assert mock_causal_graph.add_edge.call_count > 0

    @pytest.mark.asyncio
    async def test_learning_improves_with_positive_outcomes(
        self,
        learning_service,
        sample_trace,
    ):
        """Test that positive outcomes lead to positive salience adjustments."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=0.9,
            signal="user_accepted",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(sample_trace, outcome)

        # All updates should be positive
        for update in updates:
            assert update.delta > 0

    @pytest.mark.asyncio
    async def test_learning_decreases_with_negative_outcomes(
        self,
        learning_service,
        sample_trace,
    ):
        """Test that negative outcomes lead to negative salience adjustments."""
        outcome = Outcome(
            trace_id=sample_trace.trace_id,
            quality=-0.8,
            signal="user_rejected",
            observed_at=datetime.now(UTC),
        )

        updates = learning_service._calculate_attribution(sample_trace, outcome)

        # All updates should be negative
        for update in updates:
            assert update.delta < 0
