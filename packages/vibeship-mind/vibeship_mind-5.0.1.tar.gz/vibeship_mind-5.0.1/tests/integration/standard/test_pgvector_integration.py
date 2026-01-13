"""Integration tests for PgVector search adapter.

These tests verify PgVectorSearch works correctly against
a real PostgreSQL database with pgvector extension.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.integration.standard.conftest import requires_docker


pytestmark = [pytest.mark.integration, requires_docker]


class TestPgVectorSearchIntegration:
    """Integration tests for PgVectorSearch."""

    @pytest_asyncio.fixture
    async def vector_search(self, clean_db):
        """Create a PgVectorSearch instance."""
        from mind.adapters.standard.pgvector_search import PgVectorSearch
        return PgVectorSearch(pool=clean_db)

    @pytest_asyncio.fixture
    async def memory_storage(self, clean_db):
        """Create a PostgresMemoryStorage instance."""
        from mind.adapters.standard.postgres_storage import PostgresMemoryStorage
        return PostgresMemoryStorage(pool=clean_db)

    @pytest_asyncio.fixture
    async def stored_memories(self, memory_storage, test_user, sample_embedding):
        """Create and store test memories with embeddings."""
        from mind.core.memory.models import Memory, TemporalLevel
        import random

        memories = []
        for i in range(5):
            memory = Memory(
                memory_id=uuid4(),
                user_id=test_user,
                content=f"Test memory {i} with unique content",
                content_type="observation",
                temporal_level=TemporalLevel.SESSION,
                base_salience=0.5 + (i * 0.1),
                outcome_adjustment=0.0,
                valid_from=datetime.now(UTC),
            )
            await memory_storage.store(memory)
            memories.append(memory)

        return memories

    @pytest.mark.asyncio
    async def test_index_and_search_vector(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test indexing a vector and searching for it."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="User prefers Python programming language",
            content_type="preference",
            temporal_level=TemporalLevel.IDENTITY,
            base_salience=0.9,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(memory)

        # Index the embedding
        await vector_search.index(
            id=memory.memory_id,
            embedding=sample_embedding,
            metadata={"content_type": "preference"},
        )

        # Search using the same embedding (should find exact match)
        results = await vector_search.search(
            query_embedding=sample_embedding,
            limit=10,
        )

        assert len(results) >= 1
        assert results[0].id == memory.memory_id
        assert results[0].score >= 0.99  # Near-perfect match

    @pytest.mark.asyncio
    async def test_search_with_user_filter(
        self, vector_search, memory_storage, test_user, clean_db, sample_embedding
    ):
        """Test searching with user filter."""
        from mind.core.memory.models import Memory, TemporalLevel
        from mind.ports.vectors import VectorFilter

        # Create another user
        other_user = uuid4()
        async with clean_db.acquire() as conn:
            await conn.execute("INSERT INTO users (user_id) VALUES ($1)", other_user)

        # Create memory for test user
        memory1 = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Test user memory",
            content_type="observation",
            temporal_level=TemporalLevel.SESSION,
            base_salience=0.8,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(memory1)
        await vector_search.index(memory1.memory_id, sample_embedding, {})

        # Create memory for other user with slightly different embedding
        memory2 = Memory(
            memory_id=uuid4(),
            user_id=other_user,
            content="Other user memory",
            content_type="observation",
            temporal_level=TemporalLevel.SESSION,
            base_salience=0.8,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(memory2)
        # Slightly perturb the embedding
        other_embedding = [v + 0.01 for v in sample_embedding]
        await vector_search.index(memory2.memory_id, other_embedding, {})

        # Search with user filter
        filter = VectorFilter(user_id=test_user)
        results = await vector_search.search(
            query_embedding=sample_embedding,
            limit=10,
            filter=filter,
        )

        assert len(results) == 1
        assert results[0].id == memory1.memory_id

    @pytest.mark.asyncio
    async def test_search_with_min_salience_filter(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test searching with minimum salience filter."""
        from mind.core.memory.models import Memory, TemporalLevel
        from mind.ports.vectors import VectorFilter
        import random

        # Create memories with varying salience
        for i, salience in enumerate([0.3, 0.5, 0.7, 0.9]):
            memory = Memory(
                memory_id=uuid4(),
                user_id=test_user,
                content=f"Memory with salience {salience}",
                content_type="observation",
                temporal_level=TemporalLevel.SESSION,
                base_salience=salience,
                outcome_adjustment=0.0,
                valid_from=datetime.now(UTC),
            )
            await memory_storage.store(memory)

            # Create slightly different embeddings
            random.seed(42 + i)
            embedding = [random.random() for _ in range(1536)]
            await vector_search.index(memory.memory_id, embedding, {})

        # Search with minimum salience filter
        filter = VectorFilter(user_id=test_user, min_salience=0.6)
        results = await vector_search.search(
            query_embedding=sample_embedding,
            limit=10,
            filter=filter,
        )

        # Should only return memories with salience >= 0.6 (0.7 and 0.9)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_index_batch(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test batch indexing of vectors."""
        from mind.core.memory.models import Memory, TemporalLevel
        import random

        items = []
        for i in range(10):
            memory = Memory(
                memory_id=uuid4(),
                user_id=test_user,
                content=f"Batch memory {i}",
                content_type="observation",
                temporal_level=TemporalLevel.SESSION,
                base_salience=0.5,
                outcome_adjustment=0.0,
                valid_from=datetime.now(UTC),
            )
            await memory_storage.store(memory)

            random.seed(42 + i)
            embedding = [random.random() for _ in range(1536)]
            items.append((memory.memory_id, embedding, {"index": i}))

        # Batch index
        await vector_search.index_batch(items)

        # Verify count
        count = await vector_search.count()
        assert count >= 10

    @pytest.mark.asyncio
    async def test_delete_vector(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test deleting a vector from the index."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Memory to delete",
            content_type="observation",
            temporal_level=TemporalLevel.SESSION,
            base_salience=0.5,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(memory)
        await vector_search.index(memory.memory_id, sample_embedding, {})

        # Verify it's searchable
        results = await vector_search.search(sample_embedding, limit=10)
        memory_ids = [r.id for r in results]
        assert memory.memory_id in memory_ids

        # Delete the vector
        await vector_search.delete(memory.memory_id)

        # Verify embedding is null
        embedding = await vector_search.get_embedding(memory.memory_id)
        assert embedding is None

    @pytest.mark.asyncio
    async def test_search_by_id(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test finding similar vectors by ID."""
        from mind.core.memory.models import Memory, TemporalLevel
        import random

        # Create source memory
        source = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Source memory",
            content_type="preference",
            temporal_level=TemporalLevel.IDENTITY,
            base_salience=0.8,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(source)
        await vector_search.index(source.memory_id, sample_embedding, {})

        # Create similar memory (slightly different embedding)
        similar = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Similar memory",
            content_type="preference",
            temporal_level=TemporalLevel.IDENTITY,
            base_salience=0.7,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(similar)
        similar_embedding = [v + 0.001 for v in sample_embedding]  # Small perturbation
        await vector_search.index(similar.memory_id, similar_embedding, {})

        # Create dissimilar memory
        dissimilar = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Dissimilar memory",
            content_type="observation",
            temporal_level=TemporalLevel.IMMEDIATE,
            base_salience=0.5,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(dissimilar)
        random.seed(999)  # Very different embedding
        dissimilar_embedding = [random.random() for _ in range(1536)]
        await vector_search.index(dissimilar.memory_id, dissimilar_embedding, {})

        # Search by source ID
        results = await vector_search.search_by_id(source.memory_id, limit=5)

        # Should find similar but not source itself
        result_ids = [r.id for r in results]
        assert source.memory_id not in result_ids
        assert similar.memory_id in result_ids

    @pytest.mark.asyncio
    async def test_get_embedding(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test retrieving a stored embedding."""
        from mind.core.memory.models import Memory, TemporalLevel

        memory = Memory(
            memory_id=uuid4(),
            user_id=test_user,
            content="Memory with embedding",
            content_type="observation",
            temporal_level=TemporalLevel.SESSION,
            base_salience=0.5,
            outcome_adjustment=0.0,
            valid_from=datetime.now(UTC),
        )
        await memory_storage.store(memory)
        await vector_search.index(memory.memory_id, sample_embedding, {})

        # Retrieve embedding
        retrieved = await vector_search.get_embedding(memory.memory_id)

        assert retrieved is not None
        assert len(retrieved) == 1536
        # Check some values are close (may have float precision differences)
        assert abs(retrieved[0] - sample_embedding[0]) < 0.001

    @pytest.mark.asyncio
    async def test_count_with_filter(
        self, vector_search, memory_storage, test_user, sample_embedding
    ):
        """Test counting vectors with filter."""
        from mind.core.memory.models import Memory, TemporalLevel
        from mind.ports.vectors import VectorFilter
        import random

        # Create memories
        for i in range(5):
            memory = Memory(
                memory_id=uuid4(),
                user_id=test_user,
                content=f"Memory {i}",
                content_type="observation",
                temporal_level=TemporalLevel.SESSION,
                base_salience=0.6,
                outcome_adjustment=0.0,
                valid_from=datetime.now(UTC),
            )
            await memory_storage.store(memory)
            random.seed(42 + i)
            embedding = [random.random() for _ in range(1536)]
            await vector_search.index(memory.memory_id, embedding, {})

        # Count with user filter
        filter = VectorFilter(user_id=test_user)
        count = await vector_search.count(filter=filter)

        assert count == 5

    @pytest.mark.asyncio
    async def test_health_check(self, vector_search):
        """Test vector search health check."""
        result = await vector_search.health_check()
        assert result is True
