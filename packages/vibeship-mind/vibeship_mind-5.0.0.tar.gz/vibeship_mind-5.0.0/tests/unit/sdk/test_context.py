"""Unit tests for SDK decision context.

Tests for:
- DecisionContext lifecycle
- OutcomeNotRecordedError
- Feedback loop enforcement
- Context methods (retrieve, remember, track, outcome)
"""

import pytest
import warnings
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from mind.sdk.context import DecisionContext, OutcomeNotRecordedError
from mind.sdk.models import (
    Memory,
    RetrievalResult,
    TrackResult,
    OutcomeResult,
    TemporalLevel,
)


class TestOutcomeNotRecordedError:
    """Tests for OutcomeNotRecordedError."""

    def test_error_message(self):
        """Should include trace ID in message."""
        trace_id = UUID("880e8400-e29b-41d4-a716-446655440003")
        error = OutcomeNotRecordedError(trace_id)

        assert str(trace_id) in str(error)
        assert "feedback loop" in str(error).lower()

    def test_stores_trace_id(self):
        """Should store trace ID for programmatic access."""
        trace_id = UUID("880e8400-e29b-41d4-a716-446655440003")
        error = OutcomeNotRecordedError(trace_id)

        assert error.trace_id == trace_id


class TestDecisionContextInit:
    """Tests for DecisionContext initialization."""

    @pytest.fixture
    def mock_client(self):
        """Create mock MindClient."""
        client = MagicMock()
        client.retrieve = AsyncMock()
        client.remember = AsyncMock()
        client.track = AsyncMock()
        client.outcome = AsyncMock()
        return client

    def test_basic_init(self, mock_client):
        """Should initialize with required params."""
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")
        session_id = UUID("990e8400-e29b-41d4-a716-446655440004")

        ctx = DecisionContext(
            client=mock_client,
            user_id=user_id,
            session_id=session_id,
        )

        assert ctx.user_id == user_id
        assert ctx.session_id == session_id

    def test_default_decision_type(self, mock_client):
        """Should default to recommendation."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        assert ctx._decision_type == "recommendation"

    def test_strict_mode(self, mock_client):
        """Should accept strict mode flag."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=uuid4(),
            session_id=uuid4(),
            strict=True,
        )

        assert ctx._strict is True

    def test_initial_state(self, mock_client):
        """Should start with clean state."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        assert ctx.trace_id is None
        assert ctx.memories == []
        assert ctx._decision_tracked is False
        assert ctx._outcome_recorded is False


class TestDecisionContextAsyncContextManager:
    """Tests for async context manager behavior."""

    @pytest.fixture
    def mock_client(self):
        """Create mock MindClient."""
        client = MagicMock()
        client.retrieve = AsyncMock()
        client.track = AsyncMock()
        client.outcome = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_enters_context(self, mock_client):
        """Should return self on enter."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        async with ctx as entered:
            assert entered is ctx

    @pytest.mark.asyncio
    async def test_exits_cleanly_without_retrieval(self, mock_client):
        """Should exit cleanly if no memories retrieved."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        # No exception should be raised
        async with ctx:
            pass

    @pytest.mark.asyncio
    async def test_does_not_interfere_with_exception(self, mock_client):
        """Should not suppress exceptions."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        with pytest.raises(ValueError):
            async with ctx:
                raise ValueError("Test error")


class TestDecisionContextRetrieve:
    """Tests for retrieve method."""

    @pytest.fixture
    def mock_client(self):
        """Create mock MindClient with retrieval response."""
        client = MagicMock()

        # Create sample memory
        memory = Memory(
            memory_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            content="User prefers dark mode",
            content_type="preference",
            temporal_level=4,
            temporal_level_name="identity",
            effective_salience=0.95,
            retrieval_count=5,
            decision_count=3,
            positive_outcomes=2,
            negative_outcomes=1,
            valid_from=None,
            valid_until=None,
            created_at=None,
        )

        client.retrieve = AsyncMock(
            return_value=RetrievalResult(
                retrieval_id=UUID("770e8400-e29b-41d4-a716-446655440002"),
                memories=[memory],
                scores={"550e8400-e29b-41d4-a716-446655440000": 0.85},
                latency_ms=12.5,
            )
        )
        client.track = AsyncMock()
        client.outcome = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_retrieve_returns_memories(self, mock_client):
        """Should return list of memories."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        memories = await ctx.retrieve("preferences")

        assert len(memories) == 1
        assert memories[0].content == "User prefers dark mode"

    @pytest.mark.asyncio
    async def test_retrieve_tracks_memories(self, mock_client):
        """Should track retrieved memories internally."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve("preferences")

        assert len(ctx.memories) == 1
        assert len(ctx._memory_scores) == 1

    @pytest.mark.asyncio
    async def test_retrieve_accumulates(self, mock_client):
        """Should accumulate across multiple retrieves."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve("preferences")
        await ctx.retrieve("more preferences")

        assert len(ctx.memories) == 2

    @pytest.mark.asyncio
    async def test_retrieve_passes_params(self, mock_client):
        """Should pass params to client."""
        ctx = DecisionContext(
            client=mock_client,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve(
            query="preferences",
            limit=5,
            min_salience=0.5,
        )

        mock_client.retrieve.assert_called_once()
        call_kwargs = mock_client.retrieve.call_args[1]
        assert call_kwargs["limit"] == 5
        assert call_kwargs["min_salience"] == 0.5


class TestDecisionContextTrack:
    """Tests for track method."""

    @pytest.fixture
    def mock_client_with_retrieval(self):
        """Create mock client with retrieval already done."""
        client = MagicMock()

        memory = Memory(
            memory_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            content="User prefers dark mode",
            content_type="preference",
            temporal_level=4,
            temporal_level_name="identity",
            effective_salience=0.95,
            retrieval_count=5,
            decision_count=3,
            positive_outcomes=2,
            negative_outcomes=1,
            valid_from=None,
            valid_until=None,
            created_at=None,
        )

        client.retrieve = AsyncMock(
            return_value=RetrievalResult(
                retrieval_id=UUID("770e8400-e29b-41d4-a716-446655440002"),
                memories=[memory],
                scores={"550e8400-e29b-41d4-a716-446655440000": 0.85},
                latency_ms=12.5,
            )
        )

        client.track = AsyncMock(
            return_value=TrackResult(
                trace_id=UUID("880e8400-e29b-41d4-a716-446655440003"),
                created_at=None,
            )
        )

        client.outcome = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_track_requires_retrieval(self, mock_client_with_retrieval):
        """Should raise if no memories retrieved."""
        ctx = DecisionContext(
            client=mock_client_with_retrieval,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        with pytest.raises(ValueError, match="No memories retrieved"):
            await ctx.track("My decision")

    @pytest.mark.asyncio
    async def test_track_creates_trace(self, mock_client_with_retrieval):
        """Should create trace and store trace_id."""
        ctx = DecisionContext(
            client=mock_client_with_retrieval,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve("preferences")
        result = await ctx.track("Used dark mode preference")

        assert ctx.trace_id == UUID("880e8400-e29b-41d4-a716-446655440003")
        assert ctx._decision_tracked is True

    @pytest.mark.asyncio
    async def test_track_passes_memory_ids(self, mock_client_with_retrieval):
        """Should pass all retrieved memory IDs."""
        ctx = DecisionContext(
            client=mock_client_with_retrieval,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve("preferences")
        await ctx.track("Used preference")

        call_kwargs = mock_client_with_retrieval.track.call_args[1]
        assert UUID("550e8400-e29b-41d4-a716-446655440000") in call_kwargs["memory_ids"]


class TestDecisionContextOutcome:
    """Tests for outcome method."""

    @pytest.fixture
    def mock_client_full(self):
        """Create mock client for full flow."""
        client = MagicMock()

        memory = Memory(
            memory_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            content="User prefers dark mode",
            content_type="preference",
            temporal_level=4,
            temporal_level_name="identity",
            effective_salience=0.95,
            retrieval_count=5,
            decision_count=3,
            positive_outcomes=2,
            negative_outcomes=1,
            valid_from=None,
            valid_until=None,
            created_at=None,
        )

        client.retrieve = AsyncMock(
            return_value=RetrievalResult(
                retrieval_id=UUID("770e8400-e29b-41d4-a716-446655440002"),
                memories=[memory],
                scores={"550e8400-e29b-41d4-a716-446655440000": 0.85},
                latency_ms=12.5,
            )
        )

        client.track = AsyncMock(
            return_value=TrackResult(
                trace_id=UUID("880e8400-e29b-41d4-a716-446655440003"),
                created_at=None,
            )
        )

        client.outcome = AsyncMock(
            return_value=OutcomeResult(
                trace_id=UUID("880e8400-e29b-41d4-a716-446655440003"),
                outcome_quality=0.9,
                memories_updated=1,
                salience_changes={"550e8400-e29b-41d4-a716-446655440000": 0.05},
            )
        )

        return client

    @pytest.mark.asyncio
    async def test_outcome_requires_retrieval(self, mock_client_full):
        """Should raise if no memories retrieved."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=uuid4(),
            session_id=uuid4(),
        )

        with pytest.raises(ValueError, match="No memories retrieved"):
            await ctx.outcome(quality=0.9)

    @pytest.mark.asyncio
    async def test_outcome_auto_tracks(self, mock_client_full):
        """Should auto-track if not already tracked."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve("preferences")
        result = await ctx.outcome(quality=0.9)

        # Should have called track automatically
        mock_client_full.track.assert_called_once()
        assert ctx._decision_tracked is True
        assert ctx._outcome_recorded is True

    @pytest.mark.asyncio
    async def test_outcome_returns_result(self, mock_client_full):
        """Should return outcome result."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        await ctx.retrieve("preferences")
        result = await ctx.outcome(quality=0.9)

        assert result.outcome_quality == 0.9
        assert result.memories_updated == 1


class TestDecisionContextFeedbackEnforcement:
    """Tests for feedback loop enforcement."""

    @pytest.fixture
    def mock_client_full(self):
        """Create mock client for full flow."""
        client = MagicMock()

        memory = Memory(
            memory_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            content="User prefers dark mode",
            content_type="preference",
            temporal_level=4,
            temporal_level_name="identity",
            effective_salience=0.95,
            retrieval_count=5,
            decision_count=3,
            positive_outcomes=2,
            negative_outcomes=1,
            valid_from=None,
            valid_until=None,
            created_at=None,
        )

        client.retrieve = AsyncMock(
            return_value=RetrievalResult(
                retrieval_id=UUID("770e8400-e29b-41d4-a716-446655440002"),
                memories=[memory],
                scores={"550e8400-e29b-41d4-a716-446655440000": 0.85},
                latency_ms=12.5,
            )
        )

        client.track = AsyncMock(
            return_value=TrackResult(
                trace_id=UUID("880e8400-e29b-41d4-a716-446655440003"),
                created_at=None,
            )
        )

        client.outcome = AsyncMock(
            return_value=OutcomeResult(
                trace_id=UUID("880e8400-e29b-41d4-a716-446655440003"),
                outcome_quality=0.9,
                memories_updated=1,
                salience_changes={},
            )
        )

        return client

    @pytest.mark.asyncio
    async def test_warns_on_missing_outcome(self, mock_client_full):
        """Should warn if tracked but no outcome recorded (non-strict)."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
            strict=False,
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            async with ctx:
                await ctx.retrieve("preferences")
                await ctx.track("Made a decision")
                # Intentionally not calling outcome()

            # Should have issued a warning
            assert len(w) == 1
            assert "feedback loop" in str(w[0].message).lower()

    @pytest.mark.asyncio
    async def test_raises_on_missing_outcome_strict(self, mock_client_full):
        """Should raise if tracked but no outcome recorded (strict mode)."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
            strict=True,
        )

        with pytest.raises(OutcomeNotRecordedError):
            async with ctx:
                await ctx.retrieve("preferences")
                await ctx.track("Made a decision")
                # Intentionally not calling outcome()

    @pytest.mark.asyncio
    async def test_no_warning_with_outcome(self, mock_client_full):
        """Should not warn if outcome is recorded."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            async with ctx:
                await ctx.retrieve("preferences")
                await ctx.outcome(quality=0.9)

            # Should not have warnings about outcome
            outcome_warnings = [
                x for x in w if "feedback loop" in str(x.message).lower()
            ]
            assert len(outcome_warnings) == 0

    @pytest.mark.asyncio
    async def test_skip_outcome_prevents_warning(self, mock_client_full):
        """Should not warn if skip_outcome is called."""
        ctx = DecisionContext(
            client=mock_client_full,
            user_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
            session_id=uuid4(),
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            async with ctx:
                await ctx.retrieve("preferences")
                await ctx.track("Made a decision")
                await ctx.skip_outcome("Just browsing")

            # Should not have warnings
            outcome_warnings = [
                x for x in w if "feedback loop" in str(x.message).lower()
            ]
            assert len(outcome_warnings) == 0
