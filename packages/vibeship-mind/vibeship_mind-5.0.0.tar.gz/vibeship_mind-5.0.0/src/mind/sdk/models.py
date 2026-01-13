"""Mind SDK data models.

These models are used by the SDK client for type-safe interactions.
They mirror the API schemas but are simplified for SDK usage.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from uuid import UUID


class TemporalLevel(IntEnum):
    """Temporal hierarchy levels for memories.

    1. IMMEDIATE (hours): Current session context
    2. SITUATIONAL (days-weeks): Recent patterns
    3. SEASONAL (months): Recurring patterns
    4. IDENTITY (years): Core preferences
    """

    IMMEDIATE = 1
    SITUATIONAL = 2
    SEASONAL = 3
    IDENTITY = 4


@dataclass
class Memory:
    """A memory retrieved from Mind."""

    memory_id: UUID
    user_id: UUID
    content: str
    content_type: str
    temporal_level: int
    temporal_level_name: str
    effective_salience: float
    retrieval_count: int
    decision_count: int
    positive_outcomes: int
    negative_outcomes: int
    valid_from: datetime
    valid_until: datetime | None
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        """Create Memory from API response dict."""
        return cls(
            memory_id=UUID(data["memory_id"])
            if isinstance(data["memory_id"], str)
            else data["memory_id"],
            user_id=UUID(data["user_id"]) if isinstance(data["user_id"], str) else data["user_id"],
            content=data["content"],
            content_type=data["content_type"],
            temporal_level=data["temporal_level"],
            temporal_level_name=data["temporal_level_name"],
            effective_salience=data["effective_salience"],
            retrieval_count=data["retrieval_count"],
            decision_count=data["decision_count"],
            positive_outcomes=data["positive_outcomes"],
            negative_outcomes=data["negative_outcomes"],
            valid_from=datetime.fromisoformat(data["valid_from"].replace("Z", "+00:00"))
            if isinstance(data["valid_from"], str)
            else data["valid_from"],
            valid_until=datetime.fromisoformat(data["valid_until"].replace("Z", "+00:00"))
            if data.get("valid_until") and isinstance(data["valid_until"], str)
            else data.get("valid_until"),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            if isinstance(data["created_at"], str)
            else data["created_at"],
        )


@dataclass
class RetrievalResult:
    """Result of a memory retrieval operation."""

    retrieval_id: UUID
    memories: list[Memory]
    scores: dict[str, float]  # memory_id -> score
    latency_ms: float

    @classmethod
    def from_dict(cls, data: dict) -> "RetrievalResult":
        """Create RetrievalResult from API response dict."""
        return cls(
            retrieval_id=UUID(data["retrieval_id"])
            if isinstance(data["retrieval_id"], str)
            else data["retrieval_id"],
            memories=[Memory.from_dict(m) for m in data["memories"]],
            scores=data["scores"],
            latency_ms=data["latency_ms"],
        )


@dataclass
class DecisionTrace:
    """A tracked decision with associated memories."""

    trace_id: UUID
    user_id: UUID
    session_id: UUID
    memory_ids: list[UUID]
    memory_scores: dict[str, float]
    decision_type: str
    decision_summary: str
    confidence: float
    alternatives_count: int
    created_at: datetime
    outcome_observed: bool = False
    outcome_quality: float | None = None
    outcome_timestamp: datetime | None = None
    outcome_signal: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "DecisionTrace":
        """Create DecisionTrace from API response dict."""
        return cls(
            trace_id=UUID(data["trace_id"])
            if isinstance(data["trace_id"], str)
            else data["trace_id"],
            user_id=UUID(data["user_id"]) if isinstance(data["user_id"], str) else data["user_id"],
            session_id=UUID(data["session_id"])
            if isinstance(data["session_id"], str)
            else data["session_id"],
            memory_ids=[UUID(m) if isinstance(m, str) else m for m in data["memory_ids"]],
            memory_scores=data["memory_scores"],
            decision_type=data["decision_type"],
            decision_summary=data["decision_summary"],
            confidence=data["confidence"],
            alternatives_count=data["alternatives_count"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            if isinstance(data["created_at"], str)
            else data["created_at"],
            outcome_observed=data.get("outcome_observed", False),
            outcome_quality=data.get("outcome_quality"),
            outcome_timestamp=datetime.fromisoformat(
                data["outcome_timestamp"].replace("Z", "+00:00")
            )
            if data.get("outcome_timestamp") and isinstance(data["outcome_timestamp"], str)
            else data.get("outcome_timestamp"),
            outcome_signal=data.get("outcome_signal"),
        )


@dataclass
class OutcomeResult:
    """Result of recording an outcome."""

    trace_id: UUID
    outcome_quality: float
    memories_updated: int
    salience_changes: dict[str, float]  # memory_id -> delta

    @classmethod
    def from_dict(cls, data: dict) -> "OutcomeResult":
        """Create OutcomeResult from API response dict."""
        return cls(
            trace_id=UUID(data["trace_id"])
            if isinstance(data["trace_id"], str)
            else data["trace_id"],
            outcome_quality=data["outcome_quality"],
            memories_updated=data["memories_updated"],
            salience_changes=data["salience_changes"],
        )


@dataclass
class TrackResult:
    """Result of tracking a decision."""

    trace_id: UUID
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "TrackResult":
        """Create TrackResult from API response dict."""
        return cls(
            trace_id=UUID(data["trace_id"])
            if isinstance(data["trace_id"], str)
            else data["trace_id"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            if isinstance(data["created_at"], str)
            else data["created_at"],
        )
