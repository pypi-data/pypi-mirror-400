"""Vector search port interface for semantic similarity.

This port abstracts vector similarity search, allowing different implementations:
- Standard: pgvector in PostgreSQL
- Enterprise: Qdrant (dedicated vector database)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID


@dataclass
class VectorSearchResult:
    """A single result from vector similarity search."""

    id: UUID
    score: float  # Similarity score (0.0 - 1.0, higher is more similar)
    metadata: dict[str, Any]  # Associated metadata

    def __lt__(self, other: "VectorSearchResult") -> bool:
        """Compare by score for sorting (higher scores first)."""
        return self.score > other.score


@dataclass
class VectorFilter:
    """Filter criteria for vector search.

    All specified filters are ANDed together.
    """

    user_id: Optional[UUID] = None
    temporal_level: Optional[int] = None
    content_type: Optional[str] = None
    min_salience: Optional[float] = None
    valid_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for adapter implementations."""
        result = {}
        if self.user_id is not None:
            result["user_id"] = str(self.user_id)
        if self.temporal_level is not None:
            result["temporal_level"] = self.temporal_level
        if self.content_type is not None:
            result["content_type"] = self.content_type
        if self.min_salience is not None:
            result["min_salience"] = self.min_salience
        if self.valid_only:
            result["valid_only"] = True
        return result


class IVectorSearch(ABC):
    """Port for vector similarity search operations.

    Implementations:
        - PgVectorSearch (Standard): Uses pgvector extension
        - QdrantVectorSearch (Enterprise): Uses Qdrant vector DB
    """

    @abstractmethod
    async def index(
        self,
        id: UUID,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Index a vector with its metadata.

        Args:
            id: Unique identifier (usually memory_id)
            embedding: The embedding vector
            metadata: Associated metadata for filtering

        Note:
            If a vector with this ID already exists, it is updated.
        """
        pass

    @abstractmethod
    async def index_batch(
        self,
        items: list[tuple[UUID, list[float], dict[str, Any]]],
    ) -> None:
        """Index multiple vectors in a single batch.

        Args:
            items: List of (id, embedding, metadata) tuples

        Note:
            More efficient than multiple single index calls.
            Uses transactions in Standard tier.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filter: Optional[VectorFilter] = None,
    ) -> list[VectorSearchResult]:
        """Search for similar vectors.

        Args:
            query_embedding: The query vector
            limit: Maximum number of results
            filter: Optional filter criteria

        Returns:
            List of results sorted by similarity (highest first)
        """
        pass

    @abstractmethod
    async def search_by_id(
        self,
        id: UUID,
        limit: int = 10,
        filter: Optional[VectorFilter] = None,
    ) -> list[VectorSearchResult]:
        """Find vectors similar to an existing indexed vector.

        Args:
            id: ID of the vector to find similar items for
            limit: Maximum number of results
            filter: Optional filter criteria

        Returns:
            List of similar vectors (excluding the query vector)
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Remove a vector from the index.

        Args:
            id: The vector ID to delete

        Note:
            No error if ID doesn't exist.
        """
        pass

    @abstractmethod
    async def delete_batch(self, ids: list[UUID]) -> None:
        """Remove multiple vectors from the index.

        Args:
            ids: List of vector IDs to delete
        """
        pass

    @abstractmethod
    async def get_embedding(self, id: UUID) -> Optional[list[float]]:
        """Retrieve the embedding for an indexed vector.

        Args:
            id: The vector ID

        Returns:
            The embedding if found, None otherwise
        """
        pass

    @abstractmethod
    async def count(self, filter: Optional[VectorFilter] = None) -> int:
        """Count vectors matching the filter.

        Args:
            filter: Optional filter criteria

        Returns:
            Number of matching vectors
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the vector search backend is healthy.

        Returns:
            True if healthy, False otherwise
        """
        pass
