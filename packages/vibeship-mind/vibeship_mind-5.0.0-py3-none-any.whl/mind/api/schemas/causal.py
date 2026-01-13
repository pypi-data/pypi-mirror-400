"""Causal inference API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

# --- Attribution ---


class AttributionResponse(BaseModel):
    """Response with memory attribution for an outcome."""

    trace_id: UUID
    outcome_quality: float = Field(description="Quality of the outcome (-1 to 1)")
    attributions: dict[str, float] = Field(description="Memory ID to contribution (0-1) mapping")
    total_attributed: float = Field(description="Sum of attributions (should be ~1.0)")
    method: str = Field(
        description="Attribution method used: retrieval_score, causal_path, shapley"
    )
    top_contributors: list[dict] = Field(
        default_factory=list,
        description="Top contributing memories with their contribution scores",
    )


# --- Prediction ---


class PredictRequest(BaseModel):
    """Request to predict outcome for a context."""

    user_id: UUID
    memory_ids: list[UUID] = Field(min_length=1, description="Memory IDs to use as context")
    decision_type: str | None = Field(
        default=None, description="Optional decision type for more targeted prediction"
    )


class PredictResponse(BaseModel):
    """Response with predicted outcome."""

    expected_quality: float = Field(ge=-1.0, le=1.0, description="Predicted outcome quality")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in prediction")
    similar_count: int = Field(ge=0, description="Number of similar historical decisions found")
    reasoning: str = Field(description="Explanation of the prediction")


# --- Counterfactual ---


class CounterfactualRequest(BaseModel):
    """Request for counterfactual analysis."""

    user_id: UUID
    original_trace_id: UUID = Field(description="Original decision trace to compare against")
    hypothetical_memory_ids: list[UUID] = Field(
        min_length=1, description="Alternative memories to consider"
    )
    question: str = Field(max_length=500, description="The counterfactual question being asked")
    decision_type: str | None = Field(default=None, description="Optional decision type constraint")
    min_confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold"
    )


class CounterfactualResponse(BaseModel):
    """Response with counterfactual analysis results."""

    original_trace_id: UUID
    question: str
    predicted_outcome_quality: float = Field(
        description="Predicted outcome with hypothetical memories (-1 to 1)"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in prediction")
    is_positive_prediction: bool = Field(description="Whether the predicted outcome is positive")
    is_confident: bool = Field(description="Whether confidence meets the threshold")
    similar_historical_count: int = Field(description="Number of similar historical decisions")
    average_historical_outcome: float = Field(
        description="Average outcome quality from similar decisions"
    )
    reasoning: str = Field(description="Explanation of the counterfactual result")
    supporting_traces: list[UUID] = Field(
        default_factory=list, description="Trace IDs of similar historical decisions"
    )


# --- Memory Success Rate ---


class MemorySuccessRateResponse(BaseModel):
    """Response with memory success rate statistics."""

    memory_id: UUID
    success_rate: float = Field(ge=0.0, le=1.0, description="Rate of positive outcomes (0-1)")
    total_outcomes: int = Field(ge=0, description="Total number of outcomes")
    positive_outcomes: int = Field(ge=0, description="Number of positive outcomes")
    negative_outcomes: int = Field(ge=0, description="Number of negative outcomes")
    neutral_outcomes: int = Field(ge=0, description="Number of neutral outcomes")
    average_quality: float = Field(description="Average outcome quality")
