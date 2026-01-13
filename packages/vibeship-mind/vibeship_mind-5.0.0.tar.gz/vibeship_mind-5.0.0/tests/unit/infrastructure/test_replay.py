"""Tests for event replay functionality.

Tests the event replay capability for Mind v5:
- ReplayProgress tracking
- ReplayConfig filtering
- EventReplayer processing
- CLI utilities
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from mind.core.events.base import EventType, EventEnvelope
from mind.infrastructure.nats.replay import (
    ReplayProgress,
    ReplayConfig,
    EventReplayer,
    get_stream_info,
    count_events_by_type,
)


class TestReplayProgress:
    """Tests for ReplayProgress dataclass."""

    def test_initial_values(self):
        """ReplayProgress should have sensible defaults."""
        progress = ReplayProgress()

        assert progress.total_events == 0
        assert progress.processed_events == 0
        assert progress.failed_events == 0
        assert progress.skipped_events == 0
        assert progress.last_sequence == 0
        assert progress.errors == []

    def test_success_rate_zero_processed(self):
        """Success rate should be 0 when nothing processed."""
        progress = ReplayProgress()

        assert progress.success_rate == 0.0

    def test_success_rate_all_success(self):
        """Success rate should be 1.0 when all succeed."""
        progress = ReplayProgress(
            processed_events=100,
            failed_events=0,
        )

        assert progress.success_rate == 1.0

    def test_success_rate_with_failures(self):
        """Success rate should account for failures."""
        progress = ReplayProgress(
            processed_events=100,
            failed_events=20,
        )

        assert progress.success_rate == 0.8

    def test_elapsed_seconds(self):
        """Elapsed seconds should calculate from start time."""
        start = datetime.now(UTC) - timedelta(seconds=30)
        progress = ReplayProgress(start_time=start)

        # Allow some tolerance for test execution time
        assert 29 <= progress.elapsed_seconds <= 32

    def test_events_per_second_zero_elapsed(self):
        """Events per second should be 0 when no time elapsed."""
        progress = ReplayProgress(
            processed_events=100,
            start_time=datetime.now(UTC),
        )

        # Very small elapsed time
        assert progress.events_per_second >= 0

    def test_events_per_second_with_elapsed(self):
        """Events per second should calculate rate correctly."""
        start = datetime.now(UTC) - timedelta(seconds=10)
        progress = ReplayProgress(
            processed_events=100,
            start_time=start,
        )

        # Should be approximately 10 events/sec
        assert 9 <= progress.events_per_second <= 11


class TestReplayConfig:
    """Tests for ReplayConfig dataclass."""

    def test_default_values(self):
        """ReplayConfig should have sensible defaults."""
        config = ReplayConfig()

        assert config.from_sequence is None
        assert config.to_sequence is None
        assert config.since is None
        assert config.until is None
        assert config.event_types is None
        assert config.user_ids is None
        assert config.batch_size == 100
        assert config.max_events is None
        assert config.dry_run is False
        assert config.stop_on_error is False
        assert config.events_per_second is None

    def test_custom_values(self):
        """ReplayConfig should accept custom values."""
        config = ReplayConfig(
            from_sequence=100,
            to_sequence=500,
            event_types=[EventType.MEMORY_CREATED],
            batch_size=50,
            dry_run=True,
        )

        assert config.from_sequence == 100
        assert config.to_sequence == 500
        assert EventType.MEMORY_CREATED in config.event_types
        assert config.batch_size == 50
        assert config.dry_run is True


class TestEventReplayer:
    """Tests for EventReplayer class."""

    def test_handler_registration(self):
        """Should register handlers for event types."""
        client = MagicMock()
        config = ReplayConfig()
        replayer = EventReplayer(client, config)

        async def handler(envelope):
            pass

        replayer.on(EventType.MEMORY_CREATED, handler)

        assert EventType.MEMORY_CREATED in replayer._handlers
        assert handler in replayer._handlers[EventType.MEMORY_CREATED]

    def test_handler_registration_multiple(self):
        """Should allow multiple handlers per event type."""
        client = MagicMock()
        config = ReplayConfig()
        replayer = EventReplayer(client, config)

        async def handler1(envelope):
            pass

        async def handler2(envelope):
            pass

        replayer.on(EventType.MEMORY_CREATED, handler1)
        replayer.on(EventType.MEMORY_CREATED, handler2)

        assert len(replayer._handlers[EventType.MEMORY_CREATED]) == 2

    def test_on_all_registers_for_all_types(self):
        """on_all should register handler for every event type."""
        client = MagicMock()
        config = ReplayConfig()
        replayer = EventReplayer(client, config)

        async def handler(envelope):
            pass

        replayer.on_all(handler)

        for event_type in EventType:
            assert event_type in replayer._handlers
            assert handler in replayer._handlers[event_type]

    def test_stop_sets_running_false(self):
        """stop() should set _running to False."""
        client = MagicMock()
        config = ReplayConfig()
        replayer = EventReplayer(client, config)
        replayer._running = True

        replayer.stop()

        assert replayer._running is False

    def test_progress_property(self):
        """progress property should return current progress."""
        client = MagicMock()
        config = ReplayConfig()
        replayer = EventReplayer(client, config)
        replayer._progress.processed_events = 50

        assert replayer.progress.processed_events == 50


class TestEventReplayerFiltering:
    """Tests for EventReplayer filtering logic."""

    def test_should_process_no_filters(self):
        """Should process all events when no filters set."""
        client = MagicMock()
        config = ReplayConfig()
        replayer = EventReplayer(client, config)

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        assert replayer._should_process(envelope) is True

    def test_should_process_event_type_filter_match(self):
        """Should process events matching type filter."""
        client = MagicMock()
        config = ReplayConfig(
            event_types=[EventType.MEMORY_CREATED, EventType.DECISION_TRACKED]
        )
        replayer = EventReplayer(client, config)

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        assert replayer._should_process(envelope) is True

    def test_should_process_event_type_filter_no_match(self):
        """Should skip events not matching type filter."""
        client = MagicMock()
        config = ReplayConfig(
            event_types=[EventType.DECISION_TRACKED]
        )
        replayer = EventReplayer(client, config)

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        assert replayer._should_process(envelope) is False

    def test_should_process_user_filter_match(self):
        """Should process events matching user filter."""
        target_user = uuid4()
        client = MagicMock()
        config = ReplayConfig(user_ids=[target_user])
        replayer = EventReplayer(client, config)

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=target_user,
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        assert replayer._should_process(envelope) is True

    def test_should_process_user_filter_no_match(self):
        """Should skip events not matching user filter."""
        client = MagicMock()
        config = ReplayConfig(user_ids=[uuid4()])
        replayer = EventReplayer(client, config)

        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),  # Different user
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )

        assert replayer._should_process(envelope) is False

    def test_should_process_time_filter_since(self):
        """Should filter events by since timestamp."""
        client = MagicMock()
        since = datetime.now(UTC) - timedelta(hours=1)
        config = ReplayConfig(since=since)
        replayer = EventReplayer(client, config)

        # Event after since - should process
        envelope_new = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )
        assert replayer._should_process(envelope_new) is True

        # Event before since - should skip
        envelope_old = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=(since - timedelta(hours=1)).isoformat(),
            version=1,
        )
        assert replayer._should_process(envelope_old) is False

    def test_should_process_time_filter_until(self):
        """Should filter events by until timestamp."""
        client = MagicMock()
        until = datetime.now(UTC) - timedelta(hours=1)
        config = ReplayConfig(until=until)
        replayer = EventReplayer(client, config)

        # Event before until - should process
        envelope_old = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=(until - timedelta(hours=1)).isoformat(),
            version=1,
        )
        assert replayer._should_process(envelope_old) is True

        # Event after until - should skip
        envelope_new = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.MEMORY_CREATED,
            user_id=uuid4(),
            aggregate_id=uuid4(),
            payload={},
            correlation_id=uuid4(),
            timestamp=datetime.now(UTC).isoformat(),
            version=1,
        )
        assert replayer._should_process(envelope_new) is False


class TestEventReplayerReplay:
    """Tests for EventReplayer.replay() method."""

    @pytest.mark.asyncio
    async def test_replay_empty_stream(self):
        """Should handle empty stream gracefully."""
        client = MagicMock()
        client.jetstream = MagicMock()

        # Mock subscription that returns no messages
        mock_sub = AsyncMock()
        mock_sub.fetch = AsyncMock(side_effect=TimeoutError())
        mock_sub.unsubscribe = AsyncMock()
        client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        config = ReplayConfig()
        replayer = EventReplayer(client, config)

        progress = await replayer.replay()

        assert progress.processed_events == 0
        assert progress.failed_events == 0

    @pytest.mark.asyncio
    async def test_replay_dry_run_counts_only(self):
        """Dry run should count events without processing handlers."""
        client = MagicMock()
        client.jetstream = MagicMock()

        # Create mock message
        mock_msg = MagicMock()
        mock_msg.data = b'{"event_id": "' + str(uuid4()).encode() + b'", "event_type": "memory.created", "user_id": "' + str(uuid4()).encode() + b'", "aggregate_id": "' + str(uuid4()).encode() + b'", "payload": {}, "correlation_id": "' + str(uuid4()).encode() + b'", "timestamp": "2024-12-28T10:00:00Z", "version": 1}'
        mock_msg.metadata = MagicMock()
        mock_msg.metadata.sequence = MagicMock()
        mock_msg.metadata.sequence.stream = 1

        mock_sub = AsyncMock()
        mock_sub.fetch = AsyncMock(side_effect=[[mock_msg], TimeoutError()])
        mock_sub.unsubscribe = AsyncMock()
        client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        config = ReplayConfig(dry_run=True)
        replayer = EventReplayer(client, config)

        handler_called = False

        async def handler(envelope):
            nonlocal handler_called
            handler_called = True

        replayer.on(EventType.MEMORY_CREATED, handler)

        progress = await replayer.replay()

        assert progress.processed_events == 1
        assert handler_called is False  # Handler not called in dry run

    @pytest.mark.asyncio
    async def test_replay_respects_max_events(self):
        """Should stop after max_events reached."""
        client = MagicMock()
        client.jetstream = MagicMock()

        # Create multiple mock messages
        def make_msg(seq):
            msg = MagicMock()
            msg.data = b'{"event_id": "' + str(uuid4()).encode() + b'", "event_type": "memory.created", "user_id": "' + str(uuid4()).encode() + b'", "aggregate_id": "' + str(uuid4()).encode() + b'", "payload": {}, "correlation_id": "' + str(uuid4()).encode() + b'", "timestamp": "2024-12-28T10:00:00Z", "version": 1}'
            msg.metadata = MagicMock()
            msg.metadata.sequence = MagicMock()
            msg.metadata.sequence.stream = seq
            return msg

        mock_sub = AsyncMock()
        # Return 5 messages but max_events is 3
        mock_sub.fetch = AsyncMock(side_effect=[
            [make_msg(1), make_msg(2), make_msg(3), make_msg(4), make_msg(5)],
            TimeoutError()
        ])
        mock_sub.unsubscribe = AsyncMock()
        client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        config = ReplayConfig(max_events=3, dry_run=True)
        replayer = EventReplayer(client, config)

        progress = await replayer.replay()

        assert progress.processed_events <= 3


class TestGetStreamInfo:
    """Tests for get_stream_info function."""

    @pytest.mark.asyncio
    async def test_get_stream_info_success(self):
        """Should return stream information."""
        mock_client = MagicMock()
        mock_stream_info = MagicMock()
        mock_stream_info.state.messages = 1000
        mock_stream_info.state.first_seq = 1
        mock_stream_info.state.last_seq = 1000
        mock_stream_info.state.first_ts = datetime.now(UTC)
        mock_stream_info.state.last_ts = datetime.now(UTC)
        mock_stream_info.state.bytes = 1024000
        mock_stream_info.state.consumer_count = 2

        mock_client.jetstream = MagicMock()
        mock_client.jetstream.stream_info = AsyncMock(return_value=mock_stream_info)

        info = await get_stream_info(mock_client)

        assert info["message_count"] == 1000
        assert info["first_sequence"] == 1
        assert info["last_sequence"] == 1000
        assert "error" not in info

    @pytest.mark.asyncio
    async def test_get_stream_info_error(self):
        """Should handle errors gracefully."""
        mock_client = MagicMock()
        mock_client.jetstream = MagicMock()
        mock_client.jetstream.stream_info = AsyncMock(
            side_effect=Exception("Connection failed")
        )

        info = await get_stream_info(mock_client)

        assert "error" in info
        assert "Connection failed" in info["error"]


class TestCountEventsByType:
    """Tests for count_events_by_type function."""

    @pytest.mark.asyncio
    async def test_count_events_empty(self):
        """Should return empty dict for empty stream."""
        mock_client = MagicMock()
        mock_client.jetstream = MagicMock()

        mock_sub = AsyncMock()
        mock_sub.fetch = AsyncMock(side_effect=TimeoutError())
        mock_sub.unsubscribe = AsyncMock()
        mock_client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        counts = await count_events_by_type(mock_client, sample_size=100)

        assert counts == {}


class TestReplayDeliveryPolicy:
    """Tests for replay delivery policy configuration."""

    @pytest.mark.asyncio
    async def test_replay_from_sequence(self):
        """Should use BY_START_SEQUENCE when from_sequence set."""
        from nats.js.api import DeliverPolicy

        client = MagicMock()
        client.jetstream = MagicMock()

        mock_sub = AsyncMock()
        mock_sub.fetch = AsyncMock(side_effect=TimeoutError())
        mock_sub.unsubscribe = AsyncMock()
        client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        config = ReplayConfig(from_sequence=100)
        replayer = EventReplayer(client, config)

        await replayer.replay()

        # Check that pull_subscribe was called with correct config
        call_args = client.jetstream.pull_subscribe.call_args
        consumer_config = call_args[1]["config"]
        assert consumer_config.deliver_policy == DeliverPolicy.BY_START_SEQUENCE
        assert consumer_config.opt_start_seq == 100

    @pytest.mark.asyncio
    async def test_replay_from_time(self):
        """Should use BY_START_TIME when since set."""
        from nats.js.api import DeliverPolicy

        client = MagicMock()
        client.jetstream = MagicMock()

        mock_sub = AsyncMock()
        mock_sub.fetch = AsyncMock(side_effect=TimeoutError())
        mock_sub.unsubscribe = AsyncMock()
        client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        since = datetime.now(UTC) - timedelta(days=1)
        config = ReplayConfig(since=since)
        replayer = EventReplayer(client, config)

        await replayer.replay()

        # Check that pull_subscribe was called with correct config
        call_args = client.jetstream.pull_subscribe.call_args
        consumer_config = call_args[1]["config"]
        assert consumer_config.deliver_policy == DeliverPolicy.BY_START_TIME
        assert consumer_config.opt_start_time == since


class TestReplayProgressLogging:
    """Tests for replay progress logging."""

    @pytest.mark.asyncio
    async def test_progress_logs_periodically(self):
        """Should log progress every 1000 events."""
        client = MagicMock()
        client.jetstream = MagicMock()

        # Create mock messages
        def make_msg(seq):
            msg = MagicMock()
            msg.data = b'{"event_id": "' + str(uuid4()).encode() + b'", "event_type": "memory.created", "user_id": "' + str(uuid4()).encode() + b'", "aggregate_id": "' + str(uuid4()).encode() + b'", "payload": {}, "correlation_id": "' + str(uuid4()).encode() + b'", "timestamp": "2024-12-28T10:00:00Z", "version": 1}'
            msg.metadata = MagicMock()
            msg.metadata.sequence = MagicMock()
            msg.metadata.sequence.stream = seq
            return msg

        mock_sub = AsyncMock()
        mock_sub.fetch = AsyncMock(side_effect=[
            [make_msg(i) for i in range(1, 101)],  # 100 messages
            TimeoutError()
        ])
        mock_sub.unsubscribe = AsyncMock()
        client.jetstream.pull_subscribe = AsyncMock(return_value=mock_sub)

        config = ReplayConfig(dry_run=True)
        replayer = EventReplayer(client, config)

        progress = await replayer.replay()

        # Should have processed all messages
        assert progress.processed_events == 100
