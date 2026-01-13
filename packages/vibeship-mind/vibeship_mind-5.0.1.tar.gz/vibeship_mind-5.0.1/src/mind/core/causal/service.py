"""Causal inference service for Mind v5.

This service provides causal reasoning capabilities:
- Record causal relationships when decisions are made
- Query for outcome predictions based on similar contexts
- Calculate precise attributions using causal paths
- Support counterfactual analysis
- Formal causal inference with DoWhy integration
- Robustness testing with refutation methods
"""

import hashlib
from dataclasses import dataclass
from uuid import UUID

import structlog

from mind.core.causal.models import (
    CausalAttribution,
    CounterfactualQuery,
    CounterfactualResult,
)
from mind.core.decision.models import DecisionTrace, Outcome
from mind.core.errors import ErrorCode, MindError, Result
from mind.core.memory.models import Memory
from mind.observability.tracing import get_tracer

logger = structlog.get_logger()

# Tracer for causal inference operations
_tracer = get_tracer("mind.causal")


@dataclass
class PredictedOutcome:
    """Prediction for what outcome a context might lead to."""

    expected_quality: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    similar_count: int
    reasoning: str


class CausalInferenceService:
    """Service for causal inference operations.

    This service orchestrates causal graph operations and provides
    high-level causal reasoning capabilities. It works with:
    - FalkorDB for graph storage and queries
    - Memory repository for context retrieval
    - Decision repository for historical patterns
    """

    def __init__(self, graph_repository, memory_repository=None, decision_repository=None):
        """Initialize the causal inference service.

        Args:
            graph_repository: CausalGraphRepository for graph operations
            memory_repository: Optional MemoryRepository for content access
            decision_repository: Optional DecisionRepository for history
        """
        self._graph = graph_repository
        self._memories = memory_repository
        self._decisions = decision_repository

    async def record_decision_context(
        self,
        trace: DecisionTrace,
        memories: list[Memory],
    ) -> Result[None]:
        """Record the causal context for a decision.

        Creates nodes and edges in the causal graph representing:
        - Each memory that influenced the decision
        - The decision itself
        - INFLUENCED edges from memories to decision

        Args:
            trace: The decision trace
            memories: Memories that influenced the decision

        Returns:
            Result indicating success or failure
        """
        try:
            # Add decision node
            result = await self._graph.add_decision_node(
                trace_id=trace.trace_id,
                user_id=trace.user_id,
                decision_type=trace.decision_type,
                confidence=trace.confidence,
            )
            if not result.is_ok:
                return result

            # Add memory nodes and influence edges
            for i, memory in enumerate(memories):
                # Add memory node (may already exist)
                content_hash = hashlib.sha256(memory.content.encode()).hexdigest()[:16]

                result = await self._graph.add_memory_node(
                    memory_id=memory.memory_id,
                    user_id=memory.user_id,
                    content_hash=content_hash,
                    temporal_level=memory.temporal_level.value,
                    salience=memory.effective_salience,
                )
                if not result.is_ok:
                    logger.warning(
                        "causal_memory_node_failed",
                        memory_id=str(memory.memory_id),
                        error=str(result.error),
                    )
                    continue

                # Get influence score from trace
                influence_score = trace.memory_scores.get(
                    str(memory.memory_id),
                    1.0 / (i + 1),  # Default to rank-based score
                )

                # Link memory to decision
                result = await self._graph.link_memory_to_decision(
                    memory_id=memory.memory_id,
                    trace_id=trace.trace_id,
                    influence_score=influence_score,
                    rank=i + 1,
                )
                if not result.is_ok:
                    logger.warning(
                        "causal_link_failed",
                        memory_id=str(memory.memory_id),
                        trace_id=str(trace.trace_id),
                    )

            logger.info(
                "causal_context_recorded",
                trace_id=str(trace.trace_id),
                memory_count=len(memories),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "causal_context_recording_failed",
                trace_id=str(trace.trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to record causal context: {e}",
                )
            )

    async def record_outcome(
        self,
        trace_id: UUID,
        outcome: Outcome,
    ) -> Result[None]:
        """Record an outcome and link it to the decision.

        Creates the outcome node and LED_TO edge from decision.

        Args:
            trace_id: The decision trace ID
            outcome: The observed outcome

        Returns:
            Result indicating success or failure
        """
        try:
            # Add outcome node
            result = await self._graph.add_outcome_node(
                trace_id=trace_id,
                quality=outcome.quality,
                signal=outcome.signal,
            )
            if not result.is_ok:
                return result

            # Link decision to outcome
            result = await self._graph.link_decision_to_outcome(trace_id)
            if not result.is_ok:
                return result

            logger.info(
                "causal_outcome_recorded",
                trace_id=str(trace_id),
                quality=outcome.quality,
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "causal_outcome_recording_failed",
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to record outcome: {e}",
                )
            )

    async def get_memory_attribution(
        self,
        trace_id: UUID,
        use_shapley: bool = False,
    ) -> Result[CausalAttribution]:
        """Calculate attribution of outcome to memories.

        Uses the causal graph to determine how much each memory
        contributed to the outcome.

        Args:
            trace_id: The decision/outcome trace
            use_shapley: Use Shapley values for fair attribution (slower but more accurate)

        Returns:
            CausalAttribution with per-memory contributions
        """
        try:
            result = await self._graph.get_causal_attribution(trace_id)
            if not result.is_ok:
                return Result.err(result.error)

            attributions = result.value

            # Build attribution dict from graph data
            attr_dict = {a.memory_id: a.contribution for a in attributions}
            memory_ids = list(attr_dict.keys())

            # Get outcome quality if available
            outcome_result = await self._graph.get_outcome_quality(trace_id)
            outcome_quality = outcome_result.value if outcome_result.is_ok else 0.0

            if use_shapley and memory_ids:
                # Use Shapley values for fair attribution
                from mind.core.causal.shapley import compute_shapley_attribution

                # Use retrieval scores as saliences
                saliences = {mid: max(0.1, score) for mid, score in attr_dict.items()}

                shapley_result = await compute_shapley_attribution(
                    trace_id=trace_id,
                    memory_ids=memory_ids,
                    memory_saliences=saliences,
                    outcome_quality=outcome_quality,
                )

                if shapley_result.is_ok:
                    return shapley_result
                # Fall back to simple attribution if Shapley fails
                logger.warning(
                    "shapley_fallback",
                    trace_id=str(trace_id),
                    error=str(shapley_result.error),
                )

            # Simple attribution: normalize retrieval scores
            total = sum(attr_dict.values())
            if total > 0:
                attr_dict = {mid: contrib / total for mid, contrib in attr_dict.items()}
                total = 1.0

            return Result.ok(
                CausalAttribution(
                    trace_id=trace_id,
                    outcome_quality=outcome_quality,
                    attributions=attr_dict,
                    total_attributed=total,
                    method="retrieval_score",
                )
            )

        except Exception as e:
            logger.error(
                "causal_attribution_failed",
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to calculate attribution: {e}",
                )
            )

    async def predict_outcome(
        self,
        user_id: UUID,
        memory_ids: list[UUID],
        decision_type: str | None = None,
    ) -> Result[PredictedOutcome]:
        """Predict likely outcome for a given context.

        Uses historical causal patterns to predict what outcome
        might result from using these memories for a decision.

        Args:
            user_id: User making the decision
            memory_ids: Memories being used as context
            decision_type: Optional type of decision

        Returns:
            PredictedOutcome with expected quality and confidence
        """
        with _tracer.start_as_current_span("predict_outcome") as span:
            span.set_attribute("user_id", str(user_id))
            span.set_attribute("memory_count", len(memory_ids))
            if decision_type:
                span.set_attribute("decision_type", decision_type)

            try:
                # Find similar historical decisions
                result = await self._graph.find_similar_outcomes(
                    memory_ids=memory_ids,
                    limit=20,
                )

                if not result.is_ok:
                    span.record_exception(result.error)
                    return Result.err(result.error)

                similar = result.value
                span.set_attribute("similar_count", len(similar))

                if not similar:
                    return Result.ok(
                        PredictedOutcome(
                            expected_quality=0.0,
                            confidence=0.1,
                            similar_count=0,
                            reasoning="No similar historical decisions found",
                        )
                    )

                # Calculate weighted average outcome
                total_weight = 0.0
                weighted_sum = 0.0

                for s in similar:
                    weight = s.get("overlap_count", 1) * s.get("total_score", 1.0)
                    outcome_quality = s.get("outcome_quality", 0.0)
                    weighted_sum += weight * outcome_quality
                    total_weight += weight

                expected_quality = weighted_sum / total_weight if total_weight > 0 else 0.0

                # Confidence based on number of similar decisions and overlap
                confidence = min(0.9, len(similar) / 20.0 * 0.5 + 0.3)

                span.set_attribute("expected_quality", expected_quality)
                span.set_attribute("confidence", confidence)

                return Result.ok(
                    PredictedOutcome(
                        expected_quality=expected_quality,
                        confidence=confidence,
                        similar_count=len(similar),
                        reasoning=f"Based on {len(similar)} similar decisions with average outcome quality",
                    )
                )

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "causal_prediction_failed",
                    user_id=str(user_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Failed to predict outcome: {e}",
                    )
                )

    async def counterfactual_analysis(
        self,
        query: CounterfactualQuery,
    ) -> Result[CounterfactualResult]:
        """Perform counterfactual analysis.

        Answers "what if" questions about alternative contexts:
        - What if we had used different memories?
        - Would the outcome have been better or worse?

        Args:
            query: The counterfactual query

        Returns:
            CounterfactualResult with predicted outcome
        """
        with _tracer.start_as_current_span("counterfactual_analysis") as span:
            span.set_attribute("user_id", str(query.user_id))
            span.set_attribute("original_trace_id", str(query.original_trace_id))
            span.set_attribute("hypothetical_memory_count", len(query.hypothetical_memory_ids))

            try:
                # Get prediction for hypothetical context
                prediction_result = await self.predict_outcome(
                    user_id=query.user_id,
                    memory_ids=query.hypothetical_memory_ids,
                    decision_type=query.decision_type,
                )

                if not prediction_result.is_ok:
                    span.record_exception(prediction_result.error)
                    return Result.err(prediction_result.error)

                prediction = prediction_result.value

                span.set_attribute("predicted_quality", prediction.expected_quality)
                span.set_attribute("confidence", prediction.confidence)

                return Result.ok(
                    CounterfactualResult(
                        query=query,
                        predicted_outcome_quality=prediction.expected_quality,
                        confidence=prediction.confidence,
                        similar_historical_count=prediction.similar_count,
                        average_historical_outcome=prediction.expected_quality,
                        reasoning=prediction.reasoning,
                    )
                )

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "counterfactual_analysis_failed",
                    trace_id=str(query.original_trace_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Counterfactual analysis failed: {e}",
                    )
                )

    async def get_memory_success_rate(
        self,
        memory_id: UUID,
    ) -> Result[dict]:
        """Get success rate statistics for a memory.

        Returns how often this memory has led to positive outcomes.

        Args:
            memory_id: The memory to analyze

        Returns:
            Dict with success rate statistics
        """
        return await self._graph.get_memory_success_rate(memory_id)

    # =========================================================================
    # DoWhy Integration Methods
    # =========================================================================

    async def analyze_causal_effects(
        self,
        user_id: UUID,
        treatment: str = "used_identity_memories",
        outcome: str = "outcome_quality",
        min_traces: int = 20,
    ) -> Result[dict]:
        """Analyze causal effects using DoWhy formal inference.

        Uses historical decision data to estimate the true causal effect
        of memory usage on outcomes, controlling for confounders.

        Args:
            user_id: User to analyze
            treatment: Which memory feature to analyze
            outcome: Outcome variable
            min_traces: Minimum traces needed for analysis

        Returns:
            Dict with causal effect estimate and interpretation
        """
        from mind.core.causal.dowhy_integration import get_dowhy_analyzer

        analyzer = get_dowhy_analyzer()

        if not analyzer.is_available():
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="DoWhy not installed. Install with: pip install mind[ml]",
                )
            )

        with _tracer.start_as_current_span("analyze_causal_effects") as span:
            span.set_attribute("user_id", str(user_id))
            span.set_attribute("treatment", treatment)

            try:
                # Get decision traces for this user
                traces_result = await self._get_user_decision_traces(user_id, limit=500)
                if not traces_result.is_ok:
                    return Result.err(traces_result.error)

                traces = traces_result.value

                if len(traces) < min_traces:
                    return Result.err(
                        MindError(
                            code=ErrorCode.INVALID_INPUT,
                            message=f"Need at least {min_traces} decisions for causal analysis, have {len(traces)}",
                        )
                    )

                # Prepare data for DoWhy
                data = analyzer.prepare_decision_data(traces)
                if data is None:
                    return Result.err(
                        MindError(
                            code=ErrorCode.INTERNAL_ERROR,
                            message="Failed to prepare data for causal analysis",
                        )
                    )

                # Estimate causal effect
                effect_result = await analyzer.estimate_memory_effect(
                    data=data,
                    treatment=treatment,
                    outcome=outcome,
                )

                if not effect_result.is_ok:
                    return Result.err(effect_result.error)

                effect = effect_result.value

                # Build interpretation
                if effect.is_significant:
                    if effect.effect > 0:
                        interpretation = (
                            f"Using {treatment} has a positive causal effect on {outcome}. "
                            f"Each unit increase in {treatment} causes a {effect.effect:.3f} "
                            f"improvement in {outcome} (95% CI: {effect.confidence_interval[0]:.3f} "
                            f"to {effect.confidence_interval[1]:.3f})."
                        )
                    else:
                        interpretation = (
                            f"Using {treatment} has a negative causal effect on {outcome}. "
                            f"Each unit increase in {treatment} causes a {abs(effect.effect):.3f} "
                            f"decrease in {outcome}."
                        )
                else:
                    interpretation = (
                        f"No statistically significant causal effect found for {treatment} on {outcome}. "
                        f"Effect estimate: {effect.effect:.3f}, but confidence interval includes zero."
                    )

                span.set_attribute("effect", effect.effect)
                span.set_attribute("is_significant", effect.is_significant)

                logger.info(
                    "causal_effects_analyzed",
                    user_id=str(user_id),
                    treatment=treatment,
                    effect=effect.effect,
                    is_significant=effect.is_significant,
                )

                return Result.ok({
                    "treatment": treatment,
                    "outcome": outcome,
                    "effect": effect.effect,
                    "confidence_interval": effect.confidence_interval,
                    "is_significant": effect.is_significant,
                    "method": effect.method,
                    "interpretation": interpretation,
                    "sample_size": len(traces),
                })

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "causal_effects_analysis_failed",
                    user_id=str(user_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Causal effects analysis failed: {e}",
                    )
                )

    async def validate_causal_claims(
        self,
        user_id: UUID,
        treatment: str = "used_identity_memories",
        outcome: str = "outcome_quality",
    ) -> Result[dict]:
        """Validate causal claims with refutation tests.

        Runs multiple robustness checks to ensure causal estimates
        are reliable and not spurious correlations.

        Args:
            user_id: User to analyze
            treatment: Treatment variable
            outcome: Outcome variable

        Returns:
            Dict with refutation test results and overall validity
        """
        from mind.core.causal.dowhy_integration import get_dowhy_analyzer

        analyzer = get_dowhy_analyzer()

        if not analyzer.is_available():
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="DoWhy not installed",
                )
            )

        with _tracer.start_as_current_span("validate_causal_claims") as span:
            span.set_attribute("user_id", str(user_id))

            try:
                # First get the effect estimate
                effect_result = await self.analyze_causal_effects(
                    user_id=user_id,
                    treatment=treatment,
                    outcome=outcome,
                )

                if not effect_result.is_ok:
                    return Result.err(effect_result.error)

                effect_data = effect_result.value

                # Get traces for refutation
                traces_result = await self._get_user_decision_traces(user_id, limit=500)
                if not traces_result.is_ok:
                    return Result.err(traces_result.error)

                data = analyzer.prepare_decision_data(traces_result.value)

                # Run refutation tests
                refute_result = await analyzer.refute_estimate(
                    data=data,
                    treatment=treatment,
                    outcome=outcome,
                    original_effect=effect_data["effect"],
                )

                if not refute_result.is_ok:
                    return Result.err(refute_result.error)

                refutations = refute_result.value

                # Summarize results
                tests_passed = sum(1 for r in refutations if r.passed)
                tests_total = len(refutations)
                is_robust = tests_passed >= tests_total * 0.66  # 2/3 must pass

                span.set_attribute("tests_passed", tests_passed)
                span.set_attribute("is_robust", is_robust)

                logger.info(
                    "causal_claims_validated",
                    user_id=str(user_id),
                    tests_passed=tests_passed,
                    tests_total=tests_total,
                    is_robust=is_robust,
                )

                return Result.ok({
                    "original_effect": effect_data["effect"],
                    "is_significant": effect_data["is_significant"],
                    "refutation_tests": [
                        {
                            "test": r.test_name,
                            "passed": r.passed,
                            "refuted_effect": r.refuted_effect,
                            "interpretation": r.interpretation,
                        }
                        for r in refutations
                    ],
                    "tests_passed": tests_passed,
                    "tests_total": tests_total,
                    "is_robust": is_robust,
                    "recommendation": (
                        "Causal claim is robust - safe to use for decisions"
                        if is_robust
                        else "Causal claim needs more evidence - use with caution"
                    ),
                })

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "causal_validation_failed",
                    user_id=str(user_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.INTERNAL_ERROR,
                        message=f"Causal validation failed: {e}",
                    )
                )

    async def _get_user_decision_traces(
        self,
        user_id: UUID,
        limit: int = 500,
    ) -> Result[list[dict]]:
        """Get decision traces for a user formatted for DoWhy.

        Internal helper to fetch and format decision data.
        """
        try:
            # Query the graph for decision traces with outcomes
            result = await self._graph.get_user_decisions_with_outcomes(
                user_id=user_id,
                limit=limit,
            )

            if not result.is_ok:
                # If graph doesn't have this method, return empty
                return Result.ok([])

            return result

        except Exception:
            # Fallback: return empty list if method doesn't exist
            return Result.ok([])
