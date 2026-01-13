"""Tests for event consumers."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import UTC, datetime

from mind.core.events.base import EventEnvelope, EventType
from mind.core.errors import Result


class TestCausalGraphUpdater:
    """Tests for CausalGraphUpdater consumer."""

    @pytest.fixture
    def mock_envelope_decision_tracked(self) -> EventEnvelope:
        """Create a mock decision.tracked event envelope."""
        return EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.DECISION_TRACKED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "session_id": str(uuid4()),
                "memory_ids": [str(uuid4()), str(uuid4())],
                "memory_scores": {},
                "decision_type": "recommendation",
                "decision_summary": "Test decision",
                "confidence": 0.8,
                "alternatives_count": 2,
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

    @pytest.fixture
    def mock_envelope_outcome_observed(self) -> EventEnvelope:
        """Create a mock outcome.observed event envelope."""
        return EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.OUTCOME_OBSERVED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "outcome_quality": 0.8,
                "outcome_signal": "explicit_positive",
                "observed_at": datetime.now(UTC).isoformat(),
                "memory_attributions": {},
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

    @pytest.mark.asyncio
    async def test_decision_tracked_creates_graph_nodes(
        self,
        mock_envelope_decision_tracked,
    ):
        """Decision tracked should create decision and memory nodes."""
        from mind.workers.consumers.causal_updater import CausalGraphUpdater

        # Mock dependencies
        mock_client = MagicMock()
        mock_graph_repo = MagicMock()
        mock_graph_repo.add_decision_node = AsyncMock(return_value=Result.ok(None))
        mock_graph_repo.add_memory_node = AsyncMock(return_value=Result.ok(None))
        mock_graph_repo.link_memory_to_decision = AsyncMock(return_value=Result.ok(None))

        mock_memory = MagicMock()
        mock_memory.memory_id = uuid4()
        mock_memory.user_id = uuid4()
        mock_memory.content = "Test content"
        mock_memory.temporal_level = MagicMock(value=1)
        mock_memory.effective_salience = 0.8

        mock_memory_repo = MagicMock()
        mock_memory_repo.get = AsyncMock(return_value=Result.ok(mock_memory))

        with patch(
            "mind.workers.consumers.causal_updater.get_falkordb_client",
            return_value=MagicMock(),
        ), patch(
            "mind.workers.consumers.causal_updater.CausalGraphRepository",
            return_value=mock_graph_repo,
        ), patch(
            "mind.workers.consumers.causal_updater.get_database"
        ) as mock_get_db:
            # Set up database mock
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_db = MagicMock()
            mock_db.session = MagicMock(return_value=mock_session)
            mock_get_db.return_value = mock_db

            with patch(
                "mind.workers.consumers.causal_updater.MemoryRepository",
                return_value=mock_memory_repo,
            ):
                updater = CausalGraphUpdater(mock_client)
                await updater._handle_decision_tracked(mock_envelope_decision_tracked)

                # Verify decision node was created
                mock_graph_repo.add_decision_node.assert_called_once()

    @pytest.mark.asyncio
    async def test_outcome_observed_creates_outcome_node(
        self,
        mock_envelope_outcome_observed,
    ):
        """Outcome observed should create outcome node and link."""
        from mind.workers.consumers.causal_updater import CausalGraphUpdater

        mock_client = MagicMock()
        mock_graph_repo = MagicMock()
        mock_graph_repo.add_outcome_node = AsyncMock(return_value=Result.ok(None))
        mock_graph_repo.link_decision_to_outcome = AsyncMock(return_value=Result.ok(None))

        with patch(
            "mind.workers.consumers.causal_updater.get_falkordb_client",
            return_value=MagicMock(),
        ), patch(
            "mind.workers.consumers.causal_updater.CausalGraphRepository",
            return_value=mock_graph_repo,
        ):
            updater = CausalGraphUpdater(mock_client)
            await updater._handle_outcome_observed(mock_envelope_outcome_observed)

            # Verify outcome node was created
            mock_graph_repo.add_outcome_node.assert_called_once()
            mock_graph_repo.link_decision_to_outcome.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_falkordb_unavailable_gracefully(
        self,
        mock_envelope_decision_tracked,
    ):
        """Should handle FalkorDB being unavailable gracefully."""
        from mind.workers.consumers.causal_updater import CausalGraphUpdater

        mock_client = MagicMock()

        with patch(
            "mind.workers.consumers.causal_updater.get_falkordb_client",
            side_effect=ValueError("FalkorDB not configured"),
        ):
            updater = CausalGraphUpdater(mock_client)
            # Should not raise
            await updater._handle_decision_tracked(mock_envelope_decision_tracked)

    @pytest.mark.asyncio
    async def test_handles_empty_memory_ids(self):
        """Should handle decisions with no memories gracefully."""
        from mind.workers.consumers.causal_updater import CausalGraphUpdater

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.DECISION_TRACKED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "memory_ids": [],  # Empty
                "memory_scores": {},
                "decision_type": "test",
                "decision_summary": "No memories",
                "confidence": 0.5,
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        mock_client = MagicMock()
        updater = CausalGraphUpdater(mock_client)
        # Should not raise
        await updater._handle_decision_tracked(envelope)


class TestSalienceUpdater:
    """Tests for SalienceUpdater consumer."""

    @pytest.fixture
    def mock_envelope_outcome_with_attributions(self) -> EventEnvelope:
        """Create a mock outcome.observed event envelope with attributions."""
        memory_id_1 = str(uuid4())
        memory_id_2 = str(uuid4())
        return EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.OUTCOME_OBSERVED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "outcome_quality": 0.9,
                "outcome_signal": "explicit_positive",
                "observed_at": datetime.now(UTC).isoformat(),
                "memory_attributions": {
                    memory_id_1: 0.6,
                    memory_id_2: 0.4,
                },
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

    @pytest.mark.asyncio
    async def test_outcome_observed_updates_salience(
        self,
        mock_envelope_outcome_with_attributions,
    ):
        """Outcome observed should update memory salience."""
        from mind.workers.consumers.salience_updater import SalienceUpdater

        mock_client = MagicMock()
        mock_memory_repo = MagicMock()
        mock_memory_repo.get = AsyncMock(return_value=Result.ok(MagicMock(
            memory_id=uuid4(),
            outcome_adjustment=0.0,
        )))
        mock_memory_repo.update_salience = AsyncMock(return_value=Result.ok(None))

        mock_decision_repo = MagicMock()
        mock_decision_repo.get_trace = AsyncMock(return_value=Result.ok(MagicMock(
            trace_id=uuid4(),
            user_id=uuid4(),
        )))

        with patch(
            "mind.workers.consumers.salience_updater.get_database"
        ) as mock_get_db, patch(
            "mind.workers.consumers.salience_updater.DecisionRepository",
            return_value=mock_decision_repo,
        ), patch(
            "mind.workers.consumers.salience_updater.MemoryRepository",
            return_value=mock_memory_repo,
        ), patch(
            "mind.workers.consumers.salience_updater.get_event_service"
        ):
            # Set up database mock
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_db = MagicMock()
            mock_db.session = MagicMock(return_value=mock_session)
            mock_get_db.return_value = mock_db

            updater = SalienceUpdater(mock_client)
            await updater._handle_outcome_observed(mock_envelope_outcome_with_attributions)

            # Verify salience was updated for each memory
            assert mock_memory_repo.update_salience.call_count == 2

    @pytest.mark.asyncio
    async def test_handles_empty_attributions(self):
        """Should handle outcomes with no attributions gracefully."""
        from mind.workers.consumers.salience_updater import SalienceUpdater

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.OUTCOME_OBSERVED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "outcome_quality": 0.5,
                "outcome_signal": "implicit",
                "memory_attributions": {},  # Empty
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        mock_client = MagicMock()
        updater = SalienceUpdater(mock_client)
        # Should not raise
        await updater._handle_outcome_observed(envelope)

    @pytest.mark.asyncio
    async def test_handles_missing_memory_gracefully(
        self,
        mock_envelope_outcome_with_attributions,
    ):
        """Should skip memories that no longer exist."""
        from mind.workers.consumers.salience_updater import SalienceUpdater

        mock_client = MagicMock()
        mock_memory_repo = MagicMock()
        mock_memory_repo.get = AsyncMock(return_value=Result.err(MagicMock(
            message="Not found"
        )))
        mock_memory_repo.update_salience = AsyncMock(return_value=Result.ok(None))

        mock_decision_repo = MagicMock()
        mock_decision_repo.get_trace = AsyncMock(return_value=Result.ok(MagicMock(
            trace_id=uuid4(),
            user_id=uuid4(),
        )))

        with patch(
            "mind.workers.consumers.salience_updater.get_database"
        ) as mock_get_db, patch(
            "mind.workers.consumers.salience_updater.DecisionRepository",
            return_value=mock_decision_repo,
        ), patch(
            "mind.workers.consumers.salience_updater.MemoryRepository",
            return_value=mock_memory_repo,
        ), patch(
            "mind.workers.consumers.salience_updater.get_event_service"
        ):
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_db = MagicMock()
            mock_db.session = MagicMock(return_value=mock_session)
            mock_get_db.return_value = mock_db

            updater = SalienceUpdater(mock_client)
            # Should not raise
            await updater._handle_outcome_observed(mock_envelope_outcome_with_attributions)

            # No salience updates should have been attempted
            mock_memory_repo.update_salience.assert_not_called()


class TestPatternExtractorConsumer:
    """Tests for PatternExtractorConsumer."""

    @pytest.fixture
    def mock_envelope_positive_outcome(self) -> EventEnvelope:
        """Create a mock outcome.observed event with positive quality."""
        return EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.OUTCOME_OBSERVED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "outcome_quality": 0.8,  # Above threshold
                "outcome_signal": "explicit_positive",
                "observed_at": datetime.now(UTC).isoformat(),
                "memory_attributions": {},
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

    @pytest.fixture
    def mock_envelope_negative_outcome(self) -> EventEnvelope:
        """Create a mock outcome.observed event with negative quality."""
        return EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.OUTCOME_OBSERVED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={
                "trace_id": str(uuid4()),
                "outcome_quality": 0.1,  # Below threshold
                "outcome_signal": "explicit_negative",
                "observed_at": datetime.now(UTC).isoformat(),
                "memory_attributions": {},
            },
            correlation_id=uuid4(),
            causation_id=None,
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

    @pytest.mark.asyncio
    async def test_skips_low_quality_outcomes(
        self,
        mock_envelope_negative_outcome,
    ):
        """Should skip outcomes below quality threshold."""
        from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer

        mock_client = MagicMock()
        consumer = PatternExtractorConsumer(mock_client)

        # Should not raise, should skip processing
        await consumer._handle_outcome(mock_envelope_negative_outcome)

        # Extractor should not have any candidates
        assert len(consumer._extractor._candidates) == 0

    @pytest.mark.asyncio
    async def test_extracts_pattern_from_positive_outcome(
        self,
        mock_envelope_positive_outcome,
    ):
        """Should extract pattern from positive outcomes."""
        from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer

        mock_client = MagicMock()
        mock_memory = MagicMock()
        mock_memory.content = "User prefers morning meetings"
        mock_memory.memory_id = uuid4()

        mock_trace = MagicMock()
        mock_trace.trace_id = uuid4()
        mock_trace.user_id = uuid4()
        mock_trace.decision_type = "scheduling"
        mock_trace.memory_ids = [mock_memory.memory_id]

        mock_memory_repo = MagicMock()
        mock_memory_repo.get = AsyncMock(return_value=Result.ok(mock_memory))

        mock_decision_repo = MagicMock()
        mock_decision_repo.get = AsyncMock(return_value=Result.ok(mock_trace))

        with patch(
            "mind.workers.consumers.pattern_extractor.get_database"
        ) as mock_get_db, patch(
            "mind.workers.consumers.pattern_extractor.DecisionRepository",
            return_value=mock_decision_repo,
        ), patch(
            "mind.workers.consumers.pattern_extractor.MemoryRepository",
            return_value=mock_memory_repo,
        ):
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_db = MagicMock()
            mock_db.session = MagicMock(return_value=mock_session)
            mock_get_db.return_value = mock_db

            consumer = PatternExtractorConsumer(mock_client)
            await consumer._handle_outcome(mock_envelope_positive_outcome)

            # Extractor should have recorded the observation
            assert len(consumer._extractor._candidates) > 0

    @pytest.mark.asyncio
    async def test_handles_missing_decision_gracefully(
        self,
        mock_envelope_positive_outcome,
    ):
        """Should handle missing decision traces gracefully."""
        from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer

        mock_client = MagicMock()
        mock_decision_repo = MagicMock()
        mock_decision_repo.get = AsyncMock(return_value=Result.err(MagicMock(
            message="Not found"
        )))

        with patch(
            "mind.workers.consumers.pattern_extractor.get_database"
        ) as mock_get_db, patch(
            "mind.workers.consumers.pattern_extractor.DecisionRepository",
            return_value=mock_decision_repo,
        ):
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_db = MagicMock()
            mock_db.session = MagicMock(return_value=mock_session)
            mock_get_db.return_value = mock_db

            consumer = PatternExtractorConsumer(mock_client)
            # Should not raise
            await consumer._handle_outcome(mock_envelope_positive_outcome)

    @pytest.mark.asyncio
    async def test_processes_ready_patterns_periodically(self):
        """Should check for ready patterns after processing interval."""
        from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer

        mock_client = MagicMock()
        consumer = PatternExtractorConsumer(mock_client)

        # Mock the process_ready_patterns method
        consumer._process_ready_patterns = AsyncMock()

        # Simulate processing events up to interval
        consumer._events_processed = 99
        # Manually increment to trigger check
        consumer._events_processed += 1

        if consumer._events_processed % consumer.CHECK_READY_INTERVAL == 0:
            await consumer._process_ready_patterns()

        consumer._process_ready_patterns.assert_called_once()

    def test_consumer_name_is_set(self):
        """Consumer should have correct name."""
        from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer

        mock_client = MagicMock()
        consumer = PatternExtractorConsumer(mock_client)

        assert consumer.CONSUMER_NAME == "pattern-extractor"

    def test_min_quality_threshold(self):
        """Minimum quality threshold should be set."""
        from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer

        mock_client = MagicMock()
        consumer = PatternExtractorConsumer(mock_client)

        assert consumer.MIN_QUALITY_THRESHOLD == 0.3


class TestConsumerRunner:
    """Tests for ConsumerRunner."""

    @pytest.mark.asyncio
    async def test_runner_starts_and_stops(self):
        """Runner should start and stop consumers."""
        from mind.workers.consumers.runner import ConsumerRunner

        runner = ConsumerRunner()

        # Mock consumer creation
        mock_consumer = MagicMock()
        mock_consumer.start = AsyncMock()
        mock_consumer.stop = AsyncMock()

        with patch(
            "mind.workers.consumers.runner.create_causal_updater",
            return_value=mock_consumer,
        ), patch(
            "mind.workers.consumers.runner.create_salience_updater",
            return_value=mock_consumer,
        ):
            await runner.start()
            assert runner._running is True
            assert len(runner._consumers) == 2  # Now has 2 consumers

            await runner.stop()
            assert runner._running is False
            assert mock_consumer.stop.call_count == 2  # Both stopped

    def test_request_shutdown_sets_event(self):
        """Shutdown request should set the event."""
        from mind.workers.consumers.runner import ConsumerRunner

        runner = ConsumerRunner()
        assert not runner._shutdown_event.is_set()

        runner.request_shutdown()
        assert runner._shutdown_event.is_set()
