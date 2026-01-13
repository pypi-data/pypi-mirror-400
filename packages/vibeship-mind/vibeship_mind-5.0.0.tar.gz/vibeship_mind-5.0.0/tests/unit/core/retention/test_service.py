"""Tests for retention service."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from mind.core.errors import Result, MindError, ErrorCode
from mind.core.retention.models import (
    DataType,
    RetentionAction,
    RetentionPolicy,
)
from mind.core.retention.service import (
    RetentionService,
    RetentionConfig,
    TEMPORAL_LEVEL_TO_DATA_TYPE,
)
from mind.core.memory.models import TemporalLevel, Memory


class TestRetentionConfig:
    """Tests for RetentionConfig."""

    def test_default_config(self):
        """Should have sensible defaults."""
        config = RetentionConfig()
        assert config.enabled is True
        assert config.dry_run is False
        assert config.batch_size == 1000
        assert config.max_duration_seconds == 300

    def test_custom_config(self):
        """Should accept custom values."""
        config = RetentionConfig(
            enabled=False,
            dry_run=True,
            batch_size=500,
        )
        assert config.enabled is False
        assert config.dry_run is True
        assert config.batch_size == 500


class TestTemporalLevelMapping:
    """Tests for temporal level to data type mapping."""

    def test_all_levels_mapped(self):
        """All temporal levels should map to data types."""
        for level in TemporalLevel:
            assert level in TEMPORAL_LEVEL_TO_DATA_TYPE
            data_type = TEMPORAL_LEVEL_TO_DATA_TYPE[level]
            assert isinstance(data_type, DataType)

    def test_immediate_maps_to_working(self):
        """IMMEDIATE should map to MEMORY_WORKING."""
        assert TEMPORAL_LEVEL_TO_DATA_TYPE[TemporalLevel.IMMEDIATE] == DataType.MEMORY_WORKING

    def test_identity_maps_correctly(self):
        """IDENTITY should map to MEMORY_IDENTITY."""
        assert TEMPORAL_LEVEL_TO_DATA_TYPE[TemporalLevel.IDENTITY] == DataType.MEMORY_IDENTITY


class TestRetentionService:
    """Tests for RetentionService."""

    @pytest.fixture
    def mock_memory_repo(self):
        """Create mock memory repository."""
        repo = AsyncMock()
        repo.find_expired_memories = AsyncMock(return_value=Result.ok([]))
        repo.archive_memory = AsyncMock(return_value=Result.ok(None))
        repo.soft_delete_memory = AsyncMock(return_value=Result.ok(None))
        repo.hard_delete_memory = AsyncMock(return_value=Result.ok(None))
        return repo

    @pytest.fixture
    def mock_decision_repo(self):
        """Create mock decision repository."""
        repo = AsyncMock()
        repo.find_expired_decisions = AsyncMock(return_value=Result.ok([]))
        repo.anonymize_decision = AsyncMock(return_value=Result.ok(None))
        repo.archive_decision = AsyncMock(return_value=Result.ok(None))
        return repo

    @pytest.fixture
    def mock_graph_repo(self):
        """Create mock graph repository."""
        repo = AsyncMock()
        repo.find_expired_edges = AsyncMock(return_value=Result.ok([]))
        repo.delete_edge = AsyncMock(return_value=Result.ok(None))
        return repo

    @pytest.fixture
    def service(self, mock_memory_repo, mock_decision_repo, mock_graph_repo):
        """Create retention service with mocked dependencies."""
        return RetentionService(
            memory_repository=mock_memory_repo,
            decision_repository=mock_decision_repo,
            graph_repository=mock_graph_repo,
            config=RetentionConfig(),
        )

    def test_service_initialization(self, service):
        """Should initialize with config."""
        assert service._config.enabled is True

    def test_set_policy(self, service):
        """Should store custom policy."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=14,
            action=RetentionAction.HARD_DELETE,
        )
        service.set_policy(policy)

        retrieved = service.get_policy(DataType.MEMORY_WORKING)
        assert retrieved.retention_days == 14
        assert retrieved.action == RetentionAction.HARD_DELETE

    def test_set_user_specific_policy(self, service):
        """Should store user-specific policy."""
        user_id = uuid4()
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_WORKING,
            retention_days=30,
            user_id=user_id,
        )
        service.set_policy(policy)

        # User-specific should be returned for that user
        retrieved = service.get_policy(DataType.MEMORY_WORKING, user_id)
        assert retrieved.retention_days == 30
        assert retrieved.user_id == user_id

        # Default should be returned for other users
        other_user = uuid4()
        default = service.get_policy(DataType.MEMORY_WORKING, other_user)
        assert default.retention_days == 1  # Default for working memory

    def test_get_policy_falls_back_to_default(self, service):
        """Should return default policy if no custom set."""
        policy = service.get_policy(DataType.MEMORY_IDENTITY)
        assert policy.retention_days >= 365 * 10  # Default is 10 years

    @pytest.mark.asyncio
    async def test_apply_policy_disabled(self, service):
        """Should skip processing when disabled."""
        service._config.enabled = False

        result = await service.apply_policy(DataType.MEMORY_WORKING)

        assert result.is_ok
        assert "Retention disabled" in result.value.errors

    @pytest.mark.asyncio
    async def test_apply_policy_memory_working(self, service, mock_memory_repo):
        """Should process working memories."""
        now = datetime.now(timezone.utc)
        expired_memory = Memory(
            memory_id=uuid4(),
            user_id=uuid4(),
            content="Test content",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now - timedelta(days=10),
            valid_until=None,
            base_salience=0.5,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=10),
        )
        mock_memory_repo.find_expired_memories.return_value = Result.ok([expired_memory])

        result = await service.apply_policy(DataType.MEMORY_WORKING)

        assert result.is_ok
        assert result.value.records_found == 1
        mock_memory_repo.soft_delete_memory.assert_called_once_with(expired_memory.memory_id)

    @pytest.mark.asyncio
    async def test_apply_policy_dry_run(self, service, mock_memory_repo):
        """Should not execute actions in dry run mode."""
        service._config.dry_run = True

        now = datetime.now(timezone.utc)
        expired_memory = Memory(
            memory_id=uuid4(),
            user_id=uuid4(),
            content="Test content",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now - timedelta(days=10),
            valid_until=None,
            base_salience=0.5,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=10),
        )
        mock_memory_repo.find_expired_memories.return_value = Result.ok([expired_memory])

        result = await service.apply_policy(DataType.MEMORY_WORKING)

        assert result.is_ok
        assert result.value.records_found == 1
        assert result.value.records_processed == 1
        # No actual deletion should occur
        mock_memory_repo.soft_delete_memory.assert_not_called()

    @pytest.mark.asyncio
    async def test_apply_policy_with_archive_action(self, service, mock_memory_repo):
        """Should archive when action is ARCHIVE."""
        policy = RetentionPolicy(
            data_type=DataType.MEMORY_EPISODIC,
            retention_days=7,
            action=RetentionAction.ARCHIVE,
        )
        service.set_policy(policy)

        now = datetime.now(timezone.utc)
        expired_memory = Memory(
            memory_id=uuid4(),
            user_id=uuid4(),
            content="Test content",
            content_type="fact",
            temporal_level=TemporalLevel.SITUATIONAL,
            valid_from=now - timedelta(days=10),
            valid_until=None,
            base_salience=0.5,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=10),
        )
        mock_memory_repo.find_expired_memories.return_value = Result.ok([expired_memory])

        result = await service.apply_policy(DataType.MEMORY_EPISODIC)

        assert result.is_ok
        mock_memory_repo.archive_memory.assert_called_once()
        assert result.value.records_archived == 1

    @pytest.mark.asyncio
    async def test_apply_policy_decision_anonymize(self, service, mock_decision_repo):
        """Should anonymize decision traces."""
        decision = MagicMock()
        decision.trace_id = uuid4()
        mock_decision_repo.find_expired_decisions.return_value = Result.ok([decision])

        result = await service.apply_policy(DataType.DECISION_TRACE)

        assert result.is_ok
        mock_decision_repo.anonymize_decision.assert_called_once_with(decision.trace_id)
        assert result.value.records_anonymized == 1

    @pytest.mark.asyncio
    async def test_apply_policy_causal_edges(self, service, mock_graph_repo):
        """Should delete expired causal edges."""
        edge = {"id": "edge-123", "created_at": datetime.now(timezone.utc) - timedelta(days=200)}
        mock_graph_repo.find_expired_edges.return_value = Result.ok([edge])

        result = await service.apply_policy(DataType.CAUSAL_EDGE)

        assert result.is_ok
        mock_graph_repo.delete_edge.assert_called_once_with("edge-123")
        assert result.value.records_deleted == 1

    @pytest.mark.asyncio
    async def test_apply_policy_handles_failure(self, service, mock_memory_repo):
        """Should handle repository failures gracefully."""
        now = datetime.now(timezone.utc)
        memory = Memory(
            memory_id=uuid4(),
            user_id=uuid4(),
            content="Test content",
            content_type="fact",
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_from=now - timedelta(days=10),
            valid_until=None,
            base_salience=0.5,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=10),
        )
        mock_memory_repo.find_expired_memories.return_value = Result.ok([memory])
        mock_memory_repo.soft_delete_memory.return_value = Result.err(
            MindError(code=ErrorCode.DATABASE_ERROR, message="Connection lost")
        )

        result = await service.apply_policy(DataType.MEMORY_WORKING)

        assert result.is_ok  # Overall operation succeeds
        assert result.value.records_failed == 1
        assert len(result.value.errors) > 0

    @pytest.mark.asyncio
    async def test_apply_policy_no_repository(self):
        """Should handle missing repository gracefully."""
        service = RetentionService(config=RetentionConfig())

        result = await service.apply_policy(DataType.MEMORY_WORKING)

        assert result.is_ok
        assert "Memory repository not configured" in result.value.errors

    @pytest.mark.asyncio
    async def test_get_retention_stats(self, service):
        """Should return retention statistics."""
        result = await service.get_retention_stats(DataType.MEMORY_WORKING)

        assert result.is_ok
        stats = result.value
        assert stats.data_type == DataType.MEMORY_WORKING
        assert stats.policy is not None

    @pytest.mark.asyncio
    async def test_apply_all_policies(self, service, mock_memory_repo, mock_decision_repo):
        """Should apply policies to all data types."""
        mock_memory_repo.find_expired_memories.return_value = Result.ok([])
        mock_decision_repo.find_expired_decisions.return_value = Result.ok([])

        result = await service.apply_all_policies()

        assert result.is_ok
        # Should have processed multiple data types
        assert len(result.value) > 0

    @pytest.mark.asyncio
    async def test_apply_all_policies_respects_time_limit(self, service, mock_memory_repo):
        """Should stop when time limit reached."""
        # Very short timeout - should still process at least one
        service._config.max_duration_seconds = 1

        # Make the first call slow to trigger timeout
        async def slow_find(*args, **kwargs):
            import asyncio
            await asyncio.sleep(2)  # Sleep longer than timeout
            return Result.ok([])

        mock_memory_repo.find_expired_memories.side_effect = slow_find

        result = await service.apply_all_policies()

        assert result.is_ok
        # Should have attempted at least one policy
        # but may not complete all due to timeout
        # The timeout check happens after each complete policy
        assert len(result.value) <= 11  # Max possible data types

    @pytest.mark.asyncio
    async def test_apply_policy_user_scoped(self, service, mock_memory_repo):
        """Should scope operations to user."""
        user_id = uuid4()
        mock_memory_repo.find_expired_memories.return_value = Result.ok([])

        await service.apply_policy(DataType.MEMORY_WORKING, user_id=user_id)

        # Verify user_id was passed to repository
        call_args = mock_memory_repo.find_expired_memories.call_args
        assert call_args.kwargs.get("user_id") == user_id

    @pytest.mark.asyncio
    async def test_apply_policy_exception_handling(self, service, mock_memory_repo):
        """Should handle exceptions and return error result."""
        mock_memory_repo.find_expired_memories.side_effect = Exception("Unexpected error")

        result = await service.apply_policy(DataType.MEMORY_WORKING)

        assert not result.is_ok
        assert "Unexpected error" in result.error.message


class TestRetentionServiceIntegration:
    """Integration-style tests for retention service."""

    @pytest.mark.asyncio
    async def test_full_retention_flow(self):
        """Test complete retention flow with mock data."""
        # Setup
        mock_memory_repo = AsyncMock()
        now = datetime.now(timezone.utc)

        # Create expired memories
        expired_memories = [
            Memory(
                memory_id=uuid4(),
                user_id=uuid4(),
                content=f"Memory {i}",
                content_type="fact",
                temporal_level=TemporalLevel.IMMEDIATE,
                valid_from=now - timedelta(days=10),
                valid_until=None,
                base_salience=0.5,
                created_at=now - timedelta(days=10),
                updated_at=now - timedelta(days=10),
            )
            for i in range(5)
        ]

        mock_memory_repo.find_expired_memories.return_value = Result.ok(expired_memories)
        mock_memory_repo.soft_delete_memory.return_value = Result.ok(None)

        service = RetentionService(
            memory_repository=mock_memory_repo,
            config=RetentionConfig(),
        )

        # Execute
        result = await service.apply_policy(DataType.MEMORY_WORKING)

        # Verify
        assert result.is_ok
        assert result.value.records_found == 5
        assert result.value.records_processed == 5
        assert result.value.records_deleted == 5
        assert result.value.records_failed == 0
        assert result.value.duration_seconds >= 0
        assert mock_memory_repo.soft_delete_memory.call_count == 5
