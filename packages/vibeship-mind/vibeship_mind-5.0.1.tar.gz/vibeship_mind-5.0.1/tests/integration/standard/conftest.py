"""Fixtures for Standard tier integration tests.

These fixtures provide a PostgreSQL database with pgvector for testing
the Standard tier adapters using asyncpg directly.
"""

import asyncio
import os
from uuid import uuid4

import pytest
import pytest_asyncio

# Check if docker is available
def docker_available() -> bool:
    """Check if Docker is available for testcontainers."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


requires_docker = pytest.mark.skipif(
    not docker_available(),
    reason="Docker not available"
)


# Shared container state
_postgres_container = None
_postgres_host = None
_postgres_port = None
_asyncpg_pool = None


def _get_postgres_connection_info():
    """Get PostgreSQL connection info, starting container if needed."""
    global _postgres_container, _postgres_host, _postgres_port

    if _postgres_container is None:
        try:
            from testcontainers.postgres import PostgresContainer

            _postgres_container = PostgresContainer(
                image="pgvector/pgvector:pg16",
                username="mind_test",
                password="mind_test",
                dbname="mind_test",
            )
            _postgres_container.start()

            _postgres_host = _postgres_container.get_container_host_ip()
            _postgres_port = _postgres_container.get_exposed_port(5432)

            import time
            time.sleep(2)  # Wait for container
        except ImportError:
            pytest.skip("testcontainers not installed")

    return _postgres_host, _postgres_port


async def _create_standard_schema(pool):
    """Create the Standard tier schema using asyncpg."""
    async with pool.acquire() as conn:
        # Enable extensions
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                external_id VARCHAR(255) UNIQUE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create memories table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                content_type VARCHAR(50),
                embedding vector(1536),
                temporal_level INTEGER,
                valid_from TIMESTAMPTZ,
                valid_until TIMESTAMPTZ,
                base_salience FLOAT DEFAULT 1.0,
                outcome_adjustment FLOAT DEFAULT 0.0,
                retrieval_count INTEGER DEFAULT 0,
                decision_count INTEGER DEFAULT 0,
                positive_outcomes INTEGER DEFAULT 0,
                negative_outcomes INTEGER DEFAULT 0,
                promoted_from_level INTEGER,
                promotion_timestamp TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create decision_traces table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS decision_traces (
                trace_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                session_id UUID,
                context_memory_ids UUID[],
                memory_scores JSONB DEFAULT '{}',
                decision_type VARCHAR(100),
                decision_summary TEXT,
                confidence FLOAT,
                alternatives_count INTEGER DEFAULT 0,
                outcome_observed BOOLEAN DEFAULT FALSE,
                outcome_quality FLOAT,
                outcome_timestamp TIMESTAMPTZ,
                outcome_signal VARCHAR(100),
                memory_attribution JSONB,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create salience_adjustments table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS salience_adjustments (
                adjustment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                memory_id UUID REFERENCES memories(memory_id) ON DELETE CASCADE,
                trace_id UUID,
                previous_adjustment FLOAT,
                new_adjustment FLOAT,
                delta FLOAT,
                reason VARCHAR(100),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create events table for Standard tier
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                event_type VARCHAR(100) NOT NULL,
                payload JSONB DEFAULT '{}',
                user_id VARCHAR(255),
                status VARCHAR(20) DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMPTZ
            )
        """)

        # Create causal graph tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS causal_nodes (
                node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                node_type VARCHAR(50) NOT NULL,
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                properties JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS causal_edges (
                source_id UUID NOT NULL REFERENCES causal_nodes(node_id) ON DELETE CASCADE,
                target_id UUID NOT NULL REFERENCES causal_nodes(node_id) ON DELETE CASCADE,
                relationship_type VARCHAR(50) NOT NULL,
                strength FLOAT DEFAULT 0.5,
                confidence FLOAT DEFAULT 0.5,
                evidence_count INTEGER DEFAULT 1,
                properties JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id)
            )
        """)

        # Create indexes
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_memories_user_id ON memories(user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_memories_embedding ON memories "
            "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_traces_user_id ON decision_traces(user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_events_status ON events(status)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_causal_nodes_user ON causal_nodes(user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_causal_edges_source ON causal_edges(source_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_causal_edges_target ON causal_edges(target_id)"
        )

        # Create NOTIFY trigger for events
        await conn.execute("""
            CREATE OR REPLACE FUNCTION notify_event_insert()
            RETURNS TRIGGER AS $$
            BEGIN
                PERFORM pg_notify('mind_events',
                    json_build_object(
                        'event_id', NEW.event_id,
                        'event_type', NEW.event_type
                    )::text
                );
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        await conn.execute("""
            DROP TRIGGER IF EXISTS event_insert_notify ON events
        """)

        await conn.execute("""
            CREATE TRIGGER event_insert_notify
            AFTER INSERT ON events
            FOR EACH ROW EXECUTE FUNCTION notify_event_insert()
        """)


@pytest.fixture(scope="module")
def postgres_connection_info():
    """Get PostgreSQL connection info."""
    return _get_postgres_connection_info()


@pytest_asyncio.fixture(scope="module")
async def asyncpg_pool(postgres_connection_info):
    """Create asyncpg pool with Standard tier schema."""
    import asyncpg

    host, port = postgres_connection_info

    pool = await asyncpg.create_pool(
        host=host,
        port=port,
        user="mind_test",
        password="mind_test",
        database="mind_test",
        min_size=2,
        max_size=10,
    )

    await _create_standard_schema(pool)

    yield pool

    await pool.close()


@pytest_asyncio.fixture
async def clean_db(asyncpg_pool):
    """Clean database tables before each test."""
    async with asyncpg_pool.acquire() as conn:
        # Delete in order to respect foreign keys
        await conn.execute("DELETE FROM salience_adjustments")
        await conn.execute("DELETE FROM causal_edges")
        await conn.execute("DELETE FROM causal_nodes")
        await conn.execute("DELETE FROM decision_traces")
        await conn.execute("DELETE FROM memories")
        await conn.execute("DELETE FROM events")
        await conn.execute("DELETE FROM users")

    yield asyncpg_pool


@pytest_asyncio.fixture
async def test_user(clean_db):
    """Create a test user and return their ID."""
    user_id = uuid4()
    async with clean_db.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id) VALUES ($1)",
            user_id
        )
    return user_id


@pytest.fixture
def sample_embedding():
    """Generate a sample embedding vector."""
    import random
    random.seed(42)
    return [random.random() for _ in range(1536)]
