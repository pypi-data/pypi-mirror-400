"""Event port interfaces for publishing and consuming domain events.

These ports abstract the event backbone, allowing different implementations:
- Standard: PostgreSQL NOTIFY/LISTEN (synchronous, single-instance)
- Enterprise: NATS JetStream (async, distributed, replay-capable)
"""

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Optional

# Event handler type: async function that receives event payload
EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class IEventPublisher(ABC):
    """Port for publishing domain events.

    Events are the backbone of the learning loop:
    - memory.stored → Trigger embedding generation
    - decision.tracked → Record in causal graph
    - outcome.recorded → Trigger salience updates

    Implementations:
        - PostgresEventPublisher (Standard): Uses NOTIFY + events table
        - NatsEventPublisher (Enterprise): Uses NATS JetStream
    """

    @abstractmethod
    async def publish(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        user_id: Optional[str] = None,
    ) -> str:
        """Publish an event.

        Args:
            event_type: Event type (e.g., "memory.stored", "decision.tracked")
            payload: Event data (must be JSON-serializable)
            user_id: Optional user ID for routing/filtering

        Returns:
            Event ID for tracking

        Note:
            In Standard tier, events are persisted to PostgreSQL and
            processed synchronously or via PostgreSQL NOTIFY.

            In Enterprise tier, events go to NATS JetStream for
            durable, distributed processing.
        """
        pass

    @abstractmethod
    async def publish_batch(
        self,
        events: list[tuple[str, dict[str, Any]]],
        *,
        user_id: Optional[str] = None,
    ) -> list[str]:
        """Publish multiple events atomically.

        Args:
            events: List of (event_type, payload) tuples
            user_id: Optional user ID for all events

        Returns:
            List of event IDs

        Note:
            In Standard tier, this uses a database transaction.
            In Enterprise tier, this uses NATS batch publishing.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the publisher and release resources."""
        pass


class IEventConsumer(ABC):
    """Port for consuming domain events.

    Consumers handle events asynchronously (Enterprise) or
    synchronously (Standard) to trigger side effects.

    Implementations:
        - PostgresEventConsumer (Standard): Uses LISTEN + polling
        - NatsEventConsumer (Enterprise): Uses NATS JetStream consumers
    """

    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        *,
        consumer_name: Optional[str] = None,
    ) -> None:
        """Subscribe to events of a specific type.

        Args:
            event_type: Event type to subscribe to (e.g., "memory.stored")
            handler: Async function to handle events
            consumer_name: Optional name for durable subscription (Enterprise)

        Note:
            Multiple handlers can subscribe to the same event type.
            Each handler receives a copy of the event.
        """
        pass

    @abstractmethod
    async def subscribe_pattern(
        self,
        pattern: str,
        handler: EventHandler,
        *,
        consumer_name: Optional[str] = None,
    ) -> None:
        """Subscribe to events matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "memory.*", "decision.*")
            handler: Async function to handle events
            consumer_name: Optional name for durable subscription

        Note:
            Pattern syntax depends on implementation:
            - Standard: SQL LIKE pattern
            - Enterprise: NATS subject wildcards
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start consuming events.

        Must be called after subscriptions are set up.
        In Standard tier, this starts a background polling task.
        In Enterprise tier, this starts NATS consumers.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop consuming events gracefully.

        Waits for in-flight handlers to complete.
        """
        pass

    @abstractmethod
    async def acknowledge(self, event_id: str) -> None:
        """Acknowledge successful processing of an event.

        Args:
            event_id: The event ID to acknowledge

        Note:
            In Standard tier, this marks the event as processed.
            In Enterprise tier, this acknowledges to NATS.
            Unacknowledged events may be redelivered.
        """
        pass

    @abstractmethod
    async def reject(
        self,
        event_id: str,
        *,
        requeue: bool = True,
        reason: Optional[str] = None,
    ) -> None:
        """Reject an event (processing failed).

        Args:
            event_id: The event ID to reject
            requeue: If True, event will be redelivered later
            reason: Optional reason for rejection (for logging)

        Note:
            In Standard tier, this updates the event status.
            In Enterprise tier, this NAKs to NATS for redelivery.
        """
        pass


class ISyncEventHandler(ABC):
    """Port for synchronous event handling (Standard tier optimization).

    In Standard tier, we can skip the event queue entirely and
    process events synchronously for lower latency.

    This is used by the LearningService to update salience immediately
    after outcome recording, rather than waiting for async processing.
    """

    @abstractmethod
    async def handle_outcome_recorded(
        self,
        trace_id: str,
        outcome_quality: float,
        memory_attributions: dict[str, float],
    ) -> dict[str, float]:
        """Handle outcome synchronously, returning salience adjustments.

        Args:
            trace_id: The decision trace ID
            outcome_quality: Outcome quality (-1.0 to 1.0)
            memory_attributions: Memory ID -> attribution score

        Returns:
            Memory ID -> salience adjustment applied
        """
        pass
