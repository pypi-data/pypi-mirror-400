"""Unit tests for APScheduler adapter.

These tests verify the scheduler logic without running real jobs.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from mind.adapters.standard.apscheduler_runner import APSchedulerRunner
from mind.ports.scheduler import JobStatus


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def scheduler():
    """Create an APSchedulerRunner for testing."""
    return APSchedulerRunner()


@pytest.fixture
def mock_job():
    """Create a mock APScheduler job."""
    job = MagicMock()
    job.id = "test-job-1"
    job.name = "Test Job"
    job.next_run_time = datetime.now(UTC) + timedelta(hours=1)
    job.pending = False
    return job


# =============================================================================
# Interval Scheduling Tests
# =============================================================================


class TestIntervalScheduling:
    """Tests for interval-based job scheduling."""

    @pytest.mark.asyncio
    async def test_schedule_interval_job(self, scheduler):
        """Test scheduling an interval job."""
        async def dummy_job():
            pass

        job_info = await scheduler.schedule_interval(
            job_id="test-interval",
            func=dummy_job,
            interval=timedelta(minutes=5),
            name="Test Interval Job",
        )

        assert job_info.job_id == "test-interval"
        assert job_info.name == "Test Interval Job"
        assert job_info.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_schedule_interval_start_immediately(self, scheduler):
        """Test scheduling interval job to start immediately."""
        async def dummy_job():
            pass

        job_info = await scheduler.schedule_interval(
            job_id="test-immediate",
            func=dummy_job,
            interval=timedelta(minutes=5),
            start_immediately=True,
        )

        assert job_info.next_run is not None
        # Should be very close to now
        assert job_info.next_run <= datetime.now(UTC) + timedelta(seconds=5)

    @pytest.mark.asyncio
    async def test_schedule_interval_with_kwargs(self, scheduler):
        """Test scheduling interval job with kwargs."""
        async def job_with_params(param1, param2):
            pass

        job_info = await scheduler.schedule_interval(
            job_id="test-kwargs",
            func=job_with_params,
            interval=timedelta(hours=1),
            kwargs={"param1": "value1", "param2": "value2"},
        )

        assert job_info.job_id == "test-kwargs"

    @pytest.mark.asyncio
    async def test_schedule_interval_replaces_existing(self, scheduler):
        """Test that scheduling same job ID replaces existing."""
        async def job_v1():
            return "v1"

        async def job_v2():
            return "v2"

        await scheduler.schedule_interval(
            job_id="replace-test",
            func=job_v1,
            interval=timedelta(minutes=5),
        )

        job_info = await scheduler.schedule_interval(
            job_id="replace-test",
            func=job_v2,
            interval=timedelta(minutes=10),
        )

        assert job_info.job_id == "replace-test"


# =============================================================================
# Cron Scheduling Tests
# =============================================================================


class TestCronScheduling:
    """Tests for cron-based job scheduling."""

    @pytest.mark.asyncio
    async def test_schedule_cron_job(self, scheduler):
        """Test scheduling a cron job."""
        async def daily_job():
            pass

        job_info = await scheduler.schedule_cron(
            job_id="daily-cron",
            func=daily_job,
            cron_expression="0 9 * * *",  # Daily at 9 AM
            name="Daily Job",
        )

        assert job_info.job_id == "daily-cron"
        assert job_info.name == "Daily Job"

    @pytest.mark.asyncio
    async def test_schedule_cron_invalid_expression(self, scheduler):
        """Test scheduling with invalid cron expression."""
        async def dummy_job():
            pass

        with pytest.raises(ValueError, match="Invalid cron expression"):
            await scheduler.schedule_cron(
                job_id="invalid-cron",
                func=dummy_job,
                cron_expression="invalid",
            )

    @pytest.mark.asyncio
    async def test_schedule_cron_with_timezone(self, scheduler):
        """Test scheduling cron job with timezone."""
        async def timezone_job():
            pass

        job_info = await scheduler.schedule_cron(
            job_id="tz-cron",
            func=timezone_job,
            cron_expression="0 9 * * *",
            timezone="America/New_York",
        )

        assert job_info.job_id == "tz-cron"


# =============================================================================
# One-time Job Tests
# =============================================================================


class TestOneTimeJobs:
    """Tests for one-time job scheduling."""

    @pytest.mark.asyncio
    async def test_schedule_once(self, scheduler):
        """Test scheduling a one-time job."""
        async def one_time_job():
            pass

        run_at = datetime.now(UTC) + timedelta(hours=1)

        job_info = await scheduler.schedule_once(
            job_id="one-time",
            func=one_time_job,
            run_at=run_at,
            name="One Time Job",
        )

        assert job_info.job_id == "one-time"
        assert job_info.next_run == run_at

    @pytest.mark.asyncio
    async def test_schedule_delayed(self, scheduler):
        """Test scheduling a delayed job."""
        async def delayed_job():
            pass

        job_info = await scheduler.schedule_delayed(
            job_id="delayed",
            func=delayed_job,
            delay=timedelta(minutes=30),
        )

        assert job_info.job_id == "delayed"
        # Should be roughly 30 minutes from now
        expected_min = datetime.now(UTC) + timedelta(minutes=29)
        expected_max = datetime.now(UTC) + timedelta(minutes=31)
        assert expected_min <= job_info.next_run <= expected_max


# =============================================================================
# Job Management Tests
# =============================================================================


class TestJobManagement:
    """Tests for job management operations."""

    @pytest.mark.asyncio
    async def test_cancel_job(self, scheduler):
        """Test canceling a job."""
        async def dummy_job():
            pass

        await scheduler.schedule_interval(
            job_id="to-cancel",
            func=dummy_job,
            interval=timedelta(minutes=5),
        )

        result = await scheduler.cancel("to-cancel")

        assert result is True

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_job(self, scheduler):
        """Test canceling a job that doesn't exist."""
        result = await scheduler.cancel("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_pause_job(self, scheduler):
        """Test pausing a job."""
        async def dummy_job():
            pass

        await scheduler.schedule_interval(
            job_id="to-pause",
            func=dummy_job,
            interval=timedelta(minutes=5),
        )

        result = await scheduler.pause("to-pause")

        assert result is True

    @pytest.mark.asyncio
    async def test_pause_nonexistent_job(self, scheduler):
        """Test pausing a job that doesn't exist."""
        result = await scheduler.pause("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_resume_job(self, scheduler):
        """Test resuming a paused job."""
        async def dummy_job():
            pass

        await scheduler.schedule_interval(
            job_id="to-resume",
            func=dummy_job,
            interval=timedelta(minutes=5),
        )
        await scheduler.pause("to-resume")

        result = await scheduler.resume("to-resume")

        assert result is True

    @pytest.mark.asyncio
    async def test_resume_nonexistent_job(self, scheduler):
        """Test resuming a job that doesn't exist."""
        result = await scheduler.resume("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_run_now(self, scheduler):
        """Test triggering immediate job execution."""
        async def dummy_job():
            pass

        await scheduler.schedule_interval(
            job_id="run-now",
            func=dummy_job,
            interval=timedelta(hours=1),
        )

        result = await scheduler.run_now("run-now")

        assert result is True

    @pytest.mark.asyncio
    async def test_run_now_nonexistent(self, scheduler):
        """Test running a job that doesn't exist."""
        result = await scheduler.run_now("nonexistent")

        assert result is False


# =============================================================================
# Status and Monitoring Tests
# =============================================================================


class TestStatusMonitoring:
    """Tests for job status and monitoring."""

    @pytest.mark.asyncio
    async def test_get_job(self, scheduler):
        """Test getting job information."""
        async def dummy_job():
            pass

        await scheduler.schedule_interval(
            job_id="get-test",
            func=dummy_job,
            interval=timedelta(minutes=5),
            name="Get Test Job",
        )

        job_info = await scheduler.get_job("get-test")

        assert job_info is not None
        assert job_info.job_id == "get-test"
        assert job_info.name == "Get Test Job"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, scheduler):
        """Test getting a non-existent job."""
        job_info = await scheduler.get_job("nonexistent")

        assert job_info is None

    @pytest.mark.asyncio
    async def test_list_jobs(self, scheduler):
        """Test listing all jobs."""
        async def job1():
            pass

        async def job2():
            pass

        await scheduler.schedule_interval(
            job_id="list-1",
            func=job1,
            interval=timedelta(minutes=5),
        )
        await scheduler.schedule_interval(
            job_id="list-2",
            func=job2,
            interval=timedelta(minutes=10),
        )

        jobs = await scheduler.list_jobs()

        assert len(jobs) == 2
        job_ids = {j.job_id for j in jobs}
        assert "list-1" in job_ids
        assert "list-2" in job_ids

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, scheduler):
        """Test listing jobs when none exist."""
        jobs = await scheduler.list_jobs()

        assert jobs == []

    @pytest.mark.asyncio
    async def test_get_failed_jobs(self, scheduler):
        """Test getting failed jobs."""
        # Simulate failed job by setting error count
        scheduler._job_errors["failed-job"] = 3

        # Need to add a job for it to show up
        async def dummy_job():
            pass

        await scheduler.schedule_interval(
            job_id="failed-job",
            func=dummy_job,
            interval=timedelta(minutes=5),
        )

        failed = await scheduler.get_failed_jobs()

        assert len(failed) == 1
        assert failed[0].job_id == "failed-job"
        assert failed[0].error_count == 3
        assert failed[0].status == JobStatus.FAILED


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestLifecycle:
    """Tests for scheduler lifecycle operations."""

    @pytest.mark.asyncio
    async def test_start_scheduler(self, scheduler):
        """Test starting the scheduler."""
        await scheduler.start()

        assert scheduler._scheduler.running is True

        await scheduler.shutdown()

    @pytest.mark.asyncio
    async def test_start_scheduler_idempotent(self, scheduler):
        """Test that starting twice is safe."""
        await scheduler.start()
        await scheduler.start()  # Should not raise

        assert scheduler._scheduler.running is True

        await scheduler.shutdown()

    @pytest.mark.asyncio
    async def test_shutdown_scheduler(self, scheduler):
        """Test shutting down the scheduler."""
        await scheduler.start()
        await scheduler.shutdown()

        assert scheduler._scheduler.running is False

    @pytest.mark.asyncio
    async def test_shutdown_not_started(self, scheduler):
        """Test shutting down when not started."""
        # Should not raise
        await scheduler.shutdown()

    @pytest.mark.asyncio
    async def test_health_check_running(self, scheduler):
        """Test health check when running."""
        await scheduler.start()

        result = await scheduler.health_check()

        assert result is True

        await scheduler.shutdown()

    @pytest.mark.asyncio
    async def test_health_check_not_running(self, scheduler):
        """Test health check when not running."""
        result = await scheduler.health_check()

        assert result is False


# =============================================================================
# Job Wrapping Tests
# =============================================================================


class TestJobWrapping:
    """Tests for job result and error tracking."""

    @pytest.mark.asyncio
    async def test_wrap_func_success(self, scheduler):
        """Test that successful jobs track results."""
        async def success_job():
            return "completed"

        wrapped = scheduler._wrap_func("test-job", success_job)
        result = await wrapped()

        assert result == "completed"
        assert scheduler._job_results.get("test-job") == "completed"

    @pytest.mark.asyncio
    async def test_wrap_func_success_no_return(self, scheduler):
        """Test that jobs without return value track as success."""
        async def no_return_job():
            pass

        wrapped = scheduler._wrap_func("test-job", no_return_job)
        await wrapped()

        assert scheduler._job_results.get("test-job") == "success"

    @pytest.mark.asyncio
    async def test_wrap_func_error(self, scheduler):
        """Test that failed jobs track errors."""
        async def failing_job():
            raise ValueError("test error")

        wrapped = scheduler._wrap_func("test-job", failing_job)

        with pytest.raises(ValueError):
            await wrapped()

        assert scheduler._job_errors.get("test-job") == 1
        assert "error: test error" in scheduler._job_results.get("test-job")

    @pytest.mark.asyncio
    async def test_wrap_func_multiple_errors(self, scheduler):
        """Test that error count accumulates."""
        async def failing_job():
            raise RuntimeError("repeated failure")

        wrapped = scheduler._wrap_func("test-job", failing_job)

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await wrapped()

        assert scheduler._job_errors.get("test-job") == 3
