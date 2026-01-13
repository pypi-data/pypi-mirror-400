"""Federation service for cross-user pattern sharing.

This service orchestrates the full federation workflow:
1. Extract patterns from successful outcomes
2. Sanitize patterns with differential privacy
3. Store and retrieve federated patterns
4. Apply patterns to enhance decisions
"""

from uuid import UUID

import structlog

from mind.core.decision.models import DecisionTrace, Outcome
from mind.core.errors import ErrorCode, MindError, Result
from mind.core.federation.extractor import ExtractionContext, PatternExtractor
from mind.core.federation.models import (
    Pattern,
    PatternMatch,
    PrivacyBudget,
    SanitizedPattern,
)
from mind.core.federation.sanitizer import DifferentialPrivacySanitizer

logger = structlog.get_logger()


class FederationService:
    """Service for federated pattern learning and sharing.

    This service enables collective intelligence by:
    - Learning from successful outcomes across users
    - Sanitizing patterns to preserve privacy
    - Sharing patterns to improve future decisions

    Privacy is enforced at every step:
    - Content is abstracted to categories
    - Statistics are noised with differential privacy
    - Minimum thresholds prevent small-group attacks

    Patterns are persisted to PostgreSQL for durability across restarts,
    with an in-memory cache for fast access during operation.
    """

    def __init__(
        self,
        pattern_repository=None,
        privacy_budget: PrivacyBudget = PrivacyBudget(),
    ):
        """Initialize the federation service.

        Args:
            pattern_repository: Repository for storing/retrieving patterns
            privacy_budget: Privacy parameters for sanitization
        """
        self._repository = pattern_repository
        self._privacy_budget = privacy_budget
        self._extractor = PatternExtractor(privacy_budget)
        self._sanitizer = DifferentialPrivacySanitizer(privacy_budget)

        # In-memory pattern cache for fast access
        # Populated from repository on startup
        self._sanitized_patterns: dict[UUID, SanitizedPattern] = {}
        self._cache_loaded = False

    async def initialize(self) -> None:
        """Initialize the service by loading patterns from repository.

        Should be called after construction to populate the cache
        from persistent storage.
        """
        if self._cache_loaded:
            return

        if self._repository:
            try:
                result = await self._repository.get_all()
                if result.is_ok:
                    for pattern in result.value:
                        self._sanitized_patterns[pattern.pattern_id] = pattern
                    logger.info(
                        "federation_patterns_loaded",
                        count=len(result.value),
                    )
            except Exception as e:
                logger.warning(
                    "federation_pattern_load_failed",
                    error=str(e),
                )

        self._cache_loaded = True

    async def process_outcome(
        self,
        trace: DecisionTrace,
        outcome: Outcome,
        memory_contents: list[str],
    ) -> Result[Pattern | None]:
        """Process an outcome for pattern extraction.

        Called when an outcome is observed to potentially
        contribute to federated patterns.

        Args:
            trace: The decision trace
            outcome: The observed outcome
            memory_contents: Contents of memories used (will be categorized)

        Returns:
            Pattern if one was extracted and ready, None otherwise
        """
        try:
            # Categorize memory contents (never store actual content)
            from mind.core.federation.extractor import CategoryMapper

            mapper = CategoryMapper()
            categories = mapper.categorize_memories(memory_contents)

            # Create extraction context
            context = ExtractionContext(
                trace=trace,
                outcome=outcome,
                memory_categories=categories,
            )

            # Extract pattern candidate
            result = self._extractor.extract_from_outcome(context)
            if not result.is_ok:
                return Result.err(result.error)

            # Check if any patterns are ready for federation
            ready_patterns = self._extractor.get_ready_patterns()

            if ready_patterns:
                # Sanitize and store ready patterns
                for pattern in ready_patterns:
                    sanitize_result = await self._sanitize_and_store(pattern)
                    if sanitize_result.is_ok:
                        logger.info(
                            "pattern_federated",
                            pattern_id=str(pattern.pattern_id),
                        )

                # Return first ready pattern
                return Result.ok(ready_patterns[0])

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "federation_process_outcome_failed",
                trace_id=str(trace.trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to process outcome: {e}",
                )
            )

    async def get_relevant_patterns(
        self,
        decision_type: str,
        memory_categories: list[str],
        limit: int = 5,
    ) -> Result[list[PatternMatch]]:
        """Get federated patterns relevant to a decision context.

        Searches for patterns that match the decision type and
        context categories, returning ranked matches.

        Args:
            decision_type: Type of decision being made
            memory_categories: Categories of context being used
            limit: Maximum patterns to return

        Returns:
            List of PatternMatch objects ranked by relevance
        """
        try:
            # Ensure patterns are loaded from repository
            await self.initialize()

            matches = []

            for pattern in self._sanitized_patterns.values():
                # Skip expired patterns
                if pattern.is_expired():
                    continue

                # Skip invalid patterns
                if not pattern.is_valid():
                    continue

                # Calculate relevance
                relevance = self._calculate_relevance(
                    pattern,
                    decision_type,
                    memory_categories,
                )

                if relevance > 0.1:  # Minimum relevance threshold
                    matches.append(
                        PatternMatch(
                            pattern=pattern,
                            relevance_score=relevance,
                            expected_improvement=pattern.outcome_improvement * relevance,
                        )
                    )

            # Sort by recommendation strength
            matches.sort(key=lambda m: m.recommendation_strength, reverse=True)

            return Result.ok(matches[:limit])

        except Exception as e:
            logger.error(
                "federation_get_patterns_failed",
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Failed to get patterns: {e}",
                )
            )

    async def get_pattern_stats(self) -> dict:
        """Get statistics about federated patterns.

        Returns metrics useful for monitoring the federation system.
        Includes both cached and persisted pattern stats.
        """
        # Ensure patterns are loaded
        await self.initialize()

        # Get stats from repository if available
        if self._repository:
            try:
                repo_stats = await self._repository.get_stats()
                return {
                    **repo_stats,
                    "cached_patterns": len(self._sanitized_patterns),
                    "privacy_budget_spent": self._sanitizer.get_remaining_budget(),
                    "storage": "persistent",
                }
            except Exception as e:
                logger.warning("pattern_stats_repo_failed", error=str(e))

        # Fallback to in-memory stats
        total = len(self._sanitized_patterns)
        valid = sum(1 for p in self._sanitized_patterns.values() if p.is_valid())
        expired = sum(1 for p in self._sanitized_patterns.values() if p.is_expired())

        avg_confidence = 0.0
        avg_improvement = 0.0
        if total > 0:
            avg_confidence = sum(p.confidence for p in self._sanitized_patterns.values()) / total
            avg_improvement = (
                sum(p.outcome_improvement for p in self._sanitized_patterns.values()) / total
            )

        return {
            "total_patterns": total,
            "active_patterns": valid,
            "expired_patterns": expired,
            "average_confidence": avg_confidence,
            "average_improvement": avg_improvement,
            "privacy_budget_spent": self._sanitizer.get_remaining_budget(),
            "storage": "memory",
        }

    async def _sanitize_and_store(
        self,
        pattern: Pattern,
    ) -> Result[SanitizedPattern]:
        """Sanitize a pattern and store it for federation.

        Patterns are stored both in the in-memory cache for fast access
        and in the PostgreSQL repository for durability across restarts.

        Args:
            pattern: Pattern to sanitize and store

        Returns:
            The sanitized pattern
        """
        # Apply differential privacy
        result = self._sanitizer.sanitize(pattern)
        if not result.is_ok:
            return result

        sanitized = result.value

        # Always update in-memory cache first
        self._sanitized_patterns[sanitized.pattern_id] = sanitized

        # Persist to repository if configured
        if self._repository:
            try:
                save_result = await self._repository.save(sanitized)
                if save_result.is_ok:
                    logger.info(
                        "pattern_persisted",
                        pattern_id=str(sanitized.pattern_id),
                        trigger=sanitized.trigger_category,
                        confidence=sanitized.confidence,
                    )
                else:
                    logger.warning(
                        "pattern_persist_failed",
                        pattern_id=str(sanitized.pattern_id),
                        error=str(save_result.error),
                    )
            except Exception as e:
                # Log but don't fail - pattern is still in cache
                logger.warning(
                    "pattern_persist_exception",
                    pattern_id=str(sanitized.pattern_id),
                    error=str(e),
                )

        return Result.ok(sanitized)

    def _calculate_relevance(
        self,
        pattern: SanitizedPattern,
        decision_type: str,
        memory_categories: list[str],
    ) -> float:
        """Calculate how relevant a pattern is to a context.

        Uses category overlap and decision type matching.
        """
        relevance = 0.0

        # Decision type match
        if pattern.trigger_category == decision_type:
            relevance += 0.5

        # Category overlap in response strategy
        strategy_parts = set(pattern.response_strategy.split("+"))
        category_set = set(memory_categories)
        overlap = len(strategy_parts & category_set)
        total = len(strategy_parts | category_set)

        if total > 0:
            relevance += 0.5 * (overlap / total)

        return min(1.0, relevance)
