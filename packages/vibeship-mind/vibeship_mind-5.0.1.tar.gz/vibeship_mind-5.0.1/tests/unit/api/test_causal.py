"""Unit tests for causal API endpoints.

Tests the causal API schemas and request/response handling
without requiring a real FalkorDB connection.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from mind.api.schemas.causal import (
    AttributionResponse,
    PredictRequest,
    PredictResponse,
    CounterfactualRequest,
    CounterfactualResponse,
    MemorySuccessRateResponse,
)
from mind.core.causal.models import CausalAttribution, CounterfactualQuery, CounterfactualResult
from mind.core.causal.service import PredictedOutcome
from mind.core.errors import Result, MindError, ErrorCode


class TestCausalSchemas:
    """Tests for causal API schema validation."""

    def test_predict_request_requires_user_id(self):
        """PredictRequest should require user_id."""
        with pytest.raises(Exception):
            PredictRequest(memory_ids=[uuid4()])

    def test_predict_request_requires_memory_ids(self):
        """PredictRequest should require at least one memory_id."""
        with pytest.raises(Exception):
            PredictRequest(user_id=uuid4(), memory_ids=[])

    def test_predict_request_valid(self):
        """PredictRequest should accept valid data."""
        user_id = uuid4()
        memory_ids = [uuid4(), uuid4()]

        request = PredictRequest(
            user_id=user_id,
            memory_ids=memory_ids,
            decision_type="recommendation",
        )

        assert request.user_id == user_id
        assert len(request.memory_ids) == 2
        assert request.decision_type == "recommendation"

    def test_counterfactual_request_valid(self):
        """CounterfactualRequest should accept valid data."""
        user_id = uuid4()
        trace_id = uuid4()
        memory_ids = [uuid4()]

        request = CounterfactualRequest(
            user_id=user_id,
            original_trace_id=trace_id,
            hypothetical_memory_ids=memory_ids,
            question="What if we used different context?",
        )

        assert request.user_id == user_id
        assert request.original_trace_id == trace_id
        assert request.min_confidence == 0.5  # Default

    def test_counterfactual_request_custom_confidence(self):
        """CounterfactualRequest should accept custom min_confidence."""
        request = CounterfactualRequest(
            user_id=uuid4(),
            original_trace_id=uuid4(),
            hypothetical_memory_ids=[uuid4()],
            question="Test?",
            min_confidence=0.8,
        )

        assert request.min_confidence == 0.8


class TestAttributionResponse:
    """Tests for AttributionResponse schema."""

    def test_attribution_response_from_domain(self):
        """AttributionResponse should serialize correctly."""
        trace_id = uuid4()
        memory_id1 = uuid4()
        memory_id2 = uuid4()

        response = AttributionResponse(
            trace_id=trace_id,
            outcome_quality=0.8,
            attributions={
                str(memory_id1): 0.6,
                str(memory_id2): 0.4,
            },
            total_attributed=1.0,
            method="retrieval_score",
            top_contributors=[
                {"memory_id": str(memory_id1), "contribution": 0.6},
                {"memory_id": str(memory_id2), "contribution": 0.4},
            ],
        )

        assert response.trace_id == trace_id
        assert response.outcome_quality == 0.8
        assert len(response.attributions) == 2
        assert response.total_attributed == 1.0


class TestPredictResponse:
    """Tests for PredictResponse schema."""

    def test_predict_response_valid(self):
        """PredictResponse should serialize correctly."""
        response = PredictResponse(
            expected_quality=0.7,
            confidence=0.85,
            similar_count=15,
            reasoning="Based on 15 similar decisions",
        )

        assert response.expected_quality == 0.7
        assert response.confidence == 0.85
        assert response.similar_count == 15

    def test_predict_response_bounds(self):
        """PredictResponse should enforce field bounds."""
        response = PredictResponse(
            expected_quality=-0.5,  # Negative is valid
            confidence=0.0,  # Zero is valid
            similar_count=0,
            reasoning="No similar decisions",
        )

        assert response.expected_quality == -0.5
        assert response.confidence == 0.0


class TestCounterfactualResponse:
    """Tests for CounterfactualResponse schema."""

    def test_counterfactual_response_positive(self):
        """CounterfactualResponse should indicate positive prediction."""
        trace_id = uuid4()

        response = CounterfactualResponse(
            original_trace_id=trace_id,
            question="What if we used different context?",
            predicted_outcome_quality=0.8,
            confidence=0.75,
            is_positive_prediction=True,
            is_confident=True,
            similar_historical_count=10,
            average_historical_outcome=0.75,
            reasoning="Based on 10 similar decisions",
            supporting_traces=[uuid4(), uuid4()],
        )

        assert response.is_positive_prediction is True
        assert response.is_confident is True
        assert len(response.supporting_traces) == 2

    def test_counterfactual_response_negative(self):
        """CounterfactualResponse should indicate negative prediction."""
        response = CounterfactualResponse(
            original_trace_id=uuid4(),
            question="What if we used different context?",
            predicted_outcome_quality=-0.3,
            confidence=0.6,
            is_positive_prediction=False,
            is_confident=True,
            similar_historical_count=5,
            average_historical_outcome=-0.2,
            reasoning="Based on 5 similar decisions",
        )

        assert response.is_positive_prediction is False


class TestMemorySuccessRateResponse:
    """Tests for MemorySuccessRateResponse schema."""

    def test_success_rate_response_valid(self):
        """MemorySuccessRateResponse should serialize correctly."""
        memory_id = uuid4()

        response = MemorySuccessRateResponse(
            memory_id=memory_id,
            success_rate=0.75,
            total_outcomes=20,
            positive_outcomes=15,
            negative_outcomes=3,
            neutral_outcomes=2,
            average_quality=0.6,
        )

        assert response.memory_id == memory_id
        assert response.success_rate == 0.75
        assert response.total_outcomes == 20

    def test_success_rate_zero_outcomes(self):
        """MemorySuccessRateResponse should handle zero outcomes."""
        response = MemorySuccessRateResponse(
            memory_id=uuid4(),
            success_rate=0.0,
            total_outcomes=0,
            positive_outcomes=0,
            negative_outcomes=0,
            neutral_outcomes=0,
            average_quality=0.0,
        )

        assert response.success_rate == 0.0
        assert response.total_outcomes == 0


class TestCausalEndpointMocking:
    """Tests for causal API endpoints with mocked services."""

    @pytest.fixture
    def mock_causal_service(self):
        """Create a mock CausalInferenceService."""
        service = MagicMock()

        # Mock get_memory_attribution
        attribution = CausalAttribution(
            trace_id=uuid4(),
            outcome_quality=0.8,
            attributions={uuid4(): 0.6, uuid4(): 0.4},
            total_attributed=1.0,
            method="retrieval_score",
        )
        service.get_memory_attribution = AsyncMock(
            return_value=Result.ok(attribution)
        )

        # Mock predict_outcome
        prediction = PredictedOutcome(
            expected_quality=0.7,
            confidence=0.8,
            similar_count=10,
            reasoning="Based on similar decisions",
        )
        service.predict_outcome = AsyncMock(
            return_value=Result.ok(prediction)
        )

        # Mock counterfactual_analysis
        cf_result = CounterfactualResult(
            query=CounterfactualQuery(
                user_id=uuid4(),
                original_trace_id=uuid4(),
                hypothetical_memory_ids=[uuid4()],
                question="What if?",
            ),
            predicted_outcome_quality=0.6,
            confidence=0.7,
            similar_historical_count=5,
            average_historical_outcome=0.5,
            reasoning="Based on similar decisions",
        )
        service.counterfactual_analysis = AsyncMock(
            return_value=Result.ok(cf_result)
        )

        # Mock get_memory_success_rate
        success_stats = {
            "success_rate": 0.75,
            "total_outcomes": 20,
            "positive_outcomes": 15,
            "negative_outcomes": 3,
            "neutral_outcomes": 2,
            "average_quality": 0.6,
        }
        service.get_memory_success_rate = AsyncMock(
            return_value=Result.ok(success_stats)
        )

        return service

    @pytest.mark.asyncio
    async def test_predict_endpoint_success(self, mock_causal_service):
        """Predict endpoint should return prediction."""
        from mind.api.routes.causal import predict_outcome

        # Patch the service getter
        with patch(
            "mind.api.routes.causal._get_causal_service",
            return_value=mock_causal_service,
        ):
            request = PredictRequest(
                user_id=uuid4(),
                memory_ids=[uuid4(), uuid4()],
            )

            response = await predict_outcome(request)

            assert response.expected_quality == 0.7
            assert response.confidence == 0.8
            assert response.similar_count == 10

    @pytest.mark.asyncio
    async def test_attribution_endpoint_success(self, mock_causal_service):
        """Attribution endpoint should return attributions."""
        from mind.api.routes.causal import get_attribution

        trace_id = uuid4()

        with patch(
            "mind.api.routes.causal._get_causal_service",
            return_value=mock_causal_service,
        ):
            response = await get_attribution(trace_id)

            assert response.outcome_quality == 0.8
            assert response.total_attributed == 1.0
            assert response.method == "retrieval_score"

    @pytest.mark.asyncio
    async def test_success_rate_endpoint_success(self, mock_causal_service):
        """Success rate endpoint should return statistics."""
        from mind.api.routes.causal import get_memory_success_rate

        memory_id = uuid4()

        with patch(
            "mind.api.routes.causal._get_causal_service",
            return_value=mock_causal_service,
        ):
            response = await get_memory_success_rate(memory_id)

            assert response.memory_id == memory_id
            assert response.success_rate == 0.75
            assert response.total_outcomes == 20
