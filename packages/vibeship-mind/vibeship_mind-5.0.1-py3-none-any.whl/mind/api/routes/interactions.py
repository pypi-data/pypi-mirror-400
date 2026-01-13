"""Interaction recording API endpoints."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException

from mind.api.schemas.interaction import (
    RecordInteractionRequest,
    RecordInteractionResponse,
)
from mind.config import get_settings
from mind.core.events.interaction import ExtractionPriority, InteractionType
from mind.security.auth import AuthenticatedUser, get_auth_dependency
from mind.services.events import get_event_service

logger = structlog.get_logger()
router = APIRouter()


def _validate_user_access(
    request_user_id: UUID,
    authenticated_user: AuthenticatedUser | None,
) -> None:
    """Validate that authenticated user can access the requested user's data."""
    settings = get_settings()

    if settings.environment != "production" and not settings.require_auth:
        return

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if authenticated_user.user_id != request_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's data")


def _parse_interaction_type(type_str: str) -> InteractionType:
    """Parse interaction type string to enum."""
    type_map = {
        "text": InteractionType.TEXT,
        "voice_transcript": InteractionType.VOICE_TRANSCRIPT,
        "action": InteractionType.ACTION,
        "feedback": InteractionType.FEEDBACK,
        "command": InteractionType.COMMAND,
    }
    return type_map.get(type_str, InteractionType.TEXT)


def _parse_extraction_priority(priority_str: str) -> ExtractionPriority:
    """Parse extraction priority string to enum."""
    priority_map = {
        "immediate": ExtractionPriority.IMMEDIATE,
        "normal": ExtractionPriority.NORMAL,
        "batch": ExtractionPriority.BATCH,
        "skip": ExtractionPriority.SKIP,
    }
    return priority_map.get(priority_str, ExtractionPriority.NORMAL)


@router.post("/record", response_model=RecordInteractionResponse, status_code=201)
async def record_interaction(
    request: RecordInteractionRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> RecordInteractionResponse:
    """Record a user interaction for memory extraction.

    This endpoint records raw user interactions. The MemoryExtractor
    consumer will process these events and extract relevant memories.

    Flow:
        API receives interaction → Publishes InteractionRecorded event →
        MemoryExtractor processes → Creates Memory entities

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    log = logger.bind(
        user_id=str(request.user_id),
        session_id=str(request.session_id),
        content_length=len(request.content),
    )

    # Parse enums
    interaction_type = _parse_interaction_type(request.interaction_type)
    extraction_priority = _parse_extraction_priority(request.extraction_priority)

    # Publish InteractionRecorded event
    event_service = get_event_service()
    result = await event_service.publish_interaction_recorded(
        user_id=request.user_id,
        session_id=request.session_id,
        content=request.content,
        interaction_type=interaction_type,
        context=request.context,
        extraction_priority=extraction_priority,
        skip_extraction=request.skip_extraction,
    )

    if not result.is_ok:
        log.error("interaction_record_failed", error=str(result.error))
        raise HTTPException(status_code=500, detail="Failed to record interaction")

    # Determine if extraction was queued
    extraction_queued = (
        not request.skip_extraction
        and extraction_priority != ExtractionPriority.SKIP
        and len(request.content.strip()) >= 10
    )

    from uuid import uuid4

    response = RecordInteractionResponse(
        interaction_id=uuid4(),  # Generated in event, but we return a new one for response
        user_id=request.user_id,
        session_id=request.session_id,
        recorded_at=datetime.now(UTC),
        extraction_queued=extraction_queued,
    )

    log.info(
        "interaction_recorded",
        interaction_type=request.interaction_type,
        extraction_queued=extraction_queued,
    )

    return response
