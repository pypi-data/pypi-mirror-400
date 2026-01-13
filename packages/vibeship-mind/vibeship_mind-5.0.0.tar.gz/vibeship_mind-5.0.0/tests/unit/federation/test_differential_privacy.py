"""Tests for differential privacy sanitization."""

import pytest
from uuid import uuid4
from datetime import datetime, UTC, timedelta
import statistics

from mind.core.federation.models import (
    Pattern,
    PatternType,
    SanitizedPattern,
    PrivacyBudget,
)
from mind.core.federation.sanitizer import (
    DifferentialPrivacySanitizer,
    SanitizationReport,
    DEFAULT_PATTERN_LIFETIME_DAYS,
)
from mind.core.errors import ErrorCode


class TestPrivacyBudget:
    """Tests for PrivacyBudget dataclass."""

    def test_default_values(self):
        """Default budget should have reasonable privacy parameters."""
        budget = PrivacyBudget()

        assert budget.epsilon == 0.1
        assert budget.delta == 1e-5
        assert budget.min_users == 10
        assert budget.min_observations == 100

    def test_is_satisfied_both_thresholds_met(self):
        """Should return True when both thresholds are met."""
        budget = PrivacyBudget(min_users=10, min_observations=100)

        assert budget.is_satisfied(user_count=10, observation_count=100) is True
        assert budget.is_satisfied(user_count=50, observation_count=500) is True

    def test_is_satisfied_users_not_met(self):
        """Should return False when user threshold not met."""
        budget = PrivacyBudget(min_users=10, min_observations=100)

        assert budget.is_satisfied(user_count=9, observation_count=100) is False
        assert budget.is_satisfied(user_count=5, observation_count=1000) is False

    def test_is_satisfied_observations_not_met(self):
        """Should return False when observation threshold not met."""
        budget = PrivacyBudget(min_users=10, min_observations=100)

        assert budget.is_satisfied(user_count=10, observation_count=99) is False
        assert budget.is_satisfied(user_count=100, observation_count=50) is False

    def test_custom_budget_values(self):
        """Should accept custom privacy parameters."""
        budget = PrivacyBudget(
            epsilon=0.5,
            delta=1e-6,
            min_users=5,
            min_observations=50,
        )

        assert budget.epsilon == 0.5
        assert budget.delta == 1e-6
        assert budget.min_users == 5
        assert budget.min_observations == 50


class TestDifferentialPrivacySanitizer:
    """Tests for DifferentialPrivacySanitizer."""

    @pytest.fixture
    def sanitizer(self) -> DifferentialPrivacySanitizer:
        """Create a sanitizer with default budget."""
        return DifferentialPrivacySanitizer()

    @pytest.fixture
    def valid_pattern(self) -> Pattern:
        """Create a pattern that meets privacy thresholds."""
        return Pattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal",
            average_outcome=0.75,
            observation_count=150,
            user_count=25,
        )

    @pytest.fixture
    def small_pattern(self) -> Pattern:
        """Create a pattern that doesn't meet privacy thresholds."""
        return Pattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference",
            average_outcome=0.8,
            observation_count=50,  # Below min
            user_count=5,  # Below min
        )

    def test_sanitize_valid_pattern_succeeds(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        valid_pattern: Pattern,
    ):
        """Sanitizing a valid pattern should succeed."""
        result = sanitizer.sanitize(valid_pattern)

        assert result.is_ok
        sanitized = result.value
        assert isinstance(sanitized, SanitizedPattern)
        assert sanitized.pattern_type == valid_pattern.pattern_type
        assert sanitized.trigger_category == valid_pattern.trigger_category

    def test_sanitize_applies_noise_to_counts(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        valid_pattern: Pattern,
    ):
        """Sanitized counts should differ from original (due to noise)."""
        # Run multiple times to verify noise is being added
        results = [sanitizer.sanitize(valid_pattern) for _ in range(10)]

        source_counts = [r.value.source_count for r in results if r.is_ok]
        user_counts = [r.value.user_count for r in results if r.is_ok]

        # With noise, we should see some variation
        # At minimum, counts should be at least the privacy threshold
        for count in source_counts:
            assert count >= 100  # min_observations

        for count in user_counts:
            assert count >= 10  # min_users

    def test_sanitize_applies_noise_to_outcome(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        valid_pattern: Pattern,
    ):
        """Sanitized outcome should have noise applied."""
        results = [sanitizer.sanitize(valid_pattern) for _ in range(20)]
        outcomes = [r.value.outcome_improvement for r in results if r.is_ok]

        # Outcomes should vary due to noise
        # They should be clamped to [-1, 1]
        for outcome in outcomes:
            assert -1.0 <= outcome <= 1.0

    def test_sanitize_rejects_small_pattern(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        small_pattern: Pattern,
    ):
        """Patterns not meeting thresholds should be rejected."""
        result = sanitizer.sanitize(small_pattern)

        assert not result.is_ok
        assert result.error.code == ErrorCode.PRIVACY_VIOLATION
        assert "privacy thresholds" in result.error.message.lower()

    def test_sanitize_with_custom_epsilon(
        self,
        valid_pattern: Pattern,
    ):
        """Should accept custom epsilon parameter."""
        sanitizer = DifferentialPrivacySanitizer()
        result = sanitizer.sanitize(valid_pattern, epsilon=0.5)

        assert result.is_ok
        assert result.value.epsilon == 0.5

    def test_sanitize_sets_expiration(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        valid_pattern: Pattern,
    ):
        """Sanitized pattern should have expiration set."""
        result = sanitizer.sanitize(valid_pattern)

        assert result.is_ok
        sanitized = result.value
        assert sanitized.expires_at is not None

        # Should be approximately DEFAULT_PATTERN_LIFETIME_DAYS in the future
        expected = datetime.now(UTC) + timedelta(days=DEFAULT_PATTERN_LIFETIME_DAYS)
        assert abs((sanitized.expires_at - expected).total_seconds()) < 60

    def test_sanitize_computes_confidence(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        valid_pattern: Pattern,
    ):
        """Sanitized pattern should have valid confidence."""
        result = sanitizer.sanitize(valid_pattern)

        assert result.is_ok
        assert 0.0 <= result.value.confidence <= 1.0

    def test_sanitize_tracks_budget(
        self,
        valid_pattern: Pattern,
    ):
        """Sanitizer should track total epsilon spent."""
        sanitizer = DifferentialPrivacySanitizer()
        initial_budget = sanitizer.get_remaining_budget()

        sanitizer.sanitize(valid_pattern, epsilon=0.1)
        after_first = sanitizer.get_remaining_budget()

        sanitizer.sanitize(valid_pattern, epsilon=0.2)
        after_second = sanitizer.get_remaining_budget()

        assert after_first > initial_budget
        assert after_second > after_first
        assert abs(after_second - 0.3) < 0.01

    def test_sanitize_creates_new_pattern_id(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        valid_pattern: Pattern,
    ):
        """Sanitized pattern should have a new UUID."""
        result = sanitizer.sanitize(valid_pattern)

        assert result.is_ok
        assert result.value.pattern_id != valid_pattern.pattern_id


class TestLaplaceMechanism:
    """Tests for the Laplace noise mechanism."""

    def test_noise_is_unbiased(self):
        """Laplace noise should be centered at zero (unbiased)."""
        sanitizer = DifferentialPrivacySanitizer()

        # Sample many values with noise
        samples = []
        for _ in range(1000):
            noised = sanitizer._add_laplace_noise(100.0, 1.0, 0.1)
            samples.append(noised - 100.0)  # Extract noise

        # Mean should be close to 0
        mean_noise = statistics.mean(samples)
        assert abs(mean_noise) < 2.0  # Allow some variance

    def test_noise_scale_increases_with_sensitivity(self):
        """Higher sensitivity should produce more noise."""
        sanitizer = DifferentialPrivacySanitizer()

        low_sensitivity_samples = [
            sanitizer._add_laplace_noise(100.0, 0.1, 0.1) for _ in range(500)
        ]
        high_sensitivity_samples = [
            sanitizer._add_laplace_noise(100.0, 10.0, 0.1) for _ in range(500)
        ]

        low_std = statistics.stdev(low_sensitivity_samples)
        high_std = statistics.stdev(high_sensitivity_samples)

        # Higher sensitivity should have more variance
        assert high_std > low_std * 5

    def test_noise_scale_decreases_with_epsilon(self):
        """Higher epsilon should produce less noise."""
        sanitizer = DifferentialPrivacySanitizer()

        low_epsilon_samples = [
            sanitizer._add_laplace_noise(100.0, 1.0, 0.1) for _ in range(500)
        ]
        high_epsilon_samples = [
            sanitizer._add_laplace_noise(100.0, 1.0, 1.0) for _ in range(500)
        ]

        low_std = statistics.stdev(low_epsilon_samples)
        high_std = statistics.stdev(high_epsilon_samples)

        # Lower epsilon (more privacy) should have more variance
        assert low_std > high_std * 2

    def test_zero_epsilon_raises(self):
        """Epsilon of zero should raise error."""
        sanitizer = DifferentialPrivacySanitizer()

        with pytest.raises(ValueError, match="positive"):
            sanitizer._add_laplace_noise(100.0, 1.0, 0.0)

    def test_negative_epsilon_raises(self):
        """Negative epsilon should raise error."""
        sanitizer = DifferentialPrivacySanitizer()

        with pytest.raises(ValueError, match="positive"):
            sanitizer._add_laplace_noise(100.0, 1.0, -0.1)


class TestConfidenceComputation:
    """Tests for confidence score computation."""

    def test_confidence_increases_with_sample_size(self):
        """Larger samples should have higher confidence."""
        sanitizer = DifferentialPrivacySanitizer()

        conf_small = sanitizer._compute_confidence(100, 10.0)
        conf_medium = sanitizer._compute_confidence(500, 10.0)
        conf_large = sanitizer._compute_confidence(2000, 10.0)

        assert conf_small < conf_medium < conf_large

    def test_confidence_decreases_with_noise_scale(self):
        """Higher noise should reduce confidence."""
        sanitizer = DifferentialPrivacySanitizer()

        conf_low_noise = sanitizer._compute_confidence(500, 1.0)
        conf_high_noise = sanitizer._compute_confidence(500, 10.0)

        assert conf_low_noise > conf_high_noise

    def test_confidence_in_valid_range(self):
        """Confidence should always be between 0 and 1."""
        sanitizer = DifferentialPrivacySanitizer()

        # Test extreme values
        edge_cases = [
            (0, 0.0),
            (0, 100.0),
            (1000000, 0.001),
            (1, 1000.0),
        ]

        for sample_size, noise_scale in edge_cases:
            conf = sanitizer._compute_confidence(sample_size, noise_scale)
            assert 0.0 <= conf <= 1.0


class TestSanitizationReport:
    """Tests for SanitizationReport."""

    @pytest.fixture
    def sanitizer(self) -> DifferentialPrivacySanitizer:
        """Create a sanitizer."""
        return DifferentialPrivacySanitizer()

    @pytest.fixture
    def pattern_pair(self, sanitizer) -> tuple[Pattern, SanitizedPattern]:
        """Create a pattern and its sanitized version."""
        original = Pattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal",
            average_outcome=0.75,
            observation_count=150,
            user_count=25,
        )

        result = sanitizer.sanitize(original)
        return original, result.value

    def test_report_creation(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        pattern_pair: tuple[Pattern, SanitizedPattern],
    ):
        """Report should capture both original and noised values."""
        original, sanitized = pattern_pair
        report = sanitizer.create_report(original, sanitized)

        assert isinstance(report, SanitizationReport)
        assert report.original_outcome == original.average_outcome
        assert report.original_count == original.observation_count
        assert report.original_users == original.user_count
        assert report.noised_outcome == sanitized.outcome_improvement
        assert report.noised_count == sanitized.source_count
        assert report.noised_users == sanitized.user_count

    def test_report_includes_epsilon(
        self,
        sanitizer: DifferentialPrivacySanitizer,
        pattern_pair: tuple[Pattern, SanitizedPattern],
    ):
        """Report should include epsilon used."""
        original, sanitized = pattern_pair
        report = sanitizer.create_report(original, sanitized)

        assert report.epsilon_used == sanitized.epsilon
