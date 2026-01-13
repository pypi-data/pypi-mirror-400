"""SQLAlchemy models for PostgreSQL."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class UserModel(Base):
    """User account."""

    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    memories: Mapped[list["MemoryModel"]] = relationship(back_populates="user")
    decision_traces: Mapped[list["DecisionTraceModel"]] = relationship(back_populates="user")


class EventModel(Base):
    """Append-only event store."""

    __tablename__ = "events"

    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.user_id"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    aggregate_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    event_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Tracing
    correlation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)
    causation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))

    # Timing
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    __table_args__ = (Index("idx_events_user_type_created", "user_id", "event_type", "created_at"),)


class MemoryModel(Base):
    """Hierarchical temporal memory."""

    __tablename__ = "memories"

    memory_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.user_id"), index=True
    )

    # Content
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))

    # Temporal level
    temporal_level: Mapped[int] = mapped_column(Integer)

    # Validity
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Salience
    base_salience: Mapped[float] = mapped_column(Float, default=1.0)
    outcome_adjustment: Mapped[float] = mapped_column(Float, default=0.0)

    # Usage stats
    retrieval_count: Mapped[int] = mapped_column(Integer, default=0)
    decision_count: Mapped[int] = mapped_column(Integer, default=0)
    positive_outcomes: Mapped[int] = mapped_column(Integer, default=0)
    negative_outcomes: Mapped[int] = mapped_column(Integer, default=0)

    # Promotion tracking
    promoted_from_level: Mapped[int | None] = mapped_column(Integer)
    promotion_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationship
    user: Mapped["UserModel"] = relationship(back_populates="memories")

    __table_args__ = (
        Index("idx_memories_user_level", "user_id", "temporal_level"),
        Index(
            "idx_memories_user_salience",
            "user_id",
            text("(base_salience + outcome_adjustment) DESC"),
        ),
        Index(
            "idx_memories_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    @property
    def effective_salience(self) -> float:
        """Calculate effective salience."""
        return max(0.0, min(1.0, self.base_salience + self.outcome_adjustment))


class DecisionTraceModel(Base):
    """Decision tracking for outcome learning."""

    __tablename__ = "decision_traces"

    trace_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.user_id"), index=True
    )
    session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Context snapshot
    context_memory_ids: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    memory_scores: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Decision
    decision_type: Mapped[str] = mapped_column(String(100))
    decision_summary: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    alternatives_count: Mapped[int] = mapped_column(Integer, default=0)

    # Outcome (filled async)
    outcome_observed: Mapped[bool] = mapped_column(Boolean, default=False)
    outcome_quality: Mapped[float | None] = mapped_column(Float)
    outcome_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    outcome_signal: Mapped[str | None] = mapped_column(String(100))

    # Attribution
    memory_attribution: Mapped[dict | None] = mapped_column(JSONB)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationship
    user: Mapped["UserModel"] = relationship(back_populates="decision_traces")

    __table_args__ = (
        Index("idx_traces_user_outcome", "user_id", "outcome_observed"),
        Index(
            "idx_traces_pending",
            "outcome_observed",
            postgresql_where=(~outcome_observed),
        ),
    )


class SalienceAdjustmentModel(Base):
    """Log of salience adjustments for auditing."""

    __tablename__ = "salience_adjustments"

    adjustment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    memory_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memories.memory_id"), index=True
    )
    trace_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("decision_traces.trace_id"), index=True
    )

    previous_adjustment: Mapped[float] = mapped_column(Float)
    new_adjustment: Mapped[float] = mapped_column(Float)
    delta: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class UserPreferencesModel(Base):
    """User preferences for memory extraction and other settings."""

    __tablename__ = "user_preferences"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True
    )
    memory_sensitivity: Mapped[str] = mapped_column(
        String(20), default="minimal"
    )  # minimal, balanced, detailed, everything

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SanitizedPatternModel(Base):
    """Federated patterns with differential privacy guarantees.

    These patterns are safe to share across users for collective learning
    without compromising individual privacy.
    """

    __tablename__ = "federated_patterns"

    pattern_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Pattern type and content (abstracted, not PII)
    pattern_type: Mapped[str] = mapped_column(String(50), index=True)
    trigger_category: Mapped[str] = mapped_column(String(100), index=True)
    response_strategy: Mapped[str] = mapped_column(Text)

    # Noised statistics (differential privacy applied)
    outcome_improvement: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)

    # Privacy guarantees
    source_count: Mapped[int] = mapped_column(Integer)
    user_count: Mapped[int] = mapped_column(Integer)
    epsilon: Mapped[float] = mapped_column(Float)

    # Validity and expiration
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Status for soft management
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    __table_args__ = (
        Index("idx_patterns_trigger_type", "trigger_category", "pattern_type"),
        Index(
            "idx_patterns_active_confidence",
            "is_active",
            "confidence",
            postgresql_where=(is_active),
        ),
    )
