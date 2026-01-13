"""Causal inference API endpoints."""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException

from mind.api.schemas.causal import (
    AttributionResponse,
    CounterfactualRequest,
    CounterfactualResponse,
    MemorySuccessRateResponse,
    PredictRequest,
    PredictResponse,
)
from mind.config import get_settings
from mind.core.causal.models import CounterfactualQuery
from mind.core.causal.service import CausalInferenceService
from mind.core.errors import ErrorCode
from mind.infrastructure.falkordb import CausalGraphRepository, get_falkordb_client
from mind.security.auth import AuthenticatedUser, get_auth_dependency

logger = structlog.get_logger()
router = APIRouter()


def _validate_user_access(
    request_user_id: UUID,
    authenticated_user: AuthenticatedUser | None,
) -> None:
    """Validate that authenticated user can access the requested user's data."""
    settings = get_settings()

    if settings.environment != "production" and not settings.require_auth:
        return

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if authenticated_user.user_id != request_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's data")


async def _get_causal_service() -> CausalInferenceService:
    """Get the causal inference service.

    Returns:
        CausalInferenceService instance
    """
    try:
        client = await get_falkordb_client()
        graph_repo = CausalGraphRepository(client)
        return CausalInferenceService(graph_repository=graph_repo)
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "CAUSAL_SERVICE_UNAVAILABLE", "message": str(e)},
        )


@router.get("/attribution/{trace_id}", response_model=AttributionResponse)
async def get_attribution(
    trace_id: UUID,
    use_shapley: bool = False,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> AttributionResponse:
    """Get memory attribution for a decision outcome.

    Returns how much each memory contributed to the outcome.
    This enables precise salience updates and understanding
    which memories led to successful decisions.

    Query Parameters:
        use_shapley: Use Shapley values for mathematically fair attribution.
                    Slower but provides game-theoretically optimal credit assignment.

    Authentication:
        - Required in production
        - Optional in development
    """
    service = await _get_causal_service()
    result = await service.get_memory_attribution(trace_id, use_shapley=use_shapley)

    if not result.is_ok:
        if result.error.code == ErrorCode.MEMORY_NOT_FOUND:
            raise HTTPException(status_code=404, detail=result.error.to_dict())
        raise HTTPException(status_code=400, detail=result.error.to_dict())

    attribution = result.value
    return AttributionResponse(
        trace_id=attribution.trace_id,
        outcome_quality=attribution.outcome_quality,
        attributions={str(k): v for k, v in attribution.attributions.items()},
        total_attributed=attribution.total_attributed,
        method=attribution.method,
        top_contributors=[
            {"memory_id": str(mid), "contribution": contrib}
            for mid, contrib in attribution.top_contributors(5)
        ],
    )


@router.post("/predict", response_model=PredictResponse)
async def predict_outcome(
    request: PredictRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> PredictResponse:
    """Predict likely outcome for a given context.

    Uses historical causal patterns to predict what outcome
    might result from using the specified memories for a decision.

    This enables:
    - Pre-decision quality assessment
    - Context optimization before action
    - Risk evaluation for important decisions

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)
    service = await _get_causal_service()
    result = await service.predict_outcome(
        user_id=request.user_id,
        memory_ids=request.memory_ids,
        decision_type=request.decision_type,
    )

    if not result.is_ok:
        raise HTTPException(status_code=400, detail=result.error.to_dict())

    prediction = result.value
    return PredictResponse(
        expected_quality=prediction.expected_quality,
        confidence=prediction.confidence,
        similar_count=prediction.similar_count,
        reasoning=prediction.reasoning,
    )


@router.post("/counterfactual", response_model=CounterfactualResponse)
async def counterfactual_analysis(
    request: CounterfactualRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> CounterfactualResponse:
    """Perform counterfactual analysis.

    Answers "what if" questions about alternative contexts:
    - What if we had used different memories?
    - Would the outcome have been better or worse?

    This enables learning from past decisions and
    understanding how to improve future ones.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)
    query = CounterfactualQuery(
        user_id=request.user_id,
        original_trace_id=request.original_trace_id,
        hypothetical_memory_ids=request.hypothetical_memory_ids,
        question=request.question,
        decision_type=request.decision_type,
        min_confidence=request.min_confidence,
    )

    service = await _get_causal_service()
    result = await service.counterfactual_analysis(query)

    if not result.is_ok:
        raise HTTPException(status_code=400, detail=result.error.to_dict())

    cf_result = result.value
    return CounterfactualResponse(
        original_trace_id=cf_result.query.original_trace_id,
        question=cf_result.query.question,
        predicted_outcome_quality=cf_result.predicted_outcome_quality,
        confidence=cf_result.confidence,
        is_positive_prediction=cf_result.is_positive_prediction,
        is_confident=cf_result.is_confident,
        similar_historical_count=cf_result.similar_historical_count,
        average_historical_outcome=cf_result.average_historical_outcome,
        reasoning=cf_result.reasoning,
        supporting_traces=cf_result.supporting_traces,
    )


@router.get("/memory/{memory_id}/success-rate", response_model=MemorySuccessRateResponse)
async def get_memory_success_rate(
    memory_id: UUID,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> MemorySuccessRateResponse:
    """Get success rate statistics for a memory.

    Returns how often this memory has led to positive outcomes
    in past decisions. Higher success rates indicate memories
    that consistently contribute to good decisions.

    Authentication:
        - Required in production
        - Optional in development
    """
    service = await _get_causal_service()
    result = await service.get_memory_success_rate(memory_id)

    if not result.is_ok:
        if result.error.code == ErrorCode.MEMORY_NOT_FOUND:
            raise HTTPException(status_code=404, detail=result.error.to_dict())
        raise HTTPException(status_code=400, detail=result.error.to_dict())

    stats = result.value
    return MemorySuccessRateResponse(
        memory_id=memory_id,
        success_rate=stats.get("success_rate", 0.0),
        total_outcomes=stats.get("total_outcomes", 0),
        positive_outcomes=stats.get("positive_outcomes", 0),
        negative_outcomes=stats.get("negative_outcomes", 0),
        neutral_outcomes=stats.get("neutral_outcomes", 0),
        average_quality=stats.get("average_quality", 0.0),
    )


# =============================================================================
# DoWhy Integration Endpoints
# =============================================================================


@router.post("/analyze-effects/{user_id}")
async def analyze_causal_effects(
    user_id: UUID,
    treatment: str = "used_identity_memories",
    outcome: str = "outcome_quality",
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> dict:
    """Analyze causal effects using DoWhy formal inference.

    Uses historical decision data to estimate the TRUE causal effect
    of memory usage on outcomes, controlling for confounders.

    This is different from correlation - it identifies whether using
    certain types of memories actually CAUSES better outcomes.

    Query Parameters:
        treatment: Which memory feature to analyze (default: used_identity_memories)
        outcome: Outcome to measure (default: outcome_quality)

    Returns:
        - effect: Estimated causal effect size
        - confidence_interval: 95% CI for the effect
        - is_significant: Whether effect is statistically significant
        - interpretation: Human-readable explanation

    Requires: pip install mind[ml] for DoWhy support
    """
    _validate_user_access(user_id, user)
    service = await _get_causal_service()

    result = await service.analyze_causal_effects(
        user_id=user_id,
        treatment=treatment,
        outcome=outcome,
    )

    if not result.is_ok:
        raise HTTPException(status_code=400, detail=result.error.to_dict())

    return result.value


@router.post("/validate-claims/{user_id}")
async def validate_causal_claims(
    user_id: UUID,
    treatment: str = "used_identity_memories",
    outcome: str = "outcome_quality",
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> dict:
    """Validate causal claims with refutation tests.

    Runs multiple robustness checks to ensure causal estimates
    are reliable and not spurious correlations:

    1. Placebo Treatment: Does a random treatment show same effect?
    2. Data Subset: Is effect consistent across data subsets?
    3. Random Common Cause: Does adding random confounders change result?

    Returns:
        - original_effect: The estimated causal effect
        - refutation_tests: Results of each robustness test
        - is_robust: Whether the causal claim passes validation
        - recommendation: Action guidance based on results

    Requires: pip install mind[ml] for DoWhy support
    """
    _validate_user_access(user_id, user)
    service = await _get_causal_service()

    result = await service.validate_causal_claims(
        user_id=user_id,
        treatment=treatment,
        outcome=outcome,
    )

    if not result.is_ok:
        raise HTTPException(status_code=400, detail=result.error.to_dict())

    return result.value
