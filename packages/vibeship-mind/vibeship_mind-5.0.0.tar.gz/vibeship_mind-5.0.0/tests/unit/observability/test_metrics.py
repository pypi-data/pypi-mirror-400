"""Tests for observability metrics."""

import pytest

# Import the global metrics instance directly
from mind.observability.metrics import metrics


class TestMindMetrics:
    """Tests for the MindMetrics class."""

    def test_observe_retrieval(self):
        """observe_retrieval should record latency and sources."""
        metrics.observe_retrieval(
            latency_seconds=0.15,
            sources_used=["vector", "keyword"],
            result_count=10,
        )
        # Metrics are recorded - verification is that no exception is raised

    def test_observe_outcome_positive(self):
        """observe_outcome should classify positive outcomes."""
        metrics.observe_outcome(0.8)
        # Counter incremented for positive label

    def test_observe_outcome_negative(self):
        """observe_outcome should classify negative outcomes."""
        metrics.observe_outcome(-0.3)
        # Counter incremented for negative label

    def test_observe_outcome_neutral(self):
        """observe_outcome should classify neutral outcomes."""
        metrics.observe_outcome(0.0)
        # Counter incremented for neutral label


class TestDecisionQualityMetrics:
    """Tests for decision quality metrics."""

    def test_update_decision_success_rate(self):
        """update_decision_success_rate should set gauge value."""
        metrics.update_decision_success_rate(
            success_rate=0.75,
            user_cohort="all",
            decision_type="recommendation",
        )
        # Gauge is set - verification is that no exception is raised

    def test_update_decision_success_rate_defaults(self):
        """update_decision_success_rate should use defaults."""
        metrics.update_decision_success_rate(success_rate=0.82)
        # Uses default cohort "all" and decision_type "all"

    def test_observe_memory_relevance(self):
        """observe_memory_relevance should record histogram value."""
        metrics.observe_memory_relevance(
            relevance_score=0.85,
            temporal_level="SITUATIONAL",
            source="vector",
        )

    def test_observe_memory_relevance_default_source(self):
        """observe_memory_relevance should use default source."""
        metrics.observe_memory_relevance(
            relevance_score=0.72,
            temporal_level="IDENTITY",
        )
        # Uses default source "fusion"

    def test_update_causal_accuracy(self):
        """update_causal_accuracy should set gauge value."""
        metrics.update_causal_accuracy(
            accuracy=0.91,
            prediction_type="outcome",
        )

    def test_update_causal_accuracy_attribution(self):
        """update_causal_accuracy should work for attribution type."""
        metrics.update_causal_accuracy(
            accuracy=0.88,
            prediction_type="attribution",
        )

    def test_observe_context_completeness(self):
        """observe_context_completeness should record histogram value."""
        metrics.observe_context_completeness(
            completeness=0.95,
            decision_type="recommendation",
        )

    def test_observe_context_completeness_default(self):
        """observe_context_completeness should use default decision_type."""
        metrics.observe_context_completeness(completeness=0.78)
        # Uses default decision_type "unknown"

    def test_update_calibration_error(self):
        """update_calibration_error should set gauge value."""
        metrics.update_calibration_error(
            ece=0.05,
            user_cohort="active",
        )

    def test_update_calibration_error_default(self):
        """update_calibration_error should use default cohort."""
        metrics.update_calibration_error(ece=0.03)
        # Uses default cohort "all"

    def test_update_pattern_effectiveness(self):
        """update_pattern_effectiveness should set gauge value."""
        metrics.update_pattern_effectiveness(
            effectiveness=0.15,
            pattern_type="decision_strategy",
        )

    def test_record_embedding_cache_hit(self):
        """record_embedding_cache_hit should increment counter."""
        metrics.record_embedding_cache_hit()
        metrics.record_embedding_cache_hit()
        # Counter incremented twice

    def test_record_embedding_cache_miss(self):
        """record_embedding_cache_miss should increment counter."""
        metrics.record_embedding_cache_miss()
        # Counter incremented


class TestMetricsBoundaryConditions:
    """Tests for boundary conditions in metrics."""

    def test_success_rate_boundary_zero(self):
        """Should handle 0.0 success rate."""
        metrics.update_decision_success_rate(success_rate=0.0)

    def test_success_rate_boundary_one(self):
        """Should handle 1.0 success rate."""
        metrics.update_decision_success_rate(success_rate=1.0)

    def test_relevance_boundary_values(self):
        """Should handle boundary relevance values."""
        metrics.observe_memory_relevance(
            relevance_score=0.0,
            temporal_level="IMMEDIATE",
        )
        metrics.observe_memory_relevance(
            relevance_score=1.0,
            temporal_level="IDENTITY",
        )

    def test_calibration_error_zero(self):
        """Should handle perfect calibration (ECE = 0)."""
        metrics.update_calibration_error(ece=0.0)

    def test_pattern_effectiveness_negative(self):
        """Should handle negative effectiveness (pattern hurts)."""
        metrics.update_pattern_effectiveness(
            effectiveness=-0.05,
            pattern_type="decision_strategy",
        )


class TestMetricsLabels:
    """Tests for metric label handling."""

    def test_different_user_cohorts(self):
        """Should handle different user cohorts."""
        metrics.update_decision_success_rate(
            success_rate=0.8,
            user_cohort="new",
        )
        metrics.update_decision_success_rate(
            success_rate=0.85,
            user_cohort="active",
        )
        metrics.update_decision_success_rate(
            success_rate=0.9,
            user_cohort="power",
        )

    def test_different_decision_types(self):
        """Should handle different decision types."""
        metrics.update_decision_success_rate(
            success_rate=0.75,
            decision_type="recommendation",
        )
        metrics.update_decision_success_rate(
            success_rate=0.82,
            decision_type="classification",
        )

    def test_different_temporal_levels(self):
        """Should handle different temporal levels."""
        for level in ["IMMEDIATE", "SITUATIONAL", "SEASONAL", "IDENTITY"]:
            metrics.observe_memory_relevance(
                relevance_score=0.8,
                temporal_level=level,
            )

    def test_different_prediction_types(self):
        """Should handle different prediction types."""
        for pred_type in ["outcome", "attribution", "counterfactual"]:
            metrics.update_causal_accuracy(
                accuracy=0.85,
                prediction_type=pred_type,
            )


class TestMetricsExist:
    """Tests to verify all expected metrics are defined."""

    def test_decision_quality_metrics_exist(self):
        """Verify decision quality metrics are defined."""
        assert hasattr(metrics, "decision_success_rate")
        assert hasattr(metrics, "memory_retrieval_relevance")
        assert hasattr(metrics, "causal_prediction_accuracy")

    def test_embedding_metrics_exist(self):
        """Verify embedding metrics are defined."""
        assert hasattr(metrics, "embedding_cache_hits_total")
        assert hasattr(metrics, "embedding_cache_misses_total")

    def test_calibration_metrics_exist(self):
        """Verify calibration metrics are defined."""
        assert hasattr(metrics, "confidence_calibration_error")

    def test_pattern_metrics_exist(self):
        """Verify pattern metrics are defined."""
        assert hasattr(metrics, "pattern_effectiveness")

    def test_context_metrics_exist(self):
        """Verify context metrics are defined."""
        assert hasattr(metrics, "context_completeness")
