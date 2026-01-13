"""Pattern effectiveness tracking for Mind v5.

This module tracks how well federated patterns perform when applied:
- Records pattern usage and outcomes
- Calculates effectiveness metrics
- Enables pattern deprecation decisions
- Supports A/B testing of patterns

Key metrics:
- Success rate: % of uses that improved outcomes
- Average improvement: Mean outcome delta when used
- Confidence: Bayesian confidence in effectiveness
- Decay: Whether pattern is losing effectiveness
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import structlog

from mind.observability.metrics import metrics

logger = structlog.get_logger()


@dataclass
class PatternUsage:
    """Record of a pattern being applied to a decision."""

    usage_id: UUID = field(default_factory=uuid4)
    pattern_id: UUID = field(default_factory=uuid4)
    trace_id: UUID = field(default_factory=uuid4)  # Decision trace
    user_id: UUID = field(default_factory=uuid4)

    # Recommendation context
    relevance_score: float = 0.0  # Score when recommended
    recommendation_rank: int = 0  # Position in recommendations

    # Timestamps
    used_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    outcome_recorded_at: datetime | None = None

    # Outcome tracking (filled in when outcome observed)
    outcome_quality: float | None = None
    baseline_quality: float | None = None  # What we expected without pattern

    @property
    def improvement(self) -> float | None:
        """Calculate improvement over baseline."""
        if self.outcome_quality is None or self.baseline_quality is None:
            return None
        return self.outcome_quality - self.baseline_quality

    @property
    def is_improvement(self) -> bool | None:
        """Was this an improvement over baseline?"""
        if self.improvement is None:
            return None
        return self.improvement > 0


@dataclass
class PatternEffectiveness:
    """Aggregated effectiveness metrics for a pattern."""

    pattern_id: UUID
    total_uses: int = 0
    outcomes_recorded: int = 0

    # Outcome statistics
    success_count: int = 0  # Uses that improved outcomes
    total_improvement: float = 0.0  # Sum of improvements

    # Time-based tracking
    first_used: datetime | None = None
    last_used: datetime | None = None
    last_evaluated: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Rolling window stats (last 30 days)
    recent_uses: int = 0
    recent_successes: int = 0
    recent_improvement: float = 0.0

    @property
    def success_rate(self) -> float:
        """Percentage of uses that improved outcomes."""
        if self.outcomes_recorded == 0:
            return 0.0
        return self.success_count / self.outcomes_recorded

    @property
    def average_improvement(self) -> float:
        """Average improvement when pattern is used."""
        if self.outcomes_recorded == 0:
            return 0.0
        return self.total_improvement / self.outcomes_recorded

    @property
    def confidence(self) -> float:
        """Bayesian confidence in effectiveness estimate.

        Uses beta distribution with prior Beta(1, 1) uniform.
        Returns lower bound of 95% credible interval.
        """
        # Beta posterior with uniform prior
        1 + self.success_count
        1 + (self.outcomes_recorded - self.success_count)

        # Lower bound of 95% credible interval (conservative)
        # Approximation for large samples
        if self.outcomes_recorded < 10:
            return 0.0  # Not enough data

        # Wilson score interval for binomial proportion
        import math

        z = 1.96  # 95% confidence
        n = self.outcomes_recorded
        p_hat = self.success_rate

        denominator = 1 + z * z / n
        center = (p_hat + z * z / (2 * n)) / denominator
        margin = z * math.sqrt((p_hat * (1 - p_hat) + z * z / (4 * n)) / n) / denominator

        return max(0.0, center - margin)

    @property
    def recent_success_rate(self) -> float:
        """Success rate over recent window (last 30 days)."""
        if self.recent_uses == 0:
            return 0.0
        return self.recent_successes / self.recent_uses

    @property
    def is_declining(self) -> bool:
        """Is pattern effectiveness declining?

        True if recent success rate is significantly lower than overall.
        """
        if self.recent_uses < 10 or self.outcomes_recorded < 20:
            return False  # Not enough data

        decline_threshold = 0.15  # 15% drop is significant
        return self.success_rate - self.recent_success_rate > decline_threshold

    @property
    def should_deprecate(self) -> bool:
        """Should this pattern be deprecated?

        Deprecated if:
        - Success rate below 50% with confidence
        - Has been declining for a while
        """
        if self.outcomes_recorded < 30:
            return False  # Not enough data

        # Low confidence in being effective
        if self.confidence < 0.4:
            return True

        # Significant recent decline
        return bool(self.is_declining and self.recent_success_rate < 0.4)


class PatternEffectivenessTracker:
    """Tracks pattern effectiveness over time.

    Responsibilities:
    - Record pattern usage
    - Track outcomes for used patterns
    - Calculate effectiveness metrics
    - Flag declining patterns
    """

    def __init__(self, repository=None):
        """Initialize the tracker.

        Args:
            repository: Optional persistence repository
        """
        self._repository = repository

        # In-memory storage
        self._usages: dict[UUID, PatternUsage] = {}
        self._effectiveness: dict[UUID, PatternEffectiveness] = {}

        # Index for efficient lookups
        self._pattern_usages: dict[UUID, list[UUID]] = {}  # pattern_id -> [usage_ids]
        self._trace_usages: dict[UUID, list[UUID]] = {}  # trace_id -> [usage_ids]

    def record_usage(
        self,
        pattern_id: UUID,
        trace_id: UUID,
        user_id: UUID,
        relevance_score: float = 0.0,
        recommendation_rank: int = 0,
    ) -> PatternUsage:
        """Record that a pattern was used for a decision.

        Args:
            pattern_id: The pattern that was applied
            trace_id: The decision trace
            user_id: The user
            relevance_score: How relevant the pattern was rated
            recommendation_rank: Position in recommendations (0 = first)

        Returns:
            The usage record
        """
        usage = PatternUsage(
            pattern_id=pattern_id,
            trace_id=trace_id,
            user_id=user_id,
            relevance_score=relevance_score,
            recommendation_rank=recommendation_rank,
        )

        # Store usage
        self._usages[usage.usage_id] = usage

        # Update indexes
        if pattern_id not in self._pattern_usages:
            self._pattern_usages[pattern_id] = []
        self._pattern_usages[pattern_id].append(usage.usage_id)

        if trace_id not in self._trace_usages:
            self._trace_usages[trace_id] = []
        self._trace_usages[trace_id].append(usage.usage_id)

        # Update effectiveness stats
        self._update_usage_count(pattern_id)

        # Record metric
        metrics.record_pattern_usage(str(pattern_id))

        logger.info(
            "pattern_usage_recorded",
            usage_id=str(usage.usage_id),
            pattern_id=str(pattern_id),
            trace_id=str(trace_id),
        )

        return usage

    def record_outcome(
        self,
        trace_id: UUID,
        outcome_quality: float,
        baseline_quality: float = 0.5,
    ) -> list[PatternUsage]:
        """Record outcome for patterns used in a decision.

        Args:
            trace_id: The decision trace
            outcome_quality: Quality of the actual outcome (0-1)
            baseline_quality: Expected quality without patterns (0-1)

        Returns:
            List of updated usage records
        """
        updated = []

        usage_ids = self._trace_usages.get(trace_id, [])
        for usage_id in usage_ids:
            usage = self._usages.get(usage_id)
            if usage and usage.outcome_quality is None:
                # Update usage record
                usage.outcome_quality = outcome_quality
                usage.baseline_quality = baseline_quality
                usage.outcome_recorded_at = datetime.now(UTC)

                # Update effectiveness stats
                self._update_effectiveness(usage)

                # Record metrics
                if usage.is_improvement:
                    metrics.record_pattern_success(str(usage.pattern_id))
                else:
                    metrics.record_pattern_failure(str(usage.pattern_id))

                updated.append(usage)

                logger.info(
                    "pattern_outcome_recorded",
                    usage_id=str(usage_id),
                    pattern_id=str(usage.pattern_id),
                    improvement=usage.improvement,
                )

        return updated

    def get_effectiveness(self, pattern_id: UUID) -> PatternEffectiveness | None:
        """Get effectiveness metrics for a pattern.

        Args:
            pattern_id: The pattern to check

        Returns:
            PatternEffectiveness or None if not tracked
        """
        return self._effectiveness.get(pattern_id)

    def get_all_effectiveness(self) -> list[PatternEffectiveness]:
        """Get effectiveness metrics for all tracked patterns."""
        return list(self._effectiveness.values())

    def get_declining_patterns(self) -> list[PatternEffectiveness]:
        """Get patterns that are showing declining effectiveness."""
        return [e for e in self._effectiveness.values() if e.is_declining]

    def get_deprecated_patterns(self) -> list[PatternEffectiveness]:
        """Get patterns that should be deprecated."""
        return [e for e in self._effectiveness.values() if e.should_deprecate]

    def get_top_patterns(self, limit: int = 10) -> list[PatternEffectiveness]:
        """Get the most effective patterns.

        Args:
            limit: Maximum patterns to return

        Returns:
            List sorted by confidence-weighted success rate
        """
        effective = [
            e
            for e in self._effectiveness.values()
            if e.outcomes_recorded >= 10  # Minimum data
        ]

        # Sort by confidence * success_rate
        effective.sort(
            key=lambda e: e.confidence * e.success_rate,
            reverse=True,
        )

        return effective[:limit]

    def get_stats(self) -> dict:
        """Get overall tracking statistics."""
        total_patterns = len(self._effectiveness)
        total_usages = len(self._usages)
        outcomes_recorded = sum(1 for u in self._usages.values() if u.outcome_quality is not None)

        declining = len(self.get_declining_patterns())
        deprecated = len(self.get_deprecated_patterns())

        avg_success_rate = 0.0
        avg_improvement = 0.0
        if total_patterns > 0:
            rates = [
                e.success_rate for e in self._effectiveness.values() if e.outcomes_recorded > 0
            ]
            if rates:
                avg_success_rate = sum(rates) / len(rates)

            improvements = [
                e.average_improvement
                for e in self._effectiveness.values()
                if e.outcomes_recorded > 0
            ]
            if improvements:
                avg_improvement = sum(improvements) / len(improvements)

        return {
            "total_patterns_tracked": total_patterns,
            "total_usages": total_usages,
            "outcomes_recorded": outcomes_recorded,
            "average_success_rate": avg_success_rate,
            "average_improvement": avg_improvement,
            "declining_patterns": declining,
            "deprecated_patterns": deprecated,
        }

    def cleanup_old_usages(self, older_than_days: int = 90) -> int:
        """Remove old usage records to save memory.

        Args:
            older_than_days: Delete usages older than this

        Returns:
            Number of usages removed
        """
        cutoff = datetime.now(UTC) - timedelta(days=older_than_days)
        removed = 0

        to_remove = [usage_id for usage_id, usage in self._usages.items() if usage.used_at < cutoff]

        for usage_id in to_remove:
            usage = self._usages.pop(usage_id, None)
            if usage:
                # Remove from indexes
                if usage.pattern_id in self._pattern_usages:
                    self._pattern_usages[usage.pattern_id] = [
                        uid for uid in self._pattern_usages[usage.pattern_id] if uid != usage_id
                    ]
                    # Clean up empty entries
                    if not self._pattern_usages[usage.pattern_id]:
                        del self._pattern_usages[usage.pattern_id]

                if usage.trace_id in self._trace_usages:
                    self._trace_usages[usage.trace_id] = [
                        uid for uid in self._trace_usages[usage.trace_id] if uid != usage_id
                    ]
                    # Clean up empty entries
                    if not self._trace_usages[usage.trace_id]:
                        del self._trace_usages[usage.trace_id]

                removed += 1

        if removed > 0:
            logger.info("pattern_usages_cleaned", removed=removed)

        return removed

    def _update_usage_count(self, pattern_id: UUID) -> None:
        """Update usage count for a pattern."""
        if pattern_id not in self._effectiveness:
            self._effectiveness[pattern_id] = PatternEffectiveness(
                pattern_id=pattern_id,
                first_used=datetime.now(UTC),
            )

        eff = self._effectiveness[pattern_id]
        eff.total_uses += 1
        eff.last_used = datetime.now(UTC)
        eff.recent_uses += 1  # Will be adjusted in rolling window cleanup

    def _update_effectiveness(self, usage: PatternUsage) -> None:
        """Update effectiveness stats for a usage with outcome."""
        if usage.pattern_id not in self._effectiveness:
            return

        eff = self._effectiveness[usage.pattern_id]
        eff.outcomes_recorded += 1
        eff.last_evaluated = datetime.now(UTC)

        if usage.is_improvement:
            eff.success_count += 1
            eff.recent_successes += 1

        if usage.improvement is not None:
            eff.total_improvement += usage.improvement
            eff.recent_improvement += usage.improvement

    def refresh_recent_window(self, window_days: int = 30) -> None:
        """Refresh the recent window statistics.

        Call this periodically to keep recent_* stats accurate.
        """
        cutoff = datetime.now(UTC) - timedelta(days=window_days)

        for pattern_id, eff in self._effectiveness.items():
            recent_uses = 0
            recent_successes = 0
            recent_improvement = 0.0

            usage_ids = self._pattern_usages.get(pattern_id, [])
            for usage_id in usage_ids:
                usage = self._usages.get(usage_id)
                if usage and usage.used_at >= cutoff:
                    recent_uses += 1
                    if usage.outcome_quality is not None:
                        if usage.is_improvement:
                            recent_successes += 1
                        if usage.improvement is not None:
                            recent_improvement += usage.improvement

            eff.recent_uses = recent_uses
            eff.recent_successes = recent_successes
            eff.recent_improvement = recent_improvement


# Global tracker instance (for injection)
_tracker: PatternEffectivenessTracker | None = None


def get_effectiveness_tracker() -> PatternEffectivenessTracker:
    """Get the global effectiveness tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = PatternEffectivenessTracker()
    return _tracker
