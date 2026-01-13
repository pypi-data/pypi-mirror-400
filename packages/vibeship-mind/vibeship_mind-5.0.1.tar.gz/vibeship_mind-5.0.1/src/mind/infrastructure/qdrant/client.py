"""Qdrant client management.

Qdrant is used as a dedicated vector store for high-performance
similarity search. It supplements pgvector for production workloads.
"""

import structlog
from qdrant_client import QdrantClient as _QdrantClient
from qdrant_client.http import models as qdrant_models

from mind.config import get_settings

logger = structlog.get_logger()


# Type alias for the official client
QdrantClient = _QdrantClient

# Global client instance
_qdrant_client: QdrantClient | None = None


async def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client instance.

    Returns a connected Qdrant client. The client is cached
    for reuse across requests.

    Raises:
        ValueError: If Qdrant is not configured
    """
    global _qdrant_client

    if _qdrant_client is None:
        settings = get_settings()

        if not settings.qdrant_url:
            raise ValueError("Qdrant not configured. Set MIND_QDRANT_URL environment variable.")

        logger.info("qdrant_connecting", url=settings.qdrant_url)

        api_key = None
        if settings.qdrant_api_key:
            api_key = settings.qdrant_api_key.get_secret_value()

        _qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=api_key,
            timeout=30.0,
        )

        logger.info("qdrant_connected")

    return _qdrant_client


async def close_qdrant_client() -> None:
    """Close Qdrant client connection."""
    global _qdrant_client

    if _qdrant_client is not None:
        _qdrant_client.close()
        _qdrant_client = None
        logger.info("qdrant_disconnected")


async def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int = 1536,
) -> None:
    """Ensure a collection exists with the correct schema.

    Args:
        client: Qdrant client
        collection_name: Name of the collection
        vector_size: Dimension of vectors (default: 1536 for OpenAI)
    """
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if collection_name not in collection_names:
        logger.info("qdrant_creating_collection", collection=collection_name)

        client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
            # Enable payload indexing for common filters
            optimizers_config=qdrant_models.OptimizersConfigDiff(
                indexing_threshold=10000,
            ),
        )

        # Create payload indexes for efficient filtering
        client.create_payload_index(
            collection_name=collection_name,
            field_name="user_id",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=collection_name,
            field_name="temporal_level",
            field_schema=qdrant_models.PayloadSchemaType.INTEGER,
        )
        client.create_payload_index(
            collection_name=collection_name,
            field_name="effective_salience",
            field_schema=qdrant_models.PayloadSchemaType.FLOAT,
        )

        logger.info("qdrant_collection_created", collection=collection_name)
    else:
        logger.debug("qdrant_collection_exists", collection=collection_name)
