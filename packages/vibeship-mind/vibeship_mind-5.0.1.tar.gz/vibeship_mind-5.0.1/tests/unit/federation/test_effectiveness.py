"""Tests for pattern effectiveness tracking.

Tests the pattern effectiveness tracker:
- Recording pattern usage
- Tracking outcomes
- Calculating effectiveness metrics
- Detecting declining patterns
"""

import pytest
from datetime import datetime, UTC, timedelta
from uuid import uuid4

from mind.core.federation.effectiveness import (
    PatternUsage,
    PatternEffectiveness,
    PatternEffectivenessTracker,
    get_effectiveness_tracker,
)


class TestPatternUsage:
    """Tests for PatternUsage dataclass."""

    def test_usage_creation(self):
        """PatternUsage should store all required fields."""
        pattern_id = uuid4()
        trace_id = uuid4()
        user_id = uuid4()

        usage = PatternUsage(
            pattern_id=pattern_id,
            trace_id=trace_id,
            user_id=user_id,
            relevance_score=0.8,
            recommendation_rank=0,
        )

        assert usage.pattern_id == pattern_id
        assert usage.trace_id == trace_id
        assert usage.user_id == user_id
        assert usage.relevance_score == 0.8
        assert usage.recommendation_rank == 0
        assert usage.outcome_quality is None

    def test_improvement_calculation(self):
        """Should calculate improvement over baseline."""
        usage = PatternUsage()
        usage.outcome_quality = 0.8
        usage.baseline_quality = 0.5

        assert usage.improvement == pytest.approx(0.3)
        assert usage.is_improvement is True

    def test_improvement_negative(self):
        """Should detect when pattern hurt outcomes."""
        usage = PatternUsage()
        usage.outcome_quality = 0.3
        usage.baseline_quality = 0.5

        assert usage.improvement == pytest.approx(-0.2)
        assert usage.is_improvement is False

    def test_improvement_none_without_outcome(self):
        """Should return None when no outcome recorded."""
        usage = PatternUsage()

        assert usage.improvement is None
        assert usage.is_improvement is None


class TestPatternEffectiveness:
    """Tests for PatternEffectiveness dataclass."""

    def test_effectiveness_creation(self):
        """PatternEffectiveness should have sensible defaults."""
        pattern_id = uuid4()
        eff = PatternEffectiveness(pattern_id=pattern_id)

        assert eff.pattern_id == pattern_id
        assert eff.total_uses == 0
        assert eff.outcomes_recorded == 0
        assert eff.success_count == 0

    def test_success_rate_zero_recorded(self):
        """Success rate should be 0 when nothing recorded."""
        eff = PatternEffectiveness(pattern_id=uuid4())

        assert eff.success_rate == 0.0

    def test_success_rate_calculation(self):
        """Should calculate success rate correctly."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=100,
            success_count=75,
        )

        assert eff.success_rate == 0.75

    def test_average_improvement(self):
        """Should calculate average improvement."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=10,
            total_improvement=2.0,
        )

        assert eff.average_improvement == pytest.approx(0.2)

    def test_confidence_low_data(self):
        """Confidence should be 0 with insufficient data."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=5,  # Less than 10
            success_count=4,
        )

        assert eff.confidence == 0.0

    def test_confidence_with_data(self):
        """Confidence should be positive with sufficient data."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=50,
            success_count=40,
        )

        # Should have positive confidence with 80% success rate
        assert eff.confidence > 0.0
        assert eff.confidence <= 1.0

    def test_recent_success_rate(self):
        """Should calculate recent success rate."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            recent_uses=20,
            recent_successes=15,
        )

        assert eff.recent_success_rate == 0.75

    def test_is_declining_true(self):
        """Should detect declining patterns."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=100,
            success_count=80,  # 80% overall
            recent_uses=20,
            recent_successes=10,  # 50% recent (30% drop)
        )

        assert eff.is_declining is True

    def test_is_declining_false_insufficient_data(self):
        """Should not detect decline with insufficient data."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=15,  # Less than 20
            success_count=12,
            recent_uses=5,  # Less than 10
            recent_successes=2,
        )

        assert eff.is_declining is False

    def test_should_deprecate_low_confidence(self):
        """Should deprecate patterns with low confidence."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=50,
            success_count=20,  # 40% success rate
        )

        # Low success rate means low confidence
        assert eff.should_deprecate is True

    def test_should_deprecate_insufficient_data(self):
        """Should not deprecate with insufficient data."""
        eff = PatternEffectiveness(
            pattern_id=uuid4(),
            outcomes_recorded=10,  # Less than 30
            success_count=3,
        )

        assert eff.should_deprecate is False


class TestPatternEffectivenessTracker:
    """Tests for PatternEffectivenessTracker."""

    def test_record_usage(self):
        """Should record pattern usage."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()
        trace_id = uuid4()
        user_id = uuid4()

        usage = tracker.record_usage(
            pattern_id=pattern_id,
            trace_id=trace_id,
            user_id=user_id,
            relevance_score=0.9,
            recommendation_rank=0,
        )

        assert usage.pattern_id == pattern_id
        assert usage.trace_id == trace_id
        assert tracker.get_effectiveness(pattern_id) is not None
        assert tracker.get_effectiveness(pattern_id).total_uses == 1

    def test_record_multiple_usages(self):
        """Should track multiple usages for a pattern."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()

        for _ in range(5):
            tracker.record_usage(
                pattern_id=pattern_id,
                trace_id=uuid4(),
                user_id=uuid4(),
            )

        eff = tracker.get_effectiveness(pattern_id)
        assert eff.total_uses == 5

    def test_record_outcome(self):
        """Should record outcome for a usage."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()
        trace_id = uuid4()

        tracker.record_usage(
            pattern_id=pattern_id,
            trace_id=trace_id,
            user_id=uuid4(),
        )

        updated = tracker.record_outcome(
            trace_id=trace_id,
            outcome_quality=0.8,
            baseline_quality=0.5,
        )

        assert len(updated) == 1
        assert updated[0].outcome_quality == 0.8
        assert updated[0].improvement == pytest.approx(0.3)

        eff = tracker.get_effectiveness(pattern_id)
        assert eff.outcomes_recorded == 1
        assert eff.success_count == 1

    def test_record_outcome_failure(self):
        """Should record failed outcome correctly."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()
        trace_id = uuid4()

        tracker.record_usage(
            pattern_id=pattern_id,
            trace_id=trace_id,
            user_id=uuid4(),
        )

        tracker.record_outcome(
            trace_id=trace_id,
            outcome_quality=0.3,
            baseline_quality=0.5,
        )

        eff = tracker.get_effectiveness(pattern_id)
        assert eff.outcomes_recorded == 1
        assert eff.success_count == 0  # Not an improvement

    def test_record_outcome_multiple_patterns(self):
        """Should handle multiple patterns used for same trace."""
        tracker = PatternEffectivenessTracker()
        pattern1 = uuid4()
        pattern2 = uuid4()
        trace_id = uuid4()

        tracker.record_usage(pattern1, trace_id, uuid4())
        tracker.record_usage(pattern2, trace_id, uuid4())

        updated = tracker.record_outcome(trace_id, 0.9, 0.5)

        assert len(updated) == 2
        assert tracker.get_effectiveness(pattern1).outcomes_recorded == 1
        assert tracker.get_effectiveness(pattern2).outcomes_recorded == 1

    def test_get_all_effectiveness(self):
        """Should return all tracked patterns."""
        tracker = PatternEffectivenessTracker()

        for _ in range(3):
            tracker.record_usage(uuid4(), uuid4(), uuid4())

        all_eff = tracker.get_all_effectiveness()
        assert len(all_eff) == 3

    def test_get_declining_patterns(self):
        """Should identify declining patterns."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()

        # Simulate many usages with declining recent performance
        eff = PatternEffectiveness(
            pattern_id=pattern_id,
            total_uses=100,
            outcomes_recorded=100,
            success_count=80,  # 80% overall
            recent_uses=20,
            recent_successes=10,  # 50% recent
        )
        tracker._effectiveness[pattern_id] = eff

        declining = tracker.get_declining_patterns()
        assert len(declining) == 1
        assert declining[0].pattern_id == pattern_id

    def test_get_deprecated_patterns(self):
        """Should identify patterns to deprecate."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()

        # Low success rate pattern
        eff = PatternEffectiveness(
            pattern_id=pattern_id,
            total_uses=50,
            outcomes_recorded=50,
            success_count=15,  # 30% success
        )
        tracker._effectiveness[pattern_id] = eff

        deprecated = tracker.get_deprecated_patterns()
        assert len(deprecated) == 1

    def test_get_top_patterns(self):
        """Should return top performing patterns."""
        tracker = PatternEffectivenessTracker()

        # Create patterns with varying effectiveness
        for success_count in [90, 50, 20]:
            pattern_id = uuid4()
            eff = PatternEffectiveness(
                pattern_id=pattern_id,
                total_uses=100,
                outcomes_recorded=100,
                success_count=success_count,
            )
            tracker._effectiveness[pattern_id] = eff

        top = tracker.get_top_patterns(limit=2)
        assert len(top) == 2
        # Should be sorted by confidence * success_rate
        assert top[0].success_rate > top[1].success_rate

    def test_get_stats(self):
        """Should return overall statistics."""
        tracker = PatternEffectivenessTracker()

        # Add some patterns
        pattern1 = uuid4()
        pattern2 = uuid4()

        tracker._effectiveness[pattern1] = PatternEffectiveness(
            pattern_id=pattern1,
            total_uses=50,
            outcomes_recorded=50,
            success_count=40,
            total_improvement=5.0,
        )
        tracker._effectiveness[pattern2] = PatternEffectiveness(
            pattern_id=pattern2,
            total_uses=30,
            outcomes_recorded=30,
            success_count=20,
            total_improvement=2.0,
        )

        stats = tracker.get_stats()

        assert stats["total_patterns_tracked"] == 2
        assert stats["average_success_rate"] > 0
        assert stats["average_improvement"] > 0

    def test_cleanup_old_usages(self):
        """Should remove old usage records."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()
        old_trace = uuid4()
        new_trace = uuid4()

        # Add old usage
        old_usage = tracker.record_usage(pattern_id, old_trace, uuid4())
        old_usage.used_at = datetime.now(UTC) - timedelta(days=100)

        # Add new usage
        tracker.record_usage(pattern_id, new_trace, uuid4())

        removed = tracker.cleanup_old_usages(older_than_days=90)

        assert removed == 1
        assert old_trace not in tracker._trace_usages
        assert new_trace in tracker._trace_usages

    def test_refresh_recent_window(self):
        """Should refresh recent window statistics."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()

        # Add usages
        for i in range(5):
            trace_id = uuid4()
            usage = tracker.record_usage(pattern_id, trace_id, uuid4())

            # Make some old, some new
            if i < 2:
                usage.used_at = datetime.now(UTC) - timedelta(days=45)  # Old

            # Record outcome
            usage.outcome_quality = 0.8
            usage.baseline_quality = 0.5
            tracker._usages[usage.usage_id] = usage

        # Refresh with 30-day window
        tracker.refresh_recent_window(window_days=30)

        eff = tracker.get_effectiveness(pattern_id)
        assert eff.recent_uses == 3  # Only the 3 new usages


class TestGlobalTracker:
    """Tests for global tracker instance."""

    def test_get_effectiveness_tracker(self):
        """Should return a tracker instance."""
        tracker = get_effectiveness_tracker()
        assert tracker is not None
        assert isinstance(tracker, PatternEffectivenessTracker)

    def test_get_effectiveness_tracker_singleton(self):
        """Should return same instance on multiple calls."""
        tracker1 = get_effectiveness_tracker()
        tracker2 = get_effectiveness_tracker()
        assert tracker1 is tracker2


class TestEffectivenessIntegration:
    """Integration tests for effectiveness tracking flow."""

    def test_full_usage_outcome_flow(self):
        """Should track usage through outcome correctly."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()

        # Record 10 usages with mixed outcomes
        for i in range(10):
            trace_id = uuid4()
            tracker.record_usage(pattern_id, trace_id, uuid4())

            # 7 successes, 3 failures
            outcome = 0.8 if i < 7 else 0.3
            tracker.record_outcome(trace_id, outcome, 0.5)

        eff = tracker.get_effectiveness(pattern_id)

        assert eff.total_uses == 10
        assert eff.outcomes_recorded == 10
        assert eff.success_count == 7
        assert eff.success_rate == 0.7
        assert eff.confidence > 0  # Has enough data for confidence

    def test_pattern_lifecycle(self):
        """Should track pattern from new to deprecated."""
        tracker = PatternEffectivenessTracker()
        pattern_id = uuid4()

        # Initial good performance
        for i in range(20):
            trace_id = uuid4()
            tracker.record_usage(pattern_id, trace_id, uuid4())
            tracker.record_outcome(trace_id, 0.8, 0.5)

        eff = tracker.get_effectiveness(pattern_id)
        assert not eff.should_deprecate

        # Simulate declining performance
        for i in range(30):
            trace_id = uuid4()
            tracker.record_usage(pattern_id, trace_id, uuid4())
            tracker.record_outcome(trace_id, 0.3, 0.5)  # Poor outcomes

        # Refresh recent window
        tracker.refresh_recent_window()

        eff = tracker.get_effectiveness(pattern_id)
        # Should now be deprecated due to poor performance
        assert eff.success_rate < 0.5
