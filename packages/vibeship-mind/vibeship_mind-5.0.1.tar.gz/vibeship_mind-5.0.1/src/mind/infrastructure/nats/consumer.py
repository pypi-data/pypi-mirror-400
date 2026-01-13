"""Event consumption from NATS JetStream."""

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from uuid import UUID

import orjson
import structlog
from nats.js.api import AckPolicy, ConsumerConfig, DeliverPolicy

from mind.core.events.base import EventEnvelope, EventType
from mind.infrastructure.nats.client import NatsClient
from mind.observability.metrics import metrics

logger = structlog.get_logger()

# Maximum delivery attempts before sending to DLQ
MAX_DELIVERY_ATTEMPTS = 3

# Type alias for event handlers
EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventConsumer:
    """Consumes events from NATS JetStream."""

    def __init__(self, client: NatsClient, consumer_name: str):
        self._client = client
        self._consumer_name = consumer_name
        self._handlers: dict[EventType, list[EventHandler]] = {}
        self._running = False
        self._subscription = None

    def on(self, event_type: EventType, handler: EventHandler) -> None:
        """Register a handler for an event type.

        Args:
            event_type: The event type to handle
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(
            "handler_registered",
            event_type=event_type.value,
            consumer=self._consumer_name,
        )

    async def start(
        self,
        subjects: list[str] | None = None,
        deliver_policy: DeliverPolicy = DeliverPolicy.NEW,
    ) -> None:
        """Start consuming events.

        Args:
            subjects: Subjects to subscribe to (default: all Mind events)
            deliver_policy: Where to start consuming from
        """
        if self._running:
            logger.warning("consumer_already_running", consumer=self._consumer_name)
            return

        subjects = subjects or ["mind.>"]
        log = logger.bind(consumer=self._consumer_name, subjects=subjects)

        try:
            # Create durable consumer
            config = ConsumerConfig(
                durable_name=self._consumer_name,
                deliver_policy=deliver_policy,
                ack_policy=AckPolicy.EXPLICIT,
                max_deliver=MAX_DELIVERY_ATTEMPTS,  # Retry up to 3 times
                ack_wait=30,  # 30 seconds to ack
            )

            # Subscribe with pull-based consumer for better control
            self._subscription = await self._client.jetstream.pull_subscribe(
                subject=subjects[0] if len(subjects) == 1 else "mind.>",
                durable=self._consumer_name,
                config=config,
            )

            self._running = True
            log.info("consumer_started")

            # Start processing loop
            asyncio.create_task(self._process_loop())

        except Exception as e:
            log.error("consumer_start_failed", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop consuming events."""
        self._running = False
        if self._subscription:
            await self._subscription.unsubscribe()
            self._subscription = None
        logger.info("consumer_stopped", consumer=self._consumer_name)

    async def _process_loop(self) -> None:
        """Main processing loop."""
        log = logger.bind(consumer=self._consumer_name)

        while self._running:
            try:
                # Fetch batch of messages
                messages = await self._subscription.fetch(batch=10, timeout=5)

                for msg in messages:
                    await self._handle_message(msg)

            except TimeoutError:
                # No messages, continue
                continue
            except Exception as e:
                log.error("process_loop_error", error=str(e))
                await asyncio.sleep(1)  # Back off on error

    async def _handle_message(self, msg) -> None:
        """Handle a single message."""
        log = logger.bind(consumer=self._consumer_name, subject=msg.subject)

        # Get delivery attempt from metadata
        metadata = msg.metadata
        num_delivered = metadata.num_delivered if metadata else 1
        log = log.bind(attempt=num_delivered)

        try:
            # Parse envelope
            data = orjson.loads(msg.data)
            envelope = EventEnvelope(
                event_id=UUID(data["event_id"]),
                event_type=EventType(data["event_type"]),
                user_id=UUID(data["user_id"]),
                aggregate_id=UUID(data["aggregate_id"]),
                payload=data["payload"],
                correlation_id=UUID(data["correlation_id"]),
                causation_id=UUID(data["causation_id"]) if data.get("causation_id") else None,
                timestamp=data["timestamp"],
                version=data["version"],
            )

            log = log.bind(
                event_id=str(envelope.event_id),
                event_type=envelope.event_type.value,
            )

            # Find handlers
            handlers = self._handlers.get(envelope.event_type, [])
            if not handlers:
                log.debug("no_handlers")
                await msg.ack()
                return

            # Execute handlers
            handler_errors = []
            for handler in handlers:
                try:
                    await handler(envelope)
                except Exception as e:
                    log.error("handler_error", error=str(e))
                    handler_errors.append(str(e))
                    # Continue with other handlers

            # If any handler failed, check if we should send to DLQ
            if handler_errors:
                if num_delivered >= MAX_DELIVERY_ATTEMPTS:
                    await self._send_to_dlq(msg, handler_errors)
                    await msg.ack()  # Ack to prevent further retries
                else:
                    await msg.nak()  # Retry
                return

            await msg.ack()
            log.debug("message_processed")
            metrics.record_event_processed(
                consumer=self._consumer_name,
                event_type=envelope.event_type.value,
                success=True,
            )

        except Exception as e:
            log.error("message_handling_failed", error=str(e))

            # Check if we've exhausted retries
            if num_delivered >= MAX_DELIVERY_ATTEMPTS:
                await self._send_to_dlq(msg, [str(e)])
                await msg.ack()  # Ack to prevent further retries
            else:
                await msg.nak()  # Retry

            metrics.record_event_processed(
                consumer=self._consumer_name,
                event_type="unknown",
                success=False,
            )

    async def _send_to_dlq(self, msg, errors: list[str]) -> None:
        """Send a failed message to the dead letter queue."""
        log = logger.bind(
            consumer=self._consumer_name,
            subject=msg.subject,
        )

        try:
            headers = {
                "X-Consumer": self._consumer_name,
                "X-Errors": "; ".join(errors[:3]),  # Limit error length
                "X-Failed-At": datetime.now(UTC).isoformat(),
                "X-Attempts": str(msg.metadata.num_delivered if msg.metadata else 1),
            }

            await self._client.publish_to_dlq(
                original_subject=msg.subject,
                data=msg.data,
                headers=headers,
            )

            log.warning(
                "message_sent_to_dlq",
                errors=errors[:3],
            )
            metrics.record_dlq_message(
                consumer=self._consumer_name,
                event_type=msg.subject,
            )

        except Exception as e:
            log.error("dlq_publish_failed", error=str(e))
            # Nothing more we can do - message will be lost
