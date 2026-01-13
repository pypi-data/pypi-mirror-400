"""Data retention service for Mind v5.

This service enforces retention policies by:
- Finding data that has exceeded retention periods
- Applying the appropriate action (archive, delete, anonymize)
- Tracking retention statistics and compliance
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog

from mind.core.errors import ErrorCode, MindError, Result
from mind.core.memory.models import TemporalLevel
from mind.core.retention.models import (
    DataType,
    RetentionAction,
    RetentionPolicy,
    RetentionResult,
    RetentionStats,
    get_default_policy,
)
from mind.observability.tracing import get_tracer

logger = structlog.get_logger()
_tracer = get_tracer("mind.retention")


# Mapping from temporal level to data type
TEMPORAL_LEVEL_TO_DATA_TYPE = {
    TemporalLevel.IMMEDIATE: DataType.MEMORY_WORKING,
    TemporalLevel.SITUATIONAL: DataType.MEMORY_EPISODIC,
    TemporalLevel.SEASONAL: DataType.MEMORY_SEMANTIC,
    TemporalLevel.IDENTITY: DataType.MEMORY_IDENTITY,
}


@dataclass
class RetentionConfig:
    """Configuration for retention service.

    Allows customizing retention behavior per environment.
    """

    # Enable/disable retention enforcement
    enabled: bool = True

    # Dry run mode - log actions without executing
    dry_run: bool = False

    # Maximum records per batch
    batch_size: int = 1000

    # Maximum duration per run (seconds)
    max_duration_seconds: int = 300

    # Pause between batches (seconds)
    batch_pause_seconds: float = 0.1


class RetentionService:
    """Service for enforcing data retention policies.

    This service coordinates with repositories to find and process
    data that has exceeded its retention period.

    Example:
        service = RetentionService(
            memory_repo=memory_repo,
            decision_repo=decision_repo,
        )
        result = await service.apply_policy(
            DataType.MEMORY_WORKING,
            user_id=user_id,
        )
    """

    def __init__(
        self,
        memory_repository=None,
        decision_repository=None,
        event_client=None,
        graph_repository=None,
        config: RetentionConfig | None = None,
    ):
        """Initialize the retention service.

        Args:
            memory_repository: Repository for memory operations
            decision_repository: Repository for decision operations
            event_client: NATS client for event stream operations
            graph_repository: FalkorDB repository for causal graph
            config: Retention configuration
        """
        self._memories = memory_repository
        self._decisions = decision_repository
        self._events = event_client
        self._graph = graph_repository
        self._config = config or RetentionConfig()
        self._custom_policies: dict[tuple[DataType, UUID | None], RetentionPolicy] = {}

    def set_policy(
        self,
        policy: RetentionPolicy,
    ) -> None:
        """Set a custom retention policy.

        Args:
            policy: The retention policy to set
        """
        key = (policy.data_type, policy.user_id)
        self._custom_policies[key] = policy
        logger.info(
            "retention_policy_set",
            data_type=policy.data_type.value,
            retention_days=policy.retention_days,
            action=policy.action.value,
            user_id=str(policy.user_id) if policy.user_id else None,
        )

    def get_policy(
        self,
        data_type: DataType,
        user_id: UUID | None = None,
    ) -> RetentionPolicy:
        """Get the effective retention policy for a data type.

        First checks for user-specific policy, then global custom,
        then falls back to default.

        Args:
            data_type: Type of data
            user_id: Optional user for user-specific policies

        Returns:
            The effective retention policy
        """
        # Check user-specific policy
        if user_id:
            key = (data_type, user_id)
            if key in self._custom_policies:
                return self._custom_policies[key]

        # Check global custom policy
        key = (data_type, None)
        if key in self._custom_policies:
            return self._custom_policies[key]

        # Fall back to default
        return get_default_policy(data_type)

    async def apply_policy(
        self,
        data_type: DataType,
        user_id: UUID | None = None,
        policy: RetentionPolicy | None = None,
    ) -> Result[RetentionResult]:
        """Apply retention policy to a data type.

        Finds records that have exceeded retention and applies the
        configured action (archive, delete, or anonymize).

        Args:
            data_type: Type of data to process
            user_id: Optional user to scope the operation
            policy: Optional policy override

        Returns:
            Result containing RetentionResult with processing stats
        """
        with _tracer.start_as_current_span("apply_retention_policy") as span:
            span.set_attribute("data_type", data_type.value)
            if user_id:
                span.set_attribute("user_id", str(user_id))

            if not self._config.enabled:
                return Result.ok(
                    RetentionResult(
                        policy=policy or self.get_policy(data_type, user_id),
                        errors=["Retention disabled"],
                    )
                )

            effective_policy = policy or self.get_policy(data_type, user_id)
            span.set_attribute("retention_days", effective_policy.retention_days)
            span.set_attribute("action", effective_policy.action.value)

            result = RetentionResult(
                policy=effective_policy,
                started_at=datetime.now(UTC),
            )

            try:
                # Route to appropriate handler
                if data_type in (
                    DataType.MEMORY_WORKING,
                    DataType.MEMORY_EPISODIC,
                    DataType.MEMORY_SEMANTIC,
                    DataType.MEMORY_IDENTITY,
                ):
                    await self._apply_memory_retention(data_type, effective_policy, user_id, result)
                elif data_type == DataType.DECISION_TRACE:
                    await self._apply_decision_retention(effective_policy, user_id, result)
                elif data_type == DataType.EVENT_STREAM:
                    await self._apply_event_retention(effective_policy, result)
                elif data_type == DataType.CAUSAL_EDGE:
                    await self._apply_causal_retention(effective_policy, user_id, result)
                else:
                    result.errors.append(f"No handler for data type: {data_type.value}")

                result.completed_at = datetime.now(UTC)
                span.set_attribute("records_processed", result.records_processed)
                span.set_attribute("success_rate", result.success_rate)

                logger.info(
                    "retention_policy_applied",
                    data_type=data_type.value,
                    records_found=result.records_found,
                    records_processed=result.records_processed,
                    duration_seconds=result.duration_seconds,
                )

                return Result.ok(result)

            except Exception as e:
                span.record_exception(e)
                result.completed_at = datetime.now(UTC)
                result.errors.append(str(e))
                logger.error(
                    "retention_policy_failed",
                    data_type=data_type.value,
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Retention policy failed: {e}",
                    )
                )

    async def _apply_memory_retention(
        self,
        data_type: DataType,
        policy: RetentionPolicy,
        user_id: UUID | None,
        result: RetentionResult,
    ) -> None:
        """Apply retention to memory records."""
        if self._memories is None:
            result.errors.append("Memory repository not configured")
            return

        # Map data type to temporal level
        temporal_level = None
        for level, dtype in TEMPORAL_LEVEL_TO_DATA_TYPE.items():
            if dtype == data_type:
                temporal_level = level
                break

        if temporal_level is None:
            result.errors.append(f"No temporal level for {data_type.value}")
            return

        cutoff_date = datetime.now(UTC) - timedelta(days=policy.total_retention_days)

        # Find expired memories
        expired = await self._memories.find_expired_memories(
            user_id=user_id,
            temporal_level=temporal_level,
            before_date=cutoff_date,
            limit=policy.batch_size,
        )

        if not expired.is_ok:
            result.errors.append(f"Failed to find expired memories: {expired.error}")
            return

        memories = expired.value
        result.records_found = len(memories)

        for memory in memories:
            if self._config.dry_run:
                result.records_processed += 1
                continue

            try:
                if policy.action == RetentionAction.ARCHIVE:
                    archive_result = await self._memories.archive_memory(memory.memory_id)
                    if archive_result.is_ok:
                        result.records_archived += 1
                    else:
                        result.records_failed += 1
                        result.errors.append(str(archive_result.error))

                elif policy.action == RetentionAction.SOFT_DELETE:
                    delete_result = await self._memories.soft_delete_memory(memory.memory_id)
                    if delete_result.is_ok:
                        result.records_deleted += 1
                    else:
                        result.records_failed += 1
                        result.errors.append(str(delete_result.error))

                elif policy.action == RetentionAction.HARD_DELETE:
                    delete_result = await self._memories.hard_delete_memory(memory.memory_id)
                    if delete_result.is_ok:
                        result.records_deleted += 1
                    else:
                        result.records_failed += 1
                        result.errors.append(str(delete_result.error))

                result.records_processed += 1

            except Exception as e:
                result.records_failed += 1
                result.errors.append(f"Memory {memory.memory_id}: {e}")

    async def _apply_decision_retention(
        self,
        policy: RetentionPolicy,
        user_id: UUID | None,
        result: RetentionResult,
    ) -> None:
        """Apply retention to decision traces."""
        if self._decisions is None:
            result.errors.append("Decision repository not configured")
            return

        cutoff_date = datetime.now(UTC) - timedelta(days=policy.total_retention_days)

        # Find expired decisions
        expired = await self._decisions.find_expired_decisions(
            user_id=user_id,
            before_date=cutoff_date,
            limit=policy.batch_size,
        )

        if not expired.is_ok:
            result.errors.append(f"Failed to find expired decisions: {expired.error}")
            return

        decisions = expired.value
        result.records_found = len(decisions)

        for decision in decisions:
            if self._config.dry_run:
                result.records_processed += 1
                continue

            try:
                if policy.action == RetentionAction.ANONYMIZE:
                    anon_result = await self._decisions.anonymize_decision(decision.trace_id)
                    if anon_result.is_ok:
                        result.records_anonymized += 1
                    else:
                        result.records_failed += 1
                        result.errors.append(str(anon_result.error))

                elif policy.action == RetentionAction.ARCHIVE:
                    archive_result = await self._decisions.archive_decision(decision.trace_id)
                    if archive_result.is_ok:
                        result.records_archived += 1
                    else:
                        result.records_failed += 1
                        result.errors.append(str(archive_result.error))

                result.records_processed += 1

            except Exception as e:
                result.records_failed += 1
                result.errors.append(f"Decision {decision.trace_id}: {e}")

    async def _apply_event_retention(
        self,
        policy: RetentionPolicy,
        result: RetentionResult,
    ) -> None:
        """Apply retention to event streams."""
        if self._events is None:
            result.errors.append("Event client not configured")
            return

        # NATS JetStream has built-in retention policies
        # We just need to configure the stream limits
        max_age_seconds = policy.retention_days * 24 * 60 * 60

        if self._config.dry_run:
            result.records_processed = 1
            return

        try:
            # This would update NATS stream configuration
            # For now, log the intended action
            logger.info(
                "event_retention_configured",
                max_age_seconds=max_age_seconds,
                action=policy.action.value,
            )
            result.records_processed = 1
        except Exception as e:
            result.records_failed += 1
            result.errors.append(f"Event stream update failed: {e}")

    async def _apply_causal_retention(
        self,
        policy: RetentionPolicy,
        user_id: UUID | None,
        result: RetentionResult,
    ) -> None:
        """Apply retention to causal graph edges."""
        if self._graph is None:
            result.errors.append("Graph repository not configured")
            return

        cutoff_date = datetime.now(UTC) - timedelta(days=policy.total_retention_days)

        # Find expired causal edges
        expired = await self._graph.find_expired_edges(
            user_id=user_id,
            before_date=cutoff_date,
            limit=policy.batch_size,
        )

        if not expired.is_ok:
            result.errors.append(f"Failed to find expired edges: {expired.error}")
            return

        edges = expired.value
        result.records_found = len(edges)

        for edge in edges:
            if self._config.dry_run:
                result.records_processed += 1
                continue

            try:
                delete_result = await self._graph.delete_edge(edge["id"])
                if delete_result.is_ok:
                    result.records_deleted += 1
                else:
                    result.records_failed += 1
                    result.errors.append(str(delete_result.error))

                result.records_processed += 1

            except Exception as e:
                result.records_failed += 1
                result.errors.append(f"Edge {edge.get('id')}: {e}")

    async def get_retention_stats(
        self,
        data_type: DataType,
        user_id: UUID | None = None,
    ) -> Result[RetentionStats]:
        """Get retention statistics for a data type.

        Args:
            data_type: Type of data to analyze
            user_id: Optional user to scope the analysis

        Returns:
            Result containing RetentionStats
        """
        with _tracer.start_as_current_span("get_retention_stats") as span:
            span.set_attribute("data_type", data_type.value)
            if user_id:
                span.set_attribute("user_id", str(user_id))

            policy = self.get_policy(data_type, user_id)
            now = datetime.now(UTC)
            now - timedelta(days=policy.total_retention_days)
            now - timedelta(days=policy.total_retention_days - 7)

            try:
                # For now, return placeholder stats
                # Actual implementation would query repositories
                stats = RetentionStats(
                    user_id=user_id,
                    data_type=data_type,
                    total_records=0,
                    records_in_retention=0,
                    records_near_expiry=0,
                    records_expired=0,
                    oldest_record_age_days=0,
                    newest_record_age_days=0,
                    policy=policy,
                )

                # TODO: Query actual stats from repositories
                # This would involve:
                # 1. Count total records
                # 2. Count records older than expiry_threshold
                # 3. Count records between near_expiry and expiry
                # 4. Get min/max created_at dates

                return Result.ok(stats)

            except Exception as e:
                span.record_exception(e)
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Failed to get retention stats: {e}",
                    )
                )

    async def apply_all_policies(
        self,
        user_id: UUID | None = None,
    ) -> Result[list[RetentionResult]]:
        """Apply all retention policies.

        Processes all data types in priority order.

        Args:
            user_id: Optional user to scope the operations

        Returns:
            Result containing list of RetentionResults
        """
        with _tracer.start_as_current_span("apply_all_policies") as span:
            if user_id:
                span.set_attribute("user_id", str(user_id))

            results = []
            start_time = datetime.now(UTC)

            # Process in priority order (shortest retention first)
            priority_order = [
                DataType.MEMORY_WORKING,
                DataType.DLQ_MESSAGE,
                DataType.EVENT_STREAM,
                DataType.MEMORY_EPISODIC,
                DataType.DECISION_TRACE,
                DataType.CAUSAL_EDGE,
                DataType.OUTCOME,
                DataType.MEMORY_SEMANTIC,
                DataType.PATTERN,
                DataType.MEMORY_IDENTITY,
                DataType.FEDERATED_PATTERN,
            ]

            for data_type in priority_order:
                # Check time limit
                elapsed = (datetime.now(UTC) - start_time).total_seconds()
                if elapsed > self._config.max_duration_seconds:
                    logger.warning(
                        "retention_time_limit_reached",
                        elapsed_seconds=elapsed,
                        remaining_types=[dt.value for dt in priority_order[len(results) :]],
                    )
                    break

                result = await self.apply_policy(data_type, user_id)
                if result.is_ok:
                    results.append(result.value)
                else:
                    # Log error but continue with other types
                    logger.error(
                        "retention_policy_error",
                        data_type=data_type.value,
                        error=str(result.error),
                    )

            span.set_attribute("policies_applied", len(results))
            total_processed = sum(r.records_processed for r in results)
            span.set_attribute("total_records_processed", total_processed)

            return Result.ok(results)
