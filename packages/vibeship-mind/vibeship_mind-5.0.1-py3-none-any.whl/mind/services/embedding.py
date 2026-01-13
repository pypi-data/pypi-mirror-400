"""Embedding service with caching and metrics.

Provides a high-level interface for generating embeddings with:
- LRU caching to reduce API calls
- Metrics for monitoring
- Fallback handling
"""

import hashlib

import structlog

from mind.core.errors import Result
from mind.infrastructure.embeddings.openai import OpenAIEmbedder, get_embedder

logger = structlog.get_logger()

# Cache size for embeddings (in-memory LRU)
EMBEDDING_CACHE_SIZE = 10000


class EmbeddingService:
    """Service for generating and caching embeddings.

    Provides:
    - Caching to reduce duplicate API calls
    - Batch processing for efficiency
    - Metrics for monitoring usage
    """

    def __init__(self, embedder: OpenAIEmbedder | None = None):
        """Initialize the embedding service.

        Args:
            embedder: Optional embedder instance (uses global if not provided)
        """
        self._embedder = embedder or get_embedder()
        self._cache: dict[str, list[float]] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_requests = 0
        self._total_tokens = 0  # Estimated

    async def embed(self, text: str) -> Result[list[float]]:
        """Generate embedding for text, using cache if available.

        Args:
            text: Text to embed

        Returns:
            Result with embedding vector
        """
        self._total_requests += 1

        # Check cache
        cache_key = self._cache_key(text)
        if cache_key in self._cache:
            self._cache_hits += 1
            logger.debug("embedding_cache_hit", key=cache_key[:16])
            return Result.ok(self._cache[cache_key])

        self._cache_misses += 1

        # Generate embedding
        result = await self._embedder.embed(text)

        if result.is_ok:
            # Cache the result
            self._cache[cache_key] = result.value
            self._evict_if_needed()

            # Estimate tokens (rough approximation)
            self._total_tokens += len(text) // 4

        return result

    async def embed_batch(
        self,
        texts: list[str],
    ) -> Result[list[list[float]]]:
        """Generate embeddings for multiple texts.

        Uses cache for texts that have been seen before,
        only calls API for new texts.

        Args:
            texts: List of texts to embed

        Returns:
            Result with list of embedding vectors
        """
        if not texts:
            return Result.ok([])

        self._total_requests += len(texts)

        # Separate cached and uncached
        results: list[list[float] | None] = [None] * len(texts)
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        for i, text in enumerate(texts):
            cache_key = self._cache_key(text)
            if cache_key in self._cache:
                self._cache_hits += 1
                results[i] = self._cache[cache_key]
            else:
                self._cache_misses += 1
                uncached_indices.append(i)
                uncached_texts.append(text)

        # Fetch uncached embeddings
        if uncached_texts:
            result = await self._embedder.embed_batch(uncached_texts)

            if not result.is_ok:
                return Result.err(result.error)

            # Store in results and cache
            for i, embedding in enumerate(result.value):
                original_index = uncached_indices[i]
                results[original_index] = embedding

                cache_key = self._cache_key(uncached_texts[i])
                self._cache[cache_key] = embedding

                # Estimate tokens
                self._total_tokens += len(uncached_texts[i]) // 4

            self._evict_if_needed()

        return Result.ok(results)

    def get_metrics(self) -> dict:
        """Get embedding service metrics.

        Returns:
            Dict with cache and usage metrics
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0

        return {
            "total_requests": self._total_requests,
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": hit_rate,
            "estimated_tokens": self._total_tokens,
        }

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("embedding_cache_cleared")

    def _cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full.

        Simple FIFO eviction - could be improved with LRU.
        """
        while len(self._cache) > EMBEDDING_CACHE_SIZE:
            # Remove first key (oldest in insertion order)
            first_key = next(iter(self._cache))
            del self._cache[first_key]


# Global service instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
