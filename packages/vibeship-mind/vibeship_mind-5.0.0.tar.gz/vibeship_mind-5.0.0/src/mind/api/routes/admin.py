"""Admin endpoints for Mind v5.

Provides administrative operations requiring elevated permissions:
- System status and diagnostics
- Dead letter queue management
- Event replay operations
- Pattern effectiveness overview
- User scope management
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from mind.security.auth import AuthenticatedUser
from mind.security.scopes import (
    require_admin,
    require_admin_dlq,
    require_admin_replay,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# Response Models
# =============================================================================


class SystemStatusResponse(BaseModel):
    """Detailed system status."""

    status: str
    version: str
    environment: str
    uptime_seconds: float
    components: dict[str, str]
    metrics_summary: dict[str, float]


class DLQStatsResponse(BaseModel):
    """Dead letter queue statistics."""

    stream: str
    message_count: int
    oldest_sequence: int | None = None
    oldest_message_age_seconds: float = 0.0
    bytes: int = 0
    error: str | None = None


class DLQMessageResponse(BaseModel):
    """A message from the DLQ."""

    sequence: int
    subject: str
    original_subject: str
    consumer: str
    errors: str
    failed_at: str
    attempts: int
    data: dict


class DLQListResponse(BaseModel):
    """List of DLQ messages."""

    messages: list[DLQMessageResponse]
    total: int


class ReplayRequest(BaseModel):
    """Request to replay a DLQ message."""

    sequence: int


class ReplayResponse(BaseModel):
    """Result of a replay operation."""

    success: bool
    sequence: int
    message: str


class ReplayAllResponse(BaseModel):
    """Result of replay-all operation."""

    replayed_count: int
    failed_count: int


class EventStreamInfoResponse(BaseModel):
    """Event stream information."""

    stream: str
    message_count: int
    first_sequence: int | None = None
    last_sequence: int | None = None
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    bytes: int = 0
    consumer_count: int = 0
    error: str | None = None


class EventReplayRequest(BaseModel):
    """Request to replay events."""

    from_sequence: int | None = None
    to_sequence: int | None = None
    event_types: list[str] | None = None
    max_events: int | None = Field(default=1000, le=10000)
    dry_run: bool = True


class EventReplayResponse(BaseModel):
    """Result of event replay."""

    processed_events: int
    failed_events: int
    skipped_events: int
    elapsed_seconds: float
    events_per_second: float
    dry_run: bool


class PatternEffectivenessResponse(BaseModel):
    """Pattern effectiveness summary."""

    total_patterns_tracked: int
    total_usages: int
    outcomes_recorded: int
    average_success_rate: float
    average_improvement: float
    declining_patterns: int
    deprecated_patterns: int


class UserScopesResponse(BaseModel):
    """User scopes information."""

    user_id: str
    scopes: list[str]
    expanded_scopes: list[str]


# =============================================================================
# Startup time tracking
# =============================================================================

_startup_time = datetime.now(UTC)


# =============================================================================
# System Status Endpoints
# =============================================================================


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    user: AuthenticatedUser = Depends(require_admin),
) -> SystemStatusResponse:
    """Get detailed system status.

    Requires: admin scope
    """
    from mind.config import get_settings
    from mind.infrastructure.nats.client import _nats_client
    from mind.infrastructure.postgres.database import get_database

    settings = get_settings()

    # Check components
    components = {}

    # Database
    try:
        db = get_database()
        async with db.session() as session:
            await session.execute("SELECT 1")
        components["database"] = "healthy"
    except Exception as e:
        components["database"] = f"unhealthy: {e}"

    # NATS
    if _nats_client and _nats_client.is_connected:
        components["nats"] = "healthy"
    else:
        components["nats"] = "disconnected"

    # Calculate uptime
    uptime = (datetime.now(UTC) - _startup_time).total_seconds()

    return SystemStatusResponse(
        status="healthy" if all("healthy" in v for v in components.values()) else "degraded",
        version="5.0.0",
        environment=settings.environment,
        uptime_seconds=uptime,
        components=components,
        metrics_summary={
            "uptime_seconds": uptime,
        },
    )


# =============================================================================
# Dead Letter Queue Endpoints
# =============================================================================


@router.get("/dlq/stats", response_model=DLQStatsResponse)
async def get_dlq_stats(
    user: AuthenticatedUser = Depends(require_admin_dlq),
) -> DLQStatsResponse:
    """Get DLQ statistics.

    Requires: admin:dlq scope
    """
    from mind.infrastructure.nats.dlq import get_dlq_stats

    stats = await get_dlq_stats()

    return DLQStatsResponse(**stats)


@router.get("/dlq/messages", response_model=DLQListResponse)
async def list_dlq_messages(
    limit: int = Query(default=50, le=500),
    user: AuthenticatedUser = Depends(require_admin_dlq),
) -> DLQListResponse:
    """List messages in the DLQ.

    Requires: admin:dlq scope
    """
    from mind.infrastructure.nats.dlq import list_dlq_messages

    messages = await list_dlq_messages(limit=limit)

    return DLQListResponse(
        messages=[
            DLQMessageResponse(
                sequence=msg.sequence,
                subject=msg.subject,
                original_subject=msg.original_subject,
                consumer=msg.consumer,
                errors=msg.errors,
                failed_at=msg.failed_at,
                attempts=msg.attempts,
                data=msg.data,
            )
            for msg in messages
        ],
        total=len(messages),
    )


@router.get("/dlq/messages/{sequence}", response_model=DLQMessageResponse)
async def get_dlq_message(
    sequence: int,
    user: AuthenticatedUser = Depends(require_admin_dlq),
) -> DLQMessageResponse:
    """Get a specific DLQ message.

    Requires: admin:dlq scope
    """
    from mind.infrastructure.nats.dlq import inspect_dlq_message

    msg = await inspect_dlq_message(sequence)

    if msg is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {sequence} not found in DLQ",
        )

    return DLQMessageResponse(
        sequence=msg.sequence,
        subject=msg.subject,
        original_subject=msg.original_subject,
        consumer=msg.consumer,
        errors=msg.errors,
        failed_at=msg.failed_at,
        attempts=msg.attempts,
        data=msg.data,
    )


@router.post("/dlq/replay/{sequence}", response_model=ReplayResponse)
async def replay_dlq_message(
    sequence: int,
    user: AuthenticatedUser = Depends(require_admin_dlq),
) -> ReplayResponse:
    """Replay a specific DLQ message.

    Requires: admin:dlq scope
    """
    from mind.infrastructure.nats.dlq import replay_dlq_message

    success = await replay_dlq_message(sequence)

    return ReplayResponse(
        success=success,
        sequence=sequence,
        message="Message replayed successfully" if success else "Failed to replay message",
    )


@router.post("/dlq/replay-all", response_model=ReplayAllResponse)
async def replay_all_dlq_messages(
    limit: int = Query(default=100, le=1000),
    user: AuthenticatedUser = Depends(require_admin_dlq),
) -> ReplayAllResponse:
    """Replay all DLQ messages.

    Requires: admin:dlq scope
    """
    from mind.infrastructure.nats.dlq import replay_all_dlq_messages

    result = await replay_all_dlq_messages(limit=limit)

    return ReplayAllResponse(**result)


# =============================================================================
# Event Stream Endpoints
# =============================================================================


@router.get("/events/info", response_model=EventStreamInfoResponse)
async def get_event_stream_info(
    user: AuthenticatedUser = Depends(require_admin_replay),
) -> EventStreamInfoResponse:
    """Get event stream information.

    Requires: admin:replay scope
    """
    from mind.infrastructure.nats.replay import get_stream_info

    info = await get_stream_info()

    return EventStreamInfoResponse(**info)


@router.post("/events/replay", response_model=EventReplayResponse)
async def replay_events(
    request: EventReplayRequest,
    user: AuthenticatedUser = Depends(require_admin_replay),
) -> EventReplayResponse:
    """Replay events from the event stream.

    This is a dry-run by default. Set dry_run=false to actually process events.

    Requires: admin:replay scope
    """
    from mind.core.events.base import EventType
    from mind.infrastructure.nats.client import get_nats_client
    from mind.infrastructure.nats.replay import EventReplayer, ReplayConfig

    # Build config
    event_types = None
    if request.event_types:
        try:
            event_types = [EventType(et) for et in request.event_types]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {e}",
            )

    config = ReplayConfig(
        from_sequence=request.from_sequence,
        to_sequence=request.to_sequence,
        event_types=event_types,
        max_events=request.max_events,
        dry_run=request.dry_run,
    )

    client = await get_nats_client()
    replayer = EventReplayer(client, config)

    # For non-dry-run, we'd register actual handlers here
    # For now, just count events

    progress = await replayer.replay()

    return EventReplayResponse(
        processed_events=progress.processed_events,
        failed_events=progress.failed_events,
        skipped_events=progress.skipped_events,
        elapsed_seconds=progress.elapsed_seconds,
        events_per_second=progress.events_per_second,
        dry_run=request.dry_run,
    )


# =============================================================================
# Pattern Effectiveness Endpoints
# =============================================================================


@router.get("/patterns/effectiveness", response_model=PatternEffectivenessResponse)
async def get_pattern_effectiveness(
    user: AuthenticatedUser = Depends(require_admin),
) -> PatternEffectivenessResponse:
    """Get pattern effectiveness summary.

    Requires: admin scope
    """
    from mind.core.federation.effectiveness import get_effectiveness_tracker

    tracker = get_effectiveness_tracker()
    stats = tracker.get_stats()

    return PatternEffectivenessResponse(**stats)


# =============================================================================
# User Scope Endpoints
# =============================================================================


@router.get("/scopes/check", response_model=UserScopesResponse)
async def check_my_scopes(
    user: AuthenticatedUser = Depends(require_admin),
) -> UserScopesResponse:
    """Check authenticated user's scopes.

    Requires: admin scope
    """
    from mind.security.scopes import expand_scopes

    expanded = expand_scopes(user.scopes)

    return UserScopesResponse(
        user_id=str(user.user_id),
        scopes=user.scopes,
        expanded_scopes=sorted(expanded),
    )
