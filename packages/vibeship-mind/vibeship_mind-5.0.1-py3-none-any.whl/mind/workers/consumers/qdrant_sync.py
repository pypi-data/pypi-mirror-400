"""Qdrant sync consumer.

This consumer listens for memory events and syncs vectors to Qdrant
for high-performance similarity search.

Flow:
    MemoryCreated → QdrantSync → upsert to Qdrant
    MemoryDeleted → QdrantSync → delete from Qdrant
"""

import structlog

from mind.core.events.base import EventEnvelope, EventType
from mind.core.memory.models import Memory, TemporalLevel
from mind.infrastructure.nats.client import NatsClient
from mind.infrastructure.nats.consumer import EventConsumer

logger = structlog.get_logger()


class QdrantSyncConsumer:
    """Syncs memory vectors to Qdrant for high-performance search."""

    CONSUMER_NAME = "qdrant-sync"

    def __init__(self, client: NatsClient):
        self._client = client
        self._consumer = EventConsumer(client, self.CONSUMER_NAME)
        self._qdrant_repo = None
        self._embedder = None
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Register event handlers."""
        self._consumer.on(EventType.MEMORY_CREATED, self._handle_memory_created)

    async def start(self) -> None:
        """Initialize Qdrant client and start consuming."""
        # Try to connect to Qdrant
        try:
            from mind.config import get_settings
            settings = get_settings()

            if settings.qdrant_url:
                from mind.infrastructure.qdrant.client import get_qdrant_client, ensure_collection
                from mind.infrastructure.qdrant.repository import QdrantVectorRepository, MEMORIES_COLLECTION
                from mind.infrastructure.embeddings.openai import get_embedder

                client = await get_qdrant_client()
                ensure_collection(client, MEMORIES_COLLECTION)
                self._qdrant_repo = QdrantVectorRepository(client)
                self._embedder = get_embedder()
                logger.info("qdrant_sync_enabled")
            else:
                logger.info("qdrant_sync_disabled", reason="qdrant_not_configured")
        except Exception as e:
            logger.warning("qdrant_sync_init_failed", error=str(e))

        logger.info("qdrant_sync_starting")
        await self._consumer.start(subjects=["mind.memory.created.*"])

    async def stop(self) -> None:
        """Stop the consumer."""
        await self._consumer.stop()
        logger.info("qdrant_sync_stopped")

    async def _handle_memory_created(self, envelope: EventEnvelope) -> None:
        """Sync new memory to Qdrant."""
        if self._qdrant_repo is None:
            return  # Qdrant not configured

        from uuid import UUID
        from datetime import datetime

        payload = envelope.payload
        log = logger.bind(memory_id=payload.get("memory_id"))

        # Generate embedding for content
        content = payload.get("content", "")
        if not content or not self._embedder:
            log.debug("qdrant_sync_skipped", reason="no_content_or_embedder")
            return

        embed_result = await self._embedder.embed(content)
        if embed_result.is_err:
            log.warning("embedding_failed", error=str(embed_result.error))
            return

        embedding = embed_result.value

        # Create Memory object for upsert
        valid_from = payload.get("valid_from")
        if isinstance(valid_from, str):
            valid_from = datetime.fromisoformat(valid_from)
        elif valid_from is None:
            valid_from = datetime.now()

        valid_until = payload.get("valid_until")
        if isinstance(valid_until, str):
            valid_until = datetime.fromisoformat(valid_until)

        memory = Memory(
            memory_id=UUID(payload["memory_id"]),
            user_id=UUID(payload["user_id"]),
            content=content,
            content_type=payload.get("content_type", "observation"),
            temporal_level=TemporalLevel(payload.get("temporal_level", 2)),
            valid_from=valid_from,
            valid_until=valid_until,
            base_salience=payload.get("base_salience", 1.0),
            outcome_adjustment=payload.get("outcome_adjustment", 0.0),
        )

        # Upsert to Qdrant
        result = await self._qdrant_repo.upsert(memory, embedding)
        if result.is_ok:
            log.debug("qdrant_memory_synced")
        else:
            log.warning("qdrant_upsert_failed", error=str(result.error))


async def create_qdrant_sync() -> QdrantSyncConsumer:
    """Factory to create and initialize the Qdrant sync consumer."""
    from mind.infrastructure.nats.client import get_nats_client

    client = await get_nats_client()
    return QdrantSyncConsumer(client)
