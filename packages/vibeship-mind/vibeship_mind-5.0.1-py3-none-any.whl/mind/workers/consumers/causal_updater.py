"""Causal graph updater consumer.

This consumer reacts to decision and outcome events to maintain
the causal graph in FalkorDB. It enables:
- Automatic recording of memory->decision influences
- Automatic recording of decision->outcome links
- Historical pattern analysis for predictions
"""

from uuid import UUID

import structlog

from mind.core.events.base import EventEnvelope, EventType
from mind.infrastructure.falkordb import CausalGraphRepository, get_falkordb_client
from mind.infrastructure.nats.client import NatsClient
from mind.infrastructure.nats.consumer import EventConsumer
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import MemoryRepository

logger = structlog.get_logger()


class CausalGraphUpdater:
    """Updates the causal graph based on decision and outcome events.

    This consumer listens for:
    - decision.tracked: Record memory->decision influence edges
    - outcome.observed: Record decision->outcome edges and update success rates

    The causal graph enables:
    - Attribution of outcomes to specific memories
    - Prediction of outcomes based on similar contexts
    - Counterfactual analysis ("what if we used different memories?")
    """

    CONSUMER_NAME = "causal-graph-updater"

    def __init__(self, client: NatsClient):
        self._client = client
        self._consumer = EventConsumer(client, self.CONSUMER_NAME)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Register event handlers."""
        self._consumer.on(EventType.DECISION_TRACKED, self._handle_decision_tracked)
        self._consumer.on(EventType.OUTCOME_OBSERVED, self._handle_outcome_observed)

    async def start(self) -> None:
        """Start the consumer."""
        logger.info("causal_updater_starting")
        await self._consumer.start(subjects=["mind.*.decision.tracked", "mind.*.outcome.observed"])

    async def stop(self) -> None:
        """Stop the consumer."""
        await self._consumer.stop()
        logger.info("causal_updater_stopped")

    async def _handle_decision_tracked(self, envelope: EventEnvelope) -> None:
        """Handle decision.tracked events.

        Creates nodes and edges in the causal graph:
        - Decision node
        - Memory nodes (if not exist)
        - INFLUENCED edges from memories to decision
        """
        log = logger.bind(
            event_id=str(envelope.event_id),
            user_id=str(envelope.user_id),
        )

        try:
            payload = envelope.payload
            trace_id = UUID(payload["trace_id"])
            memory_ids = [UUID(mid) for mid in payload.get("memory_ids", [])]
            memory_scores = payload.get("memory_scores", {})

            log = log.bind(
                trace_id=str(trace_id),
                memory_count=len(memory_ids),
            )

            if not memory_ids:
                log.debug("no_memories_to_link")
                return

            # Get FalkorDB client and create repository
            try:
                falkor_client = await get_falkordb_client()
                graph_repo = CausalGraphRepository(falkor_client)
            except Exception as e:
                log.warning("falkordb_unavailable", error=str(e))
                return

            # Add decision node
            result = await graph_repo.add_decision_node(
                trace_id=trace_id,
                user_id=envelope.user_id,
                decision_type=payload.get("decision_type", "unknown"),
                confidence=payload.get("confidence", 0.5),
            )
            if not result.is_ok:
                log.warning("decision_node_failed", error=str(result.error))
                return

            # Fetch memories and link them
            db = get_database()
            async with db.session() as session:
                memory_repo = MemoryRepository(session)

                for i, memory_id in enumerate(memory_ids):
                    mem_result = await memory_repo.get(memory_id)
                    if not mem_result.is_ok:
                        log.debug("memory_not_found", memory_id=str(memory_id))
                        continue

                    memory = mem_result.value

                    # Add memory node
                    import hashlib

                    content_hash = hashlib.sha256(memory.content.encode()).hexdigest()[:16]

                    await graph_repo.add_memory_node(
                        memory_id=memory.memory_id,
                        user_id=memory.user_id,
                        content_hash=content_hash,
                        temporal_level=memory.temporal_level.value,
                        salience=memory.effective_salience,
                    )

                    # Link memory to decision
                    influence_score = memory_scores.get(str(memory_id), 1.0 / (i + 1))
                    await graph_repo.link_memory_to_decision(
                        memory_id=memory_id,
                        trace_id=trace_id,
                        influence_score=influence_score,
                        rank=i + 1,
                    )

            log.info("causal_context_recorded", linked_memories=len(memory_ids))

        except Exception as e:
            log.error("decision_tracking_failed", error=str(e))
            raise  # Let consumer handle retry

    async def _handle_outcome_observed(self, envelope: EventEnvelope) -> None:
        """Handle outcome.observed events.

        Creates outcome node and LED_TO edge from decision.
        Updates memory success rates in the graph.
        """
        log = logger.bind(
            event_id=str(envelope.event_id),
            user_id=str(envelope.user_id),
        )

        try:
            payload = envelope.payload
            trace_id = UUID(payload["trace_id"])
            outcome_quality = payload.get("outcome_quality", 0.0)
            outcome_signal = payload.get("outcome_signal", "unknown")

            log = log.bind(
                trace_id=str(trace_id),
                outcome_quality=outcome_quality,
            )

            # Get FalkorDB client
            try:
                falkor_client = await get_falkordb_client()
                graph_repo = CausalGraphRepository(falkor_client)
            except Exception as e:
                log.warning("falkordb_unavailable", error=str(e))
                return

            # Add outcome node
            result = await graph_repo.add_outcome_node(
                trace_id=trace_id,
                quality=outcome_quality,
                signal=outcome_signal,
            )
            if not result.is_ok:
                log.warning("outcome_node_failed", error=str(result.error))
                return

            # Link decision to outcome
            result = await graph_repo.link_decision_to_outcome(trace_id)
            if not result.is_ok:
                log.warning("outcome_link_failed", error=str(result.error))
                return

            log.info("causal_outcome_recorded")

        except Exception as e:
            log.error("outcome_recording_failed", error=str(e))
            raise  # Let consumer handle retry


async def create_causal_updater() -> CausalGraphUpdater:
    """Factory to create and initialize the causal updater."""
    from mind.infrastructure.nats.client import get_nats_client

    client = await get_nats_client()
    return CausalGraphUpdater(client)
