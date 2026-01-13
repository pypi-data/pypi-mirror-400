"""Integration tests for APScheduler adapter.

These tests verify the APSchedulerRunner works correctly
with real async job execution.
"""

import asyncio
from datetime import timedelta

import pytest
import pytest_asyncio

from tests.integration.standard.conftest import requires_docker


# These tests don't require Docker but use the integration marker
pytestmark = pytest.mark.integration


class TestAPSchedulerRunnerIntegration:
    """Integration tests for APSchedulerRunner."""

    @pytest_asyncio.fixture
    async def scheduler(self):
        """Create and start an APSchedulerRunner."""
        from mind.adapters.standard.apscheduler_runner import APSchedulerRunner

        runner = APSchedulerRunner()
        await runner.start()
        yield runner
        await runner.shutdown()

    @pytest.mark.asyncio
    async def test_schedule_and_execute_job(self, scheduler):
        """Test scheduling and executing a job."""
        from mind.ports.scheduler import JobStatus

        executed = {"count": 0}

        async def test_job():
            executed["count"] += 1
            return "completed"

        job_info = await scheduler.schedule_interval(
            job_id="test-execute",
            func=test_job,
            interval=timedelta(milliseconds=100),
            start_immediately=True,
        )

        assert job_info.status == JobStatus.PENDING

        # Wait for job to execute
        await asyncio.sleep(0.3)

        assert executed["count"] >= 1

    @pytest.mark.asyncio
    async def test_schedule_delayed_job(self, scheduler):
        """Test scheduling a delayed job."""
        executed = {"count": 0}

        async def delayed_job():
            executed["count"] += 1

        await scheduler.schedule_delayed(
            job_id="test-delayed",
            func=delayed_job,
            delay=timedelta(milliseconds=100),
        )

        # Should not have executed yet
        assert executed["count"] == 0

        # Wait for delay
        await asyncio.sleep(0.2)

        assert executed["count"] == 1

    @pytest.mark.asyncio
    async def test_cancel_job_prevents_execution(self, scheduler):
        """Test that canceling a job prevents execution."""
        executed = {"count": 0}

        async def should_not_run():
            executed["count"] += 1

        await scheduler.schedule_delayed(
            job_id="test-cancel",
            func=should_not_run,
            delay=timedelta(milliseconds=200),
        )

        # Cancel before execution
        result = await scheduler.cancel("test-cancel")
        assert result is True

        # Wait past the scheduled time
        await asyncio.sleep(0.3)

        # Should not have executed
        assert executed["count"] == 0

    @pytest.mark.asyncio
    async def test_pause_and_resume_job(self, scheduler):
        """Test pausing and resuming a job."""
        executed = {"count": 0}

        async def pausable_job():
            executed["count"] += 1

        await scheduler.schedule_interval(
            job_id="test-pause",
            func=pausable_job,
            interval=timedelta(milliseconds=100),
            start_immediately=True,
        )

        # Let it run once
        await asyncio.sleep(0.15)
        initial_count = executed["count"]
        assert initial_count >= 1

        # Pause
        await scheduler.pause("test-pause")

        # Wait and verify no more executions
        await asyncio.sleep(0.2)
        paused_count = executed["count"]
        assert paused_count == initial_count

        # Resume
        await scheduler.resume("test-pause")

        # Wait and verify executions resume
        await asyncio.sleep(0.15)
        assert executed["count"] > paused_count

    @pytest.mark.asyncio
    async def test_run_now_triggers_immediate_execution(self, scheduler):
        """Test that run_now triggers immediate execution."""
        executed = {"count": 0}

        async def on_demand_job():
            executed["count"] += 1

        # Schedule for far future
        await scheduler.schedule_interval(
            job_id="test-run-now",
            func=on_demand_job,
            interval=timedelta(hours=1),
            start_immediately=False,
        )

        # Should not have executed
        assert executed["count"] == 0

        # Trigger immediate execution
        result = await scheduler.run_now("test-run-now")
        assert result is True

        # Wait for execution
        await asyncio.sleep(0.1)

        assert executed["count"] == 1

    @pytest.mark.asyncio
    async def test_job_with_arguments(self, scheduler):
        """Test job execution with arguments."""
        results = {"value": None}

        async def job_with_args(arg1, arg2):
            results["value"] = f"{arg1}-{arg2}"

        await scheduler.schedule_delayed(
            job_id="test-args",
            func=job_with_args,
            delay=timedelta(milliseconds=50),
            kwargs={"arg1": "hello", "arg2": "world"},
        )

        await asyncio.sleep(0.15)

        assert results["value"] == "hello-world"

    @pytest.mark.asyncio
    async def test_list_jobs(self, scheduler):
        """Test listing all scheduled jobs."""
        async def job1():
            pass

        async def job2():
            pass

        await scheduler.schedule_interval(
            job_id="list-test-1",
            func=job1,
            interval=timedelta(minutes=5),
        )

        await scheduler.schedule_interval(
            job_id="list-test-2",
            func=job2,
            interval=timedelta(minutes=10),
        )

        jobs = await scheduler.list_jobs()

        job_ids = {j.job_id for j in jobs}
        assert "list-test-1" in job_ids
        assert "list-test-2" in job_ids

    @pytest.mark.asyncio
    async def test_get_job_info(self, scheduler):
        """Test getting job information."""
        async def info_job():
            pass

        await scheduler.schedule_interval(
            job_id="info-test",
            func=info_job,
            interval=timedelta(minutes=5),
            name="Info Test Job",
        )

        job_info = await scheduler.get_job("info-test")

        assert job_info is not None
        assert job_info.job_id == "info-test"
        assert job_info.name == "Info Test Job"
        assert job_info.next_run is not None

    @pytest.mark.asyncio
    async def test_job_error_tracking(self, scheduler):
        """Test that job errors are tracked."""
        async def failing_job():
            raise ValueError("Intentional failure")

        await scheduler.schedule_interval(
            job_id="error-test",
            func=failing_job,
            interval=timedelta(milliseconds=100),
            start_immediately=True,
        )

        # Wait for some executions
        await asyncio.sleep(0.35)

        # Check failed jobs
        failed = await scheduler.get_failed_jobs()

        error_job = next((j for j in failed if j.job_id == "error-test"), None)
        assert error_job is not None
        assert error_job.error_count >= 1

    @pytest.mark.asyncio
    async def test_cron_job_scheduling(self, scheduler):
        """Test cron-based job scheduling."""
        async def cron_job():
            pass

        # Schedule for every minute (just testing scheduling, not execution)
        job_info = await scheduler.schedule_cron(
            job_id="cron-test",
            func=cron_job,
            cron_expression="* * * * *",
            name="Cron Test",
        )

        assert job_info.job_id == "cron-test"
        assert job_info.next_run is not None

    @pytest.mark.asyncio
    async def test_invalid_cron_expression_raises(self, scheduler):
        """Test that invalid cron expressions raise ValueError."""
        async def dummy():
            pass

        with pytest.raises(ValueError, match="Invalid cron expression"):
            await scheduler.schedule_cron(
                job_id="invalid-cron",
                func=dummy,
                cron_expression="not-valid",
            )

    @pytest.mark.asyncio
    async def test_health_check_when_running(self, scheduler):
        """Test health check returns True when running."""
        result = await scheduler.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_when_stopped(self):
        """Test health check returns False when stopped."""
        from mind.adapters.standard.apscheduler_runner import APSchedulerRunner

        runner = APSchedulerRunner()
        # Don't start it

        result = await runner.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_replace_existing_job(self, scheduler):
        """Test that scheduling same ID replaces existing job."""
        results = {"version": None}

        async def job_v1():
            results["version"] = 1

        async def job_v2():
            results["version"] = 2

        await scheduler.schedule_delayed(
            job_id="replace-test",
            func=job_v1,
            delay=timedelta(seconds=1),
        )

        # Replace with v2
        await scheduler.schedule_delayed(
            job_id="replace-test",
            func=job_v2,
            delay=timedelta(milliseconds=50),
        )

        # Wait for execution
        await asyncio.sleep(0.15)

        # Should have executed v2
        assert results["version"] == 2
