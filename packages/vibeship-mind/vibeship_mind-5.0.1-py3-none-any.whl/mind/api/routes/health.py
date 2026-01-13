"""Health check endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness check response with all dependencies."""

    ready: bool
    database: str
    nats: str
    falkordb: str
    temporal: str
    qdrant: str | None = None


class DetailedHealthResponse(BaseModel):
    """Detailed health check with all component statuses."""

    status: str
    version: str
    components: dict[str, dict[str, str]]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Basic health check - always returns OK if API is running."""
    return HealthResponse(status="healthy", version="5.0.0")


@router.get("/ready", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    """Readiness check - verifies all dependencies are connected."""
    from sqlalchemy import text

    from mind.infrastructure.falkordb.client import check_falkordb_health
    from mind.infrastructure.nats.client import _nats_client
    from mind.infrastructure.postgres.database import get_database
    from mind.infrastructure.temporal.client import check_temporal_health

    # Check database (required)
    db_status = "disconnected"
    try:
        db = get_database()
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    # Check NATS (optional but important)
    nats_status = "disconnected"
    if _nats_client and _nats_client.is_connected:
        nats_status = "connected"

    # Check FalkorDB (optional - causal features)
    falkordb_healthy, falkordb_status = await check_falkordb_health()

    # Check Temporal (optional - workflows)
    temporal_healthy, temporal_status = await check_temporal_health()

    # Check Qdrant (optional - vector store)
    qdrant_status = None
    try:
        from mind.config import get_settings
        from mind.infrastructure.qdrant.client import get_qdrant_client

        settings = get_settings()
        if settings.qdrant_url:
            client = await get_qdrant_client()
            # Simple health check - list collections
            await client.get_collections()
            qdrant_status = "connected"
    except Exception as e:
        qdrant_status = "not_configured" if qdrant_status is None else f"error: {str(e)}"

    # Ready if database is connected (minimum requirement)
    ready = db_status == "connected"

    return ReadinessResponse(
        ready=ready,
        database=db_status,
        nats=nats_status,
        falkordb=falkordb_status,
        temporal=temporal_status,
        qdrant=qdrant_status,
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health() -> DetailedHealthResponse:
    """Detailed health check with component-level status."""
    from sqlalchemy import text

    from mind.infrastructure.falkordb.client import check_falkordb_health
    from mind.infrastructure.nats.client import _nats_client
    from mind.infrastructure.postgres.database import get_database
    from mind.infrastructure.temporal.client import check_temporal_health

    components = {}

    # Database
    try:
        db = get_database()
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
        components["database"] = {"status": "healthy", "type": "postgresql"}
    except Exception as e:
        components["database"] = {"status": "unhealthy", "error": str(e)}

    # NATS
    if _nats_client and _nats_client.is_connected:
        components["nats"] = {"status": "healthy", "type": "jetstream"}
    else:
        components["nats"] = {"status": "unhealthy", "error": "not connected"}

    # FalkorDB
    falkordb_healthy, falkordb_msg = await check_falkordb_health()
    if falkordb_healthy:
        components["falkordb"] = {"status": "healthy", "type": "graph"}
    else:
        components["falkordb"] = {"status": "unhealthy", "error": falkordb_msg}

    # Temporal
    temporal_healthy, temporal_msg = await check_temporal_health()
    if temporal_healthy:
        components["temporal"] = {"status": "healthy", "type": "workflow"}
    else:
        components["temporal"] = {"status": "unhealthy", "error": temporal_msg}

    # Qdrant (optional)
    try:
        from mind.config import get_settings
        from mind.infrastructure.qdrant.client import get_qdrant_client

        settings = get_settings()
        if settings.qdrant_url:
            client = await get_qdrant_client()
            await client.get_collections()
            components["qdrant"] = {"status": "healthy", "type": "vector"}
        else:
            components["qdrant"] = {"status": "not_configured", "type": "vector"}
    except Exception as e:
        components["qdrant"] = {"status": "unhealthy", "error": str(e)}

    # Overall status
    all_healthy = all(c.get("status") in ("healthy", "not_configured") for c in components.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        version="5.0.0",
        components=components,
    )


class AnomalyReportResponse(BaseModel):
    """Response containing anomaly detection results."""

    anomalies: list[dict]
    checked_at: str
    time_window_hours: int
    user_count_checked: int
    memory_count_checked: int
    summary: dict


@router.get("/anomalies", response_model=AnomalyReportResponse)
async def detect_anomalies(
    time_window_hours: int = Query(default=24, ge=1, le=168),
    user_id: UUID | None = Query(default=None),
) -> AnomalyReportResponse:
    """Run anomaly detection on memory patterns.

    Detects unusual patterns that may indicate:
    - Data quality issues
    - User behavior changes
    - System problems
    - Performance degradation

    Args:
        time_window_hours: Hours to look back (default 24, max 168)
        user_id: Optional user ID to check (None for system-wide)

    Returns:
        Report of detected anomalies with severity levels
    """
    from mind.infrastructure.postgres.database import get_database
    from mind.services.anomaly import get_anomaly_service

    db = get_database()
    async with db.session() as session:
        service = await get_anomaly_service(session)
        result = await service.run_detection(
            time_window_hours=time_window_hours,
            user_id=user_id,
        )

        if not result.is_ok:
            return AnomalyReportResponse(
                anomalies=[],
                checked_at=result.error.message,
                time_window_hours=time_window_hours,
                user_count_checked=0,
                memory_count_checked=0,
                summary={"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            )

        report = result.value
        return AnomalyReportResponse(
            anomalies=[a.to_dict() for a in report.anomalies],
            checked_at=report.checked_at.isoformat(),
            time_window_hours=report.time_window_hours,
            user_count_checked=report.user_count_checked,
            memory_count_checked=report.memory_count_checked,
            summary=report.to_dict()["summary"],
        )
