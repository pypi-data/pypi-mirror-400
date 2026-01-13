"""Background scheduler port interface for recurring tasks.

This port abstracts background job scheduling:
- Standard: APScheduler (in-process, single instance)
- Enterprise: Temporal.io (distributed, durable workflows)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Awaitable, Callable, Optional


class JobStatus(Enum):
    """Status of a scheduled job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobInfo:
    """Information about a scheduled job."""

    job_id: str
    name: str
    status: JobStatus
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    last_result: Optional[str]
    run_count: int
    error_count: int


# Job function type: async function with optional kwargs
JobFunc = Callable[..., Awaitable[Any]]


class IBackgroundScheduler(ABC):
    """Port for background job scheduling.

    Used for:
    - Memory consolidation (hourly)
    - Memory expiration checks (daily)
    - Memory promotion (daily)
    - Pattern detection (weekly)

    Implementations:
        - APSchedulerRunner (Standard): In-process scheduler
        - TemporalScheduler (Enterprise): Distributed workflows
    """

    # =========================================================================
    # Interval Jobs (recurring)
    # =========================================================================

    @abstractmethod
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
        """Schedule a job to run at fixed intervals.

        Args:
            job_id: Unique identifier for the job
            func: Async function to execute
            interval: Time between runs
            name: Human-readable name (defaults to job_id)
            start_immediately: If True, run once immediately
            kwargs: Arguments to pass to the function

        Returns:
            Information about the scheduled job

        Note:
            If a job with this ID exists, it is replaced.
        """
        pass

    @abstractmethod
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
        """Schedule a job using cron expression.

        Args:
            job_id: Unique identifier for the job
            func: Async function to execute
            cron_expression: Cron schedule (e.g., "0 * * * *" for hourly)
            name: Human-readable name
            timezone: Timezone for the schedule
            kwargs: Arguments to pass to the function

        Returns:
            Information about the scheduled job
        """
        pass

    # =========================================================================
    # One-time Jobs
    # =========================================================================

    @abstractmethod
    async def schedule_once(
        self,
        job_id: str,
        func: JobFunc,
        run_at: datetime,
        *,
        name: Optional[str] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """Schedule a job to run once at a specific time.

        Args:
            job_id: Unique identifier for the job
            func: Async function to execute
            run_at: When to run the job
            name: Human-readable name
            kwargs: Arguments to pass to the function

        Returns:
            Information about the scheduled job
        """
        pass

    @abstractmethod
    async def schedule_delayed(
        self,
        job_id: str,
        func: JobFunc,
        delay: timedelta,
        *,
        name: Optional[str] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """Schedule a job to run after a delay.

        Args:
            job_id: Unique identifier for the job
            func: Async function to execute
            delay: Time to wait before running
            name: Human-readable name
            kwargs: Arguments to pass to the function

        Returns:
            Information about the scheduled job
        """
        pass

    # =========================================================================
    # Job Management
    # =========================================================================

    @abstractmethod
    async def cancel(self, job_id: str) -> bool:
        """Cancel a scheduled job.

        Args:
            job_id: The job to cancel

        Returns:
            True if job was found and cancelled, False otherwise
        """
        pass

    @abstractmethod
    async def pause(self, job_id: str) -> bool:
        """Pause a scheduled job (will not run until resumed).

        Args:
            job_id: The job to pause

        Returns:
            True if job was found and paused, False otherwise
        """
        pass

    @abstractmethod
    async def resume(self, job_id: str) -> bool:
        """Resume a paused job.

        Args:
            job_id: The job to resume

        Returns:
            True if job was found and resumed, False otherwise
        """
        pass

    @abstractmethod
    async def run_now(self, job_id: str) -> bool:
        """Trigger immediate execution of a job.

        Args:
            job_id: The job to run

        Returns:
            True if job was found and triggered, False otherwise
        """
        pass

    # =========================================================================
    # Status and Monitoring
    # =========================================================================

    @abstractmethod
    async def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get information about a specific job.

        Args:
            job_id: The job to look up

        Returns:
            Job information if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_jobs(self) -> list[JobInfo]:
        """List all scheduled jobs.

        Returns:
            List of all job information
        """
        pass

    @abstractmethod
    async def get_failed_jobs(self, limit: int = 50) -> list[JobInfo]:
        """Get jobs that have failed recently.

        Args:
            limit: Maximum jobs to return

        Returns:
            List of failed job information
        """
        pass

    # =========================================================================
    # Lifecycle
    # =========================================================================

    @abstractmethod
    async def start(self) -> None:
        """Start the scheduler.

        Must be called before jobs will run.
        """
        pass

    @abstractmethod
    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler.

        Args:
            wait: If True, wait for running jobs to complete
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the scheduler is healthy.

        Returns:
            True if healthy, False otherwise
        """
        pass


# =========================================================================
# Standard Tier Job Definitions
# =========================================================================

# These constants define the default job IDs and schedules for Standard tier


class StandardJobs:
    """Default job configurations for Standard tier."""

    # Memory consolidation: merge similar memories
    CONSOLIDATION = "mind.consolidation"
    CONSOLIDATION_INTERVAL = timedelta(hours=1)

    # Memory expiration: mark old immediate memories as expired
    EXPIRATION = "mind.expiration"
    EXPIRATION_INTERVAL = timedelta(hours=24)

    # Memory promotion: elevate high-salience memories
    PROMOTION = "mind.promotion"
    PROMOTION_INTERVAL = timedelta(hours=24)

    # Pattern detection: find recurring patterns
    PATTERN_DETECTION = "mind.pattern_detection"
    PATTERN_DETECTION_INTERVAL = timedelta(days=7)

    # Cleanup: remove expired events, old traces
    CLEANUP = "mind.cleanup"
    CLEANUP_INTERVAL = timedelta(days=1)
