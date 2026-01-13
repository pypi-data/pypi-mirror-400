"""Unit tests for SDK client.

Tests for:
- MindClient initialization and lifecycle
- MindError exception
- All async methods with mocked HTTP responses
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mind.sdk.client import MindClient, MindError
from mind.sdk.models import TemporalLevel


class TestMindError:
    """Tests for MindError exception."""

    def test_basic_error(self):
        """Should create error with message."""
        error = MindError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code == 0
        assert error.details == {}

    def test_error_with_status_code(self):
        """Should include status code."""
        error = MindError("Not found", status_code=404)
        assert error.status_code == 404

    def test_error_with_details(self):
        """Should include details dict."""
        error = MindError("Validation failed", details={"field": "content"})
        assert error.details == {"field": "content"}


class TestMindClientInit:
    """Tests for MindClient initialization."""

    def test_default_init(self):
        """Should initialize with defaults."""
        client = MindClient()
        assert client.base_url == "http://localhost:8080"
        assert client.timeout == 30.0
        assert client.api_key is None

    def test_custom_base_url(self):
        """Should accept custom base URL."""
        client = MindClient(base_url="https://api.mind.example.com")
        assert client.base_url == "https://api.mind.example.com"

    def test_strips_trailing_slash(self):
        """Should strip trailing slash from base URL."""
        client = MindClient(base_url="http://localhost:8080/")
        assert client.base_url == "http://localhost:8080"

    def test_custom_timeout(self):
        """Should accept custom timeout."""
        client = MindClient(timeout=60.0)
        assert client.timeout == 60.0

    def test_api_key(self):
        """Should accept API key."""
        client = MindClient(api_key="secret-key")
        assert client.api_key == "secret-key"


class TestMindClientLifecycle:
    """Tests for client lifecycle management."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Should work as async context manager."""
        async with MindClient() as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Should close HTTP client."""
        client = MindClient()
        # Create internal client
        await client._get_client()
        assert client._client is not None

        await client.close()
        assert client._client is None


class TestMindClientHealth:
    """Tests for health check."""

    @pytest.mark.asyncio
    async def test_health_returns_status(self):
        """Should return health status."""
        client = MindClient()

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "healthy", "version": "5.0.0"}

            result = await client.health()

            assert result["status"] == "healthy"
            assert result["version"] == "5.0.0"
            mock_request.assert_called_once_with("GET", "/health")


class TestMindClientRemember:
    """Tests for remember method."""

    @pytest.fixture
    def sample_memory_response(self) -> dict:
        """Sample memory response from API."""
        return {
            "memory_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "content": "User prefers dark mode",
            "content_type": "preference",
            "temporal_level": 4,
            "temporal_level_name": "identity",
            "effective_salience": 1.0,
            "retrieval_count": 0,
            "decision_count": 0,
            "positive_outcomes": 0,
            "negative_outcomes": 0,
            "valid_from": "2024-01-01T00:00:00+00:00",
            "valid_until": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }

    @pytest.mark.asyncio
    async def test_remember_basic(self, sample_memory_response):
        """Should create memory with basic params."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_memory_response

            memory = await client.remember(
                user_id=user_id,
                content="User prefers dark mode",
            )

            assert memory.content == "User prefers dark mode"
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0] == ("POST", "/v1/memories/")

    @pytest.mark.asyncio
    async def test_remember_with_temporal_level(self, sample_memory_response):
        """Should pass temporal level to API."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_memory_response

            await client.remember(
                user_id=user_id,
                content="User prefers dark mode",
                temporal_level=TemporalLevel.IDENTITY,
            )

            call_kwargs = mock_request.call_args[1]
            assert call_kwargs["json"]["temporal_level"] == 4

    @pytest.mark.asyncio
    async def test_remember_with_salience(self, sample_memory_response):
        """Should pass salience to API."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_memory_response

            await client.remember(
                user_id=user_id,
                content="Important fact",
                salience=0.9,
            )

            call_kwargs = mock_request.call_args[1]
            assert call_kwargs["json"]["salience"] == 0.9


class TestMindClientRetrieve:
    """Tests for retrieve method."""

    @pytest.fixture
    def sample_retrieval_response(self) -> dict:
        """Sample retrieval response from API."""
        return {
            "retrieval_id": "770e8400-e29b-41d4-a716-446655440002",
            "memories": [
                {
                    "memory_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "660e8400-e29b-41d4-a716-446655440001",
                    "content": "User prefers dark mode",
                    "content_type": "preference",
                    "temporal_level": 4,
                    "temporal_level_name": "identity",
                    "effective_salience": 0.95,
                    "retrieval_count": 5,
                    "decision_count": 3,
                    "positive_outcomes": 2,
                    "negative_outcomes": 1,
                    "valid_from": "2024-01-01T00:00:00+00:00",
                    "valid_until": None,
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
            "scores": {"550e8400-e29b-41d4-a716-446655440000": 0.85},
            "latency_ms": 12.5,
        }

    @pytest.mark.asyncio
    async def test_retrieve_basic(self, sample_retrieval_response):
        """Should retrieve memories for query."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_retrieval_response

            result = await client.retrieve(
                user_id=user_id,
                query="theme preferences",
            )

            assert len(result.memories) == 1
            assert result.latency_ms == 12.5
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_with_limit(self, sample_retrieval_response):
        """Should pass limit to API."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_retrieval_response

            await client.retrieve(
                user_id=user_id,
                query="preferences",
                limit=5,
            )

            call_kwargs = mock_request.call_args[1]
            assert call_kwargs["json"]["limit"] == 5

    @pytest.mark.asyncio
    async def test_retrieve_with_temporal_levels(self, sample_retrieval_response):
        """Should pass temporal level filters."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_retrieval_response

            await client.retrieve(
                user_id=user_id,
                query="preferences",
                temporal_levels=[TemporalLevel.IDENTITY, TemporalLevel.SEASONAL],
            )

            call_kwargs = mock_request.call_args[1]
            assert call_kwargs["json"]["temporal_levels"] == [4, 3]


class TestMindClientTrack:
    """Tests for track method."""

    @pytest.fixture
    def sample_track_response(self) -> dict:
        """Sample track response from API."""
        return {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "created_at": "2024-01-01T12:00:00+00:00",
        }

    @pytest.mark.asyncio
    async def test_track_basic(self, sample_track_response):
        """Should track decision."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")
        session_id = UUID("990e8400-e29b-41d4-a716-446655440004")
        memory_ids = [UUID("550e8400-e29b-41d4-a716-446655440000")]

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_track_response

            result = await client.track(
                user_id=user_id,
                session_id=session_id,
                memory_ids=memory_ids,
                decision_type="recommendation",
                decision_summary="Recommended dark mode",
                confidence=0.9,
            )

            assert result.trace_id == UUID("880e8400-e29b-41d4-a716-446655440003")
            mock_request.assert_called_once()


class TestMindClientOutcome:
    """Tests for outcome method."""

    @pytest.fixture
    def sample_outcome_response(self) -> dict:
        """Sample outcome response from API."""
        return {
            "trace_id": "880e8400-e29b-41d4-a716-446655440003",
            "outcome_quality": 0.9,
            "memories_updated": 1,
            "salience_changes": {"550e8400-e29b-41d4-a716-446655440000": 0.05},
        }

    @pytest.mark.asyncio
    async def test_outcome_basic(self, sample_outcome_response):
        """Should record outcome."""
        client = MindClient()
        trace_id = UUID("880e8400-e29b-41d4-a716-446655440003")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_outcome_response

            result = await client.outcome(
                trace_id=trace_id,
                quality=0.9,
                signal="user_accepted",
            )

            assert result.outcome_quality == 0.9
            assert result.memories_updated == 1

    @pytest.mark.asyncio
    async def test_outcome_with_feedback(self, sample_outcome_response):
        """Should pass feedback to API."""
        client = MindClient()
        trace_id = UUID("880e8400-e29b-41d4-a716-446655440003")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_outcome_response

            await client.outcome(
                trace_id=trace_id,
                quality=0.9,
                signal="explicit_feedback",
                feedback="Great recommendation!",
            )

            call_kwargs = mock_request.call_args[1]
            assert call_kwargs["json"]["feedback"] == "Great recommendation!"


class TestMindClientDecisionContext:
    """Tests for decision context creation."""

    def test_decision_creates_context(self):
        """Should create DecisionContext."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        from mind.sdk.context import DecisionContext

        ctx = client.decision(user_id=user_id)

        assert isinstance(ctx, DecisionContext)
        assert ctx.user_id == user_id

    def test_decision_with_session_id(self):
        """Should pass session ID to context."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")
        session_id = UUID("990e8400-e29b-41d4-a716-446655440004")

        ctx = client.decision(user_id=user_id, session_id=session_id)

        assert ctx.session_id == session_id

    def test_decision_auto_generates_session_id(self):
        """Should auto-generate session ID if not provided."""
        client = MindClient()
        user_id = UUID("660e8400-e29b-41d4-a716-446655440001")

        ctx = client.decision(user_id=user_id)

        assert ctx.session_id is not None


class TestMindClientErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_raises_mind_error_on_4xx(self):
        """Should raise MindError on 4xx response."""
        client = MindClient()

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Memory not found"}

        with patch.object(client, "_get_client", new_callable=AsyncMock) as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            with pytest.raises(MindError) as exc_info:
                await client._request("GET", "/v1/memories/123")

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_handles_non_json_error_response(self):
        """Should handle non-JSON error responses."""
        client = MindClient()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.text = "Internal Server Error"

        with patch.object(client, "_get_client", new_callable=AsyncMock) as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            with pytest.raises(MindError) as exc_info:
                await client._request("GET", "/health")

            assert exc_info.value.status_code == 500
