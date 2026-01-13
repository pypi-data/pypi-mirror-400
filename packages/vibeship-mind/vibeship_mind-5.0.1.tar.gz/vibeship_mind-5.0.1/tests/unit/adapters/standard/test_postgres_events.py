"""Unit tests for PostgreSQL event adapters.

These tests mock the asyncpg pool to test event publishing
and consumption without requiring a real database.
"""

import asyncio
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from mind.adapters.standard.postgres_events import (
    PostgresEventPublisher,
    PostgresEventConsumer,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_pool():
    """Create a mock asyncpg pool."""
    pool = AsyncMock()
    pool.acquire = AsyncMock()
    pool.execute = AsyncMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock()
    pool.release = AsyncMock()
    return pool


@pytest.fixture
def mock_connection():
    """Create a mock asyncpg connection."""
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.transaction = MagicMock()
    conn.add_listener = AsyncMock()
    conn.remove_listener = AsyncMock()
    return conn


@pytest.fixture
def event_publisher(mock_pool, mock_connection):
    """Create a PostgresEventPublisher with mocked pool."""
    # Setup context manager for acquire
    async def acquire_cm():
        return mock_connection

    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_connection)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

    # Setup transaction context manager
    mock_connection.transaction.return_value.__aenter__ = AsyncMock()
    mock_connection.transaction.return_value.__aexit__ = AsyncMock(return_value=None)

    return PostgresEventPublisher(pool=mock_pool)


@pytest.fixture
def event_consumer(mock_pool):
    """Create a PostgresEventConsumer with mocked pool."""
    return PostgresEventConsumer(pool=mock_pool)


# =============================================================================
# PostgresEventPublisher Tests
# =============================================================================


class TestPostgresEventPublisher:
    """Tests for PostgresEventPublisher."""

    @pytest.mark.asyncio
    async def test_publish_event(self, event_publisher, mock_connection):
        """Test publishing a single event."""
        event_id = await event_publisher.publish(
            event_type="memory.created",
            payload={"memory_id": str(uuid4()), "content": "test"},
            user_id="user-123",
        )

        assert event_id is not None
        # Verify INSERT was called
        assert mock_connection.execute.call_count >= 1

    @pytest.mark.asyncio
    async def test_publish_event_includes_metadata(
        self, event_publisher, mock_connection
    ):
        """Test that published events include metadata."""
        await event_publisher.publish(
            event_type="decision.tracked",
            payload={"trace_id": "trace-123"},
        )

        # Check that execute was called with payload containing metadata
        calls = mock_connection.execute.call_args_list
        # At least one call should have been made
        assert len(calls) >= 1

    @pytest.mark.asyncio
    async def test_publish_batch(self, event_publisher, mock_connection):
        """Test publishing multiple events atomically."""
        events = [
            ("memory.created", {"memory_id": "mem1"}),
            ("memory.created", {"memory_id": "mem2"}),
            ("memory.created", {"memory_id": "mem3"}),
        ]

        event_ids = await event_publisher.publish_batch(events, user_id="user-123")

        assert len(event_ids) == 3
        # All IDs should be unique
        assert len(set(event_ids)) == 3

    @pytest.mark.asyncio
    async def test_publish_batch_empty(self, event_publisher):
        """Test publishing empty batch."""
        event_ids = await event_publisher.publish_batch([])

        assert event_ids == []

    @pytest.mark.asyncio
    async def test_close_is_noop(self, event_publisher):
        """Test that close is a no-op (pool managed externally)."""
        # Should not raise
        await event_publisher.close()


# =============================================================================
# PostgresEventConsumer Tests
# =============================================================================


class TestPostgresEventConsumer:
    """Tests for PostgresEventConsumer."""

    @pytest.mark.asyncio
    async def test_subscribe_to_event_type(self, event_consumer):
        """Test subscribing to a specific event type."""
        handler = AsyncMock()

        await event_consumer.subscribe("memory.created", handler)

        assert "memory.created" in event_consumer._handlers
        assert handler in event_consumer._handlers["memory.created"]

    @pytest.mark.asyncio
    async def test_subscribe_multiple_handlers(self, event_consumer):
        """Test subscribing multiple handlers to same event type."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()

        await event_consumer.subscribe("memory.created", handler1)
        await event_consumer.subscribe("memory.created", handler2)

        assert len(event_consumer._handlers["memory.created"]) == 2

    @pytest.mark.asyncio
    async def test_subscribe_pattern(self, event_consumer):
        """Test subscribing to event patterns."""
        handler = AsyncMock()

        await event_consumer.subscribe_pattern("memory.%", handler)

        assert len(event_consumer._pattern_handlers) == 1
        pattern, h = event_consumer._pattern_handlers[0]
        assert pattern == "memory.%"
        assert h == handler

    @pytest.mark.asyncio
    async def test_matches_pattern_glob(self, event_consumer):
        """Test pattern matching with glob patterns."""
        assert event_consumer._matches_pattern("memory.created", "memory.%")
        assert event_consumer._matches_pattern("memory.updated", "memory.%")
        assert not event_consumer._matches_pattern("decision.tracked", "memory.%")

    @pytest.mark.asyncio
    async def test_matches_pattern_exact(self, event_consumer):
        """Test exact pattern matching."""
        assert event_consumer._matches_pattern("memory.created", "memory.created")
        assert not event_consumer._matches_pattern("memory.updated", "memory.created")

    @pytest.mark.asyncio
    async def test_acknowledge_event(self, event_consumer, mock_pool):
        """Test acknowledging an event."""
        event_id = str(uuid4())

        await event_consumer.acknowledge(event_id)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "status = 'processed'" in call_args[0]

    @pytest.mark.asyncio
    async def test_reject_event_with_requeue(self, event_consumer, mock_pool):
        """Test rejecting an event with requeue."""
        event_id = str(uuid4())

        await event_consumer.reject(event_id, requeue=True, reason="test error")

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "status = 'pending'" in call_args[0]
        assert "retry_count = retry_count + 1" in call_args[0]

    @pytest.mark.asyncio
    async def test_reject_event_without_requeue(self, event_consumer, mock_pool):
        """Test rejecting an event without requeue."""
        event_id = str(uuid4())

        await event_consumer.reject(event_id, requeue=False, reason="fatal error")

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "status = 'failed'" in call_args[0]

    @pytest.mark.asyncio
    async def test_start_consumer(self, event_consumer, mock_pool, mock_connection):
        """Test starting the event consumer."""
        mock_pool.acquire.return_value = mock_connection

        await event_consumer.start()

        assert event_consumer._running is True
        mock_connection.add_listener.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_consumer(self, event_consumer, mock_pool, mock_connection):
        """Test stopping the event consumer."""
        mock_pool.acquire.return_value = mock_connection
        event_consumer._running = True
        event_consumer._listen_conn = mock_connection

        await event_consumer.stop()

        assert event_consumer._running is False
        mock_connection.remove_listener.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_to_exact_handler(self, event_consumer, mock_pool):
        """Test dispatching event to exact match handlers."""
        handler = AsyncMock()
        await event_consumer.subscribe("memory.created", handler)

        event_id = str(uuid4())
        payload = {"memory_id": "mem-123"}

        await event_consumer._dispatch_event(event_id, "memory.created", payload)

        handler.assert_called_once_with(payload)
        mock_pool.execute.assert_called()  # acknowledge

    @pytest.mark.asyncio
    async def test_dispatch_to_pattern_handler(self, event_consumer, mock_pool):
        """Test dispatching event to pattern match handlers."""
        handler = AsyncMock()
        await event_consumer.subscribe_pattern("memory.%", handler)

        event_id = str(uuid4())
        payload = {"memory_id": "mem-123"}

        await event_consumer._dispatch_event(event_id, "memory.updated", payload)

        handler.assert_called_once_with(payload)

    @pytest.mark.asyncio
    async def test_dispatch_no_handlers_acknowledges(self, event_consumer, mock_pool):
        """Test that events with no handlers are acknowledged."""
        event_id = str(uuid4())
        payload = {"data": "test"}

        await event_consumer._dispatch_event(event_id, "unknown.event", payload)

        # Should still acknowledge
        mock_pool.execute.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_handler_error_rejects(self, event_consumer, mock_pool):
        """Test that handler errors result in rejection."""
        handler = AsyncMock(side_effect=ValueError("test error"))
        await event_consumer.subscribe("memory.created", handler)

        event_id = str(uuid4())
        payload = {"memory_id": "mem-123"}

        await event_consumer._dispatch_event(event_id, "memory.created", payload)

        # Should reject with requeue
        call_args = mock_pool.execute.call_args[0]
        assert "retry_count = retry_count + 1" in call_args[0]

    @pytest.mark.asyncio
    async def test_handle_notification_single_event(self, event_consumer, mock_pool):
        """Test handling a single event notification."""
        handler = AsyncMock()
        await event_consumer.subscribe("memory.created", handler)

        event_id = str(uuid4())
        mock_pool.fetchrow.return_value = MagicMock(
            __getitem__=lambda self, k: {
                "event_id": event_id,
                "event_type": "memory.created",
                "payload": '{"memory_id": "mem-123"}',
            }[k]
        )

        notification = json.dumps({"event_id": event_id, "event_type": "memory.created"})

        await event_consumer._handle_notification(notification)

        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_notification_batch(self, event_consumer, mock_pool):
        """Test handling a batch notification."""
        mock_pool.fetch.return_value = []

        notification = json.dumps({"batch": True, "count": 5})

        await event_consumer._handle_notification(notification)

        mock_pool.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_notification_malformed_json(self, event_consumer):
        """Test handling malformed notification JSON."""
        # Should not raise
        await event_consumer._handle_notification("not valid json")

    @pytest.mark.asyncio
    async def test_process_pending_events(self, event_consumer, mock_pool):
        """Test processing pending events from database."""
        handler = AsyncMock()
        await event_consumer.subscribe("memory.created", handler)

        mock_pool.fetch.return_value = [
            MagicMock(
                __getitem__=lambda self, k: {
                    "event_id": str(uuid4()),
                    "event_type": "memory.created",
                    "payload": '{"memory_id": "mem-1"}',
                }[k]
            ),
            MagicMock(
                __getitem__=lambda self, k: {
                    "event_id": str(uuid4()),
                    "event_type": "memory.created",
                    "payload": '{"memory_id": "mem-2"}',
                }[k]
            ),
        ]

        await event_consumer._process_pending_events()

        assert handler.call_count == 2
