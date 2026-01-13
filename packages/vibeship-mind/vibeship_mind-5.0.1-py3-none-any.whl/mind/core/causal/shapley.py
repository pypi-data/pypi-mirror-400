"""Shapley value computation for memory attribution.

Shapley values provide a mathematically fair way to attribute
the outcome of a decision to the memories that influenced it.

Key properties of Shapley values:
1. Efficiency: Attributions sum to total outcome
2. Symmetry: Equal contributors get equal credit
3. Null player: Non-contributors get zero credit
4. Additivity: Consistent across combinations

For N memories, exact Shapley requires 2^N evaluations.
We use sampling approximation for efficiency.
"""

import random
from dataclasses import dataclass
from itertools import permutations
from typing import Callable
from uuid import UUID

import structlog

from mind.core.causal.models import CausalAttribution
from mind.core.errors import ErrorCode, MindError, Result

logger = structlog.get_logger()


@dataclass
class ShapleyConfig:
    """Configuration for Shapley value computation."""

    # Sampling settings
    max_permutations: int = 1000  # Max permutations to sample
    min_permutations: int = 100  # Min permutations for convergence
    convergence_threshold: float = 0.01  # Stop when change < this

    # Computation settings
    use_exact: bool = False  # Use exact computation (slow for N>10)
    parallel: bool = False  # Use parallel computation

    # Caching
    cache_coalitions: bool = True  # Cache coalition values


@dataclass
class ShapleyResult:
    """Result of Shapley value computation."""

    attributions: dict[UUID, float]  # memory_id -> Shapley value
    total_value: float  # Total outcome value
    permutations_sampled: int  # Number of permutations used
    convergence_achieved: bool  # Whether values converged
    method: str  # "exact" or "sampling"


class ShapleyCalculator:
    """Computes Shapley values for memory attribution.

    Given a value function that maps subsets of memories to
    predicted outcomes, computes the fair attribution of the
    final outcome to each memory.

    Example:
        calculator = ShapleyCalculator()

        def value_fn(memory_subset: set[UUID]) -> float:
            # Return predicted outcome quality for this subset
            return predict_outcome(memory_subset)

        result = await calculator.compute(
            memory_ids=[mem1, mem2, mem3],
            value_function=value_fn,
            total_value=0.8,  # Actual outcome
        )

        # result.attributions gives credit to each memory
    """

    def __init__(self, config: ShapleyConfig | None = None):
        self.config = config or ShapleyConfig()
        self._coalition_cache: dict[frozenset, float] = {}

    async def compute(
        self,
        memory_ids: list[UUID],
        value_function: Callable[[set[UUID]], float],
        total_value: float,
    ) -> Result[ShapleyResult]:
        """Compute Shapley values for memory attribution.

        Args:
            memory_ids: List of memories that influenced the decision
            value_function: Function that predicts outcome for a subset
            total_value: Actual outcome value to attribute

        Returns:
            ShapleyResult with attributions for each memory
        """
        n = len(memory_ids)

        if n == 0:
            return Result.ok(
                ShapleyResult(
                    attributions={},
                    total_value=total_value,
                    permutations_sampled=0,
                    convergence_achieved=True,
                    method="empty",
                )
            )

        if n == 1:
            # Single memory gets all credit
            return Result.ok(
                ShapleyResult(
                    attributions={memory_ids[0]: total_value},
                    total_value=total_value,
                    permutations_sampled=1,
                    convergence_achieved=True,
                    method="single",
                )
            )

        try:
            # Choose computation method based on size
            if self.config.use_exact and n <= 10:
                result = await self._compute_exact(memory_ids, value_function)
            else:
                result = await self._compute_sampling(memory_ids, value_function)

            # Normalize to match total value
            raw_total = sum(result.attributions.values())
            if raw_total != 0:
                scale = total_value / raw_total
                result.attributions = {
                    mid: val * scale for mid, val in result.attributions.items()
                }
            result.total_value = total_value

            logger.info(
                "shapley_computed",
                memory_count=n,
                method=result.method,
                permutations=result.permutations_sampled,
            )

            return Result.ok(result)

        except Exception as e:
            logger.error(
                "shapley_computation_failed",
                memory_count=n,
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Shapley computation failed: {e}",
                )
            )

    async def _compute_exact(
        self,
        memory_ids: list[UUID],
        value_function: Callable[[set[UUID]], float],
    ) -> ShapleyResult:
        """Compute exact Shapley values using all permutations.

        For each permutation, compute marginal contribution of each player.
        Average over all permutations.

        Time complexity: O(N! * N)
        """
        n = len(memory_ids)
        shapley_values = {mid: 0.0 for mid in memory_ids}
        perm_count = 0

        # Iterate over all permutations
        for perm in permutations(memory_ids):
            perm_count += 1
            coalition = set()
            prev_value = self._get_coalition_value(frozenset(), value_function)

            for memory_id in perm:
                coalition.add(memory_id)
                curr_value = self._get_coalition_value(
                    frozenset(coalition), value_function
                )
                marginal = curr_value - prev_value
                shapley_values[memory_id] += marginal
                prev_value = curr_value

        # Average over permutations
        for mid in shapley_values:
            shapley_values[mid] /= perm_count

        return ShapleyResult(
            attributions=shapley_values,
            total_value=sum(shapley_values.values()),
            permutations_sampled=perm_count,
            convergence_achieved=True,
            method="exact",
        )

    async def _compute_sampling(
        self,
        memory_ids: list[UUID],
        value_function: Callable[[set[UUID]], float],
    ) -> ShapleyResult:
        """Compute approximate Shapley values using sampling.

        Sample random permutations and average marginal contributions.
        Stop when values converge or max permutations reached.

        Time complexity: O(max_permutations * N)
        """
        n = len(memory_ids)
        shapley_values = {mid: 0.0 for mid in memory_ids}
        prev_values = {mid: 0.0 for mid in memory_ids}

        converged = False
        perm_count = 0

        while perm_count < self.config.max_permutations:
            # Sample random permutation
            perm = memory_ids.copy()
            random.shuffle(perm)

            # Compute marginal contributions
            coalition = set()
            prev_value = self._get_coalition_value(frozenset(), value_function)

            for memory_id in perm:
                coalition.add(memory_id)
                curr_value = self._get_coalition_value(
                    frozenset(coalition), value_function
                )
                marginal = curr_value - prev_value

                # Incremental average update
                shapley_values[memory_id] = (
                    shapley_values[memory_id] * perm_count + marginal
                ) / (perm_count + 1)

                prev_value = curr_value

            perm_count += 1

            # Check convergence every 50 iterations
            if perm_count >= self.config.min_permutations and perm_count % 50 == 0:
                max_change = max(
                    abs(shapley_values[mid] - prev_values[mid])
                    for mid in memory_ids
                )
                if max_change < self.config.convergence_threshold:
                    converged = True
                    break
                prev_values = shapley_values.copy()

        return ShapleyResult(
            attributions=shapley_values,
            total_value=sum(shapley_values.values()),
            permutations_sampled=perm_count,
            convergence_achieved=converged,
            method="sampling",
        )

    def _get_coalition_value(
        self,
        coalition: frozenset,
        value_function: Callable[[set[UUID]], float],
    ) -> float:
        """Get value for a coalition, using cache if enabled."""
        if self.config.cache_coalitions:
            if coalition not in self._coalition_cache:
                self._coalition_cache[coalition] = value_function(set(coalition))
            return self._coalition_cache[coalition]
        return value_function(set(coalition))

    def clear_cache(self) -> None:
        """Clear the coalition value cache."""
        self._coalition_cache.clear()


async def compute_shapley_attribution(
    trace_id: UUID,
    memory_ids: list[UUID],
    memory_saliences: dict[UUID, float],
    outcome_quality: float,
    predictor: Callable[[set[UUID]], float] | None = None,
) -> Result[CausalAttribution]:
    """Compute Shapley-based attribution for a decision.

    This is the main entry point for Shapley attribution.
    It creates a value function from memory saliences and
    computes fair attribution.

    Args:
        trace_id: Decision trace ID
        memory_ids: Memories that influenced the decision
        memory_saliences: Salience scores for each memory
        outcome_quality: Actual outcome quality
        predictor: Optional custom predictor function

    Returns:
        CausalAttribution with Shapley-based contributions
    """
    if not memory_ids:
        return Result.ok(
            CausalAttribution(
                trace_id=trace_id,
                outcome_quality=outcome_quality,
                attributions={},
                total_attributed=0.0,
                method="shapley_empty",
            )
        )

    # Default value function: weighted sum of saliences
    def default_value_fn(subset: set[UUID]) -> float:
        if not subset:
            return 0.0
        total_salience = sum(memory_saliences.get(mid, 0.5) for mid in subset)
        max_salience = sum(memory_saliences.get(mid, 0.5) for mid in memory_ids)
        return (total_salience / max_salience) * outcome_quality if max_salience > 0 else 0.0

    value_fn = predictor or default_value_fn

    calculator = ShapleyCalculator(
        ShapleyConfig(
            max_permutations=min(1000, 100 * len(memory_ids)),
            use_exact=len(memory_ids) <= 6,
        )
    )

    result = await calculator.compute(
        memory_ids=memory_ids,
        value_function=value_fn,
        total_value=outcome_quality,
    )

    if not result.is_ok:
        return Result.err(result.error)

    shapley = result.value

    return Result.ok(
        CausalAttribution(
            trace_id=trace_id,
            outcome_quality=outcome_quality,
            attributions=shapley.attributions,
            total_attributed=sum(shapley.attributions.values()),
            method=f"shapley_{shapley.method}",
        )
    )


# Convenience singleton
_calculator: ShapleyCalculator | None = None


def get_shapley_calculator() -> ShapleyCalculator:
    """Get or create the Shapley calculator singleton."""
    global _calculator
    if _calculator is None:
        _calculator = ShapleyCalculator()
    return _calculator
