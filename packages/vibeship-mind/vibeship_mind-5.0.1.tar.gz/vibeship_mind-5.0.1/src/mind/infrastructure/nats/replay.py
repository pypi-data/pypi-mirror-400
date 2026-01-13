"""Event replay capability for Mind v5.

This module provides utilities for replaying events from the event store
to rebuild projections or reprocess historical data.

Use cases:
- Rebuild projections after schema changes
- Reprocess events after bug fixes
- Migrate data to new consumers
- Backfill analytics

Usage:
    python -m mind.infrastructure.nats.replay --from-sequence 1 --to-sequence 1000
    python -m mind.infrastructure.nats.replay --event-type memory.created
    python -m mind.infrastructure.nats.replay --user-id <uuid>
    python -m mind.infrastructure.nats.replay --since 2024-01-01
"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

import orjson
import structlog
from nats.js.api import AckPolicy, ConsumerConfig, DeliverPolicy

from mind.core.events.base import EventEnvelope, EventType
from mind.infrastructure.nats.client import NatsClient, get_nats_client

logger = structlog.get_logger()

# Type alias for replay handlers
ReplayHandler = Callable[[EventEnvelope], Awaitable[None]]


@dataclass
class ReplayProgress:
    """Tracks replay progress."""

    total_events: int = 0
    processed_events: int = 0
    failed_events: int = 0
    skipped_events: int = 0
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_sequence: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.processed_events == 0:
            return 0.0
        return (self.processed_events - self.failed_events) / self.processed_events

    @property
    def elapsed_seconds(self) -> float:
        """Calculate elapsed time in seconds."""
        return (datetime.now(UTC) - self.start_time).total_seconds()

    @property
    def events_per_second(self) -> float:
        """Calculate processing rate."""
        if self.elapsed_seconds == 0:
            return 0.0
        return self.processed_events / self.elapsed_seconds


@dataclass
class ReplayConfig:
    """Configuration for event replay."""

    # Range filters
    from_sequence: int | None = None
    to_sequence: int | None = None
    since: datetime | None = None
    until: datetime | None = None

    # Content filters
    event_types: list[EventType] | None = None
    user_ids: list[UUID] | None = None

    # Processing options
    batch_size: int = 100
    max_events: int | None = None
    dry_run: bool = False
    stop_on_error: bool = False

    # Rate limiting
    events_per_second: float | None = None


class EventReplayer:
    """Replays events from the event store."""

    def __init__(
        self,
        client: NatsClient,
        config: ReplayConfig,
    ):
        self._client = client
        self._config = config
        self._handlers: dict[EventType, list[ReplayHandler]] = {}
        self._progress = ReplayProgress()
        self._running = False

    def on(self, event_type: EventType, handler: ReplayHandler) -> None:
        """Register a handler for an event type.

        Args:
            event_type: The event type to handle
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(
            "replay_handler_registered",
            event_type=event_type.value,
        )

    def on_all(self, handler: ReplayHandler) -> None:
        """Register a handler for all event types.

        Args:
            handler: Async function to handle all events
        """
        for event_type in EventType:
            self.on(event_type, handler)

    async def replay(self) -> ReplayProgress:
        """Execute the replay.

        Returns:
            ReplayProgress with statistics
        """
        log = logger.bind(
            from_sequence=self._config.from_sequence,
            event_types=[e.value for e in (self._config.event_types or [])],
            dry_run=self._config.dry_run,
        )

        log.info("replay_starting")
        self._running = True
        self._progress = ReplayProgress()

        try:
            # Determine delivery policy based on config
            deliver_policy = DeliverPolicy.ALL
            opt_start_seq = None
            opt_start_time = None

            if self._config.from_sequence:
                deliver_policy = DeliverPolicy.BY_START_SEQUENCE
                opt_start_seq = self._config.from_sequence
            elif self._config.since:
                deliver_policy = DeliverPolicy.BY_START_TIME
                opt_start_time = self._config.since

            # Create ephemeral consumer for replay
            config = ConsumerConfig(
                deliver_policy=deliver_policy,
                opt_start_seq=opt_start_seq,
                opt_start_time=opt_start_time,
                ack_policy=AckPolicy.NONE,  # Don't ack during replay
            )

            sub = await self._client.jetstream.pull_subscribe(
                subject="mind.>",
                config=config,
            )

            try:
                await self._process_events(sub)
            finally:
                await sub.unsubscribe()

        except Exception as e:
            log.error("replay_failed", error=str(e))
            self._progress.errors.append(f"Replay failed: {e}")

        self._running = False

        log.info(
            "replay_completed",
            processed=self._progress.processed_events,
            failed=self._progress.failed_events,
            skipped=self._progress.skipped_events,
            elapsed_seconds=self._progress.elapsed_seconds,
            events_per_second=self._progress.events_per_second,
        )

        return self._progress

    async def _process_events(self, sub) -> None:
        """Process events from the subscription."""
        while self._running:
            # Check if we've reached the limit
            if (
                self._config.max_events
                and self._progress.processed_events >= self._config.max_events
            ):
                logger.info("replay_max_events_reached")
                break

            try:
                messages = await sub.fetch(
                    batch=self._config.batch_size,
                    timeout=5,
                )

                if not messages:
                    # No more messages
                    break

                for msg in messages:
                    # Check max_events inside the loop too
                    if (
                        self._config.max_events
                        and self._progress.processed_events >= self._config.max_events
                    ):
                        logger.info("replay_max_events_reached")
                        self._running = False
                        break

                    await self._process_message(msg)

                    # Rate limiting
                    if self._config.events_per_second:
                        await asyncio.sleep(1 / self._config.events_per_second)

            except TimeoutError:
                # No more messages available
                break
            except Exception as e:
                logger.error("replay_batch_error", error=str(e))
                if self._config.stop_on_error:
                    break

    async def _process_message(self, msg) -> None:
        """Process a single message."""
        self._progress.total_events += 1

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

            # Check sequence limit
            if msg.metadata and msg.metadata.sequence:
                self._progress.last_sequence = msg.metadata.sequence.stream
                if (
                    self._config.to_sequence
                    and msg.metadata.sequence.stream > self._config.to_sequence
                ):
                    self._running = False
                    return

            # Check time limit
            if self._config.until and envelope.timestamp > self._config.until:
                self._running = False
                return

            # Apply filters
            if not self._should_process(envelope):
                self._progress.skipped_events += 1
                return

            # Dry run - just count
            if self._config.dry_run:
                self._progress.processed_events += 1
                return

            # Find and execute handlers
            handlers = self._handlers.get(envelope.event_type, [])
            if not handlers:
                self._progress.skipped_events += 1
                return

            for handler in handlers:
                try:
                    await handler(envelope)
                except Exception as e:
                    logger.error(
                        "replay_handler_error",
                        event_id=str(envelope.event_id),
                        error=str(e),
                    )
                    self._progress.failed_events += 1
                    self._progress.errors.append(f"Event {envelope.event_id}: {e}")
                    if self._config.stop_on_error:
                        self._running = False
                        return

            self._progress.processed_events += 1

            # Log progress periodically
            if self._progress.processed_events % 1000 == 0:
                logger.info(
                    "replay_progress",
                    processed=self._progress.processed_events,
                    failed=self._progress.failed_events,
                    events_per_second=self._progress.events_per_second,
                )

        except Exception as e:
            logger.error("replay_parse_error", error=str(e))
            self._progress.failed_events += 1

    def _should_process(self, envelope: EventEnvelope) -> bool:
        """Check if an event should be processed based on filters."""
        # Event type filter
        if self._config.event_types and envelope.event_type not in self._config.event_types:
            return False

        # User ID filter
        if self._config.user_ids and envelope.user_id not in self._config.user_ids:
            return False

        # Time range filter
        if self._config.since:
            if isinstance(envelope.timestamp, str):
                ts = datetime.fromisoformat(envelope.timestamp.replace("Z", "+00:00"))
            else:
                ts = envelope.timestamp
            if ts < self._config.since:
                return False

        if self._config.until:
            if isinstance(envelope.timestamp, str):
                ts = datetime.fromisoformat(envelope.timestamp.replace("Z", "+00:00"))
            else:
                ts = envelope.timestamp
            if ts > self._config.until:
                return False

        return True

    def stop(self) -> None:
        """Stop the replay."""
        self._running = False

    @property
    def progress(self) -> ReplayProgress:
        """Get current progress."""
        return self._progress


async def get_stream_info(client: NatsClient | None = None) -> dict:
    """Get information about the event stream.

    Returns:
        Dict with message count, sequences, timestamps
    """
    if client is None:
        client = await get_nats_client()

    try:
        stream_info = await client.jetstream.stream_info(NatsClient.STREAM_NAME)

        return {
            "stream": NatsClient.STREAM_NAME,
            "message_count": stream_info.state.messages,
            "first_sequence": stream_info.state.first_seq,
            "last_sequence": stream_info.state.last_seq,
            "first_timestamp": str(stream_info.state.first_ts)
            if stream_info.state.first_ts
            else None,
            "last_timestamp": str(stream_info.state.last_ts) if stream_info.state.last_ts else None,
            "bytes": stream_info.state.bytes,
            "consumer_count": stream_info.state.consumer_count,
        }

    except Exception as e:
        logger.error("stream_info_failed", error=str(e))
        return {
            "stream": NatsClient.STREAM_NAME,
            "error": str(e),
        }


async def count_events_by_type(
    client: NatsClient | None = None,
    sample_size: int = 10000,
) -> dict[str, int]:
    """Count events by type (samples if stream is large).

    Args:
        client: NATS client
        sample_size: Maximum events to sample

    Returns:
        Dict of event_type -> count
    """
    if client is None:
        client = await get_nats_client()

    counts: dict[str, int] = {}

    config = ReplayConfig(
        max_events=sample_size,
        dry_run=True,
    )

    replayer = EventReplayer(client, config)

    async def count_handler(envelope: EventEnvelope) -> None:
        event_type = envelope.event_type.value
        counts[event_type] = counts.get(event_type, 0) + 1

    replayer.on_all(count_handler)
    await replayer.replay()

    return counts


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Replay events from the event store")
    parser.add_argument("--from-sequence", type=int, help="Start from sequence number")
    parser.add_argument("--to-sequence", type=int, help="Stop at sequence number")
    parser.add_argument("--since", type=str, help="Start from timestamp (ISO format)")
    parser.add_argument("--until", type=str, help="Stop at timestamp (ISO format)")
    parser.add_argument("--event-type", type=str, action="append", help="Filter by event type")
    parser.add_argument("--user-id", type=str, action="append", help="Filter by user ID")
    parser.add_argument("--max-events", type=int, help="Maximum events to replay")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size")
    parser.add_argument("--rate-limit", type=float, help="Events per second limit")
    parser.add_argument("--dry-run", action="store_true", help="Count only, don't process")
    parser.add_argument("--info", action="store_true", help="Show stream info")
    parser.add_argument("--count", action="store_true", help="Count events by type")

    args = parser.parse_args()

    async def run():
        if args.info:
            info = await get_stream_info()
            print("\nEvent Stream Info:")
            print("-" * 40)
            for key, value in info.items():
                print(f"  {key}: {value}")
            return

        if args.count:
            counts = await count_events_by_type()
            print("\nEvents by Type:")
            print("-" * 40)
            for event_type, count in sorted(counts.items()):
                print(f"  {event_type}: {count}")
            print(f"\n  Total: {sum(counts.values())}")
            return

        # Build config
        config = ReplayConfig(
            from_sequence=args.from_sequence,
            to_sequence=args.to_sequence,
            since=datetime.fromisoformat(args.since) if args.since else None,
            until=datetime.fromisoformat(args.until) if args.until else None,
            event_types=[EventType(t) for t in args.event_type] if args.event_type else None,
            user_ids=[UUID(u) for u in args.user_id] if args.user_id else None,
            max_events=args.max_events,
            batch_size=args.batch_size,
            events_per_second=args.rate_limit,
            dry_run=args.dry_run,
        )

        client = await get_nats_client()
        replayer = EventReplayer(client, config)

        # For CLI, just log events
        async def log_handler(envelope: EventEnvelope) -> None:
            print(f"[{envelope.timestamp}] {envelope.event_type.value} - {envelope.event_id}")

        if not args.dry_run:
            replayer.on_all(log_handler)

        progress = await replayer.replay()

        print("\nReplay Complete:")
        print("-" * 40)
        print(f"  Processed: {progress.processed_events}")
        print(f"  Failed: {progress.failed_events}")
        print(f"  Skipped: {progress.skipped_events}")
        print(f"  Elapsed: {progress.elapsed_seconds:.2f}s")
        print(f"  Rate: {progress.events_per_second:.2f} events/sec")
        print(f"  Success Rate: {progress.success_rate * 100:.1f}%")

        if progress.errors:
            print(f"\nErrors ({len(progress.errors)}):")
            for err in progress.errors[:10]:
                print(f"  - {err}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
