"""User preferences API endpoints."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from mind.api.schemas.preferences import (
    MemorySensitivity,
    UpdatePreferencesResponse,
    UserPreferencesRequest,
    UserPreferencesResponse,
)
from mind.config import get_settings
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.models import UserPreferencesModel
from mind.infrastructure.postgres.repositories import ensure_user_exists
from mind.security.auth import AuthenticatedUser, get_auth_dependency

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


@router.post("", response_model=UpdatePreferencesResponse)
async def update_preferences(
    request: UserPreferencesRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> UpdatePreferencesResponse:
    """Update user preferences.

    Stores user preferences including memory sensitivity level.
    Persists to database for durability.
    """
    _validate_user_access(request.user_id, user)

    db = get_database()
    async with db.session() as session:
        # Ensure user exists
        await ensure_user_exists(session, request.user_id)

        # Check if preferences exist
        stmt = select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == request.user_id
        )
        result = await session.execute(stmt)
        prefs = result.scalar_one_or_none()

        now = datetime.now(UTC)

        if prefs:
            # Update existing
            prefs.memory_sensitivity = request.memory_sensitivity
            prefs.updated_at = now
        else:
            # Create new
            prefs = UserPreferencesModel(
                user_id=request.user_id,
                memory_sensitivity=request.memory_sensitivity,
                created_at=now,
                updated_at=now,
            )
            session.add(prefs)

        await session.commit()

    logger.info(
        "preferences_updated",
        user_id=str(request.user_id),
        memory_sensitivity=request.memory_sensitivity,
    )

    return UpdatePreferencesResponse(
        success=True,
        message=f"Memory sensitivity set to {request.memory_sensitivity}",
        preferences=UserPreferencesResponse(
            user_id=request.user_id,
            memory_sensitivity=request.memory_sensitivity,
            updated_at=now.isoformat(),
        ),
    )


@router.get("/{user_id}", response_model=UserPreferencesResponse)
async def get_preferences(
    user_id: UUID,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> UserPreferencesResponse:
    """Get user preferences.

    Returns user preferences including memory sensitivity level.
    Defaults to 'minimal' if not set.
    """
    _validate_user_access(user_id, user)

    db = get_database()
    async with db.session() as session:
        stmt = select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user_id
        )
        result = await session.execute(stmt)
        prefs = result.scalar_one_or_none()

        if prefs:
            return UserPreferencesResponse(
                user_id=prefs.user_id,
                memory_sensitivity=prefs.memory_sensitivity,
                updated_at=prefs.updated_at.isoformat() if prefs.updated_at else None,
            )

    # Return defaults if no preferences set
    return UserPreferencesResponse(
        user_id=user_id,
        memory_sensitivity="minimal",
        updated_at=None,
    )


async def get_user_sensitivity(user_id: UUID) -> MemorySensitivity:
    """Get user's memory sensitivity setting from database.

    Used by other services (like memory extractor) to get the setting.
    """
    db = get_database()
    async with db.session() as session:
        stmt = select(UserPreferencesModel.memory_sensitivity).where(
            UserPreferencesModel.user_id == user_id
        )
        result = await session.execute(stmt)
        sensitivity = result.scalar_one_or_none()

        if sensitivity and sensitivity in ("minimal", "balanced", "detailed", "everything"):
            return sensitivity

    return "minimal"
