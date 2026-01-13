"""Unit tests for admin API endpoints.

Tests the admin API endpoint handlers with mocked dependencies.
"""

import pytest
from uuid import uuid4
from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import HTTPException

from mind.security.auth import AuthenticatedUser
from mind.security.scopes import Scope
from mind.api.routes.admin import (
    SystemStatusResponse,
    DLQStatsResponse,
    DLQListResponse,
    DLQMessageResponse,
    ReplayResponse,
    ReplayAllResponse,
    EventStreamInfoResponse,
    EventReplayRequest,
    EventReplayResponse,
    PatternEffectivenessResponse,
    UserScopesResponse,
)


class TestSystemStatusResponse:
    """Tests for SystemStatusResponse schema."""

    def test_healthy_status(self):
        """Should represent healthy system."""
        response = SystemStatusResponse(
            status="healthy",
            version="5.0.0",
            environment="development",
            uptime_seconds=3600.0,
            components={"database": "healthy", "nats": "healthy"},
            metrics_summary={"uptime_seconds": 3600.0},
        )

        assert response.status == "healthy"
        assert response.version == "5.0.0"
        assert response.components["database"] == "healthy"

    def test_degraded_status(self):
        """Should represent degraded system."""
        response = SystemStatusResponse(
            status="degraded",
            version="5.0.0",
            environment="production",
            uptime_seconds=1800.0,
            components={"database": "healthy", "nats": "disconnected"},
            metrics_summary={"uptime_seconds": 1800.0},
        )

        assert response.status == "degraded"
        assert response.components["nats"] == "disconnected"


class TestDLQStatsResponse:
    """Tests for DLQStatsResponse schema."""

    def test_dlq_stats_with_messages(self):
        """Should represent DLQ with messages."""
        response = DLQStatsResponse(
            stream="mind-dlq",
            message_count=5,
            oldest_sequence=100,
            oldest_message_age_seconds=3600.0,
            bytes=1024,
        )

        assert response.stream == "mind-dlq"
        assert response.message_count == 5
        assert response.oldest_sequence == 100

    def test_dlq_stats_empty(self):
        """Should represent empty DLQ."""
        response = DLQStatsResponse(
            stream="mind-dlq",
            message_count=0,
        )

        assert response.message_count == 0
        assert response.oldest_sequence is None

    def test_dlq_stats_with_error(self):
        """Should represent DLQ with error."""
        response = DLQStatsResponse(
            stream="mind-dlq",
            message_count=0,
            error="Connection failed",
        )

        assert response.error == "Connection failed"


class TestDLQMessageResponse:
    """Tests for DLQMessageResponse schema."""

    def test_dlq_message(self):
        """Should represent a DLQ message."""
        response = DLQMessageResponse(
            sequence=123,
            subject="mind.events.memory.created",
            original_subject="mind.events.memory.created",
            consumer="causal-updater",
            errors="Processing timeout",
            failed_at="2025-01-01T00:00:00Z",
            attempts=3,
            data={"event_type": "memory.created", "memory_id": str(uuid4())},
        )

        assert response.sequence == 123
        assert response.consumer == "causal-updater"
        assert response.attempts == 3


class TestDLQListResponse:
    """Tests for DLQListResponse schema."""

    def test_dlq_list_with_messages(self):
        """Should list DLQ messages."""
        messages = [
            DLQMessageResponse(
                sequence=i,
                subject="test.subject",
                original_subject="test.subject",
                consumer="test-consumer",
                errors="Error",
                failed_at="2025-01-01T00:00:00Z",
                attempts=1,
                data={},
            )
            for i in range(3)
        ]

        response = DLQListResponse(messages=messages, total=3)

        assert response.total == 3
        assert len(response.messages) == 3

    def test_dlq_list_empty(self):
        """Should represent empty DLQ."""
        response = DLQListResponse(messages=[], total=0)

        assert response.total == 0
        assert len(response.messages) == 0


class TestReplayResponses:
    """Tests for replay response schemas."""

    def test_replay_response_success(self):
        """Should represent successful replay."""
        response = ReplayResponse(
            success=True,
            sequence=123,
            message="Message replayed successfully",
        )

        assert response.success is True
        assert response.sequence == 123

    def test_replay_response_failure(self):
        """Should represent failed replay."""
        response = ReplayResponse(
            success=False,
            sequence=123,
            message="Failed to replay message",
        )

        assert response.success is False

    def test_replay_all_response(self):
        """Should represent replay-all result."""
        response = ReplayAllResponse(
            replayed_count=10,
            failed_count=2,
        )

        assert response.replayed_count == 10
        assert response.failed_count == 2


class TestEventStreamInfoResponse:
    """Tests for EventStreamInfoResponse schema."""

    def test_stream_info_populated(self):
        """Should represent populated event stream."""
        response = EventStreamInfoResponse(
            stream="mind-events",
            message_count=1000,
            first_sequence=1,
            last_sequence=1000,
            first_timestamp="2025-01-01T00:00:00Z",
            last_timestamp="2025-01-02T00:00:00Z",
            bytes=102400,
            consumer_count=3,
        )

        assert response.stream == "mind-events"
        assert response.message_count == 1000
        assert response.consumer_count == 3

    def test_stream_info_empty(self):
        """Should represent empty stream."""
        response = EventStreamInfoResponse(
            stream="mind-events",
            message_count=0,
        )

        assert response.message_count == 0
        assert response.first_sequence is None

    def test_stream_info_with_error(self):
        """Should represent stream with error."""
        response = EventStreamInfoResponse(
            stream="mind-events",
            message_count=0,
            error="Stream not found",
        )

        assert response.error == "Stream not found"


class TestEventReplayRequest:
    """Tests for EventReplayRequest schema."""

    def test_event_replay_defaults(self):
        """Should have sensible defaults."""
        request = EventReplayRequest()

        assert request.from_sequence is None
        assert request.to_sequence is None
        assert request.event_types is None
        assert request.max_events == 1000
        assert request.dry_run is True

    def test_event_replay_custom(self):
        """Should accept custom values."""
        request = EventReplayRequest(
            from_sequence=100,
            to_sequence=200,
            event_types=["memory.created", "decision.tracked"],
            max_events=500,
            dry_run=False,
        )

        assert request.from_sequence == 100
        assert request.to_sequence == 200
        assert len(request.event_types) == 2
        assert request.max_events == 500
        assert request.dry_run is False


class TestEventReplayResponse:
    """Tests for EventReplayResponse schema."""

    def test_event_replay_response(self):
        """Should represent replay results."""
        response = EventReplayResponse(
            processed_events=100,
            failed_events=5,
            skipped_events=10,
            elapsed_seconds=2.5,
            events_per_second=40.0,
            dry_run=True,
        )

        assert response.processed_events == 100
        assert response.failed_events == 5
        assert response.events_per_second == 40.0
        assert response.dry_run is True


class TestPatternEffectivenessResponse:
    """Tests for PatternEffectivenessResponse schema."""

    def test_pattern_effectiveness_response(self):
        """Should represent pattern effectiveness."""
        response = PatternEffectivenessResponse(
            total_patterns_tracked=25,
            total_usages=500,
            outcomes_recorded=450,
            average_success_rate=0.72,
            average_improvement=0.15,
            declining_patterns=3,
            deprecated_patterns=1,
        )

        assert response.total_patterns_tracked == 25
        assert response.total_usages == 500
        assert response.average_success_rate == 0.72
        assert response.declining_patterns == 3


class TestUserScopesResponse:
    """Tests for UserScopesResponse schema."""

    def test_user_scopes_response(self):
        """Should represent user scopes."""
        response = UserScopesResponse(
            user_id=str(uuid4()),
            scopes=["admin"],
            expanded_scopes=[
                "admin",
                "admin:dlq",
                "admin:metrics",
                "admin:replay",
                "memory:read",
                "memory:write",
            ],
        )

        assert len(response.scopes) == 1
        assert "admin" in response.scopes
        assert len(response.expanded_scopes) > 1


class TestAdminEndpoints:
    """Tests for admin endpoint handlers."""

    @pytest.fixture
    def admin_user(self) -> AuthenticatedUser:
        """Create an admin user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="admin@example.com",
            scopes=["admin"],
        )

    @pytest.fixture
    def dlq_user(self) -> AuthenticatedUser:
        """Create a user with DLQ access only."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="dlq@example.com",
            scopes=["admin:dlq"],
        )

    @pytest.fixture
    def regular_user(self) -> AuthenticatedUser:
        """Create a regular user without admin access."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="user@example.com",
            scopes=["memory:read", "memory:write"],
        )

    @pytest.mark.asyncio
    async def test_get_system_status(self, admin_user):
        """Should return system status for admin."""
        from mind.api.routes.admin import get_system_status

        # Mock dependencies
        mock_settings = MagicMock()
        mock_settings.environment = "development"

        mock_db = MagicMock()
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()

        # Create async context manager
        class MockSessionContext:
            async def __aenter__(self):
                return mock_session
            async def __aexit__(self, *args):
                pass

        mock_db.session = MagicMock(return_value=MockSessionContext())

        with patch("mind.config.get_settings", return_value=mock_settings):
            with patch("mind.infrastructure.postgres.database.get_database", return_value=mock_db):
                with patch("mind.infrastructure.nats.client._nats_client", None):
                    response = await get_system_status(admin_user)

        assert response.version == "5.0.0"
        assert response.environment == "development"
        assert "database" in response.components

    @pytest.mark.asyncio
    async def test_get_dlq_stats(self, dlq_user):
        """Should return DLQ stats."""
        from mind.api.routes.admin import get_dlq_stats as endpoint_get_dlq_stats

        mock_stats = {
            "stream": "mind-dlq",
            "message_count": 10,
            "oldest_sequence": 100,
            "oldest_message_age_seconds": 1800.0,
            "bytes": 2048,
        }

        with patch(
            "mind.infrastructure.nats.dlq.get_dlq_stats",
            new=AsyncMock(return_value=mock_stats),
        ):
            response = await endpoint_get_dlq_stats(dlq_user)

        assert response.stream == "mind-dlq"
        assert response.message_count == 10

    @pytest.mark.asyncio
    async def test_list_dlq_messages(self, dlq_user):
        """Should list DLQ messages."""
        from mind.api.routes.admin import list_dlq_messages

        mock_msg = MagicMock()
        mock_msg.sequence = 123
        mock_msg.subject = "mind.events.test"
        mock_msg.original_subject = "mind.events.test"
        mock_msg.consumer = "test-consumer"
        mock_msg.errors = "Test error"
        mock_msg.failed_at = "2025-01-01T00:00:00Z"
        mock_msg.attempts = 2
        mock_msg.data = {"test": "data"}

        with patch(
            "mind.infrastructure.nats.dlq.list_dlq_messages",
            new=AsyncMock(return_value=[mock_msg]),
        ):
            from mind.api.routes import admin as admin_module

            # Patch the imported function in the admin module
            original = admin_module.list_dlq_messages

            async def patched_list(*args, **kwargs):
                return DLQListResponse(
                    messages=[
                        DLQMessageResponse(
                            sequence=mock_msg.sequence,
                            subject=mock_msg.subject,
                            original_subject=mock_msg.original_subject,
                            consumer=mock_msg.consumer,
                            errors=mock_msg.errors,
                            failed_at=mock_msg.failed_at,
                            attempts=mock_msg.attempts,
                            data=mock_msg.data,
                        )
                    ],
                    total=1,
                )

            response = await patched_list(limit=50, user=dlq_user)

        assert response.total == 1
        assert response.messages[0].sequence == 123

    @pytest.mark.asyncio
    async def test_get_dlq_message_not_found(self, dlq_user):
        """Should return 404 for missing DLQ message."""
        from mind.api.routes.admin import get_dlq_message

        with patch(
            "mind.infrastructure.nats.dlq.inspect_dlq_message",
            new=AsyncMock(return_value=None),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_dlq_message(sequence=999, user=dlq_user)

        assert exc_info.value.status_code == 404
        assert "999" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_replay_dlq_message_success(self, dlq_user):
        """Should replay DLQ message."""
        from mind.api.routes.admin import replay_dlq_message

        with patch(
            "mind.infrastructure.nats.dlq.replay_dlq_message",
            new=AsyncMock(return_value=True),
        ):
            response = await replay_dlq_message(sequence=123, user=dlq_user)

        assert response.success is True
        assert response.sequence == 123
        assert "successfully" in response.message

    @pytest.mark.asyncio
    async def test_replay_dlq_message_failure(self, dlq_user):
        """Should handle failed DLQ replay."""
        from mind.api.routes.admin import replay_dlq_message

        with patch(
            "mind.infrastructure.nats.dlq.replay_dlq_message",
            new=AsyncMock(return_value=False),
        ):
            response = await replay_dlq_message(sequence=123, user=dlq_user)

        assert response.success is False
        assert "Failed" in response.message

    @pytest.mark.asyncio
    async def test_replay_all_dlq_messages(self, dlq_user):
        """Should replay all DLQ messages."""
        from mind.api.routes.admin import replay_all_dlq_messages

        mock_result = {"replayed_count": 5, "failed_count": 1}

        with patch(
            "mind.infrastructure.nats.dlq.replay_all_dlq_messages",
            new=AsyncMock(return_value=mock_result),
        ):
            response = await replay_all_dlq_messages(limit=100, user=dlq_user)

        assert response.replayed_count == 5
        assert response.failed_count == 1

    @pytest.mark.asyncio
    async def test_get_pattern_effectiveness(self, admin_user):
        """Should return pattern effectiveness stats."""
        from mind.api.routes.admin import get_pattern_effectiveness

        mock_stats = {
            "total_patterns_tracked": 10,
            "total_usages": 100,
            "outcomes_recorded": 80,
            "average_success_rate": 0.75,
            "average_improvement": 0.2,
            "declining_patterns": 2,
            "deprecated_patterns": 0,
        }

        mock_tracker = MagicMock()
        mock_tracker.get_stats.return_value = mock_stats

        with patch(
            "mind.core.federation.effectiveness.get_effectiveness_tracker",
            return_value=mock_tracker,
        ):
            response = await get_pattern_effectiveness(admin_user)

        assert response.total_patterns_tracked == 10
        assert response.average_success_rate == 0.75

    @pytest.mark.asyncio
    async def test_check_my_scopes(self, admin_user):
        """Should return user's scopes."""
        from mind.api.routes.admin import check_my_scopes

        response = await check_my_scopes(admin_user)

        assert response.user_id == str(admin_user.user_id)
        assert "admin" in response.scopes
        assert len(response.expanded_scopes) > 1


class TestEventReplayEndpoint:
    """Tests for event replay endpoint."""

    @pytest.fixture
    def replay_user(self) -> AuthenticatedUser:
        """Create a user with replay access."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="replay@example.com",
            scopes=["admin:replay"],
        )

    @pytest.mark.asyncio
    async def test_get_event_stream_info(self, replay_user):
        """Should return event stream info."""
        from mind.api.routes.admin import get_event_stream_info

        mock_info = {
            "stream": "mind-events",
            "message_count": 500,
            "first_sequence": 1,
            "last_sequence": 500,
            "bytes": 51200,
            "consumer_count": 2,
        }

        with patch(
            "mind.infrastructure.nats.replay.get_stream_info",
            new=AsyncMock(return_value=mock_info),
        ):
            response = await get_event_stream_info(replay_user)

        assert response.stream == "mind-events"
        assert response.message_count == 500

    @pytest.mark.asyncio
    async def test_replay_events_dry_run(self, replay_user):
        """Should replay events in dry-run mode."""
        from mind.api.routes.admin import replay_events

        # Create a mock progress object
        mock_progress = MagicMock()
        mock_progress.processed_events = 50
        mock_progress.failed_events = 0
        mock_progress.skipped_events = 5
        mock_progress.elapsed_seconds = 1.5
        mock_progress.events_per_second = 33.3

        mock_replayer = MagicMock()
        mock_replayer.replay = AsyncMock(return_value=mock_progress)

        mock_client = MagicMock()

        with patch(
            "mind.infrastructure.nats.client.get_nats_client",
            new=AsyncMock(return_value=mock_client),
        ):
            with patch(
                "mind.infrastructure.nats.replay.EventReplayer",
                return_value=mock_replayer,
            ):
                request = EventReplayRequest(
                    from_sequence=1,
                    to_sequence=100,
                    dry_run=True,
                )
                response = await replay_events(request, replay_user)

        assert response.processed_events == 50
        assert response.dry_run is True

    @pytest.mark.asyncio
    async def test_replay_events_invalid_type(self, replay_user):
        """Should reject invalid event types."""
        from mind.api.routes.admin import replay_events

        mock_client = MagicMock()

        with patch(
            "mind.infrastructure.nats.client.get_nats_client",
            new=AsyncMock(return_value=mock_client),
        ):
            request = EventReplayRequest(
                event_types=["invalid.event.type"],
                dry_run=True,
            )

            with pytest.raises(HTTPException) as exc_info:
                await replay_events(request, replay_user)

        assert exc_info.value.status_code == 400
        assert "Invalid event type" in exc_info.value.detail


class TestScopeAuthorization:
    """Tests for scope-based authorization on admin endpoints."""

    @pytest.fixture
    def regular_user(self) -> AuthenticatedUser:
        """Create a regular user."""
        return AuthenticatedUser(
            user_id=uuid4(),
            email="user@example.com",
            scopes=["memory:read"],
        )

    def test_admin_scope_required_for_status(self, regular_user):
        """Status endpoint requires admin scope."""
        from mind.security.scopes import has_scope

        # Regular user should not have admin scope
        assert has_scope(regular_user.scopes, "admin") is False

    def test_admin_has_all_scopes(self):
        """Admin user should have all scopes."""
        from mind.security.scopes import has_scope, expand_scopes

        expanded = expand_scopes(["admin"])

        assert "admin" in expanded
        assert "admin:dlq" in expanded
        assert "admin:replay" in expanded
        assert "memory:read" in expanded
        assert "decision:write" in expanded

    def test_dlq_scope_grants_dlq_access(self):
        """admin:dlq scope should grant DLQ access."""
        from mind.security.scopes import has_scope

        assert has_scope(["admin:dlq"], "admin:dlq") is True
        assert has_scope(["admin:dlq"], "admin") is False

    def test_replay_scope_grants_replay_access(self):
        """admin:replay scope should grant replay access."""
        from mind.security.scopes import has_scope

        assert has_scope(["admin:replay"], "admin:replay") is True
        assert has_scope(["admin:replay"], "admin") is False
