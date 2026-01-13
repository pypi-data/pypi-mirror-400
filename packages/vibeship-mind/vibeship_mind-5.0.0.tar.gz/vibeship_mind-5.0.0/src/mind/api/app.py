"""FastAPI application factory.

Supports two deployment tiers:
- Standard: PostgreSQL + APScheduler (zero-config, embedded PG)
- Enterprise: Full Docker stack (NATS, Qdrant, FalkorDB, Temporal)

Tier is auto-detected from environment:
- MIND_TIER=standard or MIND_TIER=enterprise
- If not set, defaults to Standard
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mind.api.routes import admin, causal, consent, decisions, health, interactions, memories, preferences
from mind.config import get_settings
from mind.container import MindContainer, Tier, set_container
from mind.observability.logging import configure_logging
from mind.observability.metrics import MetricsMiddleware, metrics_endpoint
from mind.observability.tracing import (
    configure_tracing,
    instrument_fastapi,
    shutdown_tracing,
    uninstrument_fastapi,
)
from mind.security.middleware import (
    RateLimitConfig,
    RateLimitMiddleware,
    RequestSanitizationMiddleware,
    SecurityHeadersMiddleware,
)

logger = structlog.get_logger()

# Global container reference for cleanup
_container: Optional[MindContainer] = None


def _detect_tier() -> Tier:
    """Detect the deployment tier from configuration.

    Uses the centralized tier detection from Settings which considers:
    1. MIND_TIER environment variable (standard/enterprise/auto)
    2. Auto-detection based on configured services
    3. Default to Standard

    Returns:
        The detected Tier (STANDARD or ENTERPRISE)
    """
    settings = get_settings()
    effective_tier = settings.get_effective_tier()
    return Tier.STANDARD if effective_tier == "standard" else Tier.ENTERPRISE


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with tier support."""
    global _container

    settings = get_settings()

    # Configure logging first
    configure_logging()

    # Configure tracing
    configure_tracing(
        service_name="mind-v5",
        service_version="5.0.0",
        environment=settings.environment,
    )

    # Instrument FastAPI for automatic request tracing
    instrument_fastapi(app)

    # Detect tier
    tier = _detect_tier()
    logger.info("app_starting", tier=tier.value)

    # Initialize container based on tier
    try:
        if tier == Tier.STANDARD:
            # Standard tier: PostgreSQL + APScheduler
            # Priority: MIND_DATABASE_URL env var > settings.database_url > embedded PG
            database_url = os.environ.get("MIND_DATABASE_URL") or settings.get_database_url()
            _container = await MindContainer.create_standard(
                database_url=database_url,
            )
            logger.info(
                "standard_tier_initialized",
                embedded_pg=_container._embedded_pg is not None,
            )
        else:
            # Enterprise tier: Full Docker stack
            _container = await MindContainer.create_enterprise()
            logger.info("enterprise_tier_initialized")

        # Set global container for service access
        set_container(_container)

        # Start background services
        await _container.start()

    except Exception as e:
        logger.error("container_initialization_failed", error=str(e), tier=tier.value)
        # Try fallback to legacy initialization for backwards compatibility
        await _legacy_startup()

    yield

    # Cleanup
    logger.info("app_stopping")
    uninstrument_fastapi(app)
    shutdown_tracing()

    if _container is not None:
        await _container.shutdown()
        _container = None
    else:
        await _legacy_shutdown()

    logger.info("app_stopped")


async def _legacy_startup() -> None:
    """Legacy startup for backwards compatibility."""
    from mind.infrastructure.embeddings.openai import close_embedder
    from mind.infrastructure.postgres.database import init_database
    from mind.infrastructure.nats.client import get_nats_client
    from mind.infrastructure.falkordb.client import (
        get_falkordb_client,
        ensure_schema,
    )
    from mind.infrastructure.temporal.client import get_temporal_client

    settings = get_settings()

    try:
        await init_database()
        logger.info("database_connected")
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))

    try:
        await get_nats_client()
        logger.info("nats_connected")
    except Exception as e:
        logger.warning("nats_connection_failed", error=str(e))

    try:
        if settings.falkordb_host:
            client = await get_falkordb_client()
            await ensure_schema(client)
            logger.info("falkordb_connected")
    except Exception as e:
        logger.warning("falkordb_connection_failed", error=str(e))

    try:
        if settings.temporal_host:
            await get_temporal_client()
            logger.info("temporal_connected")
    except Exception as e:
        logger.warning("temporal_connection_failed", error=str(e))


async def _legacy_shutdown() -> None:
    """Legacy shutdown for backwards compatibility."""
    from mind.infrastructure.embeddings.openai import close_embedder
    from mind.infrastructure.postgres.database import close_database
    from mind.infrastructure.nats.client import close_nats_client
    from mind.infrastructure.falkordb.client import close_falkordb_client
    from mind.infrastructure.temporal.client import close_temporal_client

    await close_embedder()
    await close_database()
    await close_nats_client()
    await close_falkordb_client()
    await close_temporal_client()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Mind v5 API",
        description="Decision intelligence system for AI agents",
        version="5.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Middleware (order matters - first added = last executed)
    # Execution order: CORS -> Sanitization -> RateLimit -> Security -> Metrics -> Route

    # 1. Metrics - outermost, wraps everything
    app.add_middleware(MetricsMiddleware)

    # 2. Security headers - adds OWASP headers to all responses
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. Rate limiting - blocks excessive requests
    rate_limit_config = RateLimitConfig(
        requests_per_minute=120 if settings.environment == "development" else 60,
        requests_per_hour=2000 if settings.environment == "development" else 1000,
        burst_size=20 if settings.environment == "development" else 10,
    )
    app.add_middleware(RateLimitMiddleware, config=rate_limit_config)

    # 4. Request sanitization - validates content type and size
    app.add_middleware(RequestSanitizationMiddleware)

    # 5. CORS - innermost, handles preflight
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.environment == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(health.router, tags=["health"])
    app.include_router(memories.router, prefix="/v1/memories", tags=["memories"])
    app.include_router(decisions.router, prefix="/v1/decisions", tags=["decisions"])
    app.include_router(interactions.router, prefix="/v1/interactions", tags=["interactions"])
    app.include_router(causal.router, prefix="/v1/causal", tags=["causal"])
    app.include_router(admin.router, prefix="/v1", tags=["admin"])
    app.include_router(consent.router, prefix="/v1/consent", tags=["consent"])
    app.include_router(preferences.router, prefix="/v1/users/preferences", tags=["preferences"])

    # Metrics endpoint
    app.add_api_route("/metrics", metrics_endpoint, include_in_schema=False)

    return app


# Application instance for uvicorn
app = create_app()
