"""Consumer runner for Mind v5 event consumers.

This module provides the entry point for running event consumers.
Consumers react to domain events and update various projections.

Usage:
    python -m mind.workers.consumers.runner

Or programmatically:
    from mind.workers.consumers.runner import run_consumers
    await run_consumers()
"""

import asyncio
import signal
import sys
from datetime import UTC, datetime

from aiohttp import web
import structlog

from mind.observability.logging import configure_logging
from mind.workers.consumers.causal_updater import create_causal_updater
from mind.workers.consumers.memory_consolidator import create_memory_consolidator
from mind.workers.consumers.memory_extractor import create_memory_extractor
from mind.workers.consumers.pattern_extractor import create_pattern_extractor
from mind.workers.consumers.qdrant_sync import create_qdrant_sync
from mind.workers.consumers.salience_updater import create_salience_updater

logger = structlog.get_logger()


class ConsumerRunner:
    """Runs all event consumers."""

    HEALTH_PORT = 9092

    def __init__(self):
        self._consumers = []
        self._background_tasks = []
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._started_at: datetime | None = None
        self._health_app: web.Application | None = None
        self._health_runner: web.AppRunner | None = None

    async def start(self) -> None:
        """Start all consumers."""
        logger.info("consumer_runner_starting")

        try:
            # Initialize event-driven consumers
            memory_extractor = await create_memory_extractor()
            self._consumers.append(memory_extractor)

            causal_updater = await create_causal_updater()
            self._consumers.append(causal_updater)

            salience_updater = await create_salience_updater()
            self._consumers.append(salience_updater)

            pattern_extractor = await create_pattern_extractor()
            self._consumers.append(pattern_extractor)

            qdrant_sync = await create_qdrant_sync()
            self._consumers.append(qdrant_sync)

            # Start all event-driven consumers
            for consumer in self._consumers:
                await consumer.start()

            # Start scheduled background workers
            memory_consolidator = await create_memory_consolidator()
            consolidator_task = asyncio.create_task(memory_consolidator.start())
            self._background_tasks.append((memory_consolidator, consolidator_task))

            self._running = True
            self._started_at = datetime.now(UTC)

            # Start health check server
            await self._start_health_server()

            logger.info(
                "consumer_runner_started",
                consumer_count=len(self._consumers),
                background_worker_count=len(self._background_tasks),
                health_port=self.HEALTH_PORT,
            )

        except Exception as e:
            logger.error("consumer_runner_start_failed", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop all consumers gracefully."""
        logger.info("consumer_runner_stopping")

        # Stop health server first
        await self._stop_health_server()

        # Stop event-driven consumers
        for consumer in self._consumers:
            try:
                await consumer.stop()
            except Exception as e:
                logger.warning(
                    "consumer_stop_error",
                    consumer=type(consumer).__name__,
                    error=str(e),
                )

        # Stop background workers
        for worker, task in self._background_tasks:
            try:
                await worker.stop()
                task.cancel()
            except Exception as e:
                logger.warning(
                    "background_worker_stop_error",
                    worker=type(worker).__name__,
                    error=str(e),
                )

        self._running = False
        self._shutdown_event.set()
        logger.info("consumer_runner_stopped")

    async def wait_for_shutdown(self) -> None:
        """Wait until shutdown is requested."""
        await self._shutdown_event.wait()

    def request_shutdown(self) -> None:
        """Request graceful shutdown."""
        logger.info("shutdown_requested")
        self._shutdown_event.set()

    async def _start_health_server(self) -> None:
        """Start the HTTP health check server."""
        self._health_app = web.Application()
        self._health_app.router.add_get("/health", self._health_handler)
        self._health_app.router.add_get("/ready", self._ready_handler)

        self._health_runner = web.AppRunner(self._health_app)
        await self._health_runner.setup()
        site = web.TCPSite(self._health_runner, "0.0.0.0", self.HEALTH_PORT)
        await site.start()
        logger.info("health_server_started", port=self.HEALTH_PORT)

    async def _stop_health_server(self) -> None:
        """Stop the HTTP health check server."""
        if self._health_runner:
            await self._health_runner.cleanup()
            logger.info("health_server_stopped")

    async def _health_handler(self, request: web.Request) -> web.Response:
        """Handle /health endpoint."""
        uptime_seconds = 0.0
        if self._started_at:
            uptime_seconds = (datetime.now(UTC) - self._started_at).total_seconds()

        return web.json_response({
            "status": "healthy" if self._running else "unhealthy",
            "version": "5.0.0",
            "uptime_seconds": uptime_seconds,
            "consumer_count": len(self._consumers),
            "background_worker_count": len(self._background_tasks),
        })

    async def _ready_handler(self, request: web.Request) -> web.Response:
        """Handle /ready endpoint."""
        consumer_names = [type(c).__name__ for c in self._consumers]
        worker_names = [type(w).__name__ for w, _ in self._background_tasks]

        return web.json_response({
            "ready": self._running,
            "consumers": consumer_names,
            "background_workers": worker_names,
        })


async def run_consumers() -> None:
    """Main entry point for running consumers."""
    configure_logging()
    logger.info("mind_consumers_initializing")

    runner = ConsumerRunner()

    # Set up signal handlers
    loop = asyncio.get_event_loop()

    def handle_signal(sig):
        logger.info("signal_received", signal=sig.name)
        runner.request_shutdown()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    try:
        await runner.start()
        await runner.wait_for_shutdown()
    finally:
        await runner.stop()


def main() -> None:
    """CLI entry point."""
    try:
        asyncio.run(run_consumers())
    except KeyboardInterrupt:
        logger.info("interrupted")
        sys.exit(0)


if __name__ == "__main__":
    main()
