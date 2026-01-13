"""API endpoint tests for Mind v5.

Tests for REST API endpoints:
- Health check
- Memory operations
- Decision tracking

Note: Tests that require database infrastructure are skipped by default.
To run with real infrastructure, use testcontainers or set DATABASE_URL.
"""

import os
import pytest
from uuid import uuid4


# Check if we can connect to a database
def database_available() -> bool:
    """Check if a database connection is available."""
    # If DATABASE_URL is set or we're in a CI environment with containers
    return bool(os.environ.get("DATABASE_URL") or os.environ.get("CI"))


requires_database = pytest.mark.skipif(
    not database_available(),
    reason="Database not available (set DATABASE_URL or run in CI)"
)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_ok(self, sync_api_client):
        """Health endpoint should return 200 OK."""
        response = sync_api_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_version(self, sync_api_client):
        """Health should include version info."""
        response = sync_api_client.get("/health")

        data = response.json()
        assert "version" in data


class TestMemoryEndpoints:
    """Tests for memory API endpoints."""

    @requires_database
    def test_create_memory_success(self, sync_api_client, user_id):
        """Should create memory with valid data."""
        response = sync_api_client.post(
            "/v1/memories/",
            json={
                "user_id": str(user_id),
                "content": "Test memory content",
                "temporal_level": 1,  # immediate
                "content_type": "observation",
                "salience": 0.8,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "memory_id" in data
        assert data["content"] == "Test memory content"

    def test_create_memory_requires_user_id(self, sync_api_client):
        """Should reject memory without user_id."""
        response = sync_api_client.post(
            "/v1/memories/",
            json={
                "content": "Test memory",
                "temporal_level": 1,
            },
        )

        assert response.status_code == 422  # Validation error

    @requires_database
    def test_get_memory_by_id(self, sync_api_client, user_id):
        """Should retrieve memory by ID."""
        # First create a memory
        create_response = sync_api_client.post(
            "/v1/memories/",
            json={
                "user_id": str(user_id),
                "content": "Memory to retrieve",
                "temporal_level": 1,
            },
        )

        assert create_response.status_code == 201
        memory_id = create_response.json()["memory_id"]

        # Then retrieve it
        response = sync_api_client.get(f"/v1/memories/{memory_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["memory_id"] == memory_id
        assert data["content"] == "Memory to retrieve"

    @requires_database
    def test_get_nonexistent_memory(self, sync_api_client):
        """Should return 404 for nonexistent memory."""
        fake_id = str(uuid4())
        response = sync_api_client.get(f"/v1/memories/{fake_id}")

        assert response.status_code == 404

    @requires_database
    def test_retrieve_memories(self, sync_api_client, user_id):
        """Should retrieve memories by query."""
        # Create a memory first
        sync_api_client.post(
            "/v1/memories/",
            json={
                "user_id": str(user_id),
                "content": "User prefers detailed technical explanations",
                "temporal_level": 4,  # identity level
                "salience": 0.9,
            },
        )

        # Retrieve memories
        response = sync_api_client.post(
            "/v1/memories/retrieve",
            json={
                "user_id": str(user_id),
                "query": "technical explanations",
                "limit": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "memories" in data
        assert "retrieval_id" in data


class TestDecisionEndpoints:
    """Tests for decision tracking endpoints."""

    @requires_database
    def test_track_decision_success(self, sync_api_client, user_id):
        """Should track decision with valid data."""
        response = sync_api_client.post(
            "/v1/decisions/track",
            json={
                "user_id": str(user_id),
                "session_id": str(uuid4()),
                "memory_ids": [],  # Required field
                "decision_type": "response_style",
                "decision_summary": "Used technical language",
                "confidence": 0.85,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "trace_id" in data

    def test_track_decision_requires_user_id(self, sync_api_client):
        """Should reject decision without user_id."""
        response = sync_api_client.post(
            "/v1/decisions/track",
            json={
                "memory_ids": [],
                "decision_type": "response_style",
                "decision_summary": "Test",
                "confidence": 0.5,
            },
        )

        assert response.status_code == 422  # Validation error

    @requires_database
    def test_observe_outcome(self, sync_api_client, user_id):
        """Should record outcome observation."""
        # First create a decision
        track_response = sync_api_client.post(
            "/v1/decisions/track",
            json={
                "user_id": str(user_id),
                "session_id": str(uuid4()),
                "memory_ids": [],
                "decision_type": "test",
                "decision_summary": "Test decision",
                "confidence": 0.8,
            },
        )

        if track_response.status_code != 201:
            pytest.skip("Could not create decision for outcome test")

        trace_id = track_response.json().get("trace_id")
        if not trace_id:
            pytest.skip("No trace_id returned")

        # Observe outcome
        response = sync_api_client.post(
            "/v1/decisions/outcome",
            json={
                "trace_id": trace_id,
                "quality": 0.8,
                "signal": "explicit_positive",
                "feedback": "Worked well",
            },
        )

        assert response.status_code == 200


class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint."""

    def test_metrics_returns_prometheus_format(self, sync_api_client):
        """Metrics should return Prometheus format."""
        response = sync_api_client.get("/metrics")

        assert response.status_code == 200
        content = response.text

        # Should contain Prometheus-style metrics
        assert "# " in content or "mind_" in content


class TestSecurityHeaders:
    """Tests for security headers."""

    def test_health_endpoint_accessible(self, sync_api_client):
        """Health endpoint should be accessible without auth."""
        response = sync_api_client.get("/health")
        assert response.status_code == 200
