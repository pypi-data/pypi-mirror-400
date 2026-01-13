"""APScheduler adapter for background job scheduling.

This adapter implements IBackgroundScheduler using APScheduler
for in-process job scheduling.

Features:
- Interval-based recurring jobs
- Cron-based scheduling
- One-time delayed jobs
- Job management (pause, resume, cancel)

Limitations compared to Temporal (Enterprise):
- Not distributed (single process only)
- Jobs don't survive process restarts
- No workflow orchestration
"""

from datetime import datetime, timedelta, UTC
from typing import Any, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from ...ports.scheduler import (
    IBackgroundScheduler,
    JobFunc,
    JobInfo,
    JobStatus,
)


class APSchedulerRunner(IBackgroundScheduler):
    """APScheduler implementation for Standard tier background jobs.

    Uses AsyncIOScheduler for async job execution within the
    same process as the API server.
    """

    def __init__(self):
        """Initialize the scheduler (not started yet)."""
        self._scheduler = AsyncIOScheduler(
            jobstores={
                "default": MemoryJobStore(),
            },
            job_defaults={
                "coalesce": True,  # Combine missed runs
                "max_instances": 1,  # One instance per job
                "misfire_grace_time": 60,  # 1 minute grace
            },
        )
        self._job_results: dict[str, str] = {}  # job_id -> last result
        self._job_errors: dict[str, int] = {}  # job_id -> error count

    # =========================================================================
    # Interval Jobs
    # =========================================================================

    async def schedule_interval(
        self,
        job_id: str,
        func: JobFunc,
        interval: timedelta,
        *,
        name: Optional[str] = None,
        start_immediately: bool = False,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """Schedule a job to run at fixed intervals."""
        # Wrap the async function
        wrapped = self._wrap_func(job_id, func)

        # Calculate next run time
        if start_immediately:
            next_run = datetime.now(UTC)
        else:
            next_run = datetime.now(UTC) + interval

        trigger = IntervalTrigger(
            seconds=interval.total_seconds(),
            start_date=next_run,
        )

        self._scheduler.add_job(
            wrapped,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            kwargs=kwargs or {},
            replace_existing=True,
        )

        # Return info directly - don't call get_job before scheduler starts
        return JobInfo(
            job_id=job_id,
            name=name or job_id,
            status=JobStatus.PENDING,
            next_run=next_run,
            last_run=None,
            last_result=None,
            run_count=0,
            error_count=0,
        )

    async def schedule_cron(
        self,
        job_id: str,
        func: JobFunc,
        cron_expression: str,
        *,
        name: Optional[str] = None,
        timezone: str = "UTC",
        kwargs: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """Schedule a job using cron expression."""
        wrapped = self._wrap_func(job_id, func)

        # Parse cron expression (minute hour day month day_of_week)
        parts = cron_expression.split()
        if len(parts) == 5:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
                timezone=timezone,
            )
        else:
            raise ValueError(
                f"Invalid cron expression: {cron_expression}. "
                "Expected 5 parts: minute hour day month day_of_week"
            )

        self._scheduler.add_job(
            wrapped,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            kwargs=kwargs or {},
            replace_existing=True,
        )

        # Return info directly - don't call get_job before scheduler starts
        return JobInfo(
            job_id=job_id,
            name=name or job_id,
            status=JobStatus.PENDING,
            next_run=None,
            last_run=None,
            last_result=None,
            run_count=0,
            error_count=0,
        )

    # =========================================================================
    # One-time Jobs
    # =========================================================================

    async def schedule_once(
        self,
        job_id: str,
        func: JobFunc,
        run_at: datetime,
        *,
        name: Optional[str] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """Schedule a job to run once at a specific time."""
        wrapped = self._wrap_func(job_id, func)

        trigger = DateTrigger(run_date=run_at)

        self._scheduler.add_job(
            wrapped,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            kwargs=kwargs or {},
            replace_existing=True,
        )

        return JobInfo(
            job_id=job_id,
            name=name or job_id,
            status=JobStatus.PENDING,
            next_run=run_at,
            last_run=None,
            last_result=None,
            run_count=0,
            error_count=0,
        )

    async def schedule_delayed(
        self,
        job_id: str,
        func: JobFunc,
        delay: timedelta,
        *,
        name: Optional[str] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """Schedule a job to run after a delay."""
        run_at = datetime.now(UTC) + delay
        return await self.schedule_once(
            job_id,
            func,
            run_at,
            name=name,
            kwargs=kwargs,
        )

    # =========================================================================
    # Job Management
    # =========================================================================

    async def cancel(self, job_id: str) -> bool:
        """Cancel a scheduled job."""
        try:
            self._scheduler.remove_job(job_id)
            return True
        except Exception:
            return False

    async def pause(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        try:
            self._scheduler.pause_job(job_id)
            return True
        except Exception:
            return False

    async def resume(self, job_id: str) -> bool:
        """Resume a paused job."""
        try:
            self._scheduler.resume_job(job_id)
            return True
        except Exception:
            return False

    async def run_now(self, job_id: str) -> bool:
        """Trigger immediate execution of a job."""
        try:
            job = self._scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now(UTC))
                return True
            return False
        except Exception:
            return False

    # =========================================================================
    # Status and Monitoring
    # =========================================================================

    async def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get information about a specific job."""
        job = self._scheduler.get_job(job_id)
        if job is None:
            return None

        # Determine status - handle jobs before scheduler starts
        try:
            next_run = getattr(job, 'next_run_time', None)
            if next_run is None:
                status = JobStatus.COMPLETED
            else:
                status = JobStatus.PENDING
        except Exception:
            status = JobStatus.PENDING
            next_run = None

        return JobInfo(
            job_id=job.id,
            name=job.name or job.id,
            status=status,
            next_run=next_run,
            last_run=None,  # APScheduler doesn't track this
            last_result=self._job_results.get(job_id),
            run_count=0,  # Would need separate tracking
            error_count=self._job_errors.get(job_id, 0),
        )

    async def list_jobs(self) -> list[JobInfo]:
        """List all scheduled jobs."""
        jobs = self._scheduler.get_jobs()
        result = []

        for job in jobs:
            info = await self.get_job(job.id)
            if info:
                result.append(info)

        return result

    async def get_failed_jobs(self, limit: int = 50) -> list[JobInfo]:
        """Get jobs that have failed recently."""
        # Filter jobs with errors
        failed = []
        for job_id, error_count in self._job_errors.items():
            if error_count > 0:
                info = await self.get_job(job_id)
                if info:
                    info = JobInfo(
                        job_id=info.job_id,
                        name=info.name,
                        status=JobStatus.FAILED,
                        next_run=info.next_run,
                        last_run=info.last_run,
                        last_result=info.last_result,
                        run_count=info.run_count,
                        error_count=error_count,
                    )
                    failed.append(info)

        return failed[:limit]

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def start(self) -> None:
        """Start the scheduler."""
        if not self._scheduler.running:
            self._scheduler.start()

    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)

    async def health_check(self) -> bool:
        """Check if the scheduler is healthy."""
        return self._scheduler.running

    # =========================================================================
    # Helpers
    # =========================================================================

    def _wrap_func(self, job_id: str, func: JobFunc):
        """Wrap an async function to track results and errors."""

        async def wrapper(**kwargs):
            try:
                result = await func(**kwargs)
                self._job_results[job_id] = str(result) if result else "success"
                return result
            except Exception as e:
                self._job_errors[job_id] = self._job_errors.get(job_id, 0) + 1
                self._job_results[job_id] = f"error: {e}"
                raise

        return wrapper
