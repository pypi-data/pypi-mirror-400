"""Unit tests for MCP server.

Tests for:
- mind_remember tool
- mind_retrieve tool
- mind_decide tool
- mind_health tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import UUID, uuid4

# Import the MCP tools directly
from mind.mcp import server


class TestMCPServerConfig:
    """Tests for MCP server configuration."""

    def test_default_api_url(self):
        """Should use default API URL."""
        assert "localhost:8080" in server.MIND_API_URL or server.MIND_API_URL == "http://localhost:8080"

    def test_mcp_server_exists(self):
        """Should have FastMCP instance."""
        assert server.mcp is not None
        assert server.mcp.name == "mind"


class TestMindRememberTool:
    """Tests for mind_remember MCP tool."""

    @pytest.fixture
    def mock_memory(self):
        """Create mock memory object."""
        memory = MagicMock()
        memory.memory_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        memory.content = "User prefers dark mode"
        memory.temporal_level = 4
        memory.temporal_level_name = "identity"
        memory.effective_salience = 1.0
        memory.created_at = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        return memory

    @pytest.mark.asyncio
    async def test_remember_basic(self, mock_memory):
        """Should store memory and return dict."""
        mock_client = AsyncMock()
        mock_client.remember = AsyncMock(return_value=mock_memory)

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_remember(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                content="User prefers dark mode",
            )

        assert result["memory_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["content"] == "User prefers dark mode"
        assert result["effective_salience"] == 1.0

    @pytest.mark.asyncio
    async def test_remember_with_temporal_level(self, mock_memory):
        """Should map temporal level int to enum."""
        mock_client = AsyncMock()
        mock_client.remember = AsyncMock(return_value=mock_memory)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_remember(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                content="User prefers dark mode",
                temporal_level=4,  # IDENTITY
            )

        # Verify the call was made with correct temporal level
        call_kwargs = mock_client.remember.call_args[1]
        assert call_kwargs["temporal_level"].value == 4

    @pytest.mark.asyncio
    async def test_remember_with_salience(self, mock_memory):
        """Should pass salience to client."""
        mock_client = AsyncMock()
        mock_client.remember = AsyncMock(return_value=mock_memory)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_remember(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                content="Important fact",
                salience=0.9,
            )

        call_kwargs = mock_client.remember.call_args[1]
        assert call_kwargs["salience"] == 0.9

    @pytest.mark.asyncio
    async def test_remember_returns_serializable_dict(self, mock_memory):
        """Result should be JSON serializable."""
        mock_client = AsyncMock()
        mock_client.remember = AsyncMock(return_value=mock_memory)

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_remember(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                content="Test",
            )

        # All values should be strings or primitives
        assert isinstance(result["memory_id"], str)
        assert isinstance(result["created_at"], str)


class TestMindRetrieveTool:
    """Tests for mind_retrieve MCP tool."""

    @pytest.fixture
    def mock_retrieval_result(self):
        """Create mock retrieval result."""
        memory = MagicMock()
        memory.memory_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        memory.content = "User prefers dark mode"
        memory.content_type = "preference"
        memory.temporal_level = 4
        memory.temporal_level_name = "identity"
        memory.effective_salience = 0.95

        result = MagicMock()
        result.retrieval_id = UUID("770e8400-e29b-41d4-a716-446655440002")
        result.memories = [memory]
        result.scores = {"550e8400-e29b-41d4-a716-446655440000": 0.85}
        result.latency_ms = 12.5
        return result

    @pytest.mark.asyncio
    async def test_retrieve_basic(self, mock_retrieval_result):
        """Should retrieve memories and return dict."""
        mock_client = AsyncMock()
        mock_client.retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_retrieve(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                query="theme preferences",
            )

        assert result["retrieval_id"] == "770e8400-e29b-41d4-a716-446655440002"
        assert len(result["memories"]) == 1
        assert result["latency_ms"] == 12.5

    @pytest.mark.asyncio
    async def test_retrieve_includes_scores(self, mock_retrieval_result):
        """Should include relevance scores."""
        mock_client = AsyncMock()
        mock_client.retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_retrieve(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                query="theme preferences",
            )

        memory = result["memories"][0]
        assert "score" in memory
        assert memory["score"] == 0.85

    @pytest.mark.asyncio
    async def test_retrieve_with_limit(self, mock_retrieval_result):
        """Should pass limit to client."""
        mock_client = AsyncMock()
        mock_client.retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_retrieve(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                query="preferences",
                limit=5,
            )

        call_kwargs = mock_client.retrieve.call_args[1]
        assert call_kwargs["limit"] == 5

    @pytest.mark.asyncio
    async def test_retrieve_with_min_salience(self, mock_retrieval_result):
        """Should pass min_salience to client."""
        mock_client = AsyncMock()
        mock_client.retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_retrieve(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                query="preferences",
                min_salience=0.5,
            )

        call_kwargs = mock_client.retrieve.call_args[1]
        assert call_kwargs["min_salience"] == 0.5


class TestMindDecideTool:
    """Tests for mind_decide MCP tool."""

    @pytest.fixture
    def mock_track_result(self):
        """Create mock track result."""
        result = MagicMock()
        result.trace_id = UUID("880e8400-e29b-41d4-a716-446655440003")
        result.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        return result

    @pytest.fixture
    def mock_outcome_result(self):
        """Create mock outcome result."""
        result = MagicMock()
        result.outcome_quality = 0.9
        result.memories_updated = 1
        result.salience_changes = {"550e8400-e29b-41d4-a716-446655440000": 0.05}
        return result

    @pytest.mark.asyncio
    async def test_decide_basic(self, mock_track_result, mock_outcome_result):
        """Should track and record outcome."""
        mock_client = AsyncMock()
        mock_client.track = AsyncMock(return_value=mock_track_result)
        mock_client.outcome = AsyncMock(return_value=mock_outcome_result)

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_decide(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                memory_ids=["550e8400-e29b-41d4-a716-446655440000"],
                decision_summary="Used dark mode preference",
                outcome_quality=0.9,
            )

        assert result["trace_id"] == "880e8400-e29b-41d4-a716-446655440003"
        assert result["outcome_quality"] == 0.9
        assert result["memories_updated"] == 1

    @pytest.mark.asyncio
    async def test_decide_calls_track_then_outcome(self, mock_track_result, mock_outcome_result):
        """Should call track before outcome."""
        mock_client = AsyncMock()
        mock_client.track = AsyncMock(return_value=mock_track_result)
        mock_client.outcome = AsyncMock(return_value=mock_outcome_result)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_decide(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                memory_ids=["550e8400-e29b-41d4-a716-446655440000"],
                decision_summary="Decision",
                outcome_quality=0.9,
            )

        # Both should be called
        mock_client.track.assert_called_once()
        mock_client.outcome.assert_called_once()

        # Outcome should use trace_id from track
        outcome_kwargs = mock_client.outcome.call_args[1]
        assert outcome_kwargs["trace_id"] == mock_track_result.trace_id

    @pytest.mark.asyncio
    async def test_decide_with_session_id(self, mock_track_result, mock_outcome_result):
        """Should pass session_id to track."""
        mock_client = AsyncMock()
        mock_client.track = AsyncMock(return_value=mock_track_result)
        mock_client.outcome = AsyncMock(return_value=mock_outcome_result)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_decide(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                memory_ids=["550e8400-e29b-41d4-a716-446655440000"],
                decision_summary="Decision",
                outcome_quality=0.9,
                session_id="990e8400-e29b-41d4-a716-446655440004",
            )

        track_kwargs = mock_client.track.call_args[1]
        assert track_kwargs["session_id"] == UUID("990e8400-e29b-41d4-a716-446655440004")

    @pytest.mark.asyncio
    async def test_decide_auto_generates_session_id(self, mock_track_result, mock_outcome_result):
        """Should auto-generate session_id if not provided."""
        mock_client = AsyncMock()
        mock_client.track = AsyncMock(return_value=mock_track_result)
        mock_client.outcome = AsyncMock(return_value=mock_outcome_result)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_decide(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                memory_ids=["550e8400-e29b-41d4-a716-446655440000"],
                decision_summary="Decision",
                outcome_quality=0.9,
            )

        track_kwargs = mock_client.track.call_args[1]
        assert track_kwargs["session_id"] is not None

    @pytest.mark.asyncio
    async def test_decide_with_feedback(self, mock_track_result, mock_outcome_result):
        """Should pass feedback to outcome."""
        mock_client = AsyncMock()
        mock_client.track = AsyncMock(return_value=mock_track_result)
        mock_client.outcome = AsyncMock(return_value=mock_outcome_result)

        with patch.object(server, "get_client", return_value=mock_client):
            await server.mind_decide(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                memory_ids=["550e8400-e29b-41d4-a716-446655440000"],
                decision_summary="Decision",
                outcome_quality=0.9,
                feedback="Great recommendation!",
            )

        outcome_kwargs = mock_client.outcome.call_args[1]
        assert outcome_kwargs["feedback"] == "Great recommendation!"

    @pytest.mark.asyncio
    async def test_decide_returns_salience_changes(self, mock_track_result, mock_outcome_result):
        """Should include salience changes in result."""
        mock_client = AsyncMock()
        mock_client.track = AsyncMock(return_value=mock_track_result)
        mock_client.outcome = AsyncMock(return_value=mock_outcome_result)

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_decide(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                memory_ids=["550e8400-e29b-41d4-a716-446655440000"],
                decision_summary="Decision",
                outcome_quality=0.9,
            )

        assert "salience_changes" in result
        assert result["salience_changes"]["550e8400-e29b-41d4-a716-446655440000"] == 0.05


class TestMindHealthTool:
    """Tests for mind_health MCP tool."""

    @pytest.mark.asyncio
    async def test_health_returns_status(self):
        """Should return health status."""
        mock_client = AsyncMock()
        mock_client.health = AsyncMock(return_value={
            "status": "healthy",
            "version": "5.0.0",
        })

        with patch.object(server, "get_client", return_value=mock_client):
            result = await server.mind_health()

        assert result["status"] == "healthy"
        assert result["version"] == "5.0.0"


class TestGetClient:
    """Tests for lazy client initialization."""

    @pytest.mark.asyncio
    async def test_creates_client_on_first_call(self):
        """Should create client on first call."""
        # Reset global client
        server._client = None

        # MindClient is imported inside get_client, so patch in the sdk module
        with patch("mind.sdk.MindClient") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance

            client = await server.get_client()

            MockClient.assert_called_once()
            assert client is mock_instance

        # Reset for other tests
        server._client = None

    @pytest.mark.asyncio
    async def test_reuses_existing_client(self):
        """Should reuse client on subsequent calls."""
        mock_client = MagicMock()
        server._client = mock_client

        client = await server.get_client()

        assert client is mock_client

        # Reset for other tests
        server._client = None
