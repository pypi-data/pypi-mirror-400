"""Interaction events for Mind v5.

InteractionRecorded is the foundational event that captures raw user
interactions. All memories are extracted from these interactions.

Flow:
    User Input → InteractionRecorded → MemoryExtractor → MemoryCreated
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .base import Event, EventType


class InteractionType(str, Enum):
    """Types of user interactions."""

    TEXT = "text"  # Regular text message
    VOICE_TRANSCRIPT = "voice_transcript"  # Transcribed voice
    ACTION = "action"  # User action (clicked, selected, etc.)
    FEEDBACK = "feedback"  # Explicit feedback (thumbs up/down)
    COMMAND = "command"  # System command (/remember, etc.)


class ExtractionPriority(str, Enum):
    """Priority for memory extraction processing."""

    IMMEDIATE = "immediate"  # Extract now (explicit commands)
    NORMAL = "normal"  # Standard queue processing
    BATCH = "batch"  # Can wait for batch processing
    SKIP = "skip"  # No extraction needed


class InteractionRecorded(Event):
    """Event published when a user interaction is recorded.

    This is the source of truth for all user inputs. Memory extraction
    consumes these events to create memories.

    Privacy Note:
        Content may be encrypted in metadata.contains_pii scenarios.
        The extractor handles decryption with user's key.
    """

    # Identity
    interaction_id: UUID = Field(default_factory=uuid4)
    session_id: UUID

    # Content
    interaction_type: InteractionType = InteractionType.TEXT
    content: str  # The raw interaction content
    content_length: int = 0  # For analytics without reading content

    # Context (helps extraction)
    context: dict[str, Any] = Field(default_factory=dict)
    # Example context:
    # {
    #     "previous_turns": ["What tech stack?", "I recommend TypeScript"],
    #     "current_task": "API design",
    #     "tools_used": ["mind_retrieve"],
    # }

    # Processing hints
    extraction_priority: ExtractionPriority = ExtractionPriority.NORMAL
    requires_response: bool = True
    skip_extraction: bool = False  # True for system messages

    # Timing
    client_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_type(self) -> EventType:
        return EventType.INTERACTION_RECORDED

    @property
    def aggregate_id(self) -> UUID:
        return self.interaction_id

    def __post_init__(self):
        if self.content_length == 0:
            self.content_length = len(self.content)


class InteractionContext(BaseModel):
    """Context passed to memory extraction.

    Provides the extractor with conversation context to make
    better extraction decisions.
    """

    # Conversation history (last N turns)
    previous_turns: list[dict[str, str]] = Field(default_factory=list)
    # Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    # Current state
    current_task: str | None = None
    tools_used: list[str] = Field(default_factory=list)
    memories_retrieved: list[UUID] = Field(default_factory=list)

    # Session info
    session_start: datetime | None = None
    interaction_count: int = 0


class ExtractionResult(BaseModel):
    """Result of memory extraction from an interaction.

    The MemoryExtractor produces this, which is then used to
    create MemoryCreated events.
    """

    # Source
    interaction_id: UUID
    extraction_model: str = "claude-3-haiku"  # Model used for extraction

    # Extracted memories
    memories: list["ExtractedMemory"] = Field(default_factory=list)

    # Metadata
    extraction_time_ms: float = 0
    tokens_used: int = 0
    extraction_confidence: float = 0.0


class ExtractedMemory(BaseModel):
    """A single memory extracted from an interaction.

    This intermediate representation is converted to a full
    Memory entity with embeddings and graph links.
    """

    # Content
    content: str
    content_type: str = "observation"  # fact, preference, goal, skill, project, pattern, observation

    # Classification
    temporal_level: int = 2  # 1=immediate, 2=situational, 3=seasonal, 4=identity
    suggested_salience: float = 0.8

    # Reasoning
    extraction_reasoning: str = ""  # Why this was extracted
    confidence: float = 0.8  # 1.0=explicit, 0.8=strong inference, 0.6=reasonable, 0.4=weak
    source: str = "inferred"  # "direct statement", "inferred from context", "observed behavior"

    # Entity hints (for graph linking)
    entity_mentions: list[str] = Field(default_factory=list)
    # e.g., ["TypeScript", "API design", "REST"]

    # Relationship hints (for knowledge graph)
    related_to: list[str] = Field(default_factory=list)
    # e.g., ["Python", "FastAPI"] - entities this memory relates to
