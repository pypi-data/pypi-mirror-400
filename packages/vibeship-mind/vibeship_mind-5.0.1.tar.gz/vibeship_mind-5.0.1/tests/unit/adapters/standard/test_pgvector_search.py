"""Unit tests for PgVector search adapter.

These tests mock the asyncpg pool to test vector search logic
without requiring a real database with pgvector.
"""

from typing import Optional
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from mind.adapters.standard.pgvector_search import PgVectorSearch
from mind.ports.vectors import VectorFilter


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_pool():
    """Create a mock asyncpg pool."""
    pool = AsyncMock()
    pool.execute = AsyncMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock()
    pool.fetchval = AsyncMock()
    return pool


@pytest.fixture
def mock_connection():
    """Create a mock asyncpg connection."""
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.transaction = MagicMock()
    return conn


@pytest.fixture
def vector_search(mock_pool):
    """Create a PgVectorSearch with mocked pool."""
    return PgVectorSearch(pool=mock_pool)


@pytest.fixture
def sample_embedding():
    """Create a sample embedding vector."""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 256  # 1280 dimensions


# =============================================================================
# Tests
# =============================================================================


class TestPgVectorSearch:
    """Tests for PgVectorSearch."""

    @pytest.mark.asyncio
    async def test_index_vector(self, vector_search, mock_pool, sample_embedding):
        """Test indexing a vector."""
        memory_id = uuid4()

        await vector_search.index(
            id=memory_id,
            embedding=sample_embedding,
            metadata={"content_type": "observation"},
        )

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "UPDATE memories" in call_args[0]
        assert "embedding = $2::vector" in call_args[0]

    @pytest.mark.asyncio
    async def test_index_batch(self, vector_search, mock_pool, sample_embedding):
        """Test indexing multiple vectors."""
        items = [
            (uuid4(), sample_embedding, {"type": "a"}),
            (uuid4(), sample_embedding, {"type": "b"}),
            (uuid4(), sample_embedding, {"type": "c"}),
        ]

        # Setup transaction context
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_conn.transaction.return_value.__aenter__ = AsyncMock()
        mock_conn.transaction.return_value.__aexit__ = AsyncMock(return_value=None)

        await vector_search.index_batch(items)

        assert mock_conn.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_search(self, vector_search, mock_pool, sample_embedding):
        """Test vector similarity search."""
        mock_pool.fetch.return_value = [
            MagicMock(
                __getitem__=lambda self, k: {
                    "memory_id": uuid4(),
                    "content": "Test content",
                    "content_type": "observation",
                    "temporal_level": 2,
                    "base_salience": 0.8,
                    "outcome_adjustment": 0.1,
                    "similarity": 0.95,
                }[k]
            ),
        ]

        results = await vector_search.search(
            query_embedding=sample_embedding,
            limit=10,
        )

        assert len(results) == 1
        assert results[0].score == 0.95
        assert results[0].metadata["content"] == "Test content"

    @pytest.mark.asyncio
    async def test_search_with_filter(self, vector_search, mock_pool, sample_embedding):
        """Test vector search with filters."""
        mock_pool.fetch.return_value = []
        user_id = uuid4()

        filter = VectorFilter(
            user_id=user_id,
            temporal_level=2,
            content_type="preference",
            min_salience=0.5,
            valid_only=True,
        )

        await vector_search.search(
            query_embedding=sample_embedding,
            limit=10,
            filter=filter,
        )

        call_args = mock_pool.fetch.call_args[0][0]
        assert "user_id = $" in call_args
        assert "temporal_level = $" in call_args
        assert "content_type = $" in call_args
        assert "(base_salience + outcome_adjustment) >= $" in call_args
        assert "valid_until IS NULL OR valid_until > NOW()" in call_args

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, vector_search, mock_pool, sample_embedding
    ):
        """Test search with no results."""
        mock_pool.fetch.return_value = []

        results = await vector_search.search(
            query_embedding=sample_embedding,
            limit=10,
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_search_by_id(self, vector_search, mock_pool, sample_embedding):
        """Test finding similar vectors to an existing one."""
        source_id = uuid4()
        similar_id = uuid4()

        # First call gets the source embedding
        mock_pool.fetchrow.return_value = MagicMock(
            __getitem__=lambda self, k: {"embedding": sample_embedding}[k]
        )

        # Second call returns search results
        mock_pool.fetch.return_value = [
            MagicMock(
                __getitem__=lambda self, k: {
                    "memory_id": source_id,
                    "content": "Source",
                    "content_type": "observation",
                    "temporal_level": 2,
                    "base_salience": 0.8,
                    "outcome_adjustment": 0.0,
                    "similarity": 1.0,
                }[k]
            ),
            MagicMock(
                __getitem__=lambda self, k: {
                    "memory_id": similar_id,
                    "content": "Similar",
                    "content_type": "observation",
                    "temporal_level": 2,
                    "base_salience": 0.7,
                    "outcome_adjustment": 0.0,
                    "similarity": 0.9,
                }[k]
            ),
        ]

        results = await vector_search.search_by_id(source_id, limit=5)

        # Should exclude the source itself
        assert len(results) == 1
        assert results[0].id == similar_id

    @pytest.mark.asyncio
    async def test_search_by_id_not_found(self, vector_search, mock_pool):
        """Test search by ID when source doesn't exist."""
        mock_pool.fetchrow.return_value = None

        results = await vector_search.search_by_id(uuid4(), limit=5)

        assert results == []

    @pytest.mark.asyncio
    async def test_search_by_id_no_embedding(self, vector_search, mock_pool):
        """Test search by ID when source has no embedding."""
        mock_pool.fetchrow.return_value = MagicMock(
            __getitem__=lambda self, k: {"embedding": None}[k]
        )

        results = await vector_search.search_by_id(uuid4(), limit=5)

        assert results == []

    @pytest.mark.asyncio
    async def test_delete_vector(self, vector_search, mock_pool):
        """Test removing a vector from index."""
        memory_id = uuid4()

        await vector_search.delete(memory_id)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "SET embedding = NULL" in call_args[0]

    @pytest.mark.asyncio
    async def test_delete_batch(self, vector_search, mock_pool):
        """Test removing multiple vectors."""
        ids = [uuid4(), uuid4(), uuid4()]

        await vector_search.delete_batch(ids)

        mock_pool.execute.assert_called_once()
        call_args = mock_pool.execute.call_args[0]
        assert "WHERE memory_id = ANY($1)" in call_args[0]

    @pytest.mark.asyncio
    async def test_get_embedding_found(
        self, vector_search, mock_pool, sample_embedding
    ):
        """Test retrieving an embedding."""
        mock_pool.fetchrow.return_value = MagicMock(
            __getitem__=lambda self, k: {"embedding": sample_embedding}[k]
        )

        result = await vector_search.get_embedding(uuid4())

        assert result == sample_embedding

    @pytest.mark.asyncio
    async def test_get_embedding_not_found(self, vector_search, mock_pool):
        """Test retrieving non-existent embedding."""
        mock_pool.fetchrow.return_value = None

        result = await vector_search.get_embedding(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_embedding_null(self, vector_search, mock_pool):
        """Test retrieving null embedding."""
        mock_pool.fetchrow.return_value = MagicMock(
            __getitem__=lambda self, k: {"embedding": None}[k]
        )

        result = await vector_search.get_embedding(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_count_all(self, vector_search, mock_pool):
        """Test counting all indexed vectors."""
        mock_pool.fetchval.return_value = 42

        count = await vector_search.count()

        assert count == 42

    @pytest.mark.asyncio
    async def test_count_with_filter(self, vector_search, mock_pool):
        """Test counting vectors with filter."""
        mock_pool.fetchval.return_value = 10
        user_id = uuid4()

        filter = VectorFilter(
            user_id=user_id,
            min_salience=0.5,
        )

        count = await vector_search.count(filter=filter)

        assert count == 10
        call_args = mock_pool.fetchval.call_args[0][0]
        assert "user_id = $" in call_args

    @pytest.mark.asyncio
    async def test_count_returns_zero_on_none(self, vector_search, mock_pool):
        """Test that count returns 0 when result is None."""
        mock_pool.fetchval.return_value = None

        count = await vector_search.count()

        assert count == 0

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, vector_search, mock_pool):
        """Test health check when pgvector is available."""
        mock_pool.fetchval.return_value = True

        result = await vector_search.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, vector_search, mock_pool):
        """Test health check when pgvector is not available."""
        mock_pool.fetchval.return_value = False

        result = await vector_search.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_error(self, vector_search, mock_pool):
        """Test health check when database error occurs."""
        mock_pool.fetchval.side_effect = Exception("Connection failed")

        result = await vector_search.health_check()

        assert result is False
