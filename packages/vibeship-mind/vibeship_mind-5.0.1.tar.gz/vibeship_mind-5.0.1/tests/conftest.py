"""Pytest configuration and fixtures for Mind v5.

Provides shared fixtures for:
- Test data generation
- Database connections (mock and real)
- API client setup
- Authentication helpers
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import AsyncGenerator, Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Test data factories


@pytest.fixture
def user_id() -> UUID:
    """Generate a test user ID."""
    return uuid4()


@pytest.fixture
def another_user_id() -> UUID:
    """Generate another test user ID for multi-user tests."""
    return uuid4()


@pytest.fixture
def memory_id() -> UUID:
    """Generate a test memory ID."""
    return uuid4()


@pytest.fixture
def trace_id() -> UUID:
    """Generate a test decision trace ID."""
    return uuid4()


@pytest.fixture
def sample_content() -> str:
    """Sample memory content."""
    return "User prefers detailed technical explanations with code examples."


@pytest.fixture
def sample_query() -> str:
    """Sample decision query."""
    return "What approach should I use for implementing authentication?"


# Memory fixtures

@pytest.fixture
def memory_data(user_id: UUID, memory_id: UUID, sample_content: str) -> dict:
    """Complete memory data for testing."""
    return {
        "memory_id": str(memory_id),
        "user_id": str(user_id),
        "content": sample_content,
        "content_type": "preference",
        "temporal_level": "identity",
        "base_salience": 0.8,
        "outcome_adjustment": 0.05,
        "valid_from": datetime.now(UTC).isoformat(),
        "valid_until": None,
        "metadata": {"source": "test"},
    }


@pytest.fixture
def sample_memory_data(user_id: UUID, memory_id: UUID, sample_content: str) -> dict:
    """Memory data for domain model instantiation."""
    from mind.core.memory.models import TemporalLevel
    return {
        "memory_id": memory_id,
        "user_id": user_id,
        "content": sample_content,
        "content_type": "preference",
        "temporal_level": TemporalLevel.IDENTITY,
        "base_salience": 0.8,
        "outcome_adjustment": 0.0,  # Start at 0 for clean test state
        "valid_from": datetime.now(UTC),
        "valid_until": None,
    }


@pytest.fixture
def memory_list(user_id: UUID) -> list[dict]:
    """List of memories with varying salience."""
    now = datetime.now(UTC)
    return [
        {
            "memory_id": str(uuid4()),
            "user_id": str(user_id),
            "content": "High salience memory",
            "temporal_level": "identity",
            "base_salience": 0.9,
            "outcome_adjustment": 0.1,
            "valid_from": now.isoformat(),
        },
        {
            "memory_id": str(uuid4()),
            "user_id": str(user_id),
            "content": "Medium salience memory",
            "temporal_level": "seasonal",
            "base_salience": 0.5,
            "outcome_adjustment": 0.0,
            "valid_from": now.isoformat(),
        },
        {
            "memory_id": str(uuid4()),
            "user_id": str(user_id),
            "content": "Low salience memory",
            "temporal_level": "immediate",
            "base_salience": 0.2,
            "outcome_adjustment": -0.1,
            "valid_from": now.isoformat(),
        },
    ]


# Decision fixtures

@pytest.fixture
def sample_trace_data(user_id: UUID, trace_id: UUID) -> dict:
    """Sample trace data for DecisionTrace model instantiation."""
    return {
        "trace_id": trace_id,
        "user_id": user_id,
        "session_id": uuid4(),
        "memory_ids": [],
        "memory_scores": {},
        "decision_type": "recommendation",
        "decision_summary": "Test decision summary",
        "confidence": 0.8,
        "alternatives_count": 2,
        "created_at": datetime.now(UTC),
    }


@pytest.fixture
def decision_data(user_id: UUID, trace_id: UUID, sample_query: str) -> dict:
    """Complete decision data for testing."""
    return {
        "trace_id": str(trace_id),
        "user_id": str(user_id),
        "query": sample_query,
        "context_used": [],
        "decision_made": None,
        "confidence": None,
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def outcome_data(trace_id: UUID) -> dict:
    """Outcome data for testing."""
    return {
        "outcome_id": str(uuid4()),
        "trace_id": str(trace_id),
        "quality": "positive",
        "quality_score": 0.8,
        "feedback": "The recommendation was helpful",
        "observed_at": datetime.now(UTC).isoformat(),
    }


# Security fixtures

@pytest.fixture
def jwt_secret() -> str:
    """JWT secret for testing."""
    return "test-secret-key-for-jwt-signing-minimum-32-chars"


@pytest.fixture
def api_key_plaintext() -> str:
    """Plaintext API key for testing."""
    return "mind_test123456789012345678901234"


@pytest.fixture
def valid_token(jwt_secret: str, user_id: UUID) -> str:
    """Generate a valid JWT token for testing."""
    import jwt
    from datetime import timedelta

    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "email": "test@example.com",
        "scopes": ["read", "write"],
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=1)).timestamp(),
        "type": "access",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def expired_token(jwt_secret: str, user_id: UUID) -> str:
    """Generate an expired JWT token for testing."""
    import jwt

    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": (now - timedelta(hours=2)).timestamp(),
        "exp": (now - timedelta(hours=1)).timestamp(),
        "type": "access",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def auth_headers(valid_token: str) -> dict:
    """Authorization headers with valid token."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def api_key_headers(api_key_plaintext: str) -> dict:
    """Headers with API key."""
    return {"X-API-Key": api_key_plaintext}


# Mock fixtures

@pytest.fixture
def mock_embedding() -> list[float]:
    """Mock embedding vector (1536 dimensions)."""
    import random
    random.seed(42)
    return [random.random() for _ in range(1536)]


@pytest.fixture
def mock_embeddings(mock_embedding: list[float]) -> list[list[float]]:
    """Multiple mock embeddings."""
    import random
    embeddings = [mock_embedding]
    for i in range(4):
        random.seed(42 + i)
        embeddings.append([random.random() for _ in range(1536)])
    return embeddings


# Event fixtures

@pytest.fixture
def event_data(user_id: UUID) -> dict:
    """Event data for testing."""
    return {
        "event_id": str(uuid4()),
        "event_type": "MemoryCreated",
        "aggregate_type": "Memory",
        "aggregate_id": str(uuid4()),
        "user_id": str(user_id),
        "data": {"content": "Test memory content"},
        "metadata": {"source": "test"},
        "version": 1,
        "occurred_at": datetime.now(UTC).isoformat(),
    }


# Helper classes for testing

class MockDatabase:
    """Mock database for unit tests."""

    def __init__(self):
        self.memories: dict[UUID, dict] = {}
        self.decisions: dict[UUID, dict] = {}
        self.events: list[dict] = []

    async def save_memory(self, memory: dict) -> dict:
        memory_id = UUID(memory["memory_id"])
        self.memories[memory_id] = memory
        return memory

    async def get_memory(self, memory_id: UUID) -> dict | None:
        return self.memories.get(memory_id)

    async def save_decision(self, decision: dict) -> dict:
        trace_id = UUID(decision["trace_id"])
        self.decisions[trace_id] = decision
        return decision

    async def get_decision(self, trace_id: UUID) -> dict | None:
        return self.decisions.get(trace_id)

    async def publish_event(self, event: dict) -> None:
        self.events.append(event)


@pytest.fixture
def mock_db() -> MockDatabase:
    """Provide a mock database for unit tests."""
    return MockDatabase()


class MockEmbeddingService:
    """Mock embedding service for tests."""

    def __init__(self, mock_embedding: list[float]):
        self._embedding = mock_embedding
        self.call_count = 0

    async def embed(self, text: str) -> list[float]:
        self.call_count += 1
        return self._embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self.call_count += len(texts)
        return [self._embedding for _ in texts]


@pytest.fixture
def mock_embedding_service(mock_embedding: list[float]) -> MockEmbeddingService:
    """Provide a mock embedding service."""
    return MockEmbeddingService(mock_embedding)


# Integration test markers

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers",
        "temporal: marks tests that require Temporal workflow environment (may conflict with numpy in sandbox)"
    )
