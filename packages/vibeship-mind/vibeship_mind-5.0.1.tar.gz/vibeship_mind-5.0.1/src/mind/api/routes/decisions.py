"""Decision tracking API endpoints."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException

from mind.api.deps import get_decision_storage, get_memory_storage, is_container_ready
from mind.api.schemas.decision import (
    ContextRequest,
    ContextResponse,
    DecisionTraceResponse,
    OutcomeRequest,
    OutcomeResponse,
    TrackRequest,
    TrackResponse,
)
from mind.config import get_settings
from mind.core.decision.models import DecisionTrace, Outcome, SalienceUpdate
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import DecisionRepository, MemoryRepository
from mind.security.auth import AuthenticatedUser, get_auth_dependency
from mind.services.events import get_event_service

logger = structlog.get_logger()
router = APIRouter()


def _validate_user_access(
    request_user_id: UUID,
    authenticated_user: AuthenticatedUser | None,
) -> None:
    """Validate that authenticated user can access the requested user's data."""
    settings = get_settings()

    if settings.environment != "production" and not settings.require_auth:
        return

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    if authenticated_user.user_id != request_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's data")


@router.post("/track", response_model=TrackResponse, status_code=201)
async def track_decision(
    request: TrackRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> TrackResponse:
    """Track a decision and the memories that influenced it.

    This creates a decision trace that links the retrieved memories
    to the decision made. Later, when the outcome is observed,
    we can attribute success/failure to specific memories and
    adjust their salience.

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    trace = DecisionTrace(
        trace_id=uuid4(),
        user_id=request.user_id,
        session_id=request.session_id,
        memory_ids=request.memory_ids,
        memory_scores=request.memory_scores or {},
        decision_type=request.decision_type,
        decision_summary=request.decision_summary,
        confidence=request.confidence,
        alternatives_count=request.alternatives_count,
    )

    # Use container adapter if available, otherwise fall back to legacy
    if is_container_ready():
        try:
            storage = get_decision_storage()
            created_trace = await storage.store_trace(trace)
            logger.debug("trace_stored_via_container", trace_id=str(created_trace.trace_id))
        except Exception as e:
            logger.error("container_storage_failed", error=str(e))
            raise HTTPException(status_code=500, detail={"message": f"Storage error: {e}"})
    else:
        # Legacy path for backward compatibility
        db = get_database()
        async with db.session() as session:
            repo = DecisionRepository(session)
            result = await repo.create_trace(trace)

            if not result.is_ok:
                raise HTTPException(status_code=400, detail=result.error.to_dict())

            created_trace = result.value

    response = TrackResponse(
        trace_id=created_trace.trace_id,
        created_at=created_trace.created_at,
    )

    # Publish event (fire-and-forget)
    try:
        event_service = get_event_service()
        await event_service.publish_decision_tracked(created_trace)
    except Exception as e:
        logger.warning("event_publish_failed", error=str(e), trace_id=str(created_trace.trace_id))

    return response


@router.post("/outcome", response_model=OutcomeResponse)
async def observe_outcome(
    request: OutcomeRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> OutcomeResponse:
    """Record an outcome for a previous decision.

    This is the feedback loop that enables learning. When we observe
    that a decision led to a good or bad outcome, we update the
    salience of the memories that influenced that decision.

    Positive outcomes increase memory salience, making those memories
    more likely to be retrieved in similar future situations.
    Negative outcomes decrease salience.

    Authentication:
        - Required in production
        - Optional in development
    """
    outcome = Outcome(
        trace_id=request.trace_id,
        quality=request.quality,
        signal=request.signal,
        feedback_text=request.feedback,
    )

    # Use container adapter if available, otherwise fall back to legacy
    if is_container_ready():
        try:
            decision_storage = get_decision_storage()
            memory_storage = get_memory_storage()

            # Get the trace
            trace = await decision_storage.get_trace(request.trace_id)
            if trace is None:
                raise HTTPException(status_code=404, detail={"message": "Decision trace not found"})

            user_id = trace.user_id

            # Validate user can access this trace
            _validate_user_access(user_id, user)

            # Calculate attribution (simple: proportional to retrieval score)
            total_score = sum(trace.memory_scores.values()) or 1.0
            attributions = {mid: score / total_score for mid, score in trace.memory_scores.items()}

            # Record outcome
            await decision_storage.record_outcome(request.trace_id, outcome)

            # Update memory salience
            salience_updates = []
            for memory_id, contribution in attributions.items():
                update = SalienceUpdate.from_outcome(
                    memory_id=UUID(memory_id),
                    trace_id=request.trace_id,
                    outcome=outcome,
                    contribution=contribution,
                )
                salience_updates.append(update)

                await memory_storage.update_salience(UUID(memory_id), update.delta)
                await decision_storage.store_salience_update(update)

            response = OutcomeResponse(
                trace_id=request.trace_id,
                outcome_quality=outcome.quality,
                memories_updated=len(salience_updates),
                salience_changes={str(u.memory_id): u.delta for u in salience_updates},
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("container_outcome_failed", error=str(e))
            raise HTTPException(status_code=500, detail={"message": f"Storage error: {e}"})
    else:
        # Legacy path for backward compatibility
        db = get_database()
        async with db.session() as session:
            decision_repo = DecisionRepository(session)
            memory_repo = MemoryRepository(session)

            # Get the trace
            trace_result = await decision_repo.get_trace(request.trace_id)
            if not trace_result.is_ok:
                raise HTTPException(status_code=404, detail=trace_result.error.to_dict())

            trace = trace_result.value
            user_id = trace.user_id

            # Validate user can access this trace
            _validate_user_access(user_id, user)

            # Calculate attribution (simple: proportional to retrieval score)
            total_score = sum(trace.memory_scores.values()) or 1.0
            attributions = {mid: score / total_score for mid, score in trace.memory_scores.items()}

            # Record outcome
            result = await decision_repo.record_outcome(
                trace_id=request.trace_id,
                outcome=outcome,
                attributions=attributions,
            )

            if not result.is_ok:
                raise HTTPException(status_code=400, detail=result.error.to_dict())

            # Update memory salience
            salience_updates = []
            for memory_id, contribution in attributions.items():
                update = SalienceUpdate.from_outcome(
                    memory_id=UUID(memory_id),
                    trace_id=request.trace_id,
                    outcome=outcome,
                    contribution=contribution,
                )
                salience_updates.append(update)

                await memory_repo.update_salience(
                    memory_id=UUID(memory_id),
                    adjustment=update,
                )

            response = OutcomeResponse(
                trace_id=request.trace_id,
                outcome_quality=outcome.quality,
                memories_updated=len(salience_updates),
                salience_changes={str(u.memory_id): u.delta for u in salience_updates},
            )

    # Publish events (fire-and-forget)
    try:
        event_service = get_event_service()

        # Publish outcome observed event
        await event_service.publish_outcome_observed(
            user_id=user_id,
            trace_id=request.trace_id,
            outcome=outcome,
            attributions=attributions,
        )

        # Publish salience adjustment events for each memory
        for update in salience_updates:
            await event_service.publish_salience_adjusted(
                user_id=user_id,
                memory_id=update.memory_id,
                trace_id=update.trace_id,
                previous_adjustment=0.0,  # We don't track this here
                new_adjustment=update.delta,
                delta=update.delta,
                reason=update.reason,
            )
    except Exception as e:
        logger.warning("event_publish_failed", error=str(e), trace_id=str(request.trace_id))

    return response


@router.get("/{trace_id}", response_model=DecisionTraceResponse)
async def get_decision(
    trace_id: UUID,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> DecisionTraceResponse:
    """Get a decision trace by ID.

    Returns the full decision trace including outcome information
    if an outcome has been observed.

    Authentication:
        - Required in production
        - Optional in development
    """
    # Use container adapter if available, otherwise fall back to legacy
    if is_container_ready():
        try:
            storage = get_decision_storage()
            trace = await storage.get_trace(trace_id)
            if trace is None:
                raise HTTPException(status_code=404, detail={"message": "Decision trace not found"})
        except HTTPException:
            raise
        except Exception as e:
            logger.error("container_get_failed", error=str(e))
            raise HTTPException(status_code=500, detail={"message": f"Storage error: {e}"})
    else:
        db = get_database()
        async with db.session() as session:
            repo = DecisionRepository(session)
            result = await repo.get_trace(trace_id)

            if not result.is_ok:
                raise HTTPException(status_code=404, detail=result.error.to_dict())

            trace = result.value

    # Validate user can access this trace
    _validate_user_access(trace.user_id, user)

    return DecisionTraceResponse(
        trace_id=trace.trace_id,
        user_id=trace.user_id,
        session_id=trace.session_id,
        memory_ids=trace.memory_ids,
        memory_scores=trace.memory_scores,
        decision_type=trace.decision_type,
        decision_summary=trace.decision_summary,
        confidence=trace.confidence,
        alternatives_count=trace.alternatives_count,
        created_at=trace.created_at,
        outcome_observed=trace.outcome_observed,
        outcome_quality=trace.outcome_quality,
        outcome_timestamp=trace.outcome_timestamp,
        outcome_signal=trace.outcome_signal,
    )


@router.post("/context", response_model=ContextResponse)
async def get_context(
    request: ContextRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> ContextResponse:
    """Get full decision context for a user/session.

    Retrieves recent memories and decision traces to provide
    complete context for decision making. Useful for:
    - Debugging decision quality
    - Reviewing what context was available
    - Auditing memory usage

    Authentication:
        - Required in production
        - Optional in development
    """
    _validate_user_access(request.user_id, user)
    db = get_database()
    async with db.session() as session:
        memory_repo = MemoryRepository(session)
        decision_repo = DecisionRepository(session)

        memories = []
        decisions = []

        if request.include_memories:
            # Get recent memories for user
            result = await memory_repo.get_recent(
                user_id=request.user_id,
                limit=request.limit,
            )
            if result.is_ok:
                memories = [
                    {
                        "memory_id": str(m.memory_id),
                        "content": m.content,
                        "temporal_level": m.temporal_level.value,
                        "effective_salience": m.effective_salience,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in result.value
                ]

        if request.include_decisions:
            # Get decision traces
            result = await decision_repo.get_by_user(
                user_id=request.user_id,
                session_id=request.session_id,
                limit=request.limit,
            )
            if result.is_ok:
                decisions = [
                    DecisionTraceResponse(
                        trace_id=t.trace_id,
                        user_id=t.user_id,
                        session_id=t.session_id,
                        memory_ids=t.memory_ids,
                        memory_scores=t.memory_scores,
                        decision_type=t.decision_type,
                        decision_summary=t.decision_summary,
                        confidence=t.confidence,
                        alternatives_count=t.alternatives_count,
                        created_at=t.created_at,
                        outcome_observed=t.outcome_observed,
                        outcome_quality=t.outcome_quality,
                        outcome_timestamp=t.outcome_timestamp,
                        outcome_signal=t.outcome_signal,
                    )
                    for t in result.value
                ]

        return ContextResponse(
            user_id=request.user_id,
            session_id=request.session_id,
            memories=memories,
            decisions=decisions,
            retrieved_at=datetime.now(UTC),
        )
