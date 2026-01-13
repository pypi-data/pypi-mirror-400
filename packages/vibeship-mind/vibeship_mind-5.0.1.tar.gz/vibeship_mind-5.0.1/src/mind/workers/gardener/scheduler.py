"""Scheduler for Temporal workflows.

This module manages Temporal schedules that trigger the gardening
workflows on a regular basis.

Usage:
    # Create or update schedules
    python -m mind.workers.gardener.scheduler setup

    # Remove all schedules
    python -m mind.workers.gardener.scheduler teardown

    # List current schedules
    python -m mind.workers.gardener.scheduler list
"""

import asyncio
from dataclasses import dataclass
from datetime import timedelta

import structlog
from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleIntervalSpec,
    ScheduleSpec,
    ScheduleState,
)

from mind.infrastructure.temporal.client import get_temporal_client
from mind.workers.gardener.workflows import (
    AnalyzeOutcomesWorkflow,
    AnalyzeOutcomesWorkflowInput,
    CalibrateConfidenceWorkflow,
    CalibrateConfidenceWorkflowInput,
    ExtractPatternsWorkflow,
    ExtractPatternsWorkflowInput,
    ScheduledGardenerInput,
    ScheduledGardenerWorkflow,
)

logger = structlog.get_logger()

TASK_QUEUE = "gardener"


@dataclass
class ScheduleConfig:
    """Configuration for a workflow schedule."""

    schedule_id: str
    description: str
    interval: timedelta
    workflow_type: str
    workflow_args: list
    paused: bool = False


# Default schedules for gardening workflows
DEFAULT_SCHEDULES = [
    ScheduleConfig(
        schedule_id="gardener-daily",
        description="Daily memory maintenance (promotion, expiration, consolidation)",
        interval=timedelta(hours=24),
        workflow_type="ScheduledGardenerWorkflow",
        workflow_args=[],  # Will discover users dynamically
    ),
    ScheduleConfig(
        schedule_id="analyze-outcomes-weekly",
        description="Weekly outcome analysis and salience adjustments",
        interval=timedelta(days=7),
        workflow_type="AnalyzeOutcomesWorkflow",
        workflow_args=[],  # Will process all users
    ),
    ScheduleConfig(
        schedule_id="calibrate-confidence-monthly",
        description="Monthly confidence calibration",
        interval=timedelta(days=30),
        workflow_type="CalibrateConfidenceWorkflow",
        workflow_args=[],
    ),
    ScheduleConfig(
        schedule_id="extract-patterns-monthly",
        description="Monthly pattern extraction for federation",
        interval=timedelta(days=30),
        workflow_type="ExtractPatternsWorkflow",
        workflow_args=[],
    ),
]


async def setup_schedules(
    client: Client | None = None,
    schedules: list[ScheduleConfig] | None = None,
) -> list[str]:
    """Create or update Temporal schedules.

    Args:
        client: Temporal client (will create one if not provided)
        schedules: List of schedules to create (uses defaults if not provided)

    Returns:
        List of schedule IDs that were created/updated
    """
    if client is None:
        client = await get_temporal_client()

    if schedules is None:
        schedules = DEFAULT_SCHEDULES

    created = []

    for config in schedules:
        try:
            # Build the schedule action based on workflow type
            action = _build_schedule_action(config)

            # Create schedule spec with interval
            spec = ScheduleSpec(intervals=[ScheduleIntervalSpec(every=config.interval)])

            # Create or update the schedule
            try:
                # Try to get existing schedule
                handle = client.get_schedule_handle(config.schedule_id)
                await handle.update(
                    lambda _: Schedule(
                        action=action,
                        spec=spec,
                        state=ScheduleState(
                            paused=config.paused,
                            note=config.description,
                        ),
                    )
                )
                logger.info(
                    "schedule_updated",
                    schedule_id=config.schedule_id,
                    interval=str(config.interval),
                )
            except Exception:
                # Schedule doesn't exist, create it
                await client.create_schedule(
                    config.schedule_id,
                    Schedule(
                        action=action,
                        spec=spec,
                        state=ScheduleState(
                            paused=config.paused,
                            note=config.description,
                        ),
                    ),
                )
                logger.info(
                    "schedule_created",
                    schedule_id=config.schedule_id,
                    interval=str(config.interval),
                )

            created.append(config.schedule_id)

        except Exception as e:
            logger.error(
                "schedule_setup_failed",
                schedule_id=config.schedule_id,
                error=str(e),
            )

    return created


def _build_schedule_action(config: ScheduleConfig) -> ScheduleActionStartWorkflow:
    """Build the schedule action for a workflow configuration."""
    workflow_id = f"{config.schedule_id}-{{{{.ScheduledTime.Format `2006-01-02T15:04:05`}}}}"

    if config.workflow_type == "ScheduledGardenerWorkflow":
        return ScheduleActionStartWorkflow(
            ScheduledGardenerWorkflow.run,
            args=[ScheduledGardenerInput()],  # Auto-discover users
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
    elif config.workflow_type == "AnalyzeOutcomesWorkflow":
        return ScheduleActionStartWorkflow(
            AnalyzeOutcomesWorkflow.run,
            args=[AnalyzeOutcomesWorkflowInput(user_id=None)],  # All users
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
    elif config.workflow_type == "CalibrateConfidenceWorkflow":
        return ScheduleActionStartWorkflow(
            CalibrateConfidenceWorkflow.run,
            args=[CalibrateConfidenceWorkflowInput(user_id=None)],  # All users
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
    elif config.workflow_type == "ExtractPatternsWorkflow":
        return ScheduleActionStartWorkflow(
            ExtractPatternsWorkflow.run,
            args=[ExtractPatternsWorkflowInput(user_id=None)],  # All users
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
    else:
        raise ValueError(f"Unknown workflow type: {config.workflow_type}")


async def teardown_schedules(
    client: Client | None = None,
    schedule_ids: list[str] | None = None,
) -> list[str]:
    """Remove Temporal schedules.

    Args:
        client: Temporal client (will create one if not provided)
        schedule_ids: List of schedule IDs to remove (removes defaults if not provided)

    Returns:
        List of schedule IDs that were removed
    """
    if client is None:
        client = await get_temporal_client()

    if schedule_ids is None:
        schedule_ids = [s.schedule_id for s in DEFAULT_SCHEDULES]

    removed = []

    for schedule_id in schedule_ids:
        try:
            handle = client.get_schedule_handle(schedule_id)
            await handle.delete()
            logger.info("schedule_deleted", schedule_id=schedule_id)
            removed.append(schedule_id)
        except Exception as e:
            logger.warning(
                "schedule_delete_failed",
                schedule_id=schedule_id,
                error=str(e),
            )

    return removed


async def list_schedules(client: Client | None = None) -> list[dict]:
    """List all gardening schedules.

    Args:
        client: Temporal client (will create one if not provided)

    Returns:
        List of schedule info dicts
    """
    if client is None:
        client = await get_temporal_client()

    schedules = []

    for config in DEFAULT_SCHEDULES:
        try:
            handle = client.get_schedule_handle(config.schedule_id)
            desc = await handle.describe()

            schedules.append(
                {
                    "schedule_id": config.schedule_id,
                    "description": config.description,
                    "paused": desc.schedule.state.paused if desc.schedule.state else False,
                    "running_workflows": desc.info.num_actions if desc.info else 0,
                    "next_action_time": str(desc.info.next_action_times[0])
                    if desc.info and desc.info.next_action_times
                    else None,
                    "last_action_time": str(desc.info.recent_actions[-1].schedule_time)
                    if desc.info and desc.info.recent_actions
                    else None,
                }
            )
        except Exception:
            schedules.append(
                {
                    "schedule_id": config.schedule_id,
                    "description": config.description,
                    "status": "not_created",
                }
            )

    return schedules


async def pause_schedule(
    schedule_id: str,
    client: Client | None = None,
) -> bool:
    """Pause a schedule.

    Args:
        schedule_id: The schedule to pause
        client: Temporal client (will create one if not provided)

    Returns:
        True if successful
    """
    if client is None:
        client = await get_temporal_client()

    handle = client.get_schedule_handle(schedule_id)
    await handle.pause(note="Paused via scheduler API")
    logger.info("schedule_paused", schedule_id=schedule_id)
    return True


async def unpause_schedule(
    schedule_id: str,
    client: Client | None = None,
) -> bool:
    """Unpause a schedule.

    Args:
        schedule_id: The schedule to unpause
        client: Temporal client (will create one if not provided)

    Returns:
        True if successful
    """
    if client is None:
        client = await get_temporal_client()

    handle = client.get_schedule_handle(schedule_id)
    await handle.unpause(note="Unpaused via scheduler API")
    logger.info("schedule_unpaused", schedule_id=schedule_id)
    return True


async def trigger_schedule(
    schedule_id: str,
    client: Client | None = None,
) -> bool:
    """Trigger a schedule to run immediately.

    Args:
        schedule_id: The schedule to trigger
        client: Temporal client (will create one if not provided)

    Returns:
        True if successful
    """
    if client is None:
        client = await get_temporal_client()

    handle = client.get_schedule_handle(schedule_id)
    await handle.trigger()
    logger.info("schedule_triggered", schedule_id=schedule_id)
    return True


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m mind.workers.gardener.scheduler <command>")
        print("Commands: setup, teardown, list, pause <id>, unpause <id>, trigger <id>")
        sys.exit(1)

    command = sys.argv[1]

    async def run():
        if command == "setup":
            created = await setup_schedules()
            print(f"Created/updated {len(created)} schedules: {created}")

        elif command == "teardown":
            removed = await teardown_schedules()
            print(f"Removed {len(removed)} schedules: {removed}")

        elif command == "list":
            schedules = await list_schedules()
            for s in schedules:
                print(f"\n{s['schedule_id']}:")
                for k, v in s.items():
                    if k != "schedule_id":
                        print(f"  {k}: {v}")

        elif command == "pause" and len(sys.argv) > 2:
            await pause_schedule(sys.argv[2])
            print(f"Paused {sys.argv[2]}")

        elif command == "unpause" and len(sys.argv) > 2:
            await unpause_schedule(sys.argv[2])
            print(f"Unpaused {sys.argv[2]}")

        elif command == "trigger" and len(sys.argv) > 2:
            await trigger_schedule(sys.argv[2])
            print(f"Triggered {sys.argv[2]}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    asyncio.run(run())


if __name__ == "__main__":
    main()
