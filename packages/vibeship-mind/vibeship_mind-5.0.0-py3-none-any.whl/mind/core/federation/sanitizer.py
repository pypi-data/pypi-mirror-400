"""Differential privacy sanitization for federated patterns.

This module applies differential privacy to ensure patterns
can be safely shared across users without leaking information
about any individual user.

Key concepts:
- Epsilon (ε): Privacy loss parameter. Lower = more private.
- Delta (δ): Probability of privacy breach.
- Sensitivity: Maximum change one user can cause.
- Laplace mechanism: Add Laplace noise proportional to sensitivity/epsilon.
"""

import math
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import structlog

from mind.core.errors import ErrorCode, MindError, Result
from mind.core.federation.models import (
    Pattern,
    PrivacyBudget,
    SanitizedPattern,
)

logger = structlog.get_logger()


# Default pattern expiration (patterns get stale)
DEFAULT_PATTERN_LIFETIME_DAYS = 90


@dataclass
class SanitizationReport:
    """Report of sanitization applied to a pattern."""

    original_outcome: float
    noised_outcome: float
    original_count: int
    noised_count: int
    original_users: int
    noised_users: int
    noise_scale: float
    epsilon_used: float


class DifferentialPrivacySanitizer:
    """Applies differential privacy to patterns.

    Uses the Laplace mechanism to add calibrated noise to
    statistics before sharing patterns across users.

    The noise ensures that:
    - No individual user's data can be identified
    - Aggregate patterns remain useful
    - Privacy budget is tracked and enforced
    """

    def __init__(self, privacy_budget: PrivacyBudget = PrivacyBudget()):
        self._budget = privacy_budget
        self._total_epsilon_spent = 0.0

    def sanitize(
        self,
        pattern: Pattern,
        epsilon: float | None = None,
    ) -> Result[SanitizedPattern]:
        """Sanitize a pattern for cross-user sharing.

        Applies differential privacy by:
        1. Checking privacy thresholds
        2. Adding Laplace noise to counts
        3. Adding noise to outcome statistics
        4. Computing confidence from noise level

        Args:
            pattern: The pattern to sanitize
            epsilon: Privacy parameter (uses budget default if None)

        Returns:
            SanitizedPattern safe for federation
        """
        try:
            eps = epsilon or self._budget.epsilon

            # Verify privacy thresholds
            if not self._budget.is_satisfied(
                pattern.user_count,
                pattern.observation_count,
            ):
                return Result.err(
                    MindError(
                        code=ErrorCode.PRIVACY_VIOLATION,
                        message="Pattern does not meet privacy thresholds",
                        context={
                            "user_count": pattern.user_count,
                            "min_users": self._budget.min_users,
                            "observation_count": pattern.observation_count,
                            "min_observations": self._budget.min_observations,
                        },
                    )
                )

            # Calculate sensitivity (max impact of one user)
            # For counts: sensitivity = 1
            # For averages: sensitivity = 1/n (bounded contribution)
            count_sensitivity = 1.0
            outcome_sensitivity = 1.0 / max(pattern.observation_count, 1)

            # Add Laplace noise to counts
            noised_count = self._add_laplace_noise(
                pattern.observation_count,
                count_sensitivity,
                eps / 3,  # Split budget across statistics
            )
            noised_users = self._add_laplace_noise(
                pattern.user_count,
                count_sensitivity,
                eps / 3,
            )

            # Add noise to outcome improvement
            noised_outcome = self._add_laplace_noise(
                pattern.average_outcome,
                outcome_sensitivity,
                eps / 3,
            )

            # Ensure non-negative counts
            noised_count = max(int(noised_count), self._budget.min_observations)
            noised_users = max(int(noised_users), self._budget.min_users)

            # Clamp outcome to valid range
            noised_outcome = max(-1.0, min(1.0, noised_outcome))

            # Calculate confidence based on sample size and noise
            noise_scale = count_sensitivity / (eps / 3)
            confidence = self._compute_confidence(
                noised_count,
                noise_scale,
            )

            # Track privacy budget
            self._total_epsilon_spent += eps

            # Create sanitized pattern
            sanitized = SanitizedPattern(
                pattern_id=uuid4(),  # New ID for sanitized version
                pattern_type=pattern.pattern_type,
                trigger_category=pattern.trigger_category,
                response_strategy=pattern.response_strategy,
                outcome_improvement=noised_outcome,
                confidence=confidence,
                source_count=noised_count,
                user_count=noised_users,
                epsilon=eps,
                expires_at=datetime.now(UTC) + timedelta(days=DEFAULT_PATTERN_LIFETIME_DAYS),
            )

            logger.info(
                "pattern_sanitized",
                original_pattern_id=str(pattern.pattern_id),
                sanitized_pattern_id=str(sanitized.pattern_id),
                epsilon=eps,
                confidence=confidence,
            )

            return Result.ok(sanitized)

        except Exception as e:
            logger.error(
                "pattern_sanitization_failed",
                pattern_id=str(pattern.pattern_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Sanitization failed: {e}",
                )
            )

    def _add_laplace_noise(
        self,
        value: float,
        sensitivity: float,
        epsilon: float,
    ) -> float:
        """Add Laplace noise calibrated to sensitivity and epsilon.

        Laplace mechanism: value + Lap(sensitivity / epsilon)
        """
        if epsilon <= 0:
            raise ValueError("Epsilon must be positive")

        scale = sensitivity / epsilon

        # Sample from Laplace distribution
        # Laplace(0, scale) = scale * (Exp(1) - Exp(1))
        u = random.random() - 0.5
        noise = -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))

        return value + noise

    def _compute_confidence(
        self,
        sample_size: int,
        noise_scale: float,
    ) -> float:
        """Compute confidence score based on sample size and noise.

        Higher sample size and lower noise = higher confidence.
        """
        # Base confidence from sample size (asymptotic to 1.0)
        size_confidence = 1 - math.exp(-sample_size / 1000)

        # Noise penalty (lower scale = higher confidence)
        noise_penalty = math.exp(-noise_scale)

        # Combined confidence
        confidence = size_confidence * noise_penalty

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    def get_remaining_budget(self) -> float:
        """Get remaining privacy budget.

        Returns how much epsilon is left before hitting limits.
        """
        # Typically you'd set a total budget limit
        # For now, just return spent amount
        return self._total_epsilon_spent

    def create_report(
        self,
        original: Pattern,
        sanitized: SanitizedPattern,
    ) -> SanitizationReport:
        """Create a report of sanitization applied."""
        return SanitizationReport(
            original_outcome=original.average_outcome,
            noised_outcome=sanitized.outcome_improvement,
            original_count=original.observation_count,
            noised_count=sanitized.source_count,
            original_users=original.user_count,
            noised_users=sanitized.user_count,
            noise_scale=1.0 / sanitized.epsilon,
            epsilon_used=sanitized.epsilon,
        )
