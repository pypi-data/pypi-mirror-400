"""Temporal worker for the Gardener service.

The Gardener is responsible for memory lifecycle management:
- Promotion: Moving memories to higher temporal levels
- Expiration: Marking memories as no longer valid
- Decay: Gradually reducing salience of unused memories
- Consolidation: Merging similar memories

Run this worker with:
    python -m mind.workers.gardener.worker

Or use the CLI:
    mind worker gardener

Health endpoint available at http://localhost:9091/health when running.
Metrics available at http://localhost:9091/metrics when running.
"""

import asyncio
import signal
from typing import Any

import structlog
from aiohttp import web
from temporalio.worker import Worker

from mind.infrastructure.temporal.client import get_temporal_client
from mind.observability.metrics import metrics
from mind.workers.gardener.activities import (
    # Calibration activities
    analyze_confidence_calibration,
    # Outcome analysis activities
    analyze_user_outcomes,
    apply_salience_adjustments,
    archive_memory,
    consolidate_memories,
    # Reindex activities
    count_memories_for_reindex,
    extract_patterns_from_decisions,
    # Consolidation activities
    find_consolidation_candidates,
    # Expiration activities
    find_expired_memories,
    find_memories_for_reindex,
    # Promotion activities
    find_promotion_candidates,
    # Pattern extraction activities
    find_successful_decisions,
    generate_embeddings_for_batch,
    # User discovery activity
    get_active_user_ids,
    notify_consolidation,
    notify_expiration,
    notify_promotion,
    promote_memory,
    sanitize_patterns,
    store_federated_patterns,
    update_calibration_settings,
    update_memory_embeddings,
)
from mind.workers.gardener.workflows import (
    AnalyzeOutcomesWorkflow,
    CalibrateConfidenceWorkflow,
    ExtractPatternsWorkflow,
    MemoryConsolidationWorkflow,
    MemoryExpirationWorkflow,
    MemoryPromotionWorkflow,
    ReindexEmbeddingsWorkflow,
    ScheduledGardenerWorkflow,
)

logger = structlog.get_logger()

TASK_QUEUE = "gardener"
HEALTH_PORT = 9091


async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint for the worker."""
    return web.json_response(
        {
            "status": "healthy",
            "worker_type": "gardener",
            "task_queue": TASK_QUEUE,
        }
    )


async def metrics_handler(request: web.Request) -> web.Response:
    """Prometheus metrics endpoint for the worker."""
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return web.Response(
        body=generate_latest(),
        content_type=CONTENT_TYPE_LATEST,
    )


async def start_health_server() -> web.AppRunner:
    """Start the health check HTTP server."""
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/metrics", metrics_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HEALTH_PORT)
    await site.start()

    logger.info("health_server_started", port=HEALTH_PORT)
    return runner


async def run_worker() -> None:
    """Run the Gardener worker.

    This starts a Temporal worker that processes gardening tasks.
    The worker runs until interrupted (SIGINT/SIGTERM).

    Also starts:
    - Health check endpoint at http://localhost:9091/health
    - Prometheus metrics endpoint at http://localhost:9091/metrics
    """
    logger.info("gardener_starting", task_queue=TASK_QUEUE)

    # Start health server
    health_runner = await start_health_server()

    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[
            # Memory lifecycle
            MemoryPromotionWorkflow,
            MemoryExpirationWorkflow,
            MemoryConsolidationWorkflow,
            ScheduledGardenerWorkflow,
            # Decision analysis
            AnalyzeOutcomesWorkflow,
            CalibrateConfidenceWorkflow,
            ExtractPatternsWorkflow,
            # Maintenance
            ReindexEmbeddingsWorkflow,
        ],
        activities=[
            # Promotion
            find_promotion_candidates,
            promote_memory,
            notify_promotion,
            # Expiration
            find_expired_memories,
            archive_memory,
            notify_expiration,
            # Consolidation
            find_consolidation_candidates,
            consolidate_memories,
            notify_consolidation,
            # Outcome analysis
            analyze_user_outcomes,
            apply_salience_adjustments,
            # Calibration
            analyze_confidence_calibration,
            update_calibration_settings,
            # Pattern extraction
            find_successful_decisions,
            extract_patterns_from_decisions,
            sanitize_patterns,
            store_federated_patterns,
            # Reindex
            count_memories_for_reindex,
            find_memories_for_reindex,
            generate_embeddings_for_batch,
            update_memory_embeddings,
            # User discovery
            get_active_user_ids,
        ],
    )

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def handle_shutdown(sig: Any) -> None:
        logger.info("gardener_shutdown_requested", signal=sig)
        shutdown_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_shutdown, sig)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    # Record worker as active
    metrics.set_worker_active("gardener", TASK_QUEUE, active=True)

    logger.info("gardener_running", task_queue=TASK_QUEUE)

    # Run worker until shutdown
    async with worker:
        await shutdown_event.wait()

    # Record worker as inactive
    metrics.set_worker_active("gardener", TASK_QUEUE, active=False)

    # Cleanup health server
    await health_runner.cleanup()

    logger.info("gardener_stopped")


def main() -> None:
    """Entry point for running the worker."""
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
