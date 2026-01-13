"""Synchronous learning service for Standard tier.

This service implements immediate salience updates when outcomes
are recorded, without requiring an event-driven architecture.

Key features:
- Immediate salience adjustment on outcome observation
- Attribution-weighted updates (memories that contributed more get bigger adjustments)
- Bounds checking (salience stays in valid range)
- Causal graph updates (records memory → decision → outcome relationships)
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

import structlog

from mind.core.causal.models import CausalNode, CausalRelationship, NodeType, RelationshipType
from mind.core.decision.models import DecisionTrace, Outcome, SalienceUpdate
from mind.core.errors import ErrorCode, MindError, Result
from mind.ports.graphs import ICausalGraph
from mind.ports.storage import IDecisionStorage, IMemoryStorage

logger = structlog.get_logger()

# Global instance for container-based access
_learning_service: Optional["LearningService"] = None


@dataclass
class LearningResult:
    """Result of a learning operation."""

    trace_id: UUID
    outcome_quality: float
    memories_updated: int
    salience_updates: list[SalienceUpdate]
    causal_edges_created: int


class LearningService:
    """Synchronous learning service for outcome-based salience adjustment.

    This service is the core of the Standard tier's learning loop:
    1. Agent retrieves memories and makes a decision (DecisionTrace created)
    2. Outcome is observed (good/bad/neutral)
    3. LearningService immediately updates:
       - Decision trace with outcome
       - Memory salience based on attribution
       - Causal graph with decision→outcome link

    For Standard tier, all updates happen synchronously in the same request.
    Enterprise tier uses NATS events for async processing.
    """

    # Maximum salience adjustment per outcome (prevents wild swings)
    MAX_ADJUSTMENT_DELTA = 0.1

    # Minimum attribution weight to consider a memory influential
    MIN_ATTRIBUTION_WEIGHT = 0.05

    def __init__(
        self,
        memory_storage: IMemoryStorage,
        decision_storage: IDecisionStorage,
        causal_graph: Optional[ICausalGraph] = None,
    ):
        """Initialize the learning service.

        Args:
            memory_storage: Storage for memory operations
            decision_storage: Storage for decision traces
            causal_graph: Optional causal graph for relationship tracking
        """
        self._memory_storage = memory_storage
        self._decision_storage = decision_storage
        self._causal_graph = causal_graph

    async def record_outcome(
        self,
        trace_id: UUID,
        user_id: UUID,
        quality: float,
        signal: str,
        feedback: Optional[str] = None,
    ) -> Result[LearningResult]:
        """Record an outcome and immediately update memory saliences.

        This is the main entry point for the learning loop. When an outcome
        is observed:
        1. Fetch the original decision trace
        2. Calculate attribution for each memory
        3. Update each memory's salience
        4. Update the causal graph
        5. Mark the trace as having an observed outcome

        Args:
            trace_id: The decision trace this outcome is for
            user_id: The user who made the decision
            quality: Outcome quality from -1.0 (bad) to 1.0 (good)
            signal: How the outcome was observed (e.g., "user_accepted", "task_failed")
            feedback: Optional text feedback

        Returns:
            Result with learning details or error
        """
        log = logger.bind(
            trace_id=str(trace_id),
            user_id=str(user_id),
            quality=quality,
            signal=signal,
        )

        # Validate quality range
        if not -1.0 <= quality <= 1.0:
            return Result.err(
                MindError(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"Outcome quality must be between -1.0 and 1.0, got {quality}",
                )
            )

        # 1. Fetch the decision trace
        log.debug("fetching_decision_trace")
        trace = await self._decision_storage.get_trace(trace_id)
        if trace is None:
            log.warning("trace_not_found")
            return Result.err(
                MindError(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Decision trace {trace_id} not found",
                )
            )

        # Verify user ownership
        if trace.user_id != user_id:
            log.warning("unauthorized_trace_access")
            return Result.err(
                MindError(
                    code=ErrorCode.UNAUTHORIZED,
                    message="Cannot record outcome for another user's decision",
                )
            )

        # Check if already has outcome
        if trace.outcome_observed:
            log.info("outcome_already_recorded", existing_quality=trace.outcome_quality)
            return Result.err(
                MindError(
                    code=ErrorCode.CONFLICT,
                    message="Outcome already recorded for this decision",
                )
            )

        # 2. Create outcome object
        outcome = Outcome(
            trace_id=trace_id,
            quality=quality,
            signal=signal,
            observed_at=datetime.now(UTC),
            feedback_text=feedback,
        )

        # 3. Calculate attribution-weighted salience updates
        log.debug("calculating_attribution", memory_count=len(trace.memory_ids))
        salience_updates = self._calculate_attribution(trace, outcome)

        # 4. Apply salience updates to memories
        log.debug("applying_salience_updates", update_count=len(salience_updates))
        memories_updated = 0
        for update in salience_updates:
            try:
                await self._memory_storage.update_salience(
                    memory_id=update.memory_id,
                    adjustment=update.delta,
                )
                memories_updated += 1
            except Exception as e:
                log.warning(
                    "salience_update_failed",
                    memory_id=str(update.memory_id),
                    error=str(e),
                )

        # 5. Record outcome in decision storage
        log.debug("recording_outcome")
        await self._decision_storage.record_outcome(
            trace_id=trace_id,
            outcome=outcome,
        )

        # 6. Update causal graph if available
        causal_edges = 0
        if self._causal_graph:
            log.debug("updating_causal_graph")
            causal_edges = await self._update_causal_graph(trace, outcome)

        log.info(
            "learning_complete",
            memories_updated=memories_updated,
            salience_updates=len(salience_updates),
            causal_edges=causal_edges,
        )

        return Result.ok(
            LearningResult(
                trace_id=trace_id,
                outcome_quality=quality,
                memories_updated=memories_updated,
                salience_updates=salience_updates,
                causal_edges_created=causal_edges,
            )
        )

    def _calculate_attribution(
        self,
        trace: DecisionTrace,
        outcome: Outcome,
    ) -> list[SalienceUpdate]:
        """Calculate salience updates based on memory contribution.

        Uses the retrieval scores stored in the trace to weight each memory's
        contribution to the decision. Higher-scoring memories get larger
        adjustments when outcomes are observed.

        Args:
            trace: The decision trace with memory scores
            outcome: The observed outcome

        Returns:
            List of salience updates to apply
        """
        updates = []

        # Normalize weights so they sum to 1.0
        total_score = sum(trace.memory_scores.values())
        if total_score == 0:
            # No scores? Distribute equally
            if trace.memory_ids:
                equal_weight = 1.0 / len(trace.memory_ids)
                for memory_id in trace.memory_ids:
                    update = SalienceUpdate.from_outcome(
                        memory_id=memory_id,
                        trace_id=trace.trace_id,
                        outcome=outcome,
                        contribution=equal_weight,
                    )
                    updates.append(update)
            return updates

        # Calculate weighted contribution for each memory
        for memory_id in trace.memory_ids:
            memory_id_str = str(memory_id)
            if memory_id_str not in trace.memory_scores:
                continue

            raw_score = trace.memory_scores[memory_id_str]
            contribution = raw_score / total_score

            # Skip memories with negligible contribution
            if contribution < self.MIN_ATTRIBUTION_WEIGHT:
                continue

            update = SalienceUpdate.from_outcome(
                memory_id=memory_id,
                trace_id=trace.trace_id,
                outcome=outcome,
                contribution=contribution,
            )

            # Clamp delta to prevent extreme adjustments
            clamped_delta = max(
                -self.MAX_ADJUSTMENT_DELTA,
                min(self.MAX_ADJUSTMENT_DELTA, update.delta),
            )

            if clamped_delta != 0:
                updates.append(
                    SalienceUpdate(
                        memory_id=update.memory_id,
                        trace_id=update.trace_id,
                        delta=clamped_delta,
                        reason=update.reason,
                    )
                )

        return updates

    async def _update_causal_graph(
        self,
        trace: DecisionTrace,
        outcome: Outcome,
    ) -> int:
        """Update causal graph with decision→outcome relationship.

        Creates nodes and edges to represent:
        - Memory → Decision (influenced)
        - Decision → Outcome (led_to)

        This enables future queries like:
        - "Which memories tend to lead to positive outcomes?"
        - "What decision patterns have worked well?"

        Args:
            trace: The decision trace
            outcome: The observed outcome

        Returns:
            Number of edges created
        """
        if not self._causal_graph:
            return 0

        edges_created = 0

        try:
            # Create decision node
            decision_node = CausalNode(
                node_id=trace.trace_id,
                node_type=NodeType.DECISION,
                user_id=trace.user_id,
                properties={
                    "decision_type": trace.decision_type,
                    "confidence": trace.confidence,
                    "created_at": trace.created_at.isoformat(),
                },
                created_at=trace.created_at,
            )
            await self._causal_graph.add_node(decision_node)

            # Create outcome node
            from uuid import uuid4

            outcome_node_id = uuid4()
            outcome_node = CausalNode(
                node_id=outcome_node_id,
                node_type=NodeType.OUTCOME,
                user_id=trace.user_id,
                properties={
                    "quality": outcome.quality,
                    "signal": outcome.signal,
                    "observed_at": outcome.observed_at.isoformat(),
                },
                created_at=outcome.observed_at,
            )
            await self._causal_graph.add_node(outcome_node)

            # Create memory → decision edges
            for memory_id in trace.memory_ids:
                memory_id_str = str(memory_id)
                strength = trace.memory_scores.get(memory_id_str, 0.5)

                # Ensure memory node exists
                memory_node = CausalNode(
                    node_id=memory_id,
                    node_type=NodeType.MEMORY,
                    user_id=trace.user_id,
                    properties={},
                    created_at=datetime.now(UTC),
                )
                await self._causal_graph.add_node(memory_node)

                # Memory influenced decision
                await self._causal_graph.add_edge(
                    source_id=memory_id,
                    target_id=trace.trace_id,
                    relationship_type=RelationshipType.INFLUENCED,
                    strength=min(1.0, strength),
                    confidence=trace.confidence,
                )
                edges_created += 1

            # Decision led to outcome
            # Strength is based on outcome quality (absolute value for relationship strength)
            outcome_strength = abs(outcome.quality)
            await self._causal_graph.add_edge(
                source_id=trace.trace_id,
                target_id=outcome_node_id,
                relationship_type=RelationshipType.LED_TO,
                strength=outcome_strength,
                confidence=1.0,  # We directly observed this
                properties={"quality": outcome.quality},
            )
            edges_created += 1

        except Exception as e:
            logger.warning(
                "causal_graph_update_failed",
                trace_id=str(trace.trace_id),
                error=str(e),
            )

        return edges_created

    async def get_memory_effectiveness(
        self,
        user_id: UUID,
        memory_id: UUID,
    ) -> Result[dict]:
        """Get effectiveness statistics for a memory.

        Returns information about how often this memory has led to
        positive vs negative outcomes when used in decisions.

        Args:
            user_id: The user who owns the memory
            memory_id: The memory to analyze

        Returns:
            Result with effectiveness statistics
        """
        # Get the memory
        memory = await self._memory_storage.get(memory_id)
        if memory is None:
            return Result.err(
                MindError(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Memory {memory_id} not found",
                )
            )

        if memory.user_id != user_id:
            return Result.err(
                MindError(
                    code=ErrorCode.UNAUTHORIZED,
                    message="Cannot access another user's memory",
                )
            )

        # Calculate statistics
        total = memory.positive_outcomes + memory.negative_outcomes
        success_rate = (
            memory.positive_outcomes / total if total > 0 else 0.0
        )

        return Result.ok({
            "memory_id": str(memory_id),
            "decision_count": memory.decision_count,
            "positive_outcomes": memory.positive_outcomes,
            "negative_outcomes": memory.negative_outcomes,
            "success_rate": success_rate,
            "effective_salience": memory.effective_salience,
            "base_salience": memory.base_salience,
            "outcome_adjustment": memory.outcome_adjustment,
        })


def get_learning_service() -> LearningService:
    """Get or create the global LearningService instance.

    Uses the container to get the appropriate adapters for the current tier.
    For Standard tier, uses PostgreSQL adapters.
    For Enterprise tier, uses the full adapter set.

    Returns:
        LearningService configured with appropriate adapters
    """
    global _learning_service

    if _learning_service is not None:
        return _learning_service

    from mind.container import get_container

    container = get_container()
    if container is None:
        raise RuntimeError(
            "MindContainer not initialized. Call set_container() first."
        )

    _learning_service = LearningService(
        memory_storage=container.memory_storage,
        decision_storage=container.decision_storage,
        causal_graph=container.causal_graph,
    )

    return _learning_service


def reset_learning_service() -> None:
    """Reset the global LearningService (for testing)."""
    global _learning_service
    _learning_service = None
