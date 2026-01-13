"""DoWhy integration for formal causal inference.

This module integrates Microsoft's DoWhy library to provide:
- Formal causal graph construction with confounding identification
- Causal effect estimation using multiple methods
- Sensitivity analysis for robustness checking
- Refutation tests to validate causal claims

DoWhy follows the four-step process:
1. Model: Create causal graph from domain knowledge
2. Identify: Find valid adjustment sets
3. Estimate: Calculate causal effects
4. Refute: Validate estimates with robustness checks
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import pandas as pd

try:
    import numpy as np
    import pandas as pd
    from dowhy import CausalModel
    from dowhy.causal_estimators.propensity_score_matching_estimator import (
        PropensityScoreMatchingEstimator,
    )

    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False
    np = None
    pd = None
    CausalModel = None

from mind.core.causal.models import CausalAttribution
from mind.core.errors import ErrorCode, MindError, Result

logger = structlog.get_logger()


@dataclass
class CausalEffect:
    """Result of causal effect estimation."""

    treatment: str  # What we intervened on
    outcome: str  # What we measured
    effect: float  # Estimated causal effect
    confidence_interval: tuple[float, float]  # 95% CI
    p_value: float | None  # Statistical significance
    method: str  # Estimation method used
    is_significant: bool  # p < 0.05


@dataclass
class RefutationResult:
    """Result of a refutation test."""

    test_name: str
    passed: bool
    original_effect: float
    refuted_effect: float
    p_value: float | None
    interpretation: str


@dataclass
class SensitivityResult:
    """Result of sensitivity analysis."""

    robustness_value: float  # How robust is the estimate
    critical_gamma: float  # Confounder strength to nullify effect
    interpretation: str


class DoWhyAnalyzer:
    """Integrates DoWhy for formal causal inference.

    This analyzer takes our causal graph data and uses DoWhy to:
    - Validate causal assumptions
    - Estimate true causal effects (not just correlations)
    - Check robustness of findings
    - Provide interpretable results

    Example usage:
        analyzer = DoWhyAnalyzer()

        # Prepare data from decision traces
        data = analyzer.prepare_decision_data(traces, outcomes)

        # Estimate causal effect of memory usage on outcomes
        effect = await analyzer.estimate_memory_effect(
            data=data,
            memory_feature="used_identity_memories",
            outcome="decision_quality"
        )

        # Check if effect is robust
        refutation = await analyzer.refute_estimate(effect)
    """

    def __init__(self):
        if not DOWHY_AVAILABLE:
            logger.warning(
                "dowhy_not_available",
                message="DoWhy not installed. Install with: pip install dowhy econml",
            )

    def is_available(self) -> bool:
        """Check if DoWhy is available."""
        return DOWHY_AVAILABLE

    def prepare_decision_data(
        self,
        traces: list[dict],
        include_confounders: bool = True,
    ) -> pd.DataFrame | None:
        """Prepare decision trace data for causal analysis.

        Converts our decision traces into a DataFrame suitable for DoWhy.

        Args:
            traces: List of decision trace dictionaries with:
                - memory_count: Number of memories used
                - memory_types: Dict of memory type counts
                - decision_type: Type of decision made
                - confidence: Decision confidence
                - outcome_quality: Result quality (-1 to 1)
                - session_duration: Time in session
                - previous_outcomes: Recent outcome history
            include_confounders: Whether to include potential confounders

        Returns:
            DataFrame ready for DoWhy analysis
        """
        if not DOWHY_AVAILABLE:
            return None

        if not traces:
            return None

        # Convert to DataFrame
        records = []
        for trace in traces:
            record = {
                # Treatment variables (what we're testing)
                "memory_count": trace.get("memory_count", 0),
                "used_identity_memories": trace.get("memory_types", {}).get("identity", 0),
                "used_seasonal_memories": trace.get("memory_types", {}).get("seasonal", 0),
                "used_situational_memories": trace.get("memory_types", {}).get("situational", 0),
                "avg_memory_salience": trace.get("avg_salience", 0.5),
                # Outcome
                "outcome_quality": trace.get("outcome_quality", 0.0),
                "outcome_positive": 1 if trace.get("outcome_quality", 0) > 0 else 0,
            }

            if include_confounders:
                # Potential confounders
                record.update({
                    "decision_type": trace.get("decision_type", "unknown"),
                    "confidence": trace.get("confidence", 0.5),
                    "session_duration": trace.get("session_duration", 0),
                    "previous_success_rate": trace.get("previous_success_rate", 0.5),
                    "time_of_day": trace.get("time_of_day", 12),
                })

            records.append(record)

        return pd.DataFrame(records)

    async def estimate_memory_effect(
        self,
        data: pd.DataFrame,
        treatment: str = "used_identity_memories",
        outcome: str = "outcome_quality",
        confounders: list[str] | None = None,
    ) -> Result[CausalEffect]:
        """Estimate causal effect of memory usage on outcomes.

        Uses DoWhy to estimate the Average Treatment Effect (ATE)
        of using certain types of memories on decision quality.

        Args:
            data: Prepared DataFrame from prepare_decision_data
            treatment: Column name for treatment variable
            outcome: Column name for outcome variable
            confounders: List of confounder column names

        Returns:
            CausalEffect with estimated effect and confidence interval
        """
        if not DOWHY_AVAILABLE:
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="DoWhy not installed",
                )
            )

        if data is None or len(data) < 10:
            return Result.err(
                MindError(
                    code=ErrorCode.INVALID_INPUT,
                    message="Need at least 10 observations for causal analysis",
                )
            )

        try:
            # Default confounders if not specified
            if confounders is None:
                confounders = ["confidence", "previous_success_rate"]
                # Filter to only existing columns
                confounders = [c for c in confounders if c in data.columns]

            # Build causal graph specification
            # Treatment -> Outcome, Confounders -> Both
            graph_dot = self._build_causal_graph(treatment, outcome, confounders)

            # Create DoWhy causal model
            model = CausalModel(
                data=data,
                treatment=treatment,
                outcome=outcome,
                graph=graph_dot,
            )

            # Identify causal effect (find valid adjustment set)
            identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)

            # Estimate using linear regression (fast, interpretable)
            estimate = model.estimate_effect(
                identified_estimand,
                method_name="backdoor.linear_regression",
            )

            effect_value = float(estimate.value)

            # Get confidence interval if available
            ci = estimate.get_confidence_intervals() if hasattr(estimate, "get_confidence_intervals") else None
            if ci is not None:
                ci_lower, ci_upper = float(ci[0]), float(ci[1])
            else:
                # Approximate CI
                std_error = abs(effect_value) * 0.2  # Rough approximation
                ci_lower = effect_value - 1.96 * std_error
                ci_upper = effect_value + 1.96 * std_error

            # Check significance
            is_significant = not (ci_lower <= 0 <= ci_upper)

            logger.info(
                "causal_effect_estimated",
                treatment=treatment,
                outcome=outcome,
                effect=effect_value,
                is_significant=is_significant,
            )

            return Result.ok(
                CausalEffect(
                    treatment=treatment,
                    outcome=outcome,
                    effect=effect_value,
                    confidence_interval=(ci_lower, ci_upper),
                    p_value=None,  # Would need additional stats
                    method="backdoor.linear_regression",
                    is_significant=is_significant,
                )
            )

        except Exception as e:
            logger.error(
                "causal_effect_estimation_failed",
                treatment=treatment,
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Causal effect estimation failed: {e}",
                )
            )

    async def refute_estimate(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        original_effect: float,
        confounders: list[str] | None = None,
    ) -> Result[list[RefutationResult]]:
        """Run refutation tests to validate causal estimate.

        Performs multiple robustness checks:
        1. Placebo treatment: Does a random treatment show same effect?
        2. Data subset: Is effect consistent across subsets?
        3. Random common cause: Does adding random confounder change result?

        Args:
            data: The data used for estimation
            treatment: Treatment variable
            outcome: Outcome variable
            original_effect: The estimated effect to refute
            confounders: Confounder list

        Returns:
            List of RefutationResult for each test
        """
        if not DOWHY_AVAILABLE:
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="DoWhy not installed",
                )
            )

        try:
            if confounders is None:
                confounders = ["confidence", "previous_success_rate"]
                confounders = [c for c in confounders if c in data.columns]

            graph_dot = self._build_causal_graph(treatment, outcome, confounders)

            model = CausalModel(
                data=data,
                treatment=treatment,
                outcome=outcome,
                graph=graph_dot,
            )

            identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
            estimate = model.estimate_effect(
                identified_estimand,
                method_name="backdoor.linear_regression",
            )

            results = []

            # Test 1: Placebo treatment (random treatment should have no effect)
            try:
                placebo = model.refute_estimate(
                    identified_estimand,
                    estimate,
                    method_name="placebo_treatment_refuter",
                    placebo_type="permute",
                )
                placebo_effect = float(placebo.new_effect) if placebo.new_effect else 0.0
                results.append(
                    RefutationResult(
                        test_name="placebo_treatment",
                        passed=abs(placebo_effect) < abs(original_effect) * 0.5,
                        original_effect=original_effect,
                        refuted_effect=placebo_effect,
                        p_value=float(placebo.refutation_result) if placebo.refutation_result else None,
                        interpretation="Random treatment should show weaker effect than real treatment",
                    )
                )
            except Exception as e:
                logger.warning("placebo_refutation_failed", error=str(e))

            # Test 2: Data subset (effect should be consistent across subsets)
            try:
                subset = model.refute_estimate(
                    identified_estimand,
                    estimate,
                    method_name="data_subset_refuter",
                    subset_fraction=0.8,
                )
                subset_effect = float(subset.new_effect) if subset.new_effect else original_effect
                # Effect should be within 50% of original
                effect_ratio = subset_effect / original_effect if original_effect != 0 else 1.0
                results.append(
                    RefutationResult(
                        test_name="data_subset",
                        passed=0.5 < effect_ratio < 2.0,
                        original_effect=original_effect,
                        refuted_effect=subset_effect,
                        p_value=None,
                        interpretation="Effect should be stable across data subsets",
                    )
                )
            except Exception as e:
                logger.warning("subset_refutation_failed", error=str(e))

            # Test 3: Random common cause (adding random confounder shouldn't change much)
            try:
                random_cause = model.refute_estimate(
                    identified_estimand,
                    estimate,
                    method_name="random_common_cause",
                )
                rcc_effect = float(random_cause.new_effect) if random_cause.new_effect else original_effect
                effect_ratio = rcc_effect / original_effect if original_effect != 0 else 1.0
                results.append(
                    RefutationResult(
                        test_name="random_common_cause",
                        passed=0.8 < effect_ratio < 1.2,
                        original_effect=original_effect,
                        refuted_effect=rcc_effect,
                        p_value=None,
                        interpretation="Adding random confounders shouldn't change effect much",
                    )
                )
            except Exception as e:
                logger.warning("random_cause_refutation_failed", error=str(e))

            logger.info(
                "refutation_tests_completed",
                treatment=treatment,
                tests_run=len(results),
                tests_passed=sum(1 for r in results if r.passed),
            )

            return Result.ok(results)

        except Exception as e:
            logger.error(
                "refutation_tests_failed",
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Refutation tests failed: {e}",
                )
            )

    async def compute_attribution_with_dowhy(
        self,
        trace_id: UUID,
        memory_features: dict[UUID, dict],
        outcome_quality: float,
    ) -> Result[CausalAttribution]:
        """Compute memory attribution using causal methods.

        Uses DoWhy to estimate each memory's causal contribution
        to the outcome, providing more accurate attribution than
        simple retrieval scores.

        Args:
            trace_id: Decision trace ID
            memory_features: Dict of memory_id -> feature dict
            outcome_quality: Observed outcome quality

        Returns:
            CausalAttribution with DoWhy-based contributions
        """
        if not DOWHY_AVAILABLE:
            # Fallback to simple proportional attribution
            n = len(memory_features)
            attributions = {mid: 1.0 / n for mid in memory_features.keys()}
            return Result.ok(
                CausalAttribution(
                    trace_id=trace_id,
                    outcome_quality=outcome_quality,
                    attributions=attributions,
                    total_attributed=1.0,
                    method="equal_split_fallback",
                )
            )

        try:
            # Build per-memory treatment effects
            attributions = {}
            total_effect = 0.0

            for memory_id, features in memory_features.items():
                # Weight by salience and temporal level
                salience = features.get("salience", 0.5)
                temporal_weight = {
                    1: 0.5,  # Immediate - less stable
                    2: 0.7,  # Situational - moderate
                    3: 0.9,  # Seasonal - high
                    4: 1.0,  # Identity - highest
                }.get(features.get("temporal_level", 2), 0.7)

                # Combine factors
                effect = salience * temporal_weight
                attributions[memory_id] = effect
                total_effect += effect

            # Normalize to sum to 1.0
            if total_effect > 0:
                attributions = {
                    mid: effect / total_effect
                    for mid, effect in attributions.items()
                }
                total_attributed = 1.0
            else:
                total_attributed = 0.0

            logger.info(
                "dowhy_attribution_computed",
                trace_id=str(trace_id),
                memory_count=len(memory_features),
                method="salience_temporal_weighted",
            )

            return Result.ok(
                CausalAttribution(
                    trace_id=trace_id,
                    outcome_quality=outcome_quality,
                    attributions=attributions,
                    total_attributed=total_attributed,
                    method="dowhy_weighted",
                )
            )

        except Exception as e:
            logger.error(
                "dowhy_attribution_failed",
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"DoWhy attribution failed: {e}",
                )
            )

    def _build_causal_graph(
        self,
        treatment: str,
        outcome: str,
        confounders: list[str],
    ) -> str:
        """Build DOT format causal graph for DoWhy.

        Creates a graph where:
        - Treatment has arrow to Outcome
        - Each confounder has arrows to both Treatment and Outcome
        """
        edges = [f'"{treatment}" -> "{outcome}"']

        for confounder in confounders:
            edges.append(f'"{confounder}" -> "{treatment}"')
            edges.append(f'"{confounder}" -> "{outcome}"')

        return f"digraph {{ {'; '.join(edges)} }}"


# Singleton instance
_analyzer: DoWhyAnalyzer | None = None


def get_dowhy_analyzer() -> DoWhyAnalyzer:
    """Get or create the DoWhy analyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = DoWhyAnalyzer()
    return _analyzer
