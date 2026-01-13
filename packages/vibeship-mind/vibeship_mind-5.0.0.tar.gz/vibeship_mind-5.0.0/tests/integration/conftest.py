"""Integration test fixtures for Mind v5.

Provides fixtures for integration tests with real databases:
- PostgreSQL with pgvector
- Qdrant vector store
- FalkorDB graph database
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio


# Check if docker is available for testcontainers
def docker_available() -> bool:
    """Check if Docker is available for testcontainers."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


# Skip integration tests if Docker not available
requires_docker = pytest.mark.skipif(
    not docker_available(),
    reason="Docker not available"
)


class PostgresTestContainer:
    """PostgreSQL container for integration tests."""

    def __init__(self):
        self.container = None
        self.connection_url = None

    async def start(self):
        """Start PostgreSQL container."""
        try:
            from testcontainers.postgres import PostgresContainer
            
            self.container = PostgresContainer(
                image="pgvector/pgvector:pg16",
                username="mind_test",
                password="mind_test",
                dbname="mind_test",
            )
            self.container.start()
            self.connection_url = self.container.get_connection_url()
            
            # Wait for container to be ready
            await asyncio.sleep(2)
            
            return self.connection_url
        except ImportError:
            pytest.skip("testcontainers not installed")

    async def stop(self):
        """Stop PostgreSQL container."""
        if self.container:
            self.container.stop()


class QdrantTestContainer:
    """Qdrant container for integration tests."""

    def __init__(self):
        self.container = None
        self.url = None

    async def start(self):
        """Start Qdrant container."""
        try:
            from testcontainers.core.container import DockerContainer
            
            self.container = DockerContainer("qdrant/qdrant:latest")
            self.container.with_exposed_ports(6333)
            self.container.start()
            
            host = self.container.get_container_host_ip()
            port = self.container.get_exposed_port(6333)
            self.url = f"http://{host}:{port}"
            
            await asyncio.sleep(3)
            
            return self.url
        except ImportError:
            pytest.skip("testcontainers not installed")

    async def stop(self):
        """Stop Qdrant container."""
        if self.container:
            self.container.stop()


# Shared container state (module-level for persistence across tests)
_postgres_container = None
_postgres_url = None
_schema_created = False
_cached_engine = None


def _start_postgres_sync():
    """Start postgres container synchronously."""
    global _postgres_container, _postgres_url
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
            _postgres_url = _postgres_container.get_connection_url()
            import time
            time.sleep(2)  # Wait for container
        except ImportError:
            pytest.skip("testcontainers not installed")
    return _postgres_url


def _create_schema_sync(url):
    """Create schema synchronously using psycopg2."""
    global _schema_created
    if _schema_created:
        return

    import psycopg2
    import re

    # Strip driver from URL for psycopg2
    clean_url = re.sub(r'postgresql(\+\w+)?://', 'postgresql://', url)

    conn = psycopg2.connect(clean_url)
    conn.autocommit = True
    cur = conn.cursor()

    # Enable extensions
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            external_id VARCHAR(255) UNIQUE,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create memories table
    cur.execute("""
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS decision_traces (
            trace_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
            session_id UUID,
            context_memory_ids TEXT[],
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

    # Create salience_adjustments table (trace_id is optional for test flexibility)
    cur.execute("""
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
            event_type VARCHAR(50),
            aggregate_id UUID,
            payload JSONB DEFAULT '{}',
            event_metadata JSONB DEFAULT '{}',
            correlation_id UUID,
            causation_id UUID,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS ix_memories_user_id ON memories(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_memories_temporal_level ON memories(temporal_level)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_decision_traces_user_id ON decision_traces(user_id)")

    cur.close()
    conn.close()
    _schema_created = True


@pytest.fixture(scope="module")
def postgres_url():
    """Get PostgreSQL URL, starting container and creating schema if needed."""
    url = _start_postgres_sync()
    _create_schema_sync(url)
    return url


@pytest_asyncio.fixture
async def db_engine(postgres_url):
    """Create database engine for tests."""
    from sqlalchemy.ext.asyncio import create_async_engine
    import re

    # Convert URL for async
    url = re.sub(r'postgresql(\+\w+)?://', 'postgresql+asyncpg://', postgres_url)

    engine = create_async_engine(url, echo=False, pool_pre_ping=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def qdrant_container():
    """Qdrant container fixture."""
    container = QdrantTestContainer()
    url = await container.start()
    yield url
    await container.stop()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Database session fixture with proper cleanup.

    Uses db_engine which ensures schema is created first.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            # Ensure proper cleanup
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def session(db_session):
    """Alias for db_session for backward compatibility."""
    yield db_session


@pytest_asyncio.fixture
async def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest_asyncio.fixture
async def user_id(db_session):
    """Create a test user and return their ID.

    This fixture creates a real user in the database so that
    foreign key constraints on memories and decisions work.
    """
    from sqlalchemy import text

    user_id = uuid4()
    await db_session.execute(
        text("INSERT INTO users (user_id) VALUES (:user_id)"),
        {"user_id": user_id}
    )
    await db_session.commit()
    return user_id


# Mock fixtures for when containers are not available

@pytest.fixture
def mock_postgres_url():
    """Mock PostgreSQL URL for unit tests."""
    return "postgresql://mind:mind@localhost:5432/mind_test"


@pytest.fixture
def mock_qdrant_url():
    """Mock Qdrant URL for unit tests."""
    return "http://localhost:6333"


# API client fixtures

@pytest_asyncio.fixture
async def api_client():
    """Async HTTP client for API tests."""
    from httpx import AsyncClient
    from mind.api.app import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sync_api_client():
    """Sync HTTP client for API tests with proper cleanup."""
    from fastapi.testclient import TestClient
    from mind.api.app import app

    with TestClient(app) as client:
        yield client
    # TestClient context manager handles cleanup automatically
