"""Integration tests for PostgreSQL event adapters.

These tests verify PostgresEventPublisher and PostgresEventConsumer
work correctly against a real PostgreSQL database.
"""

import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.integration.standard.conftest import requires_docker


pytestmark = [pytest.mark.integration, requires_docker]


class TestPostgresEventPublisherIntegration:
    """Integration tests for PostgresEventPublisher."""

    @pytest_asyncio.fixture
    async def publisher(self, clean_db):
        """Create a PostgresEventPublisher instance."""
        from mind.adapters.standard.postgres_events import PostgresEventPublisher
        return PostgresEventPublisher(pool=clean_db)

    @pytest.mark.asyncio
    async def test_publish_event(self, publisher, clean_db):
        """Test publishing a single event."""
        event_id = await publisher.publish(
            event_type="memory.created",
            payload={"memory_id": str(uuid4()), "content": "test"},
            user_id="user-123",
        )

        assert event_id is not None

        # Verify event in database
        async with clean_db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM events WHERE event_id = $1",
                event_id,
            )

        assert row is not None
        assert row["event_type"] == "memory.created"
        assert row["status"] == "pending"

    @pytest.mark.asyncio
    async def test_publish_batch(self, publisher, clean_db):
        """Test publishing multiple events atomically."""
        events = [
            ("memory.created", {"memory_id": str(uuid4())}),
            ("memory.updated", {"memory_id": str(uuid4())}),
            ("decision.tracked", {"trace_id": str(uuid4())}),
        ]

        event_ids = await publisher.publish_batch(events, user_id="user-123")

        assert len(event_ids) == 3

        # Verify all events in database
        async with clean_db.acquire() as conn:
            for event_id in event_ids:
                row = await conn.fetchrow(
                    "SELECT * FROM events WHERE event_id = $1",
                    event_id,
                )
                assert row is not None

    @pytest.mark.asyncio
    async def test_publish_event_with_metadata(self, publisher, clean_db):
        """Test that published events include metadata."""
        event_id = await publisher.publish(
            event_type="outcome.recorded",
            payload={"trace_id": str(uuid4()), "quality": 0.9},
        )

        async with clean_db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM events WHERE event_id = $1",
                event_id,
            )

        assert row is not None
        # Payload should be stored
        import json
        payload = json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
        assert "trace_id" in payload
        assert "quality" in payload


class TestPostgresEventConsumerIntegration:
    """Integration tests for PostgresEventConsumer."""

    @pytest_asyncio.fixture
    async def consumer(self, clean_db):
        """Create a PostgresEventConsumer instance."""
        from mind.adapters.standard.postgres_events import PostgresEventConsumer
        consumer = PostgresEventConsumer(pool=clean_db)
        yield consumer
        # Clean up
        await consumer.stop()

    @pytest_asyncio.fixture
    async def publisher(self, clean_db):
        """Create a PostgresEventPublisher instance."""
        from mind.adapters.standard.postgres_events import PostgresEventPublisher
        return PostgresEventPublisher(pool=clean_db)

    @pytest.mark.asyncio
    async def test_subscribe_and_receive(self, consumer, publisher, clean_db):
        """Test subscribing and receiving events."""
        received_events = []

        async def handler(payload):
            received_events.append(payload)

        await consumer.subscribe("memory.created", handler)

        # Publish event directly to database (simulating publisher)
        event_id = str(uuid4())
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, $2, $3, 'pending')
                """,
                uuid4(),
                "memory.created",
                '{"memory_id": "mem-123"}',
            )

        # Process pending events
        await consumer._process_pending_events()

        assert len(received_events) == 1
        assert received_events[0]["memory_id"] == "mem-123"

    @pytest.mark.asyncio
    async def test_subscribe_pattern(self, consumer, clean_db):
        """Test subscribing to event patterns."""
        received_events = []

        async def handler(payload):
            received_events.append(payload)

        await consumer.subscribe_pattern("memory.%", handler)

        # Insert events
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, 'memory.created', '{"id": 1}', 'pending')
                """,
                uuid4(),
            )
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, 'memory.updated', '{"id": 2}', 'pending')
                """,
                uuid4(),
            )
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, 'decision.tracked', '{"id": 3}', 'pending')
                """,
                uuid4(),
            )

        # Process events
        await consumer._process_pending_events()

        # Should receive memory.created and memory.updated but not decision.tracked
        assert len(received_events) == 2

    @pytest.mark.asyncio
    async def test_acknowledge_event(self, consumer, clean_db):
        """Test acknowledging an event."""
        # Insert event
        event_id = uuid4()
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, 'test.event', '{}', 'pending')
                """,
                event_id,
            )

        # Acknowledge
        await consumer.acknowledge(str(event_id))

        # Verify status
        async with clean_db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT status FROM events WHERE event_id = $1",
                event_id,
            )

        assert row["status"] == "processed"

    @pytest.mark.asyncio
    async def test_reject_event_with_requeue(self, consumer, clean_db):
        """Test rejecting an event with requeue."""
        # Insert event
        event_id = uuid4()
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status, retry_count)
                VALUES ($1, 'test.event', '{}', 'pending', 0)
                """,
                event_id,
            )

        # Reject with requeue
        await consumer.reject(str(event_id), requeue=True, reason="test error")

        # Verify status and retry count
        async with clean_db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT status, retry_count FROM events WHERE event_id = $1",
                event_id,
            )

        assert row["status"] == "pending"
        assert row["retry_count"] == 1

    @pytest.mark.asyncio
    async def test_reject_event_without_requeue(self, consumer, clean_db):
        """Test rejecting an event without requeue."""
        # Insert event
        event_id = uuid4()
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, 'test.event', '{}', 'pending')
                """,
                event_id,
            )

        # Reject without requeue
        await consumer.reject(str(event_id), requeue=False, reason="fatal error")

        # Verify status
        async with clean_db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT status FROM events WHERE event_id = $1",
                event_id,
            )

        assert row["status"] == "failed"

    @pytest.mark.asyncio
    async def test_handler_error_rejects_event(self, consumer, clean_db):
        """Test that handler errors result in event rejection."""
        async def failing_handler(payload):
            raise ValueError("Handler failed")

        await consumer.subscribe("error.test", failing_handler)

        # Insert event
        event_id = uuid4()
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status, retry_count)
                VALUES ($1, 'error.test', '{"data": "test"}', 'pending', 0)
                """,
                event_id,
            )

        # Process events (should catch error)
        await consumer._process_pending_events()

        # Verify event was requeued
        async with clean_db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT status, retry_count FROM events WHERE event_id = $1",
                event_id,
            )

        assert row["status"] == "pending"
        assert row["retry_count"] == 1

    @pytest.mark.asyncio
    async def test_multiple_handlers_same_event(self, consumer, clean_db):
        """Test multiple handlers for the same event type."""
        results = {"handler1": False, "handler2": False}

        async def handler1(payload):
            results["handler1"] = True

        async def handler2(payload):
            results["handler2"] = True

        await consumer.subscribe("multi.test", handler1)
        await consumer.subscribe("multi.test", handler2)

        # Insert event
        async with clean_db.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO events (event_id, event_type, payload, status)
                VALUES ($1, 'multi.test', '{}', 'pending')
                """,
                uuid4(),
            )

        # Process
        await consumer._process_pending_events()

        # Both handlers should have been called
        assert results["handler1"] is True
        assert results["handler2"] is True


class TestEventFlowIntegration:
    """Integration tests for complete event flow."""

    @pytest_asyncio.fixture
    async def publisher(self, clean_db):
        """Create publisher."""
        from mind.adapters.standard.postgres_events import PostgresEventPublisher
        return PostgresEventPublisher(pool=clean_db)

    @pytest_asyncio.fixture
    async def consumer(self, clean_db):
        """Create consumer."""
        from mind.adapters.standard.postgres_events import PostgresEventConsumer
        consumer = PostgresEventConsumer(pool=clean_db)
        yield consumer
        await consumer.stop()

    @pytest.mark.asyncio
    async def test_publish_and_consume_flow(self, publisher, consumer, clean_db):
        """Test complete publish -> consume flow."""
        received = []

        async def handler(payload):
            received.append(payload)

        await consumer.subscribe("flow.test", handler)

        # Publish event
        await publisher.publish(
            event_type="flow.test",
            payload={"message": "hello"},
            user_id="test-user",
        )

        # Process pending
        await consumer._process_pending_events()

        assert len(received) == 1
        assert received[0]["message"] == "hello"

    @pytest.mark.asyncio
    async def test_event_ordering(self, publisher, consumer, clean_db):
        """Test that events are processed in order."""
        received = []

        async def handler(payload):
            received.append(payload["order"])

        await consumer.subscribe("order.test", handler)

        # Publish events in order
        for i in range(5):
            await publisher.publish(
                event_type="order.test",
                payload={"order": i},
            )

        # Process
        await consumer._process_pending_events()

        assert received == [0, 1, 2, 3, 4]
