"""Dead Letter Queue utilities for Mind v5.

This module provides utilities for managing failed messages in the DLQ:
- Listing messages in the DLQ
- Inspecting message details
- Replaying messages back to the main stream
- Purging acknowledged messages

Usage:
    python -m mind.infrastructure.nats.dlq list
    python -m mind.infrastructure.nats.dlq inspect <sequence>
    python -m mind.infrastructure.nats.dlq replay <sequence>
    python -m mind.infrastructure.nats.dlq replay-all
    python -m mind.infrastructure.nats.dlq stats
"""

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

import orjson
import structlog
from nats.js.api import AckPolicy, ConsumerConfig, DeliverPolicy

from mind.infrastructure.nats.client import NatsClient, get_nats_client
from mind.observability.metrics import metrics

logger = structlog.get_logger()


@dataclass
class DLQMessage:
    """A message from the dead letter queue."""

    sequence: int
    subject: str
    original_subject: str
    data: dict
    consumer: str
    errors: str
    failed_at: str
    attempts: int
    timestamp: datetime


async def get_dlq_stats(client: NatsClient | None = None) -> dict:
    """Get statistics about the dead letter queue.

    Returns:
        Dict with message_count, oldest_message_age, consumer_breakdown
    """
    if client is None:
        client = await get_nats_client()

    try:
        stream_info = await client.jetstream.stream_info(NatsClient.DLQ_STREAM_NAME)

        message_count = stream_info.state.messages
        first_seq = stream_info.state.first_seq
        first_ts = stream_info.state.first_ts

        oldest_age_seconds = 0.0
        if first_ts:
            oldest_age_seconds = (datetime.now(UTC) - first_ts).total_seconds()

        # Update metrics
        metrics.set_dlq_depth(NatsClient.DLQ_STREAM_NAME, message_count)
        if oldest_age_seconds > 0:
            metrics.set_dlq_oldest_age(NatsClient.DLQ_STREAM_NAME, oldest_age_seconds)

        return {
            "stream": NatsClient.DLQ_STREAM_NAME,
            "message_count": message_count,
            "oldest_sequence": first_seq,
            "oldest_message_age_seconds": oldest_age_seconds,
            "bytes": stream_info.state.bytes,
        }

    except Exception as e:
        logger.error("dlq_stats_failed", error=str(e))
        return {
            "stream": NatsClient.DLQ_STREAM_NAME,
            "message_count": 0,
            "error": str(e),
        }


async def list_dlq_messages(
    client: NatsClient | None = None,
    limit: int = 100,
) -> list[DLQMessage]:
    """List messages in the dead letter queue.

    Args:
        client: NATS client (will create one if not provided)
        limit: Maximum number of messages to return

    Returns:
        List of DLQMessage objects
    """
    if client is None:
        client = await get_nats_client()

    messages = []

    try:
        # Create ephemeral consumer to read messages
        config = ConsumerConfig(
            deliver_policy=DeliverPolicy.ALL,
            ack_policy=AckPolicy.NONE,  # Don't ack, just peek
        )

        sub = await client.jetstream.pull_subscribe(
            subject="mind.dlq.>",
            config=config,
        )

        try:
            fetched = await sub.fetch(batch=limit, timeout=5)

            for msg in fetched:
                dlq_msg = _parse_dlq_message(msg)
                if dlq_msg:
                    messages.append(dlq_msg)

        except TimeoutError:
            pass  # No more messages

        finally:
            await sub.unsubscribe()

    except Exception as e:
        logger.error("dlq_list_failed", error=str(e))

    return messages


async def inspect_dlq_message(
    sequence: int,
    client: NatsClient | None = None,
) -> DLQMessage | None:
    """Get details of a specific DLQ message.

    Args:
        sequence: The sequence number of the message
        client: NATS client

    Returns:
        DLQMessage or None if not found
    """
    if client is None:
        client = await get_nats_client()

    try:
        msg = await client.jetstream.get_msg(
            NatsClient.DLQ_STREAM_NAME,
            sequence,
        )
        return _parse_dlq_message(msg)

    except Exception as e:
        logger.error("dlq_inspect_failed", sequence=sequence, error=str(e))
        return None


async def replay_dlq_message(
    sequence: int,
    client: NatsClient | None = None,
) -> bool:
    """Replay a DLQ message back to the main stream.

    Args:
        sequence: The sequence number of the message
        client: NATS client

    Returns:
        True if replay succeeded
    """
    if client is None:
        client = await get_nats_client()

    try:
        # Get the message
        msg = await client.jetstream.get_msg(
            NatsClient.DLQ_STREAM_NAME,
            sequence,
        )

        # Get original subject from headers
        headers = msg.headers or {}
        original_subject = headers.get("X-Original-Subject", "")

        if not original_subject:
            logger.error("dlq_replay_failed_no_subject", sequence=sequence)
            return False

        # Republish to original subject
        await client.jetstream.publish(
            original_subject,
            msg.data,
            headers={"X-Replayed-From-DLQ": "true"},
        )

        # Delete from DLQ
        await client.jetstream.delete_msg(
            NatsClient.DLQ_STREAM_NAME,
            sequence,
        )

        logger.info(
            "dlq_message_replayed",
            sequence=sequence,
            original_subject=original_subject,
        )
        return True

    except Exception as e:
        logger.error("dlq_replay_failed", sequence=sequence, error=str(e))
        return False


async def replay_all_dlq_messages(
    client: NatsClient | None = None,
    limit: int = 1000,
) -> dict:
    """Replay all messages from the DLQ.

    Args:
        client: NATS client
        limit: Maximum number of messages to replay

    Returns:
        Dict with replayed_count, failed_count
    """
    if client is None:
        client = await get_nats_client()

    messages = await list_dlq_messages(client, limit=limit)

    replayed = 0
    failed = 0

    for msg in messages:
        success = await replay_dlq_message(msg.sequence, client)
        if success:
            replayed += 1
        else:
            failed += 1

    logger.info(
        "dlq_replay_all_complete",
        replayed=replayed,
        failed=failed,
    )

    return {
        "replayed_count": replayed,
        "failed_count": failed,
    }


async def purge_dlq(
    client: NatsClient | None = None,
    older_than_days: int = 30,
) -> int:
    """Purge old messages from the DLQ.

    Args:
        client: NATS client
        older_than_days: Delete messages older than this

    Returns:
        Number of messages purged
    """
    if client is None:
        client = await get_nats_client()

    # NATS JetStream handles this via max_age config
    # For manual purge, we'd need to iterate and delete
    # This is a placeholder for future implementation

    logger.info(
        "dlq_purge_requested",
        older_than_days=older_than_days,
    )

    return 0  # TODO: Implement manual purge if needed


def _parse_dlq_message(msg) -> DLQMessage | None:
    """Parse a NATS message into a DLQMessage."""
    try:
        headers = msg.headers or {}
        data = orjson.loads(msg.data)

        return DLQMessage(
            sequence=msg.seq if hasattr(msg, "seq") else 0,
            subject=msg.subject,
            original_subject=headers.get("X-Original-Subject", ""),
            data=data,
            consumer=headers.get("X-Consumer", "unknown"),
            errors=headers.get("X-Errors", ""),
            failed_at=headers.get("X-Failed-At", ""),
            attempts=int(headers.get("X-Attempts", "0")),
            timestamp=msg.time if hasattr(msg, "time") else datetime.now(UTC),
        )
    except Exception as e:
        logger.error("dlq_parse_failed", error=str(e))
        return None


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m mind.infrastructure.nats.dlq <command>")
        print("Commands: list, inspect <seq>, replay <seq>, replay-all, stats")
        sys.exit(1)

    command = sys.argv[1]

    async def run():
        if command == "list":
            messages = await list_dlq_messages(limit=50)
            print(f"\nDLQ Messages ({len(messages)} found):")
            print("-" * 80)
            for msg in messages:
                print(f"  [{msg.sequence}] {msg.original_subject}")
                print(f"      Consumer: {msg.consumer}")
                print(f"      Errors: {msg.errors[:100]}")
                print(f"      Failed: {msg.failed_at}")
                print()

        elif command == "stats":
            stats = await get_dlq_stats()
            print("\nDLQ Statistics:")
            print("-" * 40)
            for key, value in stats.items():
                print(f"  {key}: {value}")

        elif command == "inspect" and len(sys.argv) > 2:
            seq = int(sys.argv[2])
            msg = await inspect_dlq_message(seq)
            if msg:
                print(f"\nMessage {seq}:")
                print(f"  Subject: {msg.subject}")
                print(f"  Original: {msg.original_subject}")
                print(f"  Consumer: {msg.consumer}")
                print(f"  Errors: {msg.errors}")
                print(f"  Failed at: {msg.failed_at}")
                print(f"  Attempts: {msg.attempts}")
                print("\nData:")
                print(orjson.dumps(msg.data, option=orjson.OPT_INDENT_2).decode())
            else:
                print(f"Message {seq} not found")

        elif command == "replay" and len(sys.argv) > 2:
            seq = int(sys.argv[2])
            success = await replay_dlq_message(seq)
            if success:
                print(f"Message {seq} replayed successfully")
            else:
                print(f"Failed to replay message {seq}")

        elif command == "replay-all":
            result = await replay_all_dlq_messages()
            print(f"\nReplayed: {result['replayed_count']}")
            print(f"Failed: {result['failed_count']}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    asyncio.run(run())


if __name__ == "__main__":
    main()
