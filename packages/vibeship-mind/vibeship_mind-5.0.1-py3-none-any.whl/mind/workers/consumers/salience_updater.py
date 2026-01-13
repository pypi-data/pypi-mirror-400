"""Memory salience updater consumer.

This consumer reacts to outcome events and updates memory salience.
It enables asynchronous salience adjustment with retry semantics.

Note: The API currently updates salience synchronously for consistency.
This consumer provides an async path for:
- Retry handling if sync updates fail
- Eventual migration to fully async updates
- Propagating salience changes to other systems
"""

from uuid import UUID

import structlog

from mind.core.decision.models import Outcome, SalienceUpdate
from mind.core.events.base import EventEnvelope, EventType
from mind.infrastructure.nats.client import NatsClient
from mind.infrastructure.nats.consumer import EventConsumer
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import DecisionRepository, MemoryRepository
from mind.services.events import get_event_service

logger = structlog.get_logger()


class SalienceUpdater:
    """Updates memory salience based on outcome events.

    This consumer listens for:
    - outcome.observed: Update salience of memories that influenced the decision

    The salience update algorithm:
    1. Get decision trace to find contributing memories
    2. Calculate attribution based on memory scores
    3. Compute salience delta based on outcome quality
    4. Apply updates to each memory
    5. Publish salience_adjusted events
    """

    CONSUMER_NAME = "salience-updater"

    def __init__(self, client: NatsClient):
        self._client = client
        self._consumer = EventConsumer(client, self.CONSUMER_NAME)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Register event handlers."""
        self._consumer.on(EventType.OUTCOME_OBSERVED, self._handle_outcome_observed)

    async def start(self) -> None:
        """Start the consumer."""
        logger.info("salience_updater_starting")
        await self._consumer.start(subjects=["mind.outcome.observed.*"])

    async def stop(self) -> None:
        """Stop the consumer."""
        await self._consumer.stop()
        logger.info("salience_updater_stopped")

    async def _handle_outcome_observed(self, envelope: EventEnvelope) -> None:
        """Handle outcome.observed events.

        Computes attribution and updates salience for all memories
        that contributed to the decision.
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
            memory_attributions = payload.get("memory_attributions", {})

            log = log.bind(
                trace_id=str(trace_id),
                outcome_quality=outcome_quality,
                memory_count=len(memory_attributions),
            )

            if not memory_attributions:
                log.debug("no_memories_to_update")
                return

            db = get_database()
            async with db.session() as session:
                decision_repo = DecisionRepository(session)
                memory_repo = MemoryRepository(session)

                # Get the decision trace for context
                trace_result = await decision_repo.get_trace(trace_id)
                if not trace_result.is_ok:
                    log.warning("trace_not_found", trace_id=str(trace_id))
                    return

                # Build outcome object
                outcome = Outcome(
                    trace_id=trace_id,
                    quality=outcome_quality,
                    signal=outcome_signal,
                )

                # Process each memory attribution
                salience_updates = []
                for memory_id_str, contribution in memory_attributions.items():
                    memory_id = UUID(memory_id_str)

                    # Check if memory still exists
                    mem_result = await memory_repo.get(memory_id)
                    if not mem_result.is_ok:
                        log.debug("memory_not_found", memory_id=memory_id_str)
                        continue

                    memory = mem_result.value
                    previous_adjustment = memory.outcome_adjustment

                    # Calculate salience update
                    update = SalienceUpdate.from_outcome(
                        memory_id=memory_id,
                        trace_id=trace_id,
                        outcome=outcome,
                        contribution=contribution,
                    )

                    # Apply update
                    result = await memory_repo.update_salience(
                        memory_id=memory_id,
                        adjustment=update,
                    )

                    if result.is_ok:
                        salience_updates.append(
                            {
                                "memory_id": memory_id,
                                "previous_adjustment": previous_adjustment,
                                "new_adjustment": previous_adjustment + update.delta,
                                "delta": update.delta,
                                "reason": update.reason,
                            }
                        )
                        log.debug(
                            "salience_updated",
                            memory_id=memory_id_str,
                            delta=update.delta,
                        )
                    else:
                        log.warning(
                            "salience_update_failed",
                            memory_id=memory_id_str,
                            error=str(result.error),
                        )

            # Publish salience adjustment events
            await self._publish_salience_events(
                user_id=envelope.user_id,
                salience_updates=salience_updates,
            )

            log.info(
                "salience_updates_applied",
                updates_count=len(salience_updates),
            )

        except Exception as e:
            log.error("salience_update_failed", error=str(e))
            raise  # Let consumer handle retry

    async def _publish_salience_events(
        self,
        user_id: UUID,
        salience_updates: list[dict],
    ) -> None:
        """Publish salience_adjusted events for each update."""
        try:
            event_service = get_event_service()

            for update in salience_updates:
                await event_service.publish_salience_adjusted(
                    user_id=user_id,
                    memory_id=update["memory_id"],
                    trace_id=update.get("trace_id"),
                    previous_adjustment=update["previous_adjustment"],
                    new_adjustment=update["new_adjustment"],
                    delta=update["delta"],
                    reason=update["reason"],
                )

        except Exception as e:
            logger.warning(
                "salience_event_publish_failed",
                error=str(e),
                user_id=str(user_id),
            )


async def create_salience_updater() -> SalienceUpdater:
    """Factory to create and initialize the salience updater."""
    from mind.infrastructure.nats.client import get_nats_client

    client = await get_nats_client()
    return SalienceUpdater(client)
