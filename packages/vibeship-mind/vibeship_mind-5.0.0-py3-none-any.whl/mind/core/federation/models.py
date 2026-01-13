"""Federation domain models.

These models represent patterns that can be safely shared across users
to enable collective learning without compromising privacy.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class PatternType(Enum):
    """Types of learnable patterns."""

    DECISION_STRATEGY = "decision_strategy"  # How to approach a type of decision
    CONTEXT_COMBINATION = "context_combination"  # What context works together
    OUTCOME_PREDICTOR = "outcome_predictor"  # What predicts good outcomes
    TEMPORAL_SEQUENCE = "temporal_sequence"  # Order of information


@dataclass(frozen=True)
class PrivacyBudget:
    """Privacy budget for differential privacy.

    Controls how much privacy loss is acceptable when sharing patterns.
    Lower epsilon = more privacy, less utility.
    """

    epsilon: float = 0.1  # Privacy parameter (lower = more private)
    delta: float = 1e-5  # Probability of privacy breach
    min_users: int = 10  # Minimum users before sharing
    min_observations: int = 100  # Minimum observations

    def is_satisfied(self, user_count: int, observation_count: int) -> bool:
        """Check if privacy thresholds are met."""
        return user_count >= self.min_users and observation_count >= self.min_observations


@dataclass
class PatternCandidate:
    """A candidate pattern before privacy sanitization.

    This is an internal representation that may contain
    information that needs to be sanitized before sharing.
    """

    candidate_id: UUID = field(default_factory=uuid4)
    pattern_type: PatternType = PatternType.DECISION_STRATEGY

    # Pattern content (to be abstracted)
    trigger_category: str = ""  # Abstracted trigger type
    response_strategy: str = ""  # Abstracted response approach

    # Evidence
    source_traces: list[UUID] = field(default_factory=list)
    source_users: set[UUID] = field(default_factory=set)
    outcome_sum: float = 0.0  # Sum of outcome qualities
    observation_count: int = 0

    # Timing
    first_observed: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_observed: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def average_outcome(self) -> float:
        """Calculate average outcome quality."""
        if self.observation_count == 0:
            return 0.0
        return self.outcome_sum / self.observation_count

    @property
    def user_count(self) -> int:
        """Number of unique users contributing."""
        return len(self.source_users)

    def add_observation(
        self,
        trace_id: UUID,
        user_id: UUID,
        outcome_quality: float,
    ) -> None:
        """Add an observation to this pattern candidate."""
        self.source_traces.append(trace_id)
        self.source_users.add(user_id)
        self.outcome_sum += outcome_quality
        self.observation_count += 1
        self.last_observed = datetime.now(UTC)


@dataclass(frozen=True)
class Pattern:
    """A validated pattern ready for storage.

    This is a pattern that has been validated but not yet
    sanitized for cross-user sharing.
    """

    pattern_id: UUID
    pattern_type: PatternType
    trigger_category: str
    response_strategy: str
    average_outcome: float
    observation_count: int
    user_count: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_candidate(cls, candidate: PatternCandidate) -> "Pattern":
        """Create a Pattern from a validated candidate."""
        return cls(
            pattern_id=uuid4(),
            pattern_type=candidate.pattern_type,
            trigger_category=candidate.trigger_category,
            response_strategy=candidate.response_strategy,
            average_outcome=candidate.average_outcome,
            observation_count=candidate.observation_count,
            user_count=candidate.user_count,
        )


@dataclass(frozen=True)
class SanitizedPattern:
    """Pattern safe for cross-user federation.

    This pattern has been sanitized with differential privacy
    and is safe to share across users without leaking PII.
    """

    pattern_id: UUID
    pattern_type: PatternType
    trigger_category: str  # Abstract category, not specific content
    response_strategy: str  # Abstract strategy description

    # Noised statistics (differential privacy applied)
    outcome_improvement: float  # Expected outcome improvement
    confidence: float  # Confidence in the pattern (0-1)

    # Privacy guarantees
    source_count: int  # Noised observation count
    user_count: int  # Noised unique user count
    epsilon: float  # Privacy parameter used

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    def is_valid(self) -> bool:
        """Check if pattern meets minimum thresholds."""
        return (
            self.source_count >= 100
            and self.user_count >= 10
            and self.epsilon <= 0.1
            and self.confidence >= 0.5
        )

    def is_expired(self) -> bool:
        """Check if pattern has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


@dataclass
class PatternMatch:
    """A pattern that matches a query context."""

    pattern: SanitizedPattern
    relevance_score: float  # How relevant to the query (0-1)
    expected_improvement: float  # Expected outcome improvement

    @property
    def recommendation_strength(self) -> float:
        """Combined score for ranking recommendations."""
        return self.relevance_score * self.pattern.confidence * self.expected_improvement
