"""PostgreSQL event adapters using NOTIFY/LISTEN.

These adapters implement IEventPublisher and IEventConsumer using
PostgreSQL's built-in NOTIFY/LISTEN mechanism for event delivery.

For Standard tier, this provides:
- Durable event storage (events table)
- Real-time notification (NOTIFY/LISTEN)
- At-least-once delivery semantics
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

import asyncpg

from ...ports.events import IEventPublisher, IEventConsumer, EventHandler


class PostgresEventPublisher(IEventPublisher):
    """PostgreSQL implementation of event publishing.

    Events are:
    1. Persisted to the events table for durability
    2. Published via NOTIFY for real-time consumption

    This ensures events survive crashes and can be replayed if needed.
    """

    CHANNEL = "mind_events"

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with a connection pool.

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool

    async def publish(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        user_id: Optional[str] = None,
    ) -> str:
        """Publish an event."""
        event_id = str(uuid4())
        now = datetime.now(UTC)

        # Add metadata to payload
        enriched_payload = {
            **payload,
            "_event_id": event_id,
            "_event_type": event_type,
            "_timestamp": now.isoformat(),
        }
        if user_id:
            enriched_payload["_user_id"] = user_id

        payload_json = json.dumps(enriched_payload)

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Persist to events table
                await conn.execute(
                    """
                    INSERT INTO events (
                        event_id, event_type, payload, user_id,
                        status, created_at
                    ) VALUES ($1, $2, $3, $4, 'pending', $5)
                    """,
                    event_id,
                    event_type,
                    payload_json,
                    user_id,
                    now,
                )

                # Notify listeners
                # PostgreSQL NOTIFY payload has a limit, so we send just the ID
                notification = json.dumps({
                    "event_id": event_id,
                    "event_type": event_type,
                })
                await conn.execute(
                    f"NOTIFY {self.CHANNEL}, $1",
                    notification,
                )

        return event_id

    async def publish_batch(
        self,
        events: list[tuple[str, dict[str, Any]]],
        *,
        user_id: Optional[str] = None,
    ) -> list[str]:
        """Publish multiple events atomically."""
        event_ids = []
        now = datetime.now(UTC)

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for event_type, payload in events:
                    event_id = str(uuid4())
                    event_ids.append(event_id)

                    enriched_payload = {
                        **payload,
                        "_event_id": event_id,
                        "_event_type": event_type,
                        "_timestamp": now.isoformat(),
                    }
                    if user_id:
                        enriched_payload["_user_id"] = user_id

                    payload_json = json.dumps(enriched_payload)

                    await conn.execute(
                        """
                        INSERT INTO events (
                            event_id, event_type, payload, user_id,
                            status, created_at
                        ) VALUES ($1, $2, $3, $4, 'pending', $5)
                        """,
                        event_id,
                        event_type,
                        payload_json,
                        user_id,
                        now,
                    )

                # Notify once for the batch
                notification = json.dumps({
                    "batch": True,
                    "count": len(events),
                })
                await conn.execute(
                    f"NOTIFY {self.CHANNEL}, $1",
                    notification,
                )

        return event_ids

    async def close(self) -> None:
        """Close the publisher."""
        # Pool is managed externally, nothing to close here
        pass


class PostgresEventConsumer(IEventConsumer):
    """PostgreSQL implementation of event consumption.

    Uses LISTEN for real-time notifications, with polling fallback
    for events that might have been missed.

    Processing flow:
    1. LISTEN receives notification
    2. Fetch full event from events table
    3. Call registered handlers
    4. Mark event as processed
    """

    CHANNEL = "mind_events"
    POLL_INTERVAL = 5.0  # Seconds between polls for missed events

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with a connection pool.

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool
        self._handlers: dict[str, list[EventHandler]] = {}
        self._pattern_handlers: list[tuple[str, EventHandler]] = []
        self._running = False
        self._listen_conn: Optional[asyncpg.Connection] = None
        self._tasks: list[asyncio.Task] = []

    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        *,
        consumer_name: Optional[str] = None,
    ) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def subscribe_pattern(
        self,
        pattern: str,
        handler: EventHandler,
        *,
        consumer_name: Optional[str] = None,
    ) -> None:
        """Subscribe to events matching a pattern.

        Pattern uses SQL LIKE syntax:
        - 'memory.%' matches memory.stored, memory.updated, etc.
        - 'decision.%' matches all decision events
        """
        self._pattern_handlers.append((pattern, handler))

    async def start(self) -> None:
        """Start consuming events."""
        if self._running:
            return

        self._running = True

        # Start listener task
        self._listen_conn = await self.pool.acquire()
        await self._listen_conn.add_listener(
            self.CHANNEL,
            self._notification_callback,
        )

        # Start poller task for missed events
        poller_task = asyncio.create_task(self._poll_loop())
        self._tasks.append(poller_task)

    async def stop(self) -> None:
        """Stop consuming events gracefully."""
        self._running = False

        # Cancel tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks.clear()

        # Release listener connection
        if self._listen_conn:
            await self._listen_conn.remove_listener(
                self.CHANNEL,
                self._notification_callback,
            )
            await self.pool.release(self._listen_conn)
            self._listen_conn = None

    async def acknowledge(self, event_id: str) -> None:
        """Acknowledge successful processing of an event."""
        await self.pool.execute(
            """
            UPDATE events
            SET status = 'processed',
                processed_at = NOW()
            WHERE event_id = $1
            """,
            event_id,
        )

    async def reject(
        self,
        event_id: str,
        *,
        requeue: bool = True,
        reason: Optional[str] = None,
    ) -> None:
        """Reject an event (processing failed)."""
        if requeue:
            await self.pool.execute(
                """
                UPDATE events
                SET status = 'pending',
                    retry_count = retry_count + 1,
                    last_error = $2
                WHERE event_id = $1
                """,
                event_id,
                reason,
            )
        else:
            await self.pool.execute(
                """
                UPDATE events
                SET status = 'failed',
                    last_error = $2
                WHERE event_id = $1
                """,
                event_id,
                reason,
            )

    def _notification_callback(
        self,
        connection: asyncpg.Connection,
        pid: int,
        channel: str,
        payload: str,
    ) -> None:
        """Handle incoming NOTIFY messages."""
        # Schedule async processing
        asyncio.create_task(self._handle_notification(payload))

    async def _handle_notification(self, payload: str) -> None:
        """Process a notification payload."""
        try:
            data = json.loads(payload)

            if data.get("batch"):
                # Batch notification - poll for new events
                await self._process_pending_events()
            else:
                # Single event notification
                event_id = data.get("event_id")
                if event_id:
                    await self._process_event(event_id)

        except json.JSONDecodeError:
            pass  # Ignore malformed notifications
        except Exception as e:
            # Log but don't crash
            import sys
            print(f"Error processing notification: {e}", file=sys.stderr)

    async def _process_event(self, event_id: str) -> None:
        """Process a single event by ID."""
        row = await self.pool.fetchrow(
            """
            SELECT event_id, event_type, payload
            FROM events
            WHERE event_id = $1 AND status = 'pending'
            """,
            event_id,
        )

        if row is None:
            return  # Already processed or doesn't exist

        await self._dispatch_event(
            row["event_id"],
            row["event_type"],
            json.loads(row["payload"]),
        )

    async def _dispatch_event(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Dispatch event to matching handlers."""
        handlers_to_call = []

        # Exact match handlers
        if event_type in self._handlers:
            handlers_to_call.extend(self._handlers[event_type])

        # Pattern match handlers
        for pattern, handler in self._pattern_handlers:
            # Convert glob pattern to simple matching
            if self._matches_pattern(event_type, pattern):
                handlers_to_call.append(handler)

        if not handlers_to_call:
            # No handlers, acknowledge anyway
            await self.acknowledge(event_id)
            return

        # Call all handlers
        try:
            for handler in handlers_to_call:
                await handler(payload)
            await self.acknowledge(event_id)
        except Exception as e:
            await self.reject(event_id, requeue=True, reason=str(e))

    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches a pattern."""
        # Simple glob matching: % matches any characters
        import fnmatch
        # Convert SQL LIKE to fnmatch
        fnmatch_pattern = pattern.replace("%", "*")
        return fnmatch.fnmatch(event_type, fnmatch_pattern)

    async def _poll_loop(self) -> None:
        """Periodically poll for missed events."""
        while self._running:
            try:
                await asyncio.sleep(self.POLL_INTERVAL)
                await self._process_pending_events()
            except asyncio.CancelledError:
                break
            except Exception as e:
                import sys
                print(f"Error in poll loop: {e}", file=sys.stderr)

    async def _process_pending_events(self) -> None:
        """Process all pending events."""
        rows = await self.pool.fetch(
            """
            SELECT event_id, event_type, payload
            FROM events
            WHERE status = 'pending'
              AND retry_count < 5
            ORDER BY created_at ASC
            LIMIT 100
            """
        )

        for row in rows:
            await self._dispatch_event(
                row["event_id"],
                row["event_type"],
                json.loads(row["payload"]),
            )
