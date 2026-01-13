"""PostgreSQL pgvector adapter for vector similarity search.

This adapter implements IVectorSearch using PostgreSQL's pgvector
extension for efficient vector similarity search.

Requirements:
- PostgreSQL with pgvector extension installed
- memories table with embedding column of type vector
"""

from typing import Any, Optional
from uuid import UUID

import asyncpg

from ...ports.vectors import IVectorSearch, VectorSearchResult, VectorFilter


class PgVectorSearch(IVectorSearch):
    """PostgreSQL pgvector implementation of vector search.

    Uses cosine similarity for vector comparisons.
    Vectors are stored in the memories table alongside other fields.
    """

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with a connection pool.

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool

    async def index(
        self,
        id: UUID,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Index a vector with its metadata.

        For pgvector, we update the embedding column in the memories table.
        The metadata is already stored in other columns.
        """
        # Convert list to pgvector format
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

        await self.pool.execute(
            """
            UPDATE memories
            SET embedding = $2::vector,
                updated_at = NOW()
            WHERE memory_id = $1
            """,
            id,
            embedding_str,
        )

    async def index_batch(
        self,
        items: list[tuple[UUID, list[float], dict[str, Any]]],
    ) -> None:
        """Index multiple vectors in a single batch."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for id, embedding, metadata in items:
                    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
                    await conn.execute(
                        """
                        UPDATE memories
                        SET embedding = $2::vector,
                            updated_at = NOW()
                        WHERE memory_id = $1
                        """,
                        id,
                        embedding_str,
                    )

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filter: Optional[VectorFilter] = None,
    ) -> list[VectorSearchResult]:
        """Search for similar vectors using cosine similarity."""
        # Build query with filters
        conditions = ["embedding IS NOT NULL"]
        params: list[Any] = []
        param_idx = 1

        # Query embedding as first parameter
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        params.append(embedding_str)
        param_idx += 1

        if filter:
            if filter.user_id is not None:
                conditions.append(f"user_id = ${param_idx}")
                params.append(filter.user_id)
                param_idx += 1

            if filter.temporal_level is not None:
                conditions.append(f"temporal_level = ${param_idx}")
                params.append(filter.temporal_level)
                param_idx += 1

            if filter.content_type is not None:
                conditions.append(f"content_type = ${param_idx}")
                params.append(filter.content_type)
                param_idx += 1

            if filter.min_salience is not None:
                conditions.append(
                    f"(base_salience + outcome_adjustment) >= ${param_idx}"
                )
                params.append(filter.min_salience)
                param_idx += 1

            if filter.valid_only:
                conditions.append(
                    "(valid_until IS NULL OR valid_until > NOW())"
                )

        where_clause = " AND ".join(conditions)
        params.append(limit)

        # Cosine similarity: 1 - cosine_distance
        # pgvector uses <=> for cosine distance
        query = f"""
            SELECT
                memory_id,
                content,
                content_type,
                temporal_level,
                base_salience,
                outcome_adjustment,
                1 - (embedding <=> $1::vector) AS similarity
            FROM memories
            WHERE {where_clause}
            ORDER BY embedding <=> $1::vector
            LIMIT ${param_idx}
        """

        rows = await self.pool.fetch(query, *params)

        return [
            VectorSearchResult(
                id=row["memory_id"],
                score=float(row["similarity"]),
                metadata={
                    "content": row["content"],
                    "content_type": row["content_type"],
                    "temporal_level": row["temporal_level"],
                    "effective_salience": (
                        row["base_salience"] + row["outcome_adjustment"]
                    ),
                },
            )
            for row in rows
        ]

    async def search_by_id(
        self,
        id: UUID,
        limit: int = 10,
        filter: Optional[VectorFilter] = None,
    ) -> list[VectorSearchResult]:
        """Find vectors similar to an existing indexed vector."""
        # First get the embedding for the given ID
        row = await self.pool.fetchrow(
            "SELECT embedding FROM memories WHERE memory_id = $1",
            id,
        )

        if row is None or row["embedding"] is None:
            return []

        # Use the embedding to search
        # Note: pgvector stores as native type, we need to extract values
        embedding = list(row["embedding"])

        # Search excluding the query vector itself
        results = await self.search(embedding, limit + 1, filter)

        # Filter out the query vector
        return [r for r in results if r.id != id][:limit]

    async def delete(self, id: UUID) -> None:
        """Remove a vector from the index (set to NULL)."""
        await self.pool.execute(
            """
            UPDATE memories
            SET embedding = NULL,
                updated_at = NOW()
            WHERE memory_id = $1
            """,
            id,
        )

    async def delete_batch(self, ids: list[UUID]) -> None:
        """Remove multiple vectors from the index."""
        await self.pool.execute(
            """
            UPDATE memories
            SET embedding = NULL,
                updated_at = NOW()
            WHERE memory_id = ANY($1)
            """,
            ids,
        )

    async def get_embedding(self, id: UUID) -> Optional[list[float]]:
        """Retrieve the embedding for an indexed vector."""
        row = await self.pool.fetchrow(
            "SELECT embedding FROM memories WHERE memory_id = $1",
            id,
        )

        if row is None or row["embedding"] is None:
            return None

        return list(row["embedding"])

    async def count(self, filter: Optional[VectorFilter] = None) -> int:
        """Count vectors matching the filter."""
        conditions = ["embedding IS NOT NULL"]
        params: list[Any] = []
        param_idx = 1

        if filter:
            if filter.user_id is not None:
                conditions.append(f"user_id = ${param_idx}")
                params.append(filter.user_id)
                param_idx += 1

            if filter.temporal_level is not None:
                conditions.append(f"temporal_level = ${param_idx}")
                params.append(filter.temporal_level)
                param_idx += 1

            if filter.content_type is not None:
                conditions.append(f"content_type = ${param_idx}")
                params.append(filter.content_type)
                param_idx += 1

            if filter.min_salience is not None:
                conditions.append(
                    f"(base_salience + outcome_adjustment) >= ${param_idx}"
                )
                params.append(filter.min_salience)
                param_idx += 1

            if filter.valid_only:
                conditions.append(
                    "(valid_until IS NULL OR valid_until > NOW())"
                )

        where_clause = " AND ".join(conditions)

        query = f"SELECT COUNT(*) FROM memories WHERE {where_clause}"
        count = await self.pool.fetchval(query, *params)

        return count or 0

    async def health_check(self) -> bool:
        """Check if pgvector is available and working."""
        try:
            # Check if vector extension is installed
            result = await self.pool.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1 FROM pg_extension WHERE extname = 'vector'
                )
                """
            )
            return bool(result)
        except Exception:
            return False
