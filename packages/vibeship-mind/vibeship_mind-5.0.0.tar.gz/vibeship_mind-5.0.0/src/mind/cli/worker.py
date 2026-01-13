"""Mind worker command - Run or manage background jobs.

This command provides direct access to background job operations:

Standard tier:
- Run individual jobs manually for testing/debugging
- List scheduled jobs and their status
- Trigger immediate job execution

Enterprise tier:
- Start Temporal workers for workflow execution

Usage:
    mind worker status              # Show scheduled jobs status
    mind worker run consolidation   # Run consolidation job now
    mind worker run --all           # Run all jobs immediately
"""

import asyncio
import sys
from typing import Optional

import structlog

logger = structlog.get_logger()


async def run_job(job_name: str) -> str:
    """Run a specific background job.

    Args:
        job_name: Name of the job to run

    Returns:
        Result message from the job
    """
    from mind.workers.standard.jobs import (
        cleanup_job,
        consolidation_job,
        expiration_job,
        pattern_detection_job,
        promotion_job,
    )

    jobs = {
        "consolidation": consolidation_job,
        "expiration": expiration_job,
        "promotion": promotion_job,
        "pattern_detection": pattern_detection_job,
        "cleanup": cleanup_job,
    }

    if job_name not in jobs:
        available = ", ".join(jobs.keys())
        raise ValueError(f"Unknown job '{job_name}'. Available: {available}")

    logger.info("running_job", job=job_name)
    result = await jobs[job_name]()
    logger.info("job_completed", job=job_name, result=result)
    return result


async def run_all_jobs() -> dict[str, str]:
    """Run all background jobs.

    Returns:
        Dictionary of job names to results
    """
    from mind.workers.standard.jobs import (
        cleanup_job,
        consolidation_job,
        expiration_job,
        pattern_detection_job,
        promotion_job,
    )

    results = {}

    for name, job in [
        ("consolidation", consolidation_job),
        ("expiration", expiration_job),
        ("promotion", promotion_job),
        ("pattern_detection", pattern_detection_job),
        ("cleanup", cleanup_job),
    ]:
        try:
            logger.info("running_job", job=name)
            result = await job()
            results[name] = result
            logger.info("job_completed", job=name, result=result)
        except Exception as e:
            results[name] = f"error: {e}"
            logger.error("job_failed", job=name, error=str(e))

    return results


async def get_job_status() -> list[dict]:
    """Get status of all scheduled jobs.

    Returns:
        List of job info dictionaries
    """
    from mind.container import get_container

    try:
        container = get_container()
        if container._worker_runner is not None:
            jobs = await container._worker_runner.list_jobs()
            return [
                {
                    "job_id": j.job_id,
                    "name": j.name,
                    "status": j.status.value,
                    "next_run": j.next_run.isoformat() if j.next_run else None,
                    "last_result": j.last_result,
                    "error_count": j.error_count,
                }
                for j in jobs
            ]
    except RuntimeError:
        # Container not initialized
        pass

    return []


def worker_command(
    action: str = "status",
    job_name: Optional[str] = None,
    run_all: bool = False,
) -> None:
    """Worker command handler.

    Args:
        action: Action to perform (status, run)
        job_name: Name of job to run (for run action)
        run_all: Run all jobs (for run action)
    """
    from mind.observability.logging import configure_logging

    configure_logging()

    if action == "status":
        print("\nScheduled Jobs Status")
        print("=" * 50)

        jobs = asyncio.run(get_job_status())
        if not jobs:
            print("No jobs scheduled (server may not be running)")
        else:
            for job in jobs:
                print(f"\n  {job['name']} ({job['job_id']})")
                print(f"    Status: {job['status']}")
                if job["next_run"]:
                    print(f"    Next run: {job['next_run']}")
                if job["last_result"]:
                    print(f"    Last result: {job['last_result']}")
                if job["error_count"]:
                    print(f"    Errors: {job['error_count']}")

    elif action == "run":
        if run_all:
            print("\nRunning all background jobs...")
            print("=" * 50)

            results = asyncio.run(run_all_jobs())
            for name, result in results.items():
                status = "OK" if not result.startswith("error:") else "FAILED"
                print(f"  {name}: {status} - {result}")

        elif job_name:
            print(f"\nRunning job: {job_name}")
            print("=" * 50)

            try:
                result = asyncio.run(run_job(job_name))
                print(f"  Result: {result}")
            except ValueError as e:
                print(f"  Error: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"  Failed: {e}")
                sys.exit(1)

        else:
            print("Error: Specify --job <name> or --all")
            print("\nAvailable jobs:")
            print("  - consolidation")
            print("  - expiration")
            print("  - promotion")
            print("  - pattern_detection")
            print("  - cleanup")
            sys.exit(1)

    else:
        print(f"Unknown action: {action}")
        print("Available actions: status, run")
        sys.exit(1)
