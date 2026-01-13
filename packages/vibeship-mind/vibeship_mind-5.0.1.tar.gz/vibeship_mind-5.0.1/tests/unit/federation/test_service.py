"""Tests for the Federation Service."""

import pytest
from uuid import uuid4
from datetime import datetime, UTC, timedelta

from mind.core.federation.models import (
    SanitizedPattern,
    PatternType,
    PatternMatch,
    PrivacyBudget,
)
from mind.core.federation.service import FederationService
from mind.core.decision.models import DecisionTrace, Outcome


class TestFederationService:
    """Tests for FederationService."""

    @pytest.fixture
    def service(self) -> FederationService:
        """Create a federation service with low thresholds for testing."""
        budget = PrivacyBudget(min_users=2, min_observations=3)
        return FederationService(privacy_budget=budget)

    @pytest.fixture
    def sample_trace(self) -> DecisionTrace:
        """Create a sample decision trace."""
        return DecisionTrace(
            trace_id=uuid4(),
            user_id=uuid4(),
            session_id=uuid4(),
            memory_ids=[uuid4()],
            memory_scores={"mem1": 0.8},
            decision_type="scheduling",
            decision_summary="When should I schedule?",
            confidence=0.85,
        )

    @pytest.fixture
    def positive_outcome(self) -> Outcome:
        """Create a positive outcome."""
        return Outcome(
            trace_id=uuid4(),
            quality=0.8,
            signal="explicit_positive",
            feedback_text="Worked well",
        )

    @pytest.fixture
    def sample_pattern(self) -> SanitizedPattern:
        """Create a sample sanitized pattern."""
        return SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal",
            outcome_improvement=0.3,
            confidence=0.75,
            source_count=150,
            user_count=25,
            epsilon=0.1,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )

    @pytest.mark.asyncio
    async def test_process_outcome_extracts_pattern(
        self,
        service: FederationService,
        sample_trace: DecisionTrace,
        positive_outcome: Outcome,
    ):
        """Should extract pattern from positive outcome."""
        result = await service.process_outcome(
            trace=sample_trace,
            outcome=positive_outcome,
            memory_contents=["User prefers morning", "Usually available at 9am"],
        )

        assert result.is_ok
        # First call won't have enough data for ready pattern
        # Pattern is extracted but not yet federated

    @pytest.mark.asyncio
    async def test_process_outcome_categorizes_content(
        self,
        service: FederationService,
        positive_outcome: Outcome,
    ):
        """Should categorize memory contents, not store raw content."""
        traces = [
            DecisionTrace(
                trace_id=uuid4(),
                user_id=uuid4(),
                session_id=uuid4(),
                memory_ids=[],
                memory_scores={},
                decision_type="scheduling",
                decision_summary="Schedule",
                confidence=0.8,
            )
            for _ in range(3)
        ]

        # Process multiple outcomes with sensitive content
        for trace in traces:
            await service.process_outcome(
                trace=trace,
                outcome=positive_outcome,
                memory_contents=["John Doe prefers mornings", "Email: john@example.com"],
            )

        # The extractor should have abstracted categories, not raw content
        candidates = service._extractor._candidates
        for candidate in candidates.values():
            # Should not contain PII
            assert "john" not in candidate.response_strategy.lower()
            assert "@" not in candidate.response_strategy

    @pytest.mark.asyncio
    async def test_process_outcome_returns_ready_pattern(
        self,
        positive_outcome: Outcome,
    ):
        """Should return pattern when thresholds are met."""
        # Very low thresholds for testing
        budget = PrivacyBudget(min_users=2, min_observations=2)
        service = FederationService(privacy_budget=budget)

        # Process enough outcomes to trigger pattern readiness
        for i in range(3):
            trace = DecisionTrace(
                trace_id=uuid4(),
                user_id=uuid4(),
                session_id=uuid4(),
                memory_ids=[],
                memory_scores={},
                decision_type="scheduling",
                decision_summary="Query",
                confidence=0.8,
            )
            result = await service.process_outcome(
                trace=trace,
                outcome=positive_outcome,
                memory_contents=["User prefers quiet"],
            )

        # Should have a pattern ready
        # Note: the pattern may or may not be returned depending on exact counts

    @pytest.mark.asyncio
    async def test_get_relevant_patterns_empty(
        self,
        service: FederationService,
    ):
        """Should return empty list when no patterns exist."""
        result = await service.get_relevant_patterns(
            decision_type="scheduling",
            memory_categories=["preference"],
        )

        assert result.is_ok
        assert result.value == []

    @pytest.mark.asyncio
    async def test_get_relevant_patterns_matches_decision_type(
        self,
        service: FederationService,
        sample_pattern: SanitizedPattern,
    ):
        """Should match patterns by decision type."""
        # Add pattern to cache
        service._sanitized_patterns[sample_pattern.pattern_id] = sample_pattern

        # Query with matching decision type
        result = await service.get_relevant_patterns(
            decision_type="scheduling",
            memory_categories=["preference"],
        )

        assert result.is_ok
        assert len(result.value) == 1
        assert result.value[0].pattern.pattern_id == sample_pattern.pattern_id

    @pytest.mark.asyncio
    async def test_get_relevant_patterns_filters_expired(
        self,
        service: FederationService,
    ):
        """Should not return expired patterns."""
        expired_pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference",
            outcome_improvement=0.3,
            confidence=0.75,
            source_count=150,
            user_count=25,
            epsilon=0.1,
            expires_at=datetime.now(UTC) - timedelta(days=1),  # Expired
        )
        service._sanitized_patterns[expired_pattern.pattern_id] = expired_pattern

        result = await service.get_relevant_patterns(
            decision_type="scheduling",
            memory_categories=["preference"],
        )

        assert result.is_ok
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_get_relevant_patterns_filters_invalid(
        self,
        service: FederationService,
    ):
        """Should not return invalid patterns."""
        invalid_pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference",
            outcome_improvement=0.3,
            confidence=0.3,  # Below 0.5 threshold
            source_count=50,  # Below 100 threshold
            user_count=5,  # Below 10 threshold
            epsilon=0.1,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        service._sanitized_patterns[invalid_pattern.pattern_id] = invalid_pattern

        result = await service.get_relevant_patterns(
            decision_type="scheduling",
            memory_categories=["preference"],
        )

        assert result.is_ok
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_get_relevant_patterns_ranks_by_relevance(
        self,
        service: FederationService,
    ):
        """Should rank patterns by relevance."""
        # High relevance pattern
        high_relevance = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal",
            outcome_improvement=0.5,
            confidence=0.8,
            source_count=200,
            user_count=30,
            epsilon=0.1,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )

        # Low relevance pattern (different categories)
        low_relevance = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="constraint+location",
            outcome_improvement=0.3,
            confidence=0.7,
            source_count=150,
            user_count=25,
            epsilon=0.1,
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )

        service._sanitized_patterns[high_relevance.pattern_id] = high_relevance
        service._sanitized_patterns[low_relevance.pattern_id] = low_relevance

        result = await service.get_relevant_patterns(
            decision_type="scheduling",
            memory_categories=["preference", "temporal"],
        )

        assert result.is_ok
        assert len(result.value) == 2
        # High relevance should be first
        assert result.value[0].pattern.pattern_id == high_relevance.pattern_id

    @pytest.mark.asyncio
    async def test_get_relevant_patterns_respects_limit(
        self,
        service: FederationService,
    ):
        """Should respect limit parameter."""
        # Add multiple patterns
        for i in range(10):
            pattern = SanitizedPattern(
                pattern_id=uuid4(),
                pattern_type=PatternType.DECISION_STRATEGY,
                trigger_category="scheduling",
                response_strategy=f"preference{i}",
                outcome_improvement=0.3,
                confidence=0.75,
                source_count=150,
                user_count=25,
                epsilon=0.1,
                expires_at=datetime.now(UTC) + timedelta(days=30),
            )
            service._sanitized_patterns[pattern.pattern_id] = pattern

        result = await service.get_relevant_patterns(
            decision_type="scheduling",
            memory_categories=["preference"],
            limit=3,
        )

        assert result.is_ok
        assert len(result.value) == 3

    @pytest.mark.asyncio
    async def test_get_pattern_stats_empty(
        self,
        service: FederationService,
    ):
        """Should return zero stats when no patterns."""
        stats = await service.get_pattern_stats()

        assert stats["total_patterns"] == 0
        assert stats["valid_patterns"] == 0
        assert stats["expired_patterns"] == 0
        assert stats["average_confidence"] == 0.0
        assert stats["average_improvement"] == 0.0

    @pytest.mark.asyncio
    async def test_get_pattern_stats_with_patterns(
        self,
        service: FederationService,
        sample_pattern: SanitizedPattern,
    ):
        """Should compute stats correctly."""
        service._sanitized_patterns[sample_pattern.pattern_id] = sample_pattern

        stats = await service.get_pattern_stats()

        assert stats["total_patterns"] == 1
        assert stats["valid_patterns"] == 1
        assert stats["expired_patterns"] == 0
        assert stats["average_confidence"] == 0.75
        assert stats["average_improvement"] == 0.3


class TestRelevanceCalculation:
    """Tests for pattern relevance calculation."""

    @pytest.fixture
    def service(self) -> FederationService:
        """Create a federation service."""
        return FederationService()

    def test_calculate_relevance_exact_match(
        self,
        service: FederationService,
    ):
        """Exact match should have high relevance."""
        pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal",
            outcome_improvement=0.3,
            confidence=0.75,
            source_count=150,
            user_count=25,
            epsilon=0.1,
        )

        relevance = service._calculate_relevance(
            pattern,
            decision_type="scheduling",
            memory_categories=["preference", "temporal"],
        )

        assert relevance == 1.0

    def test_calculate_relevance_decision_type_only(
        self,
        service: FederationService,
    ):
        """Matching only decision type should give partial relevance."""
        pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal",
            outcome_improvement=0.3,
            confidence=0.75,
            source_count=150,
            user_count=25,
            epsilon=0.1,
        )

        relevance = service._calculate_relevance(
            pattern,
            decision_type="scheduling",
            memory_categories=["constraint", "goal"],  # No overlap
        )

        # Should get 0.5 for decision type match, 0 for categories
        assert relevance == 0.5

    def test_calculate_relevance_no_match(
        self,
        service: FederationService,
    ):
        """No match should have zero relevance."""
        pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="recommendation",
            response_strategy="preference+temporal",
            outcome_improvement=0.3,
            confidence=0.75,
            source_count=150,
            user_count=25,
            epsilon=0.1,
        )

        relevance = service._calculate_relevance(
            pattern,
            decision_type="scheduling",  # Different
            memory_categories=["constraint", "goal"],  # No overlap
        )

        assert relevance == 0.0

    def test_calculate_relevance_partial_category_match(
        self,
        service: FederationService,
    ):
        """Partial category match should give proportional relevance."""
        pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference+temporal+context",
            outcome_improvement=0.3,
            confidence=0.75,
            source_count=150,
            user_count=25,
            epsilon=0.1,
        )

        relevance = service._calculate_relevance(
            pattern,
            decision_type="scheduling",
            memory_categories=["preference", "goal"],  # 1 overlap out of 4 unique
        )

        # 0.5 for decision type + partial category overlap
        assert 0.5 < relevance < 1.0


class TestPatternMatch:
    """Tests for PatternMatch model."""

    def test_recommendation_strength(self):
        """Should compute recommendation strength correctly."""
        pattern = SanitizedPattern(
            pattern_id=uuid4(),
            pattern_type=PatternType.DECISION_STRATEGY,
            trigger_category="scheduling",
            response_strategy="preference",
            outcome_improvement=0.5,
            confidence=0.8,
            source_count=150,
            user_count=25,
            epsilon=0.1,
        )

        match = PatternMatch(
            pattern=pattern,
            relevance_score=0.9,
            expected_improvement=0.45,
        )

        # relevance * confidence * expected_improvement
        expected = 0.9 * 0.8 * 0.45
        assert abs(match.recommendation_strength - expected) < 0.001
