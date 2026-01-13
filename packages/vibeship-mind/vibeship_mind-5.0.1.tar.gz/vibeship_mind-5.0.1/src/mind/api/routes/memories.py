"""Memory-related API endpoints."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException

from mind.api.deps import get_memory_storage, is_container_ready
from mind.api.schemas.memory import (
    MemoryCreate,
    MemoryResponse,
    RetrieveRequest,
    RetrieveResponse,
)
from mind.config import get_settings
from mind.core.memory.models import Memory
from mind.core.memory.retrieval import RetrievalRequest
from mind.infrastructure.embeddings.openai import get_embedder
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import MemoryRepository
from mind.observability.metrics import metrics
from mind.ports.storage import IMemoryStorage
from mind.security.auth import AuthenticatedUser, get_auth_dependency
from mind.security.pii import get_pii_detector
from mind.services.embedding import get_embedding_service
from mind.services.events import get_event_service
from mind.services.retrieval import RetrievalService

logger = structlog.get_logger()
router = APIRouter()


def _validate_user_access(
    request_user_id: UUID,
    authenticated_user: AuthenticatedUser | None,
) -> None:
    """Validate that authenticated user can access the requested user's data.

    In production, users can only access their own data.
    In development without auth, allow any access.
    """
    settings = get_settings()

    # Skip validation in development without auth
    if settings.environment != "production" and not settings.require_auth:
        return

    if authenticated_user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    if authenticated_user.user_id != request_user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access another user's data",
        )


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(
    request: MemoryCreate,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> MemoryResponse:
    """Create a new memory with embedding for semantic search.

    Memories are the core unit of context storage in Mind.
    They are stored in a hierarchical temporal structure.
    Embeddings are generated for semantic retrieval.

    Authentication:
        - Required in production (user can only create memories for themselves)
        - Optional in development
    """
    _validate_user_access(request.user_id, user)

    # Check for PII and optionally scrub
    content = request.content
    pii_detector = get_pii_detector()
    pii_result = pii_detector.detect(content)

    if pii_result.pii_found:
        pii_types = [t.value for t in pii_result.pii_types_found]
        logger.warning(
            "pii_detected_in_memory",
            user_id=str(request.user_id),
            pii_types=pii_types,
            match_count=len(pii_result.matches),
        )
        # Automatically scrub PII for safety
        content = pii_result.scrubbed_text

    memory = Memory(
        memory_id=uuid4(),
        user_id=request.user_id,
        content=content,
        content_type=request.content_type,
        temporal_level=request.temporal_level,
        valid_from=request.valid_from or datetime.now(UTC),
        valid_until=request.valid_until,
        base_salience=request.salience,
    )

    # Generate embedding for semantic search (optional, may fail if no API key)
    embedding = None
    try:
        embedding_service = get_embedding_service()
        embed_result = await embedding_service.embed(content)
        if embed_result.is_ok:
            embedding = embed_result.value
            logger.debug(
                "embedding_generated",
                memory_id=str(memory.memory_id),
                embedding_dim=len(embedding),
            )
        else:
            logger.debug(
                "embedding_generation_skipped",
                memory_id=str(memory.memory_id),
                reason=str(embed_result.error),
            )
    except Exception as e:
        logger.debug(
            "embedding_generation_unavailable",
            memory_id=str(memory.memory_id),
            reason=str(e),
        )

    # Use container adapter if available, otherwise fall back to legacy
    if is_container_ready():
        try:
            storage = get_memory_storage()
            created_memory = await storage.store(memory)
            logger.debug("memory_stored_via_container", memory_id=str(created_memory.memory_id))
        except Exception as e:
            logger.error("container_storage_failed", error=str(e))
            raise HTTPException(status_code=500, detail={"message": f"Storage error: {e}"})
    else:
        # Legacy path for backward compatibility
        db = get_database()
        async with db.session() as session:
            repo = MemoryRepository(session)
            result = await repo.create(memory, embedding=embedding)

            if not result.is_ok:
                raise HTTPException(status_code=400, detail=result.error.to_dict())

            created_memory = result.value

    # Publish event (fire-and-forget, don't block on failure)
    try:
        event_service = get_event_service()
        await event_service.publish_memory_created(created_memory)
    except Exception as e:
        logger.debug(
            "event_publish_skipped", error=str(e), memory_id=str(created_memory.memory_id)
        )

    return MemoryResponse.from_domain(created_memory)


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: UUID,
    user_id: UUID,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> None:
    """Delete a memory by ID.

    Requires user_id query param to ensure user can only delete their own memories.
    """
    _validate_user_access(user_id, user)

    # Use container adapter if available, otherwise fall back to legacy
    if is_container_ready():
        try:
            storage = get_memory_storage()
            await storage.expire(memory_id)  # Soft delete via expiration
            logger.info("memory_expired_via_container", memory_id=str(memory_id))
        except Exception as e:
            logger.error("container_delete_failed", error=str(e))
            raise HTTPException(status_code=404, detail={"message": f"Memory not found: {e}"})
    else:
        db = get_database()
        async with db.session() as session:
            repo = MemoryRepository(session)
            result = await repo.delete(memory_id, user_id)

            if not result.is_ok:
                raise HTTPException(status_code=404, detail=result.error.to_dict())

    logger.info("memory_deleted", memory_id=str(memory_id), user_id=str(user_id))


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: UUID) -> MemoryResponse:
    """Get a memory by ID."""
    # Use container adapter if available, otherwise fall back to legacy
    if is_container_ready():
        try:
            storage = get_memory_storage()
            memory = await storage.get(memory_id)
            if memory is None:
                raise HTTPException(status_code=404, detail={"message": "Memory not found"})
            return MemoryResponse.from_domain(memory)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("container_get_failed", error=str(e))
            raise HTTPException(status_code=500, detail={"message": f"Storage error: {e}"})
    else:
        db = get_database()
        async with db.session() as session:
            repo = MemoryRepository(session)
            result = await repo.get(memory_id)

            if not result.is_ok:
                raise HTTPException(status_code=404, detail=result.error.to_dict())

            return MemoryResponse.from_domain(result.value)


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_memories(
    request: RetrieveRequest,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> RetrieveResponse:
    """Retrieve relevant memories for a query.

    This is the main retrieval endpoint. It uses multi-source
    fusion (vector, keyword, salience, recency) with RRF to find
    the most relevant memories for the given query.

    Sources combined:
    - Vector similarity (semantic search via embeddings)
    - Keyword/BM25 (full-text search)
    - Salience ranking (outcome-weighted importance)
    - Recency decay (time-based freshness)

    Returns a trace_id that can be used to track the decision
    made with this context and observe outcomes.

    Authentication:
        - Required in production (user can only retrieve their memories)
        - Optional in development
    """
    _validate_user_access(request.user_id, user)
    retrieval_request = RetrievalRequest(
        user_id=request.user_id,
        query=request.query,
        limit=request.limit,
        temporal_levels=request.temporal_levels,
        min_salience=request.min_salience,
    )

    db = get_database()
    async with db.session() as session:
        # Use retrieval service with RRF fusion
        embedder = get_embedder()

        # Use Qdrant if configured as the vector backend
        qdrant_repo = None
        settings = get_settings()
        if settings.vector_backend == "qdrant" and settings.qdrant_url:
            try:
                from mind.infrastructure.qdrant.client import get_qdrant_client
                from mind.infrastructure.qdrant.repository import QdrantVectorRepository

                qdrant_client = await get_qdrant_client()
                qdrant_repo = QdrantVectorRepository(qdrant_client)
                logger.debug("using_qdrant_for_retrieval")
            except Exception as e:
                logger.warning("qdrant_init_failed", error=str(e))

        service = RetrievalService(
            session=session,
            embedder=embedder,
            qdrant_repo=qdrant_repo,
        )
        result = await service.retrieve(retrieval_request)

        if not result.is_ok:
            raise HTTPException(status_code=500, detail=result.error.to_dict())

        retrieval = result.value

        # Record metrics
        sources_used = set()
        for sm in retrieval.memories:
            if sm.vector_score:
                sources_used.add("vector")
            if sm.keyword_score:
                sources_used.add("keyword")
            if sm.salience_score:
                sources_used.add("salience")
            if sm.recency_score:
                sources_used.add("recency")

        metrics.observe_retrieval(
            latency_seconds=retrieval.latency_ms / 1000,
            sources_used=list(sources_used),
            result_count=len(retrieval.memories),
        )

        # Build response and event data while session is still active
        response = RetrieveResponse(
            retrieval_id=retrieval.retrieval_id,
            memories=[MemoryResponse.from_domain(sm.memory) for sm in retrieval.memories],
            scores={str(sm.memory.memory_id): sm.final_score for sm in retrieval.memories},
            latency_ms=retrieval.latency_ms,
        )

        # Capture event data for publishing after session closes
        event_data = {
            "retrieval_id": retrieval.retrieval_id,
            "query": request.query,
            "latency_ms": retrieval.latency_ms,
            "memories": [
                (sm.memory.memory_id, sm.rank, sm.final_score, "fusion")
                for sm in retrieval.memories
            ],
        }

    # Publish retrieval event (fire-and-forget, outside session)
    try:
        event_service = get_event_service()
        await event_service.publish_memory_retrieval(
            user_id=request.user_id,
            retrieval_id=event_data["retrieval_id"],
            query=event_data["query"],
            memories=event_data["memories"],
            latency_ms=event_data["latency_ms"],
        )
    except Exception as e:
        logger.warning("event_publish_failed", error=str(e), event_type="memory.retrieval")

    return response


@router.get("/", response_model=list[MemoryResponse])
async def list_memories(
    user_id: UUID,
    limit: int = 100,
    offset: int = 0,
    temporal_level: int | None = None,
    min_salience: float = 0.0,
    user: AuthenticatedUser | None = Depends(get_auth_dependency()),
) -> list[MemoryResponse]:
    """List memories for a user.

    This is a simpler alternative to /retrieve that doesn't require
    semantic search. It returns memories ordered by creation time.

    Args:
        user_id: The user's UUID
        limit: Maximum memories to return (default 100)
        offset: Skip this many memories (for pagination)
        temporal_level: Filter by level (1=immediate, 2=situational, 3=seasonal, 4=identity)
        min_salience: Minimum salience threshold (0.0-1.0)

    Returns:
        List of memories matching the criteria
    """
    _validate_user_access(user_id, user)

    # Use container adapter if available
    if is_container_ready():
        try:
            from mind.core.memory.models import TemporalLevel as TL

            storage = get_memory_storage()
            level = TL(temporal_level) if temporal_level else None
            memories = await storage.get_by_user(
                user_id=user_id,
                limit=limit,
                offset=offset,
                temporal_level=level,
                min_salience=min_salience,
                valid_only=True,
            )
            return [MemoryResponse.from_domain(m) for m in memories]
        except Exception as e:
            logger.error("container_list_failed", error=str(e))
            raise HTTPException(status_code=500, detail={"message": f"Storage error: {e}"})

    # Fall back to legacy repository - return empty list on error
    try:
        db = get_database()
        async with db.session() as session:
            repo = MemoryRepository(session)
            result = await repo.get_recent(
                user_id=user_id,
                limit=limit + offset,  # Over-fetch to support offset
            )

            if not result.is_ok:
                logger.warning("legacy_list_failed", error=str(result.error))
                return []

            # Apply offset manually (get_recent doesn't support offset)
            memories = result.value[offset:offset + limit] if offset > 0 else result.value[:limit]
            return [MemoryResponse.from_domain(m) for m in memories]
    except Exception as e:
        logger.warning("legacy_database_unavailable", error=str(e))
        return []  # Return empty list when database is unavailable
