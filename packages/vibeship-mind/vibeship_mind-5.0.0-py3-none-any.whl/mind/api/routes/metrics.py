"""Prometheus metrics endpoint.

Exposes metrics in Prometheus format for monitoring:
- API request counts and latencies
- Memory and decision metrics
- Embedding service metrics
- Federation pattern metrics
"""

from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Response

logger = structlog.get_logger()
router = APIRouter()


class MetricsCollector:
    """Collects and formats metrics for Prometheus.

    Tracks:
    - Request counts by endpoint and status
    - Request latencies
    - Memory operations
    - Decision tracking
    - Embedding usage
    """

    def __init__(self):
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._start_time = datetime.now(UTC)

    def inc_counter(self, name: str, labels: dict[str, str] = None, value: int = 1) -> None:
        """Increment a counter metric."""
        key = self._metric_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value

    def set_gauge(self, name: str, value: float, labels: dict[str, str] = None) -> None:
        """Set a gauge metric."""
        key = self._metric_key(name, labels)
        self._gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: dict[str, str] = None) -> None:
        """Record a histogram observation."""
        key = self._metric_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)

    def format_prometheus(self) -> str:
        """Format all metrics in Prometheus text format."""
        lines = []

        # Add uptime
        uptime = (datetime.now(UTC) - self._start_time).total_seconds()
        lines.append("# HELP mind_uptime_seconds Time since service start")
        lines.append("# TYPE mind_uptime_seconds gauge")
        lines.append(f"mind_uptime_seconds {uptime:.2f}")
        lines.append("")

        # Format counters
        for key, value in self._counters.items():
            name, labels = self._parse_key(key)
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{key} {value}")

        # Format gauges
        for key, value in self._gauges.items():
            name, labels = self._parse_key(key)
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{key} {value:.4f}")

        # Format histograms (simplified - just sum and count)
        for key, values in self._histograms.items():
            name, labels = self._parse_key(key)
            count = len(values)
            total = sum(values)
            avg = total / count if count > 0 else 0

            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{key}_count {count}")
            lines.append(f"{key}_sum {total:.4f}")
            lines.append(f"{key}_avg {avg:.4f}")

        return "\n".join(lines)

    def _metric_key(self, name: str, labels: dict[str, str] | None = None) -> str:
        """Build metric key with labels."""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _parse_key(self, key: str) -> tuple[str, dict]:
        """Parse metric key to name and labels."""
        if "{" not in key:
            return key, {}
        name = key.split("{")[0]
        return name, {}


# Global collector
_collector: MetricsCollector | None = None


def get_collector() -> MetricsCollector:
    """Get or create metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    collector = get_collector()

    # Collect current metrics from services
    await _collect_service_metrics(collector)

    content = collector.format_prometheus()

    return Response(
        content=content,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


async def _collect_service_metrics(collector: MetricsCollector) -> None:
    """Collect metrics from various services."""

    # Embedding service metrics
    try:
        from mind.services.embedding import get_embedding_service

        service = get_embedding_service()
        metrics = service.get_metrics()

        collector.set_gauge("mind_embedding_cache_size", metrics["cache_size"])
        collector.set_gauge("mind_embedding_cache_hit_rate", metrics["cache_hit_rate"])
        collector.set_gauge("mind_embedding_requests_total", metrics["total_requests"])
        collector.set_gauge("mind_embedding_tokens_total", metrics["estimated_tokens"])
    except Exception as e:
        logger.debug("embedding_metrics_failed", error=str(e))

    # Database pool metrics
    try:
        from mind.infrastructure.postgres.database import get_database

        db = get_database()
        pool = db.engine.pool

        collector.set_gauge("mind_db_pool_size", pool.size())
        collector.set_gauge("mind_db_pool_checkedout", pool.checkedout())
        collector.set_gauge("mind_db_pool_overflow", pool.overflow())
    except Exception as e:
        logger.debug("db_metrics_failed", error=str(e))


# Middleware for request metrics
class MetricsMiddleware:
    """Middleware to track request metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = datetime.now(UTC)
        collector = get_collector()

        # Track request
        path = scope.get("path", "/")
        method = scope.get("method", "GET")

        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = (datetime.now(UTC) - start).total_seconds()

            collector.inc_counter(
                "mind_http_requests_total",
                {"method": method, "path": path, "status": str(status_code)},
            )
            collector.observe_histogram(
                "mind_http_request_duration_seconds",
                duration,
                {"method": method, "path": path},
            )
