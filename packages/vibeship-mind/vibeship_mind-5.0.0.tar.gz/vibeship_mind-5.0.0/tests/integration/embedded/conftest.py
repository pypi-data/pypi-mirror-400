"""Fixtures for embedded PostgreSQL integration tests.

Uses embedded PostgreSQL for testing without Docker.
Requires: pip install testing.postgresql psycopg2-binary

Note: pgvector extension is not available with embedded PostgreSQL.
These tests focus on non-vector functionality.
"""

import asyncio
import os
from uuid import uuid4

import pytest
import pytest_asyncio


def embedded_pg_available() -> bool:
    """Check if embedded PostgreSQL is available."""
    try:
        import testing.postgresql
        return True
    except ImportError:
        return False


requires_embedded_pg = pytest.mark.skipif(
    not embedded_pg_available(),
    reason="testing.postgresql not installed (pip install testing.postgresql)"
)


# Shared PostgreSQL instance
_postgresql = None
_asyncpg_pool = None


def _start_embedded_pg():
    """Start embedded PostgreSQL instance."""
    global _postgresql
    if _postgresql is None:
        try:
            import testing.postgresql

            _postgresql = testing.postgresql.Postgresql()
        except Exception as e:
            pytest.skip(f"Could not start embedded PostgreSQL: {e}")

    return _postgresql


async def _create_embedded_schema(pool):
    """Create schema for embedded PostgreSQL (without pgvector)."""
    async with pool.acquire() as conn:
        # Enable UUID extension
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

        # Create memories table (without vector column for embedded PG)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                content_type VARCHAR(50),
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

        # Create events table
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
            "CREATE INDEX IF NOT EXISTS ix_traces_user_id ON decision_traces(user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_events_status ON events(status)"
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
def embedded_pg():
    """Get embedded PostgreSQL instance."""
    pg = _start_embedded_pg()
    yield pg
    # Cleanup happens at module end


@pytest_asyncio.fixture(scope="module")
async def asyncpg_pool(embedded_pg):
    """Create asyncpg pool for embedded PostgreSQL."""
    import asyncpg
    from urllib.parse import urlparse

    dsn = embedded_pg.url()
    parsed = urlparse(dsn)

    pool = await asyncpg.create_pool(
        host=parsed.hostname,
        port=parsed.port,
        user=parsed.username or "postgres",
        password=parsed.password or "",
        database=parsed.path.lstrip("/") or "test",
        min_size=2,
        max_size=10,
    )

    await _create_embedded_schema(pool)

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
