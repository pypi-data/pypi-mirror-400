"""Standard tier worker runner.

This runner initializes and manages all Standard tier background jobs
using APScheduler for in-process scheduling.
"""

import structlog

from mind.adapters.standard.apscheduler_runner import APSchedulerRunner
from mind.ports.scheduler import StandardJobs

from .jobs import (
    cleanup_job,
    consolidation_job,
    expiration_job,
    pattern_detection_job,
    promotion_job,
)

logger = structlog.get_logger()


class StandardWorkerRunner:
    """Manages Standard tier background workers.

    This runner:
    1. Initializes APScheduler
    2. Registers all lifecycle jobs with correct intervals
    3. Provides start/stop lifecycle methods

    Jobs scheduled:
    - Consolidation (hourly): Merge similar memories
    - Expiration (daily): Mark old memories as expired
    - Promotion (daily): Elevate high-salience memories
    - Pattern Detection (weekly): Find recurring patterns
    - Cleanup (daily): Remove old events and traces
    """

    def __init__(self, *, start_immediately: bool = False):
        """Initialize the worker runner.

        Args:
            start_immediately: If True, run jobs immediately on start.
                             If False, wait for first interval.
        """
        self._scheduler = APSchedulerRunner()
        self._start_immediately = start_immediately
        self._initialized = False

    async def initialize(self) -> None:
        """Register all background jobs with the scheduler."""
        if self._initialized:
            return

        log = logger.bind(component="worker_runner")
        log.info("registering_standard_jobs")

        # Register consolidation job (hourly)
        await self._scheduler.schedule_interval(
            job_id=StandardJobs.CONSOLIDATION,
            func=consolidation_job,
            interval=StandardJobs.CONSOLIDATION_INTERVAL,
            name="Memory Consolidation",
            start_immediately=self._start_immediately,
        )
        log.debug("job_registered", job_id=StandardJobs.CONSOLIDATION)

        # Register expiration job (daily)
        await self._scheduler.schedule_interval(
            job_id=StandardJobs.EXPIRATION,
            func=expiration_job,
            interval=StandardJobs.EXPIRATION_INTERVAL,
            name="Memory Expiration",
            start_immediately=self._start_immediately,
        )
        log.debug("job_registered", job_id=StandardJobs.EXPIRATION)

        # Register promotion job (daily)
        await self._scheduler.schedule_interval(
            job_id=StandardJobs.PROMOTION,
            func=promotion_job,
            interval=StandardJobs.PROMOTION_INTERVAL,
            name="Memory Promotion",
            start_immediately=self._start_immediately,
        )
        log.debug("job_registered", job_id=StandardJobs.PROMOTION)

        # Register pattern detection job (weekly)
        await self._scheduler.schedule_interval(
            job_id=StandardJobs.PATTERN_DETECTION,
            func=pattern_detection_job,
            interval=StandardJobs.PATTERN_DETECTION_INTERVAL,
            name="Pattern Detection",
            start_immediately=self._start_immediately,
        )
        log.debug("job_registered", job_id=StandardJobs.PATTERN_DETECTION)

        # Register cleanup job (daily)
        await self._scheduler.schedule_interval(
            job_id=StandardJobs.CLEANUP,
            func=cleanup_job,
            interval=StandardJobs.CLEANUP_INTERVAL,
            name="Cleanup",
            start_immediately=self._start_immediately,
        )
        log.debug("job_registered", job_id=StandardJobs.CLEANUP)

        self._initialized = True
        log.info("standard_jobs_registered", job_count=5)

    async def start(self) -> None:
        """Start the worker runner.

        This will:
        1. Register all jobs if not already done
        2. Start the APScheduler

        Jobs will begin running at their scheduled intervals.
        """
        if not self._initialized:
            await self.initialize()

        await self._scheduler.start()
        logger.info("standard_worker_started")

    async def stop(self, wait: bool = True) -> None:
        """Stop the worker runner.

        Args:
            wait: If True, wait for running jobs to complete.
        """
        await self._scheduler.shutdown(wait=wait)
        logger.info("standard_worker_stopped")

    async def run_job_now(self, job_id: str) -> bool:
        """Trigger immediate execution of a specific job.

        Args:
            job_id: The job to run (use StandardJobs constants)

        Returns:
            True if job was triggered, False if not found
        """
        return await self._scheduler.run_now(job_id)

    async def get_job_status(self, job_id: str):
        """Get status of a specific job."""
        return await self._scheduler.get_job(job_id)

    async def list_jobs(self):
        """List all scheduled jobs with their status."""
        return await self._scheduler.list_jobs()

    async def health_check(self) -> bool:
        """Check if the worker runner is healthy."""
        return await self._scheduler.health_check()

    @property
    def scheduler(self) -> APSchedulerRunner:
        """Access the underlying scheduler for advanced operations."""
        return self._scheduler
