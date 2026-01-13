"""Pattern extraction from successful outcomes.

This module extracts learnable patterns from decision outcomes
that can potentially be shared across users after sanitization.
"""

from collections import defaultdict
from dataclasses import dataclass

import structlog

from mind.core.decision.models import DecisionTrace, Outcome
from mind.core.errors import ErrorCode, MindError, Result
from mind.core.federation.models import (
    Pattern,
    PatternCandidate,
    PatternType,
    PrivacyBudget,
)

logger = structlog.get_logger()


# Minimum outcome quality to consider for pattern extraction
MIN_OUTCOME_QUALITY = 0.3


@dataclass
class ExtractionContext:
    """Context for pattern extraction."""

    trace: DecisionTrace
    outcome: Outcome
    memory_categories: list[str]  # Abstracted categories of memories used


class PatternExtractor:
    """Extracts patterns from successful outcomes.

    The extractor identifies recurring successful patterns:
    - What types of decisions succeed
    - What context combinations work well
    - What strategies lead to good outcomes

    All extraction preserves privacy by abstracting to categories
    rather than specific content.
    """

    def __init__(self, privacy_budget: PrivacyBudget = PrivacyBudget()):
        self._privacy_budget = privacy_budget
        # In-memory candidate storage (would be database in production)
        self._candidates: dict[str, PatternCandidate] = {}
        self._category_mapper = CategoryMapper()

    def extract_from_outcome(
        self,
        context: ExtractionContext,
    ) -> Result[PatternCandidate | None]:
        """Extract pattern candidate from a successful outcome.

        Only considers outcomes above quality threshold.
        Abstracts content to categories for privacy.

        Args:
            context: Extraction context with trace, outcome, categories

        Returns:
            PatternCandidate if pattern was extracted, None if not applicable
        """
        try:
            # Only extract from positive outcomes
            if context.outcome.quality < MIN_OUTCOME_QUALITY:
                logger.debug(
                    "pattern_extraction_skipped_low_quality",
                    trace_id=str(context.trace.trace_id),
                    quality=context.outcome.quality,
                )
                return Result.ok(None)

            # Generate pattern key from abstracted categories
            pattern_key = self._generate_pattern_key(
                decision_type=context.trace.decision_type,
                memory_categories=context.memory_categories,
            )

            # Get or create candidate
            if pattern_key in self._candidates:
                candidate = self._candidates[pattern_key]
            else:
                candidate = PatternCandidate(
                    pattern_type=PatternType.DECISION_STRATEGY,
                    trigger_category=context.trace.decision_type,
                    response_strategy=self._abstract_strategy(context.memory_categories),
                )
                self._candidates[pattern_key] = candidate

            # Add observation
            candidate.add_observation(
                trace_id=context.trace.trace_id,
                user_id=context.trace.user_id,
                outcome_quality=context.outcome.quality,
            )

            logger.debug(
                "pattern_observation_added",
                pattern_key=pattern_key,
                observation_count=candidate.observation_count,
                user_count=candidate.user_count,
            )

            return Result.ok(candidate)

        except Exception as e:
            logger.error(
                "pattern_extraction_failed",
                trace_id=str(context.trace.trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Pattern extraction failed: {e}",
                )
            )

    def get_ready_patterns(self) -> list[Pattern]:
        """Get patterns that meet privacy thresholds.

        Returns patterns that have enough observations from
        enough users to be considered for sanitization.
        """
        ready = []

        for _key, candidate in self._candidates.items():
            if self._privacy_budget.is_satisfied(
                candidate.user_count,
                candidate.observation_count,
            ):
                pattern = Pattern.from_candidate(candidate)
                ready.append(pattern)

                logger.info(
                    "pattern_ready_for_federation",
                    pattern_id=str(pattern.pattern_id),
                    user_count=pattern.user_count,
                    observation_count=pattern.observation_count,
                )

        return ready

    def _generate_pattern_key(
        self,
        decision_type: str,
        memory_categories: list[str],
    ) -> str:
        """Generate a key for pattern deduplication.

        Uses abstracted categories, not specific content.
        """
        sorted_categories = sorted(set(memory_categories))
        return f"{decision_type}:{':'.join(sorted_categories)}"

    def _abstract_strategy(self, memory_categories: list[str]) -> str:
        """Create abstract strategy description from categories.

        This ensures no PII leaks into the strategy description.
        """
        if not memory_categories:
            return "general_context"

        # Group by category type
        category_groups = defaultdict(int)
        for cat in memory_categories:
            category_groups[cat] += 1

        # Build description
        parts = []
        for cat, count in sorted(category_groups.items()):
            if count > 1:
                parts.append(f"{cat}({count})")
            else:
                parts.append(cat)

        return "+".join(parts)


class CategoryMapper:
    """Maps content to abstract categories.

    This is a critical privacy component that ensures specific
    content is never stored in patterns - only abstract categories.
    """

    # Predefined category mappings
    CATEGORY_KEYWORDS = {
        "preference": ["prefer", "like", "want", "favorite", "choice"],
        "constraint": ["cannot", "must not", "avoid", "never", "allergic"],
        "goal": ["goal", "objective", "target", "aim", "want to"],
        "context": ["usually", "typically", "often", "sometimes"],
        "identity": ["am", "my", "always", "personality"],
        "temporal": ["morning", "evening", "weekend", "daily", "weekly"],
        "location": ["at home", "at work", "traveling", "location"],
        "social": ["with friends", "alone", "family", "meeting"],
    }

    def categorize(self, content: str) -> str:
        """Map content to an abstract category.

        Args:
            content: The content to categorize

        Returns:
            Abstract category string (never the content itself)
        """
        content_lower = content.lower()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return category

        return "general"

    def categorize_memories(self, memory_contents: list[str]) -> list[str]:
        """Categorize a list of memory contents.

        Args:
            memory_contents: List of memory content strings

        Returns:
            List of abstract categories
        """
        return [self.categorize(content) for content in memory_contents]
