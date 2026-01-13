"""Tests for the gardener scheduler.

Tests the Temporal schedule setup and configuration.
"""

import pytest
from datetime import timedelta
from uuid import uuid4

from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from mind.workers.gardener.workflows import (
    ScheduledGardenerWorkflow,
    ScheduledGardenerInput,
    ScheduledGardenerResult,
    GardenerResult,
    MemoryPromotionWorkflow,
    MemoryExpirationWorkflow,
    MemoryConsolidationWorkflow,
    PromotionWorkflowInput,
    PromotionWorkflowResult,
    ExpirationWorkflowInput,
    ExpirationWorkflowResult,
    ConsolidationWorkflowInput,
    ConsolidationWorkflowResult,
)
from mind.workers.gardener.scheduler import (
    ScheduleConfig,
    DEFAULT_SCHEDULES,
)


class TestScheduleConfig:
    """Tests for ScheduleConfig dataclass."""

    def test_schedule_config_creation(self):
        """ScheduleConfig should be created with all required fields."""
        config = ScheduleConfig(
            schedule_id="test-schedule",
            description="Test schedule",
            interval=timedelta(hours=24),
            workflow_type="ScheduledGardenerWorkflow",
            workflow_args=[],
        )

        assert config.schedule_id == "test-schedule"
        assert config.description == "Test schedule"
        assert config.interval == timedelta(hours=24)
        assert config.workflow_type == "ScheduledGardenerWorkflow"
        assert config.workflow_args == []
        assert config.paused is False

    def test_schedule_config_with_paused(self):
        """ScheduleConfig should support paused state."""
        config = ScheduleConfig(
            schedule_id="paused-schedule",
            description="Paused schedule",
            interval=timedelta(hours=1),
            workflow_type="TestWorkflow",
            workflow_args=[],
            paused=True,
        )

        assert config.paused is True


class TestDefaultSchedules:
    """Tests for default schedule configurations."""

    def test_default_schedules_exist(self):
        """Default schedules should be defined."""
        assert len(DEFAULT_SCHEDULES) >= 4

    def test_gardener_daily_schedule(self):
        """Daily gardener schedule should be configured."""
        gardener = next(
            (s for s in DEFAULT_SCHEDULES if s.schedule_id == "gardener-daily"),
            None,
        )

        assert gardener is not None
        assert gardener.interval == timedelta(hours=24)
        assert gardener.workflow_type == "ScheduledGardenerWorkflow"

    def test_outcome_analysis_schedule(self):
        """Weekly outcome analysis should be configured."""
        outcomes = next(
            (s for s in DEFAULT_SCHEDULES if "outcomes" in s.schedule_id),
            None,
        )

        assert outcomes is not None
        assert outcomes.interval == timedelta(days=7)

    def test_calibration_schedule(self):
        """Monthly calibration should be configured."""
        calibration = next(
            (s for s in DEFAULT_SCHEDULES if "calibrate" in s.schedule_id),
            None,
        )

        assert calibration is not None
        assert calibration.interval == timedelta(days=30)

    def test_pattern_extraction_schedule(self):
        """Monthly pattern extraction should be configured."""
        patterns = next(
            (s for s in DEFAULT_SCHEDULES if "pattern" in s.schedule_id),
            None,
        )

        assert patterns is not None
        assert patterns.interval == timedelta(days=30)


class TestScheduledGardenerInput:
    """Tests for ScheduledGardenerInput dataclass."""

    def test_input_defaults(self):
        """ScheduledGardenerInput should have sensible defaults."""
        input = ScheduledGardenerInput()

        assert input.user_ids is None
        assert input.days_active == 30
        assert input.max_users == 1000

    def test_input_with_user_ids(self):
        """ScheduledGardenerInput should accept explicit user IDs."""
        user_ids = [uuid4(), uuid4()]
        input = ScheduledGardenerInput(user_ids=user_ids)

        assert input.user_ids == user_ids


class TestScheduledGardenerWorkflow:
    """Tests for the ScheduledGardenerWorkflow with user discovery."""

    @pytest.mark.asyncio
    async def test_workflow_with_no_users(self):
        """Workflow should handle case with no active users."""
        task_queue = f"gardener-sched-empty-{uuid4()}"

        @activity.defn(name="get_active_user_ids")
        async def mock_get_users(days_active: int, limit: int) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ScheduledGardenerWorkflow],
                activities=[mock_get_users],
            ):
                result = await env.client.execute_workflow(
                    ScheduledGardenerWorkflow.run,
                    ScheduledGardenerInput(),
                    id=f"test-gardener-empty-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.users_processed == 0
                assert result.total_promotions == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_discovers_users(self):
        """Workflow should discover users when none provided."""
        task_queue = f"gardener-sched-discover-{uuid4()}"
        discovered_users = [uuid4(), uuid4()]

        @activity.defn(name="get_active_user_ids")
        async def mock_get_users(days_active: int, limit: int) -> list:
            return discovered_users

        @activity.defn(name="find_promotion_candidates")
        async def mock_find_promo(user_id, batch_size) -> list:
            return []

        @activity.defn(name="find_expired_memories")
        async def mock_find_expired(user_id, batch_size) -> list:
            return []

        @activity.defn(name="find_consolidation_candidates")
        async def mock_find_consol(user_id, batch_size, min_memories) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[
                    ScheduledGardenerWorkflow,
                    MemoryPromotionWorkflow,
                    MemoryExpirationWorkflow,
                    MemoryConsolidationWorkflow,
                ],
                activities=[
                    mock_get_users,
                    mock_find_promo,
                    mock_find_expired,
                    mock_find_consol,
                ],
            ):
                result = await env.client.execute_workflow(
                    ScheduledGardenerWorkflow.run,
                    ScheduledGardenerInput(),
                    id=f"test-gardener-discover-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.users_processed == 2
                assert len(result.user_results) == 2

    @pytest.mark.asyncio
    async def test_workflow_with_explicit_users(self):
        """Workflow should use provided user IDs without discovery."""
        task_queue = f"gardener-sched-explicit-{uuid4()}"
        explicit_users = [uuid4()]

        @activity.defn(name="find_promotion_candidates")
        async def mock_find_promo(user_id, batch_size) -> list:
            return []

        @activity.defn(name="find_expired_memories")
        async def mock_find_expired(user_id, batch_size) -> list:
            return []

        @activity.defn(name="find_consolidation_candidates")
        async def mock_find_consol(user_id, batch_size, min_memories) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[
                    ScheduledGardenerWorkflow,
                    MemoryPromotionWorkflow,
                    MemoryExpirationWorkflow,
                    MemoryConsolidationWorkflow,
                ],
                activities=[
                    mock_find_promo,
                    mock_find_expired,
                    mock_find_consol,
                ],
            ):
                result = await env.client.execute_workflow(
                    ScheduledGardenerWorkflow.run,
                    ScheduledGardenerInput(user_ids=explicit_users),
                    id=f"test-gardener-explicit-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.users_processed == 1
                assert str(explicit_users[0]) in result.user_results

    @pytest.mark.asyncio
    async def test_workflow_user_discovery_failure(self):
        """Workflow should handle user discovery failure gracefully."""
        task_queue = f"gardener-sched-fail-{uuid4()}"

        @activity.defn(name="get_active_user_ids")
        async def mock_get_users_fail(days_active: int, limit: int) -> list:
            raise Exception("Database connection failed")

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ScheduledGardenerWorkflow],
                activities=[mock_get_users_fail],
            ):
                result = await env.client.execute_workflow(
                    ScheduledGardenerWorkflow.run,
                    ScheduledGardenerInput(),
                    id=f"test-gardener-fail-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.users_processed == 0
                assert len(result.errors) > 0
                assert "discover users" in result.errors[0].lower()


class TestScheduledGardenerResult:
    """Tests for ScheduledGardenerResult dataclass."""

    def test_result_creation(self):
        """ScheduledGardenerResult should be created with all fields."""
        result = ScheduledGardenerResult(
            users_processed=5,
            total_promotions=10,
            total_expirations=3,
            total_consolidations=2,
            total_memories_merged=4,
            user_results={},
            errors=[],
        )

        assert result.users_processed == 5
        assert result.total_promotions == 10
        assert result.total_expirations == 3
        assert result.total_consolidations == 2
        assert result.total_memories_merged == 4

    def test_result_with_errors(self):
        """ScheduledGardenerResult should store errors."""
        result = ScheduledGardenerResult(
            users_processed=1,
            total_promotions=0,
            total_expirations=0,
            total_consolidations=0,
            total_memories_merged=0,
            user_results={},
            errors=["Error 1", "Error 2"],
        )

        assert len(result.errors) == 2
