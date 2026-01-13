"""Prometheus metrics for Mind v5."""

import time
from collections.abc import Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


class MindMetrics:
    """Prometheus metrics for Mind v5."""

    def __init__(self):
        # HTTP metrics
        self.http_requests_total = Counter(
            "mind_http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
        )

        self.http_request_duration_seconds = Histogram(
            "mind_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
        )

        # Memory retrieval metrics
        self.retrieval_latency_seconds = Histogram(
            "mind_retrieval_latency_seconds",
            "Memory retrieval latency in seconds",
            ["source"],  # vector, keyword, salience, recency, fusion
            buckets=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
        )

        self.retrieval_results_total = Counter(
            "mind_retrieval_results_total",
            "Total memories retrieved",
            ["temporal_level"],
        )

        self.retrieval_sources_used = Counter(
            "mind_retrieval_sources_used_total",
            "Retrieval sources used",
            ["source"],
        )

        # Decision tracking metrics
        self.decisions_tracked_total = Counter(
            "mind_decisions_tracked_total",
            "Total decisions tracked",
            ["decision_type"],
        )

        self.outcomes_observed_total = Counter(
            "mind_outcomes_observed_total",
            "Total outcomes observed",
            ["quality"],  # positive, negative, neutral
        )

        self.salience_adjustments_total = Counter(
            "mind_salience_adjustments_total",
            "Total salience adjustments",
            ["direction"],  # increase, decrease
        )

        # Memory metrics
        self.memories_created_total = Counter(
            "mind_memories_created_total",
            "Total memories created",
            ["temporal_level", "content_type"],
        )

        self.memories_promoted_total = Counter(
            "mind_memories_promoted_total",
            "Total memories promoted",
            ["from_level", "to_level"],
        )

        # Event metrics
        self.events_published_total = Counter(
            "mind_events_published_total",
            "Total events published",
            ["event_type"],
        )

        self.events_consumed_total = Counter(
            "mind_events_consumed_total",
            "Total events consumed",
            ["event_type", "consumer"],
        )

        # Event consumer processing metrics
        self.events_processed_total = Counter(
            "mind_events_processed_total",
            "Total events processed by consumers",
            ["consumer", "event_type", "status"],  # status: success, failure
        )

        # Dead letter queue metrics
        self.dlq_messages_total = Counter(
            "mind_dlq_messages_total",
            "Total messages sent to dead letter queue",
            ["consumer", "event_type"],
        )

        self.dlq_depth = Gauge(
            "mind_dlq_depth",
            "Current depth of dead letter queue",
            ["stream"],
        )

        self.dlq_oldest_message_age_seconds = Gauge(
            "mind_dlq_oldest_message_age_seconds",
            "Age of oldest message in DLQ in seconds",
            ["stream"],
        )

        # Embedding metrics
        self.embeddings_generated_total = Counter(
            "mind_embeddings_generated_total",
            "Total embeddings generated",
        )

        self.embedding_latency_seconds = Histogram(
            "mind_embedding_latency_seconds",
            "Embedding generation latency",
            buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0],
        )

        # Connection pool metrics
        self.db_pool_size = Gauge(
            "mind_db_pool_size",
            "Database connection pool size",
        )

        self.db_pool_checked_out = Gauge(
            "mind_db_pool_checked_out",
            "Database connections currently checked out",
        )

        # Federation metrics
        self.patterns_extracted_total = Counter(
            "mind_patterns_extracted_total",
            "Total patterns extracted from outcomes",
        )

        self.patterns_sanitized_total = Counter(
            "mind_patterns_sanitized_total",
            "Total patterns sanitized for federation",
        )

        self.patterns_applied_total = Counter(
            "mind_patterns_applied_total",
            "Total federated patterns applied to decisions",
        )

        self.privacy_budget_spent = Gauge(
            "mind_privacy_budget_spent",
            "Cumulative epsilon spent on differential privacy",
        )

        # Causal inference metrics
        self.causal_edges_created_total = Counter(
            "mind_causal_edges_created_total",
            "Total causal edges created",
            ["edge_type"],  # influenced, led_to
        )

        self.causal_attributions_computed_total = Counter(
            "mind_causal_attributions_computed_total",
            "Total causal attributions computed",
        )

        self.counterfactual_queries_total = Counter(
            "mind_counterfactual_queries_total",
            "Total counterfactual queries executed",
        )

        # =============================================================================
        # Decision Quality Metrics (SLO-critical)
        # =============================================================================

        # Rolling success rate by user cohort
        self.decision_success_rate = Gauge(
            "mind_decision_success_rate",
            "Rolling decision success rate (0-1)",
            ["user_cohort", "decision_type"],
        )

        # Memory retrieval relevance distribution
        self.memory_retrieval_relevance = Histogram(
            "mind_memory_retrieval_relevance",
            "Relevance score of retrieved memories",
            ["temporal_level", "source"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )

        # Causal prediction accuracy
        self.causal_prediction_accuracy = Gauge(
            "mind_causal_prediction_accuracy",
            "Accuracy of causal outcome predictions (0-1)",
            ["prediction_type"],  # outcome, attribution, counterfactual
        )

        # Embedding quality metrics
        self.embedding_cache_hits_total = Counter(
            "mind_embedding_cache_hits_total",
            "Total embedding cache hits",
        )

        self.embedding_cache_misses_total = Counter(
            "mind_embedding_cache_misses_total",
            "Total embedding cache misses",
        )

        # Decision context quality
        self.context_completeness = Histogram(
            "mind_context_completeness",
            "Completeness of context provided for decisions (0-1)",
            ["decision_type"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )

        # Calibration metrics
        self.confidence_calibration_error = Gauge(
            "mind_confidence_calibration_error",
            "Expected Calibration Error for confidence predictions",
            ["user_cohort"],
        )

        # Pattern effectiveness
        self.pattern_effectiveness = Gauge(
            "mind_pattern_effectiveness",
            "Effectiveness of applied patterns (outcome improvement)",
            ["pattern_type"],
        )

        # Pattern success/failure tracking
        self.pattern_success_total = Counter(
            "mind_pattern_success_total",
            "Total pattern applications that improved outcomes",
            ["pattern_id"],
        )

        self.pattern_failure_total = Counter(
            "mind_pattern_failure_total",
            "Total pattern applications that did not improve outcomes",
            ["pattern_id"],
        )

        self.pattern_success_rate = Gauge(
            "mind_pattern_success_rate",
            "Success rate for a specific pattern",
            ["pattern_id"],
        )

        # =============================================================================
        # Temporal Workflow Metrics
        # =============================================================================

        # Workflow execution counts
        self.workflow_executions_total = Counter(
            "mind_workflow_executions_total",
            "Total workflow executions",
            ["workflow_type", "status"],  # status: started, completed, failed
        )

        # Workflow execution duration
        self.workflow_duration_seconds = Histogram(
            "mind_workflow_duration_seconds",
            "Workflow execution duration in seconds",
            ["workflow_type"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0],
        )

        # Activity execution counts
        self.activity_executions_total = Counter(
            "mind_activity_executions_total",
            "Total activity executions",
            ["activity_type", "status"],  # status: started, completed, failed
        )

        # Activity execution duration
        self.activity_duration_seconds = Histogram(
            "mind_activity_duration_seconds",
            "Activity execution duration in seconds",
            ["activity_type"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
        )

        # Workflow processing metrics
        self.workflow_users_processed = Counter(
            "mind_workflow_users_processed_total",
            "Total users processed by workflows",
            ["workflow_type"],
        )

        self.workflow_items_processed = Counter(
            "mind_workflow_items_processed_total",
            "Total items processed by workflows",
            ["workflow_type", "item_type"],  # item_type: memory, decision, pattern
        )

        # Schedule metrics
        self.schedule_runs_total = Counter(
            "mind_schedule_runs_total",
            "Total scheduled workflow runs",
            ["schedule_id"],
        )

        self.schedule_last_run_timestamp = Gauge(
            "mind_schedule_last_run_timestamp",
            "Timestamp of last scheduled run",
            ["schedule_id"],
        )

        # Worker health
        self.worker_active = Gauge(
            "mind_worker_active",
            "Whether worker is active (1) or inactive (0)",
            ["worker_type", "task_queue"],
        )

        self.worker_tasks_polled = Counter(
            "mind_worker_tasks_polled_total",
            "Total tasks polled by worker",
            ["worker_type", "task_queue"],
        )

        # Gardener-specific metrics
        self.gardener_promotions_succeeded = Counter(
            "mind_gardener_promotions_succeeded_total",
            "Total successful memory promotions",
        )

        self.gardener_expirations_succeeded = Counter(
            "mind_gardener_expirations_succeeded_total",
            "Total successful memory expirations",
        )

        self.gardener_consolidations_succeeded = Counter(
            "mind_gardener_consolidations_succeeded_total",
            "Total successful memory consolidations",
        )

        self.gardener_memories_merged = Counter(
            "mind_gardener_memories_merged_total",
            "Total memories merged during consolidation",
        )

        # Reindex metrics
        self.reindex_memories_processed = Counter(
            "mind_reindex_memories_processed_total",
            "Total memories processed during reindexing",
            ["status"],  # status: updated, failed, skipped
        )

    def observe_retrieval(
        self,
        latency_seconds: float,
        sources_used: list[str],
        result_count: int,
    ) -> None:
        """Record retrieval metrics."""
        self.retrieval_latency_seconds.labels(source="fusion").observe(latency_seconds)
        for source in sources_used:
            self.retrieval_sources_used.labels(source=source).inc()

    def observe_outcome(self, quality: float) -> None:
        """Record outcome observation."""
        if quality > 0:
            label = "positive"
        elif quality < 0:
            label = "negative"
        else:
            label = "neutral"
        self.outcomes_observed_total.labels(quality=label).inc()

    def update_decision_success_rate(
        self,
        success_rate: float,
        user_cohort: str = "all",
        decision_type: str = "all",
    ) -> None:
        """Update rolling decision success rate.

        Args:
            success_rate: Success rate between 0 and 1
            user_cohort: User cohort (e.g., "all", "new", "active")
            decision_type: Type of decision (e.g., "all", "recommendation")
        """
        self.decision_success_rate.labels(
            user_cohort=user_cohort,
            decision_type=decision_type,
        ).set(success_rate)

    def observe_memory_relevance(
        self,
        relevance_score: float,
        temporal_level: str,
        source: str = "fusion",
    ) -> None:
        """Record memory retrieval relevance.

        Args:
            relevance_score: Relevance score between 0 and 1
            temporal_level: Memory temporal level
            source: Retrieval source (vector, keyword, fusion)
        """
        self.memory_retrieval_relevance.labels(
            temporal_level=temporal_level,
            source=source,
        ).observe(relevance_score)

    def update_causal_accuracy(
        self,
        accuracy: float,
        prediction_type: str,
    ) -> None:
        """Update causal prediction accuracy.

        Args:
            accuracy: Accuracy between 0 and 1
            prediction_type: Type of prediction (outcome, attribution, counterfactual)
        """
        self.causal_prediction_accuracy.labels(
            prediction_type=prediction_type,
        ).set(accuracy)

    def observe_context_completeness(
        self,
        completeness: float,
        decision_type: str = "unknown",
    ) -> None:
        """Record decision context completeness.

        Args:
            completeness: Completeness score between 0 and 1
            decision_type: Type of decision
        """
        self.context_completeness.labels(
            decision_type=decision_type,
        ).observe(completeness)

    def update_calibration_error(
        self,
        ece: float,
        user_cohort: str = "all",
    ) -> None:
        """Update Expected Calibration Error.

        Args:
            ece: Expected Calibration Error (lower is better)
            user_cohort: User cohort
        """
        self.confidence_calibration_error.labels(
            user_cohort=user_cohort,
        ).set(ece)

    def update_pattern_effectiveness(
        self,
        effectiveness: float,
        pattern_type: str,
    ) -> None:
        """Update pattern effectiveness metric.

        Args:
            effectiveness: Outcome improvement from pattern
            pattern_type: Type of pattern
        """
        self.pattern_effectiveness.labels(
            pattern_type=pattern_type,
        ).set(effectiveness)

    def record_embedding_cache_hit(self) -> None:
        """Record an embedding cache hit."""
        self.embedding_cache_hits_total.inc()

    def record_embedding_cache_miss(self) -> None:
        """Record an embedding cache miss."""
        self.embedding_cache_misses_total.inc()

    # =========================================================================
    # Workflow Metrics Methods
    # =========================================================================

    def record_workflow_started(self, workflow_type: str) -> None:
        """Record a workflow execution start."""
        self.workflow_executions_total.labels(
            workflow_type=workflow_type,
            status="started",
        ).inc()

    def record_workflow_completed(
        self,
        workflow_type: str,
        duration_seconds: float,
        success: bool = True,
    ) -> None:
        """Record a workflow execution completion.

        Args:
            workflow_type: Name of the workflow
            duration_seconds: How long the workflow took
            success: Whether the workflow succeeded
        """
        status = "completed" if success else "failed"
        self.workflow_executions_total.labels(
            workflow_type=workflow_type,
            status=status,
        ).inc()
        self.workflow_duration_seconds.labels(
            workflow_type=workflow_type,
        ).observe(duration_seconds)

    def record_activity_started(self, activity_type: str) -> None:
        """Record an activity execution start."""
        self.activity_executions_total.labels(
            activity_type=activity_type,
            status="started",
        ).inc()

    def record_activity_completed(
        self,
        activity_type: str,
        duration_seconds: float,
        success: bool = True,
    ) -> None:
        """Record an activity execution completion.

        Args:
            activity_type: Name of the activity
            duration_seconds: How long the activity took
            success: Whether the activity succeeded
        """
        status = "completed" if success else "failed"
        self.activity_executions_total.labels(
            activity_type=activity_type,
            status=status,
        ).inc()
        self.activity_duration_seconds.labels(
            activity_type=activity_type,
        ).observe(duration_seconds)

    def record_workflow_users_processed(
        self,
        workflow_type: str,
        count: int,
    ) -> None:
        """Record users processed by a workflow."""
        self.workflow_users_processed.labels(
            workflow_type=workflow_type,
        ).inc(count)

    def record_workflow_items_processed(
        self,
        workflow_type: str,
        item_type: str,
        count: int,
    ) -> None:
        """Record items processed by a workflow."""
        self.workflow_items_processed.labels(
            workflow_type=workflow_type,
            item_type=item_type,
        ).inc(count)

    def record_schedule_run(self, schedule_id: str) -> None:
        """Record a scheduled workflow run."""
        import time

        self.schedule_runs_total.labels(schedule_id=schedule_id).inc()
        self.schedule_last_run_timestamp.labels(schedule_id=schedule_id).set(time.time())

    def set_worker_active(
        self,
        worker_type: str,
        task_queue: str,
        active: bool = True,
    ) -> None:
        """Set worker active status."""
        self.worker_active.labels(
            worker_type=worker_type,
            task_queue=task_queue,
        ).set(1 if active else 0)

    def record_gardener_results(
        self,
        promotions: int = 0,
        expirations: int = 0,
        consolidations: int = 0,
        memories_merged: int = 0,
    ) -> None:
        """Record gardener workflow results."""
        if promotions > 0:
            self.gardener_promotions_succeeded.inc(promotions)
        if expirations > 0:
            self.gardener_expirations_succeeded.inc(expirations)
        if consolidations > 0:
            self.gardener_consolidations_succeeded.inc(consolidations)
        if memories_merged > 0:
            self.gardener_memories_merged.inc(memories_merged)

    def record_reindex_result(
        self,
        updated: int = 0,
        failed: int = 0,
        skipped: int = 0,
    ) -> None:
        """Record reindex workflow results."""
        if updated > 0:
            self.reindex_memories_processed.labels(status="updated").inc(updated)
        if failed > 0:
            self.reindex_memories_processed.labels(status="failed").inc(failed)
        if skipped > 0:
            self.reindex_memories_processed.labels(status="skipped").inc(skipped)

    # =========================================================================
    # Event Consumer Metrics
    # =========================================================================

    def record_event_processed(
        self,
        consumer: str,
        event_type: str,
        success: bool = True,
    ) -> None:
        """Record an event processed by a consumer."""
        status = "success" if success else "failure"
        self.events_processed_total.labels(
            consumer=consumer,
            event_type=event_type,
            status=status,
        ).inc()

    def record_dlq_message(
        self,
        consumer: str,
        event_type: str,
    ) -> None:
        """Record a message sent to dead letter queue."""
        self.dlq_messages_total.labels(
            consumer=consumer,
            event_type=event_type,
        ).inc()

    def set_dlq_depth(
        self,
        stream: str,
        depth: int,
    ) -> None:
        """Set current DLQ depth."""
        self.dlq_depth.labels(stream=stream).set(depth)

    def set_dlq_oldest_age(
        self,
        stream: str,
        age_seconds: float,
    ) -> None:
        """Set age of oldest DLQ message."""
        self.dlq_oldest_message_age_seconds.labels(stream=stream).set(age_seconds)

    # =========================================================================
    # Pattern Effectiveness Metrics
    # =========================================================================

    def record_pattern_usage(self, pattern_id: str) -> None:
        """Record that a pattern was used for a decision."""
        self.patterns_applied_total.inc()

    def record_pattern_success(self, pattern_id: str) -> None:
        """Record a pattern use that improved the outcome."""
        self.pattern_success_total.labels(pattern_id=pattern_id).inc()

    def record_pattern_failure(self, pattern_id: str) -> None:
        """Record a pattern use that did not improve the outcome."""
        self.pattern_failure_total.labels(pattern_id=pattern_id).inc()

    def set_pattern_effectiveness(
        self,
        pattern_type: str,
        effectiveness: float,
    ) -> None:
        """Set effectiveness score for a pattern type."""
        self.pattern_effectiveness.labels(pattern_type=pattern_type).set(effectiveness)

    def set_pattern_success_rate(
        self,
        pattern_id: str,
        success_rate: float,
    ) -> None:
        """Set success rate for a specific pattern."""
        self.pattern_success_rate.labels(pattern_id=pattern_id).set(success_rate)


# Global metrics instance
metrics = MindMetrics()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record HTTP metrics."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time

        # Extract endpoint (remove path parameters)
        endpoint = request.url.path
        for key, value in request.path_params.items():
            endpoint = endpoint.replace(str(value), f"{{{key}}}")

        metrics.http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()

        metrics.http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(duration)

        return response


async def metrics_endpoint(request: Request) -> StarletteResponse:
    """Prometheus metrics endpoint."""
    return StarletteResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
