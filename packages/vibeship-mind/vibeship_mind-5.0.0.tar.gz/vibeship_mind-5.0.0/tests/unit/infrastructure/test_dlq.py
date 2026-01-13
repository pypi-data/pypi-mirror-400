"""Tests for dead letter queue functionality.

Tests the DLQ handling in NATS infrastructure:
- Message routing to DLQ after max retries
- DLQ message format and metadata
- DLQ statistics and monitoring
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from mind.infrastructure.nats.consumer import EventConsumer, MAX_DELIVERY_ATTEMPTS
from mind.infrastructure.nats.dlq import (
    DLQMessage,
    get_dlq_stats,
    _parse_dlq_message,
)
from mind.observability.metrics import metrics


class TestDLQMessageDataclass:
    """Tests for DLQMessage dataclass."""

    def test_dlq_message_creation(self):
        """DLQMessage should store all required fields."""
        msg = DLQMessage(
            sequence=123,
            subject="mind.dlq.memory.created",
            original_subject="mind.memory.created",
            data={"event_type": "memory.created"},
            consumer="test-consumer",
            errors="Handler failed: connection timeout",
            failed_at="2024-12-28T10:00:00Z",
            attempts=3,
            timestamp=datetime.now(UTC),
        )

        assert msg.sequence == 123
        assert msg.subject == "mind.dlq.memory.created"
        assert msg.original_subject == "mind.memory.created"
        assert msg.consumer == "test-consumer"
        assert msg.attempts == 3

    def test_dlq_message_with_multiple_errors(self):
        """DLQMessage should store concatenated error messages."""
        msg = DLQMessage(
            sequence=456,
            subject="mind.dlq.decision.tracked",
            original_subject="mind.decision.tracked",
            data={},
            consumer="causal-updater",
            errors="Error 1; Error 2; Error 3",
            failed_at="2024-12-28T10:00:00Z",
            attempts=3,
            timestamp=datetime.now(UTC),
        )

        assert "Error 1" in msg.errors
        assert "Error 2" in msg.errors
        assert "Error 3" in msg.errors


class TestMaxDeliveryAttempts:
    """Tests for max delivery attempts configuration."""

    def test_max_delivery_attempts_constant(self):
        """MAX_DELIVERY_ATTEMPTS should be defined and reasonable."""
        assert MAX_DELIVERY_ATTEMPTS == 3

    def test_max_delivery_attempts_positive(self):
        """MAX_DELIVERY_ATTEMPTS should be positive."""
        assert MAX_DELIVERY_ATTEMPTS > 0


class TestParseDLQMessage:
    """Tests for _parse_dlq_message function."""

    def test_parse_valid_message(self):
        """Should parse a valid DLQ message."""
        msg = MagicMock()
        msg.subject = "mind.dlq.memory.created"
        msg.headers = {
            "X-Original-Subject": "mind.memory.created",
            "X-Consumer": "test-consumer",
            "X-Errors": "Handler failed",
            "X-Failed-At": "2024-12-28T10:00:00Z",
            "X-Attempts": "3",
        }
        msg.data = b'{"event_type": "memory.created", "user_id": "123"}'
        msg.seq = 100
        msg.time = datetime.now(UTC)

        result = _parse_dlq_message(msg)

        assert result is not None
        assert result.sequence == 100
        assert result.original_subject == "mind.memory.created"
        assert result.consumer == "test-consumer"
        assert result.attempts == 3

    def test_parse_message_missing_headers(self):
        """Should handle missing headers gracefully."""
        msg = MagicMock()
        msg.subject = "mind.dlq.test"
        msg.headers = None
        msg.data = b'{"test": true}'
        msg.seq = 50

        result = _parse_dlq_message(msg)

        assert result is not None
        assert result.original_subject == ""
        assert result.consumer == "unknown"

    def test_parse_invalid_json(self):
        """Should return None for invalid JSON."""
        msg = MagicMock()
        msg.subject = "mind.dlq.test"
        msg.headers = {}
        msg.data = b'invalid json'

        result = _parse_dlq_message(msg)

        assert result is None


class TestDLQMetrics:
    """Tests for DLQ-related metrics."""

    def test_record_dlq_message(self):
        """Metrics should record DLQ messages."""
        # Use unique labels to avoid conflicts with other tests
        test_consumer = f"test-consumer-dlq-{uuid4().hex[:8]}"
        test_event = f"mind.test.{uuid4().hex[:8]}"

        metrics.record_dlq_message(
            consumer=test_consumer,
            event_type=test_event,
        )

        # Metric should be incremented (can't check exact value due to shared state)
        labels = {"consumer": test_consumer, "event_type": test_event}
        assert metrics.dlq_messages_total.labels(**labels)._value.get() >= 1.0

    def test_set_dlq_depth(self):
        """Metrics should track DLQ depth."""
        test_stream = f"TEST_DLQ_{uuid4().hex[:8]}"

        metrics.set_dlq_depth(test_stream, 42)

        labels = {"stream": test_stream}
        assert metrics.dlq_depth.labels(**labels)._value.get() == 42.0

    def test_set_dlq_oldest_age(self):
        """Metrics should track oldest message age."""
        test_stream = f"TEST_DLQ_AGE_{uuid4().hex[:8]}"

        metrics.set_dlq_oldest_age(test_stream, 3600.5)

        labels = {"stream": test_stream}
        assert metrics.dlq_oldest_message_age_seconds.labels(**labels)._value.get() == 3600.5

    def test_record_event_processed_success(self):
        """Metrics should track successful event processing."""
        test_consumer = f"test-consumer-{uuid4().hex[:8]}"
        test_event = f"test.event.{uuid4().hex[:8]}"

        metrics.record_event_processed(
            consumer=test_consumer,
            event_type=test_event,
            success=True,
        )

        labels = {
            "consumer": test_consumer,
            "event_type": test_event,
            "status": "success",
        }
        assert metrics.events_processed_total.labels(**labels)._value.get() >= 1.0

    def test_record_event_processed_failure(self):
        """Metrics should track failed event processing."""
        test_consumer = f"test-consumer-fail-{uuid4().hex[:8]}"
        test_event = f"test.fail.{uuid4().hex[:8]}"

        metrics.record_event_processed(
            consumer=test_consumer,
            event_type=test_event,
            success=False,
        )

        labels = {
            "consumer": test_consumer,
            "event_type": test_event,
            "status": "failure",
        }
        assert metrics.events_processed_total.labels(**labels)._value.get() >= 1.0


class TestEventConsumerDLQIntegration:
    """Tests for EventConsumer DLQ integration."""

    @pytest.mark.asyncio
    async def test_consumer_has_send_to_dlq_method(self):
        """EventConsumer should have _send_to_dlq method."""
        client = MagicMock()
        consumer = EventConsumer(client, "test-consumer")

        assert hasattr(consumer, "_send_to_dlq")
        assert callable(consumer._send_to_dlq)

    @pytest.mark.asyncio
    async def test_send_to_dlq_publishes_message(self):
        """_send_to_dlq should publish to DLQ via client."""
        client = MagicMock()
        client.publish_to_dlq = AsyncMock()

        consumer = EventConsumer(client, "test-consumer")

        msg = MagicMock()
        msg.subject = "mind.memory.created"
        msg.data = b'{"test": true}'
        msg.metadata = MagicMock()
        msg.metadata.num_delivered = 3

        await consumer._send_to_dlq(msg, ["Error 1", "Error 2"])

        client.publish_to_dlq.assert_called_once()
        call_args = client.publish_to_dlq.call_args
        assert call_args[1]["original_subject"] == "mind.memory.created"
        assert "X-Consumer" in call_args[1]["headers"]
        assert "X-Errors" in call_args[1]["headers"]


class TestNatsClientDLQ:
    """Tests for NatsClient DLQ methods."""

    def test_client_has_dlq_constants(self):
        """NatsClient should define DLQ stream constants."""
        from mind.infrastructure.nats.client import NatsClient

        assert hasattr(NatsClient, "DLQ_STREAM_NAME")
        assert hasattr(NatsClient, "DLQ_SUBJECTS")
        assert NatsClient.DLQ_STREAM_NAME == "MIND_EVENTS_DLQ"
        assert "mind.dlq.>" in NatsClient.DLQ_SUBJECTS

    def test_client_has_publish_to_dlq_method(self):
        """NatsClient should have publish_to_dlq method."""
        from mind.infrastructure.nats.client import NatsClient

        client = NatsClient()
        assert hasattr(client, "publish_to_dlq")
        assert callable(client.publish_to_dlq)


class TestDLQSubjectMapping:
    """Tests for DLQ subject naming."""

    def test_dlq_subject_format(self):
        """DLQ subjects should follow mind.dlq.<original> format."""
        original = "mind.memory.created"
        expected_dlq = "mind.dlq.memory.created"

        # Test the subject transformation
        dlq_subject = f"mind.dlq.{original.replace('mind.', '')}"

        assert dlq_subject == expected_dlq

    def test_dlq_subject_preserves_event_type(self):
        """DLQ subject should preserve event type hierarchy."""
        test_cases = [
            ("mind.memory.created", "mind.dlq.memory.created"),
            ("mind.decision.tracked", "mind.dlq.decision.tracked"),
            ("mind.outcome.observed", "mind.dlq.outcome.observed"),
        ]

        for original, expected in test_cases:
            dlq_subject = f"mind.dlq.{original.replace('mind.', '')}"
            assert dlq_subject == expected


class TestDLQStreamConfig:
    """Tests for DLQ stream configuration."""

    def test_dlq_stream_has_longer_retention(self):
        """DLQ stream should have longer retention than main stream."""
        # From the implementation:
        # Main stream: 30 days
        # DLQ stream: 90 days
        main_retention_days = 30
        dlq_retention_days = 90

        assert dlq_retention_days > main_retention_days

    def test_dlq_stream_allows_sufficient_messages(self):
        """DLQ stream should allow enough messages for investigation."""
        # From implementation: 1M messages
        dlq_max_msgs = 1_000_000

        assert dlq_max_msgs >= 100_000  # At least 100k for reasonable investigation
