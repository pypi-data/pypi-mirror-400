"""Interaction API schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RecordInteractionRequest(BaseModel):
    """Request to record a user interaction."""

    user_id: UUID = Field(..., description="User ID")
    session_id: UUID = Field(..., description="Session ID for grouping interactions")
    content: str = Field(..., description="The interaction content")
    interaction_type: str = Field(
        default="text",
        description="Type of interaction: text, voice_transcript, action, feedback, command",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (previous turns, current task, etc.)",
    )
    extraction_priority: str = Field(
        default="normal",
        description="Priority for memory extraction: immediate, normal, batch, skip",
    )
    skip_extraction: bool = Field(
        default=False,
        description="Set to true to skip memory extraction for this interaction",
    )


class RecordInteractionResponse(BaseModel):
    """Response after recording an interaction."""

    interaction_id: UUID = Field(..., description="Unique ID of the recorded interaction")
    user_id: UUID = Field(..., description="User ID")
    session_id: UUID = Field(..., description="Session ID")
    recorded_at: datetime = Field(..., description="When the interaction was recorded")
    extraction_queued: bool = Field(
        ..., description="Whether memory extraction was queued"
    )
