"""Qdrant vector repository for memory embeddings.

This repository provides high-performance vector similarity search
for memory retrieval. It works alongside PostgreSQL which stores
the full memory data.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from mind.core.errors import ErrorCode, MindError, Result
from mind.core.memory.models import Memory, TemporalLevel

logger = structlog.get_logger()

# Default collection name
MEMORIES_COLLECTION = "mind_memories"


@dataclass
class VectorSearchResult:
    """Result from a vector similarity search."""

    memory_id: UUID
    user_id: UUID
    score: float  # Similarity score (0-1 for cosine)
    temporal_level: TemporalLevel
    effective_salience: float


class QdrantVectorRepository:
    """Repository for vector operations on memories.

    This repository handles vector storage and similarity search.
    It does not store full memory content - that remains in PostgreSQL.
    """

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = MEMORIES_COLLECTION,
    ):
        self._client = client
        self._collection_name = collection_name

    async def upsert(self, memory: Memory, embedding: list[float]) -> Result[None]:
        """Store or update a memory's vector.

        Args:
            memory: The memory to store
            embedding: The embedding vector

        Returns:
            Result indicating success or failure
        """
        try:
            self._client.upsert(
                collection_name=self._collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=str(memory.memory_id),
                        vector=embedding,
                        payload={
                            "user_id": str(memory.user_id),
                            "temporal_level": memory.temporal_level.value,
                            "effective_salience": memory.effective_salience,
                            "valid_from": memory.valid_from.isoformat(),
                            "valid_until": (
                                memory.valid_until.isoformat() if memory.valid_until else None
                            ),
                            "created_at": memory.created_at.isoformat(),
                        },
                    )
                ],
            )

            logger.debug(
                "qdrant_upsert_success",
                memory_id=str(memory.memory_id),
                collection=self._collection_name,
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "qdrant_upsert_failed",
                memory_id=str(memory.memory_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to upsert vector: {e}",
                    context={"memory_id": str(memory.memory_id)},
                )
            )

    async def search(
        self,
        user_id: UUID,
        query_vector: list[float],
        limit: int = 10,
        temporal_levels: list[TemporalLevel] | None = None,
        min_salience: float = 0.0,
        score_threshold: float = 0.0,
    ) -> Result[list[VectorSearchResult]]:
        """Search for similar memories.

        Args:
            user_id: User whose memories to search
            query_vector: Query embedding vector
            limit: Maximum results to return
            temporal_levels: Filter by temporal levels (None = all)
            min_salience: Minimum effective salience
            score_threshold: Minimum similarity score

        Returns:
            List of search results ordered by similarity
        """
        try:
            # Build filter conditions
            must_conditions = [
                qdrant_models.FieldCondition(
                    key="user_id",
                    match=qdrant_models.MatchValue(value=str(user_id)),
                ),
                qdrant_models.FieldCondition(
                    key="effective_salience",
                    range=qdrant_models.Range(gte=min_salience),
                ),
            ]

            # Add temporal level filter if specified
            if temporal_levels:
                level_values = [level.value for level in temporal_levels]
                must_conditions.append(
                    qdrant_models.FieldCondition(
                        key="temporal_level",
                        match=qdrant_models.MatchAny(any=level_values),
                    )
                )

            # Add validity filter (not expired)
            now_iso = datetime.now(UTC).isoformat()
            should_conditions = [
                qdrant_models.FieldCondition(
                    key="valid_until",
                    match=qdrant_models.MatchValue(value=None),
                ),
                qdrant_models.FieldCondition(
                    key="valid_until",
                    range=qdrant_models.Range(gt=now_iso),
                ),
            ]

            search_result = self._client.search(
                collection_name=self._collection_name,
                query_vector=query_vector,
                query_filter=qdrant_models.Filter(
                    must=must_conditions,
                    should=should_conditions,
                ),
                limit=limit,
                score_threshold=score_threshold,
            )

            results = []
            for point in search_result:
                payload = point.payload or {}
                results.append(
                    VectorSearchResult(
                        memory_id=UUID(point.id),
                        user_id=UUID(payload.get("user_id", str(user_id))),
                        score=point.score,
                        temporal_level=TemporalLevel(payload.get("temporal_level", 0)),
                        effective_salience=payload.get("effective_salience", 1.0),
                    )
                )

            logger.debug(
                "qdrant_search_complete",
                user_id=str(user_id),
                results_count=len(results),
                limit=limit,
            )

            return Result.ok(results)

        except Exception as e:
            logger.error(
                "qdrant_search_failed",
                user_id=str(user_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Vector search failed: {e}",
                    context={"user_id": str(user_id)},
                )
            )

    async def delete(self, memory_id: UUID) -> Result[None]:
        """Delete a memory's vector.

        Args:
            memory_id: ID of memory to delete

        Returns:
            Result indicating success or failure
        """
        try:
            self._client.delete(
                collection_name=self._collection_name,
                points_selector=qdrant_models.PointIdsList(
                    points=[str(memory_id)],
                ),
            )

            logger.debug(
                "qdrant_delete_success",
                memory_id=str(memory_id),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "qdrant_delete_failed",
                memory_id=str(memory_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to delete vector: {e}",
                    context={"memory_id": str(memory_id)},
                )
            )

    async def update_salience(
        self,
        memory_id: UUID,
        new_salience: float,
    ) -> Result[None]:
        """Update the salience score for a memory.

        This allows efficient filtering by salience without
        re-indexing the full vector.

        Args:
            memory_id: ID of memory to update
            new_salience: New effective salience value

        Returns:
            Result indicating success or failure
        """
        try:
            self._client.set_payload(
                collection_name=self._collection_name,
                payload={"effective_salience": new_salience},
                points=[str(memory_id)],
            )

            logger.debug(
                "qdrant_salience_updated",
                memory_id=str(memory_id),
                salience=new_salience,
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "qdrant_salience_update_failed",
                memory_id=str(memory_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to update salience: {e}",
                    context={"memory_id": str(memory_id)},
                )
            )

    async def update_temporal_level(
        self,
        memory_id: UUID,
        new_level: TemporalLevel,
    ) -> Result[None]:
        """Update the temporal level for a memory.

        Called when a memory is promoted.

        Args:
            memory_id: ID of memory to update
            new_level: New temporal level

        Returns:
            Result indicating success or failure
        """
        try:
            self._client.set_payload(
                collection_name=self._collection_name,
                payload={"temporal_level": new_level.value},
                points=[str(memory_id)],
            )

            logger.debug(
                "qdrant_level_updated",
                memory_id=str(memory_id),
                level=new_level.name,
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "qdrant_level_update_failed",
                memory_id=str(memory_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to update temporal level: {e}",
                    context={"memory_id": str(memory_id)},
                )
            )
