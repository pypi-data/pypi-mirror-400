"""Data retention policy models for Mind v5.

Defines the data structures for configuring and tracking
data retention policies across different data types.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID


class DataType(str, Enum):
    """Types of data subject to retention policies."""

    # Core memory data
    MEMORY_WORKING = "memory_working"  # Short-term working memories
    MEMORY_EPISODIC = "memory_episodic"  # Session-level memories
    MEMORY_SEMANTIC = "memory_semantic"  # Factual knowledge
    MEMORY_IDENTITY = "memory_identity"  # Long-term identity memories

    # Decision and outcome data
    DECISION_TRACE = "decision_trace"  # Decision tracking data
    OUTCOME = "outcome"  # Outcome observations

    # Event data
    EVENT_STREAM = "event_stream"  # NATS event streams
    DLQ_MESSAGE = "dlq_message"  # Dead letter queue messages

    # Federation and pattern data
    PATTERN = "pattern"  # Extracted patterns
    FEDERATED_PATTERN = "federated_pattern"  # Shared anonymized patterns

    # Causal graph data
    CAUSAL_EDGE = "causal_edge"  # Causal relationship edges


class RetentionAction(str, Enum):
    """Actions to take when retention period expires."""

    ARCHIVE = "archive"  # Move to cold storage, keep accessible
    SOFT_DELETE = "soft_delete"  # Mark as deleted, don't physically remove
    HARD_DELETE = "hard_delete"  # Physically remove data
    ANONYMIZE = "anonymize"  # Remove PII but keep aggregated data


@dataclass(frozen=True)
class RetentionPolicy:
    """Defines retention rules for a data type.

    Retention policies specify how long to keep data and what to do
    when the retention period expires. Policies can be customized
    per user or applied globally.

    Example:
        Working memories expire after 24 hours:
        >>> policy = RetentionPolicy(
        ...     data_type=DataType.MEMORY_WORKING,
        ...     retention_days=1,
        ...     action=RetentionAction.SOFT_DELETE,
        ... )
    """

    # What data this policy applies to
    data_type: DataType

    # How long to retain (days)
    retention_days: int

    # What to do when expired
    action: RetentionAction = RetentionAction.ARCHIVE

    # Grace period before action (days)
    grace_period_days: int = 0

    # Maximum records to process per run
    batch_size: int = 1000

    # Whether this is a user-specific override
    user_id: UUID | None = None

    # Policy metadata
    description: str = ""

    @property
    def retention_duration(self) -> timedelta:
        """Get retention as timedelta."""
        return timedelta(days=self.retention_days)

    @property
    def total_retention_days(self) -> int:
        """Total days including grace period."""
        return self.retention_days + self.grace_period_days

    def is_expired(self, created_at: datetime, now: datetime | None = None) -> bool:
        """Check if a record has exceeded retention period.

        Args:
            created_at: When the record was created
            now: Current time (defaults to UTC now)

        Returns:
            True if the record should be processed for retention
        """
        from datetime import UTC

        if now is None:
            now = datetime.now(UTC)

        # Ensure created_at is timezone-aware
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        age = now - created_at
        return age.days >= self.total_retention_days


@dataclass
class RetentionResult:
    """Result of applying a retention policy.

    Tracks how many records were processed and any errors.
    """

    policy: RetentionPolicy
    records_found: int = 0
    records_processed: int = 0
    records_archived: int = 0
    records_deleted: int = 0
    records_anonymized: int = 0
    records_failed: int = 0
    errors: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.records_found == 0:
            return 1.0
        return (self.records_found - self.records_failed) / self.records_found

    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds."""
        if self.started_at is None or self.completed_at is None:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()


@dataclass
class RetentionStats:
    """Statistics about retention policy application.

    Provides visibility into what data is being retained
    and what's been cleaned up.
    """

    user_id: UUID | None
    data_type: DataType
    total_records: int
    records_in_retention: int
    records_near_expiry: int  # Within 7 days of expiry
    records_expired: int
    oldest_record_age_days: int
    newest_record_age_days: int
    policy: RetentionPolicy | None = None

    @property
    def retention_health(self) -> str:
        """Assess health of retention for this data type.

        Returns:
            "healthy", "warning", or "critical"
        """
        if self.records_expired > 0:
            return "critical"
        if self.records_near_expiry > self.total_records * 0.2:
            return "warning"
        return "healthy"


# Default retention policies
DEFAULT_RETENTION_POLICIES = {
    DataType.MEMORY_WORKING: RetentionPolicy(
        data_type=DataType.MEMORY_WORKING,
        retention_days=1,
        action=RetentionAction.SOFT_DELETE,
        description="Working memories are short-lived, delete after 24 hours",
    ),
    DataType.MEMORY_EPISODIC: RetentionPolicy(
        data_type=DataType.MEMORY_EPISODIC,
        retention_days=30,
        action=RetentionAction.ARCHIVE,
        grace_period_days=7,
        description="Episodic memories archived after 30 days",
    ),
    DataType.MEMORY_SEMANTIC: RetentionPolicy(
        data_type=DataType.MEMORY_SEMANTIC,
        retention_days=365,
        action=RetentionAction.ARCHIVE,
        grace_period_days=30,
        description="Semantic knowledge retained for 1 year",
    ),
    DataType.MEMORY_IDENTITY: RetentionPolicy(
        data_type=DataType.MEMORY_IDENTITY,
        retention_days=3650,  # 10 years
        action=RetentionAction.ARCHIVE,
        grace_period_days=90,
        description="Identity memories retained long-term",
    ),
    DataType.DECISION_TRACE: RetentionPolicy(
        data_type=DataType.DECISION_TRACE,
        retention_days=90,
        action=RetentionAction.ANONYMIZE,
        grace_period_days=14,
        description="Decision traces anonymized after 90 days",
    ),
    DataType.OUTCOME: RetentionPolicy(
        data_type=DataType.OUTCOME,
        retention_days=180,
        action=RetentionAction.ARCHIVE,
        grace_period_days=14,
        description="Outcomes archived after 6 months",
    ),
    DataType.EVENT_STREAM: RetentionPolicy(
        data_type=DataType.EVENT_STREAM,
        retention_days=30,
        action=RetentionAction.HARD_DELETE,
        description="Event streams purged after 30 days",
    ),
    DataType.DLQ_MESSAGE: RetentionPolicy(
        data_type=DataType.DLQ_MESSAGE,
        retention_days=7,
        action=RetentionAction.HARD_DELETE,
        description="DLQ messages deleted after 7 days",
    ),
    DataType.PATTERN: RetentionPolicy(
        data_type=DataType.PATTERN,
        retention_days=365,
        action=RetentionAction.ARCHIVE,
        description="Patterns retained for 1 year",
    ),
    DataType.FEDERATED_PATTERN: RetentionPolicy(
        data_type=DataType.FEDERATED_PATTERN,
        retention_days=730,  # 2 years
        action=RetentionAction.ARCHIVE,
        description="Federated patterns retained for 2 years",
    ),
    DataType.CAUSAL_EDGE: RetentionPolicy(
        data_type=DataType.CAUSAL_EDGE,
        retention_days=180,
        action=RetentionAction.HARD_DELETE,
        grace_period_days=30,
        description="Causal edges pruned after 6 months",
    ),
}


def get_default_policy(data_type: DataType) -> RetentionPolicy:
    """Get the default retention policy for a data type.

    Args:
        data_type: The type of data

    Returns:
        The default RetentionPolicy for that type
    """
    return DEFAULT_RETENTION_POLICIES.get(
        data_type,
        RetentionPolicy(
            data_type=data_type,
            retention_days=90,
            action=RetentionAction.ARCHIVE,
            description="Default retention policy",
        ),
    )
