"""Event service for publishing domain events.

This service abstracts event publishing across tiers:
- Standard tier: Uses PostgresEventPublisher (container adapter)
- Enterprise tier: Uses NATS-based EventPublisher

For backwards compatibility, falls back to NATS if container is not initialized.
"""

from uuid import UUID

import structlog

from typing import Any

from mind.core.decision.models import DecisionTrace, Outcome
from mind.core.errors import Result
from mind.core.events.decision import DecisionTracked, OutcomeObserved
from mind.core.events.interaction import (
    InteractionRecorded,
    InteractionType,
    ExtractionPriority,
)
from mind.core.events.memory import (
    MemoryCreated,
    MemoryRetrieval,
    MemorySalienceAdjusted,
    RetrievedMemory,
)
from mind.core.memory.models import Memory
from mind.infrastructure.nats.client import NatsClient, get_nats_client
from mind.infrastructure.nats.publisher import EventPublisher
from mind.ports.events import IEventPublisher

logger = structlog.get_logger()


class EventService:
    """Service for publishing domain events.

    This service provides high-level methods for publishing domain
    events. It handles connection management and wraps events in
    envelopes with proper correlation IDs.

    Tier handling:
    - Standard: Uses container's PostgresEventPublisher
    - Enterprise: Uses NATS EventPublisher
    """

    def __init__(self, client: NatsClient | None = None):
        self._client = client
        self._publisher: EventPublisher | None = None
        self._container_publisher: IEventPublisher | None = None
        self._use_container = False

    def _try_get_container_publisher(self) -> IEventPublisher | None:
        """Try to get event publisher from container."""
        try:
            from mind.container import get_container
            container = get_container()
            return container.event_publisher
        except RuntimeError:
            # Container not initialized
            return None

    async def _ensure_publisher(self) -> EventPublisher | IEventPublisher | None:
        """Lazily initialize publisher.

        Priority:
        1. Container's event publisher (Standard or Enterprise)
        2. Direct NATS publisher (backwards compatibility)
        3. None (graceful degradation)
        """
        # Try container first
        if self._container_publisher is None and not self._use_container:
            self._container_publisher = self._try_get_container_publisher()
            if self._container_publisher is not None:
                self._use_container = True
                return self._container_publisher

        if self._use_container:
            return self._container_publisher

        # Fall back to NATS publisher for backwards compatibility
        if self._publisher is None:
            if self._client is None:
                try:
                    self._client = await get_nats_client()
                except Exception as e:
                    logger.debug("nats_unavailable", error=str(e))
                    return None
            self._publisher = EventPublisher(self._client)
        return self._publisher

    async def _publish_via_container(
        self,
        event_type: str,
        payload: dict,
        user_id: UUID | None = None,
    ) -> None:
        """Publish via container's IEventPublisher."""
        await self._container_publisher.publish(
            event_type=event_type,
            payload=payload,
            user_id=str(user_id) if user_id else None,
        )

    async def publish_memory_created(
        self,
        memory: Memory,
        correlation_id: UUID | None = None,
    ) -> Result[None]:
        """Publish a MemoryCreated event."""
        try:
            publisher = await self._ensure_publisher()
            if publisher is None:
                return Result.ok(None)  # Graceful degradation

            event = MemoryCreated(
                memory_id=memory.memory_id,
                content=memory.content,
                content_type=memory.content_type,
                temporal_level=memory.temporal_level,
                base_salience=memory.base_salience,
                valid_from=memory.valid_from,
            )

            # Use container publisher if available
            if self._use_container:
                await self._publish_via_container(
                    event_type="memory.created",
                    payload={
                        "memory_id": str(memory.memory_id),
                        "content": memory.content,
                        "content_type": memory.content_type,
                        "temporal_level": memory.temporal_level.name.lower(),
                        "base_salience": memory.base_salience,
                        "valid_from": memory.valid_from.isoformat(),
                    },
                    user_id=memory.user_id,
                )
                return Result.ok(None)

            # NATS publisher
            result = await publisher.publish_event(
                event=event,
                user_id=memory.user_id,
                correlation_id=correlation_id,
            )

            if result.is_ok:
                return Result.ok(None)
            return Result.err(result.error)

        except Exception as e:
            logger.warning("event_publish_skipped", error=str(e), event_type="memory.created")
            # Don't fail the operation if event publishing fails
            return Result.ok(None)

    async def publish_memory_retrieval(
        self,
        user_id: UUID,
        retrieval_id: UUID,
        query: str,
        memories: list[tuple[UUID, int, float, str]],  # (memory_id, rank, score, source)
        latency_ms: float,
        trace_id: UUID | None = None,
        correlation_id: UUID | None = None,
    ) -> Result[None]:
        """Publish a MemoryRetrieval event."""
        try:
            publisher = await self._ensure_publisher()
            if publisher is None:
                return Result.ok(None)  # Graceful degradation

            # Use container publisher if available
            if self._use_container:
                await self._publish_via_container(
                    event_type="memory.retrieval",
                    payload={
                        "retrieval_id": str(retrieval_id),
                        "query": query,
                        "memories": [
                            {"memory_id": str(mid), "rank": rank, "score": score, "source": source}
                            for mid, rank, score, source in memories
                        ],
                        "latency_ms": latency_ms,
                        "trace_id": str(trace_id) if trace_id else None,
                    },
                    user_id=user_id,
                )
                return Result.ok(None)

            # NATS publisher
            retrieved = [
                RetrievedMemory(
                    memory_id=mid,
                    rank=rank,
                    score=score,
                    source=source,
                )
                for mid, rank, score, source in memories
            ]

            event = MemoryRetrieval(
                retrieval_id=retrieval_id,
                query=query,
                memories=retrieved,
                latency_ms=latency_ms,
                trace_id=trace_id,
            )

            result = await publisher.publish_event(
                event=event,
                user_id=user_id,
                correlation_id=correlation_id,
            )

            if result.is_ok:
                return Result.ok(None)
            return Result.err(result.error)

        except Exception as e:
            logger.warning("event_publish_skipped", error=str(e), event_type="memory.retrieval")
            return Result.ok(None)

    async def publish_salience_adjusted(
        self,
        user_id: UUID,
        memory_id: UUID,
        trace_id: UUID,
        previous_adjustment: float,
        new_adjustment: float,
        delta: float,
        reason: str,
        correlation_id: UUID | None = None,
    ) -> Result[None]:
        """Publish a MemorySalienceAdjusted event."""
        try:
            publisher = await self._ensure_publisher()
            if publisher is None:
                return Result.ok(None)  # Graceful degradation

            # Use container publisher if available
            if self._use_container:
                await self._publish_via_container(
                    event_type="memory.salience_adjusted",
                    payload={
                        "memory_id": str(memory_id),
                        "trace_id": str(trace_id),
                        "previous_adjustment": previous_adjustment,
                        "new_adjustment": new_adjustment,
                        "delta": delta,
                        "reason": reason,
                    },
                    user_id=user_id,
                )
                return Result.ok(None)

            # NATS publisher
            event = MemorySalienceAdjusted(
                memory_id=memory_id,
                trace_id=trace_id,
                previous_adjustment=previous_adjustment,
                new_adjustment=new_adjustment,
                delta=delta,
                reason=reason,
            )

            result = await publisher.publish_event(
                event=event,
                user_id=user_id,
                correlation_id=correlation_id,
            )

            if result.is_ok:
                return Result.ok(None)
            return Result.err(result.error)

        except Exception as e:
            logger.warning(
                "event_publish_skipped", error=str(e), event_type="memory.salience_adjusted"
            )
            return Result.ok(None)

    async def publish_decision_tracked(
        self,
        trace: DecisionTrace,
        correlation_id: UUID | None = None,
    ) -> Result[None]:
        """Publish a DecisionTracked event."""
        try:
            publisher = await self._ensure_publisher()
            if publisher is None:
                return Result.ok(None)  # Graceful degradation

            # Use container publisher if available
            if self._use_container:
                await self._publish_via_container(
                    event_type="decision.tracked",
                    payload={
                        "trace_id": str(trace.trace_id),
                        "session_id": str(trace.session_id) if trace.session_id else None,
                        "memory_ids": [str(m) for m in trace.memory_ids],
                        "memory_scores": trace.memory_scores,
                        "decision_type": trace.decision_type,
                        "decision_summary": trace.decision_summary,
                        "confidence": trace.confidence,
                        "alternatives_count": trace.alternatives_count,
                    },
                    user_id=trace.user_id,
                )
                return Result.ok(None)

            # NATS publisher
            event = DecisionTracked(
                trace_id=trace.trace_id,
                session_id=trace.session_id,
                memory_ids=trace.memory_ids,
                memory_scores=trace.memory_scores,
                decision_type=trace.decision_type,
                decision_summary=trace.decision_summary,
                confidence=trace.confidence,
                alternatives_count=trace.alternatives_count,
            )

            result = await publisher.publish_event(
                event=event,
                user_id=trace.user_id,
                correlation_id=correlation_id,
            )

            if result.is_ok:
                return Result.ok(None)
            return Result.err(result.error)

        except Exception as e:
            logger.warning("event_publish_skipped", error=str(e), event_type="decision.tracked")
            return Result.ok(None)

    async def publish_outcome_observed(
        self,
        user_id: UUID,
        trace_id: UUID,
        outcome: Outcome,
        attributions: dict[str, float],
        correlation_id: UUID | None = None,
    ) -> Result[None]:
        """Publish an OutcomeObserved event."""
        try:
            publisher = await self._ensure_publisher()
            if publisher is None:
                return Result.ok(None)  # Graceful degradation

            # Use container publisher if available
            if self._use_container:
                await self._publish_via_container(
                    event_type="outcome.observed",
                    payload={
                        "trace_id": str(trace_id),
                        "outcome_quality": outcome.quality,
                        "outcome_signal": outcome.signal,
                        "observed_at": outcome.observed_at.isoformat() if outcome.observed_at else None,
                        "memory_attributions": attributions,
                    },
                    user_id=user_id,
                )
                return Result.ok(None)

            # NATS publisher
            event = OutcomeObserved(
                trace_id=trace_id,
                outcome_quality=outcome.quality,
                outcome_signal=outcome.signal,
                observed_at=outcome.observed_at,
                memory_attributions=attributions,
            )

            result = await publisher.publish_event(
                event=event,
                user_id=user_id,
                correlation_id=correlation_id,
            )

            if result.is_ok:
                return Result.ok(None)
            return Result.err(result.error)

        except Exception as e:
            logger.warning("event_publish_skipped", error=str(e), event_type="outcome.observed")
            return Result.ok(None)

    async def publish_interaction_recorded(
        self,
        user_id: UUID,
        session_id: UUID,
        content: str,
        interaction_type: InteractionType = InteractionType.TEXT,
        context: dict | None = None,
        extraction_priority: ExtractionPriority = ExtractionPriority.NORMAL,
        skip_extraction: bool = False,
        correlation_id: UUID | None = None,
    ) -> Result[None]:
        """Publish an InteractionRecorded event.

        This event triggers the memory extraction pipeline.
        """
        try:
            publisher = await self._ensure_publisher()
            if publisher is None:
                return Result.ok(None)  # Graceful degradation

            # Use container publisher if available
            if self._use_container:
                from uuid import uuid4
                interaction_id = uuid4()
                await self._publish_via_container(
                    event_type="interaction.recorded",
                    payload={
                        "interaction_id": str(interaction_id),
                        "session_id": str(session_id),
                        "interaction_type": interaction_type.value,
                        "content": content,
                        "content_length": len(content),
                        "context": context or {},
                        "extraction_priority": extraction_priority.value,
                        "skip_extraction": skip_extraction,
                    },
                    user_id=user_id,
                )
                logger.debug(
                    "interaction_recorded_published",
                    interaction_id=str(interaction_id),
                    content_length=len(content),
                )
                return Result.ok(None)

            # NATS publisher
            event = InteractionRecorded(
                session_id=session_id,
                interaction_type=interaction_type,
                content=content,
                content_length=len(content),
                context=context or {},
                extraction_priority=extraction_priority,
                skip_extraction=skip_extraction,
            )

            result = await publisher.publish_event(
                event=event,
                user_id=user_id,
                correlation_id=correlation_id,
            )

            if result.is_ok:
                logger.debug(
                    "interaction_recorded_published",
                    interaction_id=str(event.interaction_id),
                    content_length=len(content),
                )
                return Result.ok(None)
            return Result.err(result.error)

        except Exception as e:
            logger.warning(
                "event_publish_skipped", error=str(e), event_type="interaction.recorded"
            )
            return Result.ok(None)


# Global event service instance
_event_service: EventService | None = None


def get_event_service() -> EventService:
    """Get or create event service instance."""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
