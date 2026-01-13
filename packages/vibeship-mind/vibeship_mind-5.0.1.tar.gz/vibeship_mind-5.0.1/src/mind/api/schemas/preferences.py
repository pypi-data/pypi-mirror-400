"""User preferences API schemas."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


MemorySensitivity = Literal["minimal", "balanced", "detailed", "everything"]


class UserPreferencesRequest(BaseModel):
    """Request to update user preferences."""

    user_id: UUID = Field(..., description="User ID")
    memory_sensitivity: MemorySensitivity = Field(
        "minimal",
        description="Memory sensitivity level",
    )


class UserPreferencesResponse(BaseModel):
    """User preferences response."""

    user_id: UUID
    memory_sensitivity: MemorySensitivity = "minimal"
    updated_at: str | None = None


class UpdatePreferencesResponse(BaseModel):
    """Response after updating preferences."""

    success: bool
    message: str
    preferences: UserPreferencesResponse
