"""Temporal workflows for memory lifecycle management.

Workflows are the durable, long-running orchestrators that
coordinate activities. They handle retries, timeouts, and
maintain state across failures.
"""

from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity stubs (not the actual implementations)
with workflow.unsafe.imports_passed_through():
    from mind.workers.gardener.activities import (
        CalibrationResult,
        ConsolidationResult,
        DecisionPatternData,
        ExpirationResult,
        OutcomeAnalysisResult,
        PatternExtractionResult,
        PromotionResult,
        ReindexBatch,
        ReindexCandidate,
        ReindexResult,
        SalienceAdjustmentBatch,
        SanitizationResult,
        analyze_confidence_calibration,
        analyze_user_outcomes,
        apply_salience_adjustments,
        archive_memory,
        consolidate_memories,
        count_memories_for_reindex,
        extract_patterns_from_decisions,
        find_consolidation_candidates,
        find_expired_memories,
        find_memories_for_reindex,
        find_promotion_candidates,
        find_successful_decisions,
        generate_embeddings_for_batch,
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


@dataclass
class PromotionWorkflowInput:
    """Input for the memory promotion workflow."""

    user_id: UUID
    batch_size: int = 100
    max_promotions_per_run: int = 50


@dataclass
class PromotionWorkflowResult:
    """Result of the memory promotion workflow."""

    candidates_found: int
    promotions_attempted: int
    promotions_succeeded: int
    promotions_failed: int
    errors: list[str]


@workflow.defn
class MemoryPromotionWorkflow:
    """Workflow that promotes memories to higher temporal levels.

    This workflow runs periodically (via a scheduled workflow or cron)
    to evaluate and promote memories that have proven stable and valuable.

    The workflow:
    1. Finds candidate memories for promotion
    2. Promotes each candidate (with retries)
    3. Publishes events for successful promotions
    4. Returns summary of actions taken

    Example usage:
        # Start a single run
        handle = await client.start_workflow(
            MemoryPromotionWorkflow.run,
            PromotionWorkflowInput(user_id=user_id),
            id=f"promote-{user_id}",
            task_queue="gardener",
        )

        # Or schedule recurring runs
        await client.start_workflow(
            MemoryPromotionWorkflow.run,
            PromotionWorkflowInput(user_id=user_id),
            id=f"promote-scheduled-{user_id}",
            task_queue="gardener",
            cron_schedule="0 3 * * *",  # Daily at 3 AM
        )
    """

    @workflow.run
    async def run(self, input: PromotionWorkflowInput) -> PromotionWorkflowResult:
        """Execute the memory promotion workflow."""

        workflow.logger.info(
            f"Starting memory promotion for user {input.user_id}, batch_size={input.batch_size}"
        )

        errors = []

        # Step 1: Find candidates
        try:
            candidates = await workflow.execute_activity(
                find_promotion_candidates,
                args=[input.user_id, input.batch_size],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to find candidates: {e}")
            return PromotionWorkflowResult(
                candidates_found=0,
                promotions_attempted=0,
                promotions_succeeded=0,
                promotions_failed=0,
                errors=[f"Failed to find candidates: {str(e)}"],
            )

        candidates_found = len(candidates)
        workflow.logger.info(f"Found {candidates_found} promotion candidates")

        if candidates_found == 0:
            return PromotionWorkflowResult(
                candidates_found=0,
                promotions_attempted=0,
                promotions_succeeded=0,
                promotions_failed=0,
                errors=[],
            )

        # Limit number of promotions per run
        candidates_to_process = candidates[: input.max_promotions_per_run]

        # Step 2: Promote each candidate
        promotions_attempted = 0
        promotions_succeeded = 0
        promotions_failed = 0

        for candidate in candidates_to_process:
            promotions_attempted += 1

            try:
                result: PromotionResult = await workflow.execute_activity(
                    promote_memory,
                    args=[candidate],
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )

                if result.success:
                    promotions_succeeded += 1

                    # Step 3: Publish promotion event
                    try:
                        await workflow.execute_activity(
                            notify_promotion,
                            args=[result, input.user_id],
                            start_to_close_timeout=timedelta(seconds=30),
                            retry_policy=RetryPolicy(
                                initial_interval=timedelta(seconds=1),
                                maximum_interval=timedelta(seconds=10),
                                maximum_attempts=2,
                            ),
                        )
                    except Exception as e:
                        # Don't fail the workflow for notification failures
                        workflow.logger.warning(
                            f"Failed to notify promotion for {candidate.memory_id}: {e}"
                        )

                else:
                    promotions_failed += 1
                    errors.append(f"Memory {candidate.memory_id}: {result.error}")

            except Exception as e:
                promotions_failed += 1
                errors.append(f"Memory {candidate.memory_id}: {str(e)}")
                workflow.logger.error(f"Failed to promote {candidate.memory_id}: {e}")

        workflow.logger.info(
            f"Promotion complete: {promotions_succeeded}/{promotions_attempted} succeeded"
        )

        return PromotionWorkflowResult(
            candidates_found=candidates_found,
            promotions_attempted=promotions_attempted,
            promotions_succeeded=promotions_succeeded,
            promotions_failed=promotions_failed,
            errors=errors,
        )


@dataclass
class ExpirationWorkflowInput:
    """Input for the memory expiration workflow."""

    user_id: UUID
    batch_size: int = 100
    max_expirations_per_run: int = 100


@dataclass
class ExpirationWorkflowResult:
    """Result of the memory expiration workflow."""

    candidates_found: int
    expirations_attempted: int
    expirations_succeeded: int
    expirations_failed: int
    errors: list[str]


@workflow.defn
class MemoryExpirationWorkflow:
    """Workflow that archives expired memories.

    This workflow runs periodically to find and archive memories that:
    1. Have passed their valid_until timestamp
    2. Have dropped below salience thresholds

    The workflow:
    1. Finds expired memory candidates
    2. Archives each candidate (with retries)
    3. Publishes events for successful expirations
    4. Returns summary of actions taken

    Example usage:
        # Start a single run
        handle = await client.start_workflow(
            MemoryExpirationWorkflow.run,
            ExpirationWorkflowInput(user_id=user_id),
            id=f"expire-{user_id}",
            task_queue="gardener",
        )

        # Or schedule recurring runs
        await client.start_workflow(
            MemoryExpirationWorkflow.run,
            ExpirationWorkflowInput(user_id=user_id),
            id=f"expire-scheduled-{user_id}",
            task_queue="gardener",
            cron_schedule="0 4 * * *",  # Daily at 4 AM
        )
    """

    @workflow.run
    async def run(self, input: ExpirationWorkflowInput) -> ExpirationWorkflowResult:
        """Execute the memory expiration workflow."""

        workflow.logger.info(
            f"Starting memory expiration for user {input.user_id}, batch_size={input.batch_size}"
        )

        errors = []

        # Step 1: Find expired candidates
        try:
            candidates = await workflow.execute_activity(
                find_expired_memories,
                args=[input.user_id, input.batch_size],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to find expired memories: {e}")
            return ExpirationWorkflowResult(
                candidates_found=0,
                expirations_attempted=0,
                expirations_succeeded=0,
                expirations_failed=0,
                errors=[f"Failed to find expired memories: {str(e)}"],
            )

        candidates_found = len(candidates)
        workflow.logger.info(f"Found {candidates_found} expiration candidates")

        if candidates_found == 0:
            return ExpirationWorkflowResult(
                candidates_found=0,
                expirations_attempted=0,
                expirations_succeeded=0,
                expirations_failed=0,
                errors=[],
            )

        # Limit number of expirations per run
        candidates_to_process = candidates[: input.max_expirations_per_run]

        # Step 2: Archive each candidate
        expirations_attempted = 0
        expirations_succeeded = 0
        expirations_failed = 0

        for candidate in candidates_to_process:
            expirations_attempted += 1

            try:
                result: ExpirationResult = await workflow.execute_activity(
                    archive_memory,
                    args=[candidate],
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )

                if result.success:
                    expirations_succeeded += 1

                    # Step 3: Publish expiration event
                    try:
                        await workflow.execute_activity(
                            notify_expiration,
                            args=[result, candidate],
                            start_to_close_timeout=timedelta(seconds=30),
                            retry_policy=RetryPolicy(
                                initial_interval=timedelta(seconds=1),
                                maximum_interval=timedelta(seconds=10),
                                maximum_attempts=2,
                            ),
                        )
                    except Exception as e:
                        # Don't fail the workflow for notification failures
                        workflow.logger.warning(
                            f"Failed to notify expiration for {candidate.memory_id}: {e}"
                        )

                else:
                    expirations_failed += 1
                    errors.append(f"Memory {candidate.memory_id}: {result.error}")

            except Exception as e:
                expirations_failed += 1
                errors.append(f"Memory {candidate.memory_id}: {str(e)}")
                workflow.logger.error(f"Failed to archive {candidate.memory_id}: {e}")

        workflow.logger.info(
            f"Expiration complete: {expirations_succeeded}/{expirations_attempted} succeeded"
        )

        return ExpirationWorkflowResult(
            candidates_found=candidates_found,
            expirations_attempted=expirations_attempted,
            expirations_succeeded=expirations_succeeded,
            expirations_failed=expirations_failed,
            errors=errors,
        )


@dataclass
class ConsolidationWorkflowInput:
    """Input for the memory consolidation workflow."""

    user_id: UUID
    batch_size: int = 50
    max_consolidations_per_run: int = 20


@dataclass
class ConsolidationWorkflowResult:
    """Result of the memory consolidation workflow."""

    candidates_found: int
    consolidations_attempted: int
    consolidations_succeeded: int
    consolidations_failed: int
    memories_merged: int
    errors: list[str]


@workflow.defn
class MemoryConsolidationWorkflow:
    """Workflow that consolidates similar memories.

    This workflow runs periodically to find and merge memories that:
    1. Have high semantic similarity (>85%)
    2. Are in the same temporal level
    3. Are old enough to be stable (>48 hours)

    Consolidation reduces redundancy while preserving information by:
    - Keeping the primary memory content
    - Appending unique information from similar memories
    - Combining retrieval/outcome statistics
    - Archiving the source memories

    Example usage:
        # Start a single run
        handle = await client.start_workflow(
            MemoryConsolidationWorkflow.run,
            ConsolidationWorkflowInput(user_id=user_id),
            id=f"consolidate-{user_id}",
            task_queue="gardener",
        )

        # Or schedule recurring runs
        await client.start_workflow(
            MemoryConsolidationWorkflow.run,
            ConsolidationWorkflowInput(user_id=user_id),
            id=f"consolidate-scheduled-{user_id}",
            task_queue="gardener",
            cron_schedule="0 5 * * *",  # Daily at 5 AM
        )
    """

    @workflow.run
    async def run(self, input: ConsolidationWorkflowInput) -> ConsolidationWorkflowResult:
        """Execute the memory consolidation workflow."""

        workflow.logger.info(
            f"Starting memory consolidation for user {input.user_id}, batch_size={input.batch_size}"
        )

        errors = []
        total_memories_merged = 0

        # Step 1: Find candidates
        try:
            candidates = await workflow.execute_activity(
                find_consolidation_candidates,
                args=[input.user_id, input.batch_size],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to find candidates: {e}")
            return ConsolidationWorkflowResult(
                candidates_found=0,
                consolidations_attempted=0,
                consolidations_succeeded=0,
                consolidations_failed=0,
                memories_merged=0,
                errors=[f"Failed to find candidates: {str(e)}"],
            )

        candidates_found = len(candidates)
        workflow.logger.info(f"Found {candidates_found} consolidation candidates")

        if candidates_found == 0:
            return ConsolidationWorkflowResult(
                candidates_found=0,
                consolidations_attempted=0,
                consolidations_succeeded=0,
                consolidations_failed=0,
                memories_merged=0,
                errors=[],
            )

        # Limit number of consolidations per run
        candidates_to_process = candidates[: input.max_consolidations_per_run]

        # Step 2: Consolidate each candidate group
        consolidations_attempted = 0
        consolidations_succeeded = 0
        consolidations_failed = 0

        for candidate in candidates_to_process:
            consolidations_attempted += 1

            try:
                result: ConsolidationResult = await workflow.execute_activity(
                    consolidate_memories,
                    args=[candidate],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )

                if result.success:
                    consolidations_succeeded += 1
                    total_memories_merged += result.memories_merged

                    # Step 3: Publish consolidation event
                    try:
                        await workflow.execute_activity(
                            notify_consolidation,
                            args=[result, input.user_id],
                            start_to_close_timeout=timedelta(seconds=30),
                            retry_policy=RetryPolicy(
                                initial_interval=timedelta(seconds=1),
                                maximum_interval=timedelta(seconds=10),
                                maximum_attempts=2,
                            ),
                        )
                    except Exception as e:
                        # Don't fail the workflow for notification failures
                        workflow.logger.warning(
                            f"Failed to notify consolidation for {candidate.primary_memory_id}: {e}"
                        )

                else:
                    consolidations_failed += 1
                    errors.append(f"Memory {candidate.primary_memory_id}: {result.error}")

            except Exception as e:
                consolidations_failed += 1
                errors.append(f"Memory {candidate.primary_memory_id}: {str(e)}")
                workflow.logger.error(f"Failed to consolidate {candidate.primary_memory_id}: {e}")

        workflow.logger.info(
            f"Consolidation complete: {consolidations_succeeded}/{consolidations_attempted} succeeded, "
            f"{total_memories_merged} memories merged"
        )

        return ConsolidationWorkflowResult(
            candidates_found=candidates_found,
            consolidations_attempted=consolidations_attempted,
            consolidations_succeeded=consolidations_succeeded,
            consolidations_failed=consolidations_failed,
            memories_merged=total_memories_merged,
            errors=errors,
        )


@dataclass
class ScheduledGardenerInput:
    """Input for the scheduled gardener workflow."""

    user_ids: list[UUID] | None = None  # None = discover active users
    days_active: int = 30  # Look back window for user discovery
    max_users: int = 1000  # Maximum users to process per run


@dataclass
class GardenerResult:
    """Result from a single user's gardening run."""

    promotions_succeeded: int
    expirations_succeeded: int
    consolidations_succeeded: int
    memories_merged: int
    errors: list[str]


@dataclass
class ScheduledGardenerResult:
    """Result from a scheduled gardening run."""

    users_processed: int
    total_promotions: int
    total_expirations: int
    total_consolidations: int
    total_memories_merged: int
    user_results: dict[str, GardenerResult]
    errors: list[str]


@workflow.defn
class ScheduledGardenerWorkflow:
    """Parent workflow that runs gardening tasks on a schedule.

    This workflow is designed to run continuously with a cron schedule.
    It coordinates multiple gardening tasks:
    - Memory promotion
    - Memory expiration
    - Memory consolidation

    The workflow can either:
    1. Accept a specific list of user IDs to process
    2. Automatically discover active users if none provided

    Example usage:
        # Run for specific users
        await client.execute_workflow(
            ScheduledGardenerWorkflow.run,
            ScheduledGardenerInput(user_ids=[user1, user2]),
            id="gardener-manual",
            task_queue="gardener",
        )

        # Auto-discover active users
        await client.execute_workflow(
            ScheduledGardenerWorkflow.run,
            ScheduledGardenerInput(),  # Will discover users
            id="gardener-scheduled",
            task_queue="gardener",
        )
    """

    @workflow.run
    async def run(self, input: ScheduledGardenerInput) -> ScheduledGardenerResult:
        """Run gardening tasks for all users.

        Args:
            input: Configuration for the gardening run

        Returns:
            Summary of actions taken
        """
        errors = []

        # Step 1: Discover users if not provided
        if input.user_ids:
            user_ids = input.user_ids
            workflow.logger.info(f"Using {len(user_ids)} provided user IDs")
        else:
            workflow.logger.info("Discovering active users...")
            try:
                user_ids = await workflow.execute_activity(
                    get_active_user_ids,
                    args=[input.days_active, input.max_users],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(minutes=1),
                        maximum_attempts=3,
                    ),
                )
                workflow.logger.info(f"Discovered {len(user_ids)} active users")
            except Exception as e:
                workflow.logger.error(f"Failed to discover users: {e}")
                return ScheduledGardenerResult(
                    users_processed=0,
                    total_promotions=0,
                    total_expirations=0,
                    total_consolidations=0,
                    total_memories_merged=0,
                    user_results={},
                    errors=[f"Failed to discover users: {str(e)}"],
                )

        if not user_ids:
            workflow.logger.info("No active users found, nothing to do")
            return ScheduledGardenerResult(
                users_processed=0,
                total_promotions=0,
                total_expirations=0,
                total_consolidations=0,
                total_memories_merged=0,
                user_results={},
                errors=[],
            )

        workflow.logger.info(f"Starting scheduled gardening for {len(user_ids)} users")

        user_results = {}
        total_promotions = 0
        total_expirations = 0
        total_consolidations = 0
        total_memories_merged = 0

        for user_id in user_ids:
            user_errors = []
            promotions_succeeded = 0
            expirations_succeeded = 0
            consolidations_succeeded = 0
            memories_merged = 0

            # Run promotion workflow
            try:
                promotion_result = await workflow.execute_child_workflow(
                    MemoryPromotionWorkflow.run,
                    args=[PromotionWorkflowInput(user_id=user_id)],
                    id=f"promote-child-{user_id}-{workflow.info().workflow_id}",
                )
                promotions_succeeded = promotion_result.promotions_succeeded
                user_errors.extend(promotion_result.errors)
            except Exception as e:
                workflow.logger.error(f"Failed promotion for user {user_id}: {e}")
                user_errors.append(f"Promotion failed: {str(e)}")

            # Run expiration workflow
            try:
                expiration_result = await workflow.execute_child_workflow(
                    MemoryExpirationWorkflow.run,
                    args=[ExpirationWorkflowInput(user_id=user_id)],
                    id=f"expire-child-{user_id}-{workflow.info().workflow_id}",
                )
                expirations_succeeded = expiration_result.expirations_succeeded
                user_errors.extend(expiration_result.errors)
            except Exception as e:
                workflow.logger.error(f"Failed expiration for user {user_id}: {e}")
                user_errors.append(f"Expiration failed: {str(e)}")

            # Run consolidation workflow
            try:
                consolidation_result = await workflow.execute_child_workflow(
                    MemoryConsolidationWorkflow.run,
                    args=[ConsolidationWorkflowInput(user_id=user_id)],
                    id=f"consolidate-child-{user_id}-{workflow.info().workflow_id}",
                )
                consolidations_succeeded = consolidation_result.consolidations_succeeded
                memories_merged = consolidation_result.memories_merged
                user_errors.extend(consolidation_result.errors)
            except Exception as e:
                workflow.logger.error(f"Failed consolidation for user {user_id}: {e}")
                user_errors.append(f"Consolidation failed: {str(e)}")

            user_results[str(user_id)] = GardenerResult(
                promotions_succeeded=promotions_succeeded,
                expirations_succeeded=expirations_succeeded,
                consolidations_succeeded=consolidations_succeeded,
                memories_merged=memories_merged,
                errors=user_errors,
            )

            total_promotions += promotions_succeeded
            total_expirations += expirations_succeeded
            total_consolidations += consolidations_succeeded
            total_memories_merged += memories_merged
            errors.extend(user_errors)

        workflow.logger.info(
            f"Gardening complete: {len(user_ids)} users, "
            f"{total_promotions} promotions, {total_expirations} expirations, "
            f"{total_consolidations} consolidations, {total_memories_merged} merged"
        )

        return ScheduledGardenerResult(
            users_processed=len(user_ids),
            total_promotions=total_promotions,
            total_expirations=total_expirations,
            total_consolidations=total_consolidations,
            total_memories_merged=total_memories_merged,
            user_results=user_results,
            errors=errors,
        )


# =============================================================================
# Decision Analysis Workflows
# =============================================================================


@dataclass
class AnalyzeOutcomesWorkflowInput:
    """Input for the outcome analysis workflow."""

    user_id: UUID | None = None  # None = process all active users
    days_back: int = 7
    apply_adjustments: bool = True
    boost_threshold: float = 0.7  # Memories above this get boosted
    penalize_threshold: float = 0.3  # Memories below this get penalized
    adjustment_magnitude: float = 0.05  # Max salience adjustment


@dataclass
class AnalyzeOutcomesWorkflowResult:
    """Result of the outcome analysis workflow."""

    success: bool
    total_decisions_analyzed: int
    success_rate: float
    adjustments_applied: int
    top_memories: list[str]  # String UUIDs for serialization
    underperforming_memories: list[str]
    errors: list[str]


@workflow.defn
class AnalyzeOutcomesWorkflow:
    """Workflow that analyzes decision outcomes and adjusts memory salience.

    This workflow runs periodically to:
    1. Analyze decision outcomes over a time period
    2. Identify top-performing and underperforming memories
    3. Adjust salience based on outcome contribution
    4. Track decision patterns for insights

    The outcome analysis helps the system learn from experience:
    - Memories that consistently lead to good decisions gain salience
    - Memories that lead to poor decisions lose salience
    - This creates a feedback loop that improves retrieval quality

    Example usage:
        # Analyze for a specific user
        handle = await client.start_workflow(
            AnalyzeOutcomesWorkflow.run,
            AnalyzeOutcomesWorkflowInput(user_id=user_id, days_back=7),
            id=f"analyze-outcomes-{user_id}",
            task_queue="gardener",
        )

        # Analyze for all active users
        await client.start_workflow(
            AnalyzeOutcomesWorkflow.run,
            AnalyzeOutcomesWorkflowInput(user_id=None),  # All users
            id="analyze-outcomes-all",
            task_queue="gardener",
        )
    """

    @workflow.run
    async def run(self, input: AnalyzeOutcomesWorkflowInput) -> AnalyzeOutcomesWorkflowResult:
        """Execute the outcome analysis workflow."""

        # If user_id is None, discover and process all active users
        if input.user_id is None:
            return await self._run_for_all_users(input)

        return await self._run_for_single_user(input)

    async def _run_for_all_users(
        self, input: AnalyzeOutcomesWorkflowInput
    ) -> AnalyzeOutcomesWorkflowResult:
        """Run outcome analysis for all active users."""
        workflow.logger.info("Discovering active users for outcome analysis...")

        try:
            user_ids = await workflow.execute_activity(
                get_active_user_ids,
                args=[30, 1000],  # Last 30 days, max 1000 users
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to discover users: {e}")
            return AnalyzeOutcomesWorkflowResult(
                success=False,
                total_decisions_analyzed=0,
                success_rate=0.0,
                adjustments_applied=0,
                top_memories=[],
                underperforming_memories=[],
                errors=[f"Failed to discover users: {str(e)}"],
            )

        if not user_ids:
            workflow.logger.info("No active users found")
            return AnalyzeOutcomesWorkflowResult(
                success=True,
                total_decisions_analyzed=0,
                success_rate=0.0,
                adjustments_applied=0,
                top_memories=[],
                underperforming_memories=[],
                errors=[],
            )

        workflow.logger.info(f"Analyzing outcomes for {len(user_ids)} users")

        # Aggregate results across all users
        total_decisions = 0
        total_adjustments = 0
        all_top_memories = []
        all_underperforming = []
        all_errors = []
        success_rates = []

        for user_id in user_ids:
            user_input = AnalyzeOutcomesWorkflowInput(
                user_id=user_id,
                days_back=input.days_back,
                apply_adjustments=input.apply_adjustments,
                boost_threshold=input.boost_threshold,
                penalize_threshold=input.penalize_threshold,
                adjustment_magnitude=input.adjustment_magnitude,
            )
            result = await self._run_for_single_user(user_input)

            total_decisions += result.total_decisions_analyzed
            total_adjustments += result.adjustments_applied
            all_top_memories.extend(result.top_memories[:5])
            all_underperforming.extend(result.underperforming_memories[:5])
            all_errors.extend(result.errors)
            if result.total_decisions_analyzed > 0:
                success_rates.append(result.success_rate)

        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0

        workflow.logger.info(
            f"Outcome analysis complete: {len(user_ids)} users, "
            f"{total_decisions} decisions, {avg_success_rate:.1%} avg success rate"
        )

        return AnalyzeOutcomesWorkflowResult(
            success=len(all_errors) == 0,
            total_decisions_analyzed=total_decisions,
            success_rate=avg_success_rate,
            adjustments_applied=total_adjustments,
            top_memories=all_top_memories[:20],
            underperforming_memories=all_underperforming[:20],
            errors=all_errors,
        )

    async def _run_for_single_user(
        self, input: AnalyzeOutcomesWorkflowInput
    ) -> AnalyzeOutcomesWorkflowResult:
        """Run outcome analysis for a single user."""
        workflow.logger.info(
            f"Starting outcome analysis for user {input.user_id}, days_back={input.days_back}"
        )

        errors = []

        # Step 1: Analyze outcomes
        try:
            analysis_result: OutcomeAnalysisResult = await workflow.execute_activity(
                analyze_user_outcomes,
                args=[input.user_id, input.days_back],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to analyze outcomes: {e}")
            return AnalyzeOutcomesWorkflowResult(
                success=False,
                total_decisions_analyzed=0,
                success_rate=0.0,
                adjustments_applied=0,
                top_memories=[],
                underperforming_memories=[],
                errors=[f"Failed to analyze outcomes: {str(e)}"],
            )

        if not analysis_result.success or not analysis_result.analysis:
            return AnalyzeOutcomesWorkflowResult(
                success=False,
                total_decisions_analyzed=0,
                success_rate=0.0,
                adjustments_applied=0,
                top_memories=[],
                underperforming_memories=[],
                errors=[analysis_result.error or "Unknown analysis error"],
            )

        analysis = analysis_result.analysis
        workflow.logger.info(
            f"Analysis complete: {analysis.total_decisions} decisions, "
            f"{analysis.success_rate:.1%} success rate"
        )

        # If no decisions or adjustments disabled, return early
        if analysis.total_decisions == 0 or not input.apply_adjustments:
            return AnalyzeOutcomesWorkflowResult(
                success=True,
                total_decisions_analyzed=analysis.total_decisions,
                success_rate=analysis.success_rate,
                adjustments_applied=0,
                top_memories=[str(m[0]) for m in analysis.top_performing_memories],
                underperforming_memories=[str(m[0]) for m in analysis.underperforming_memories],
                errors=[],
            )

        # Step 2: Calculate salience adjustments
        adjustments = []

        # Boost top performers
        for memory_id, contribution in analysis.top_performing_memories:
            if contribution >= input.boost_threshold:
                adjustment = min(input.adjustment_magnitude, contribution * 0.1)
                adjustments.append(
                    SalienceAdjustmentBatch(
                        memory_id=memory_id,
                        adjustment=adjustment,
                        reason=f"Top performer: {contribution:.2f} contribution",
                    )
                )

        # Penalize underperformers
        for memory_id, contribution in analysis.underperforming_memories:
            if contribution <= input.penalize_threshold:
                adjustment = -min(input.adjustment_magnitude, (1 - contribution) * 0.1)
                adjustments.append(
                    SalienceAdjustmentBatch(
                        memory_id=memory_id,
                        adjustment=adjustment,
                        reason=f"Underperformer: {contribution:.2f} contribution",
                    )
                )

        # Step 3: Apply adjustments
        adjustments_applied = 0
        if adjustments:
            try:
                adjustments_applied = await workflow.execute_activity(
                    apply_salience_adjustments,
                    args=[adjustments],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )
            except Exception as e:
                workflow.logger.error(f"Failed to apply adjustments: {e}")
                errors.append(f"Failed to apply adjustments: {str(e)}")

        workflow.logger.info(
            f"Outcome analysis complete: {adjustments_applied} adjustments applied"
        )

        return AnalyzeOutcomesWorkflowResult(
            success=True,
            total_decisions_analyzed=analysis.total_decisions,
            success_rate=analysis.success_rate,
            adjustments_applied=adjustments_applied,
            top_memories=[str(m[0]) for m in analysis.top_performing_memories],
            underperforming_memories=[str(m[0]) for m in analysis.underperforming_memories],
            errors=errors,
        )


@dataclass
class CalibrateConfidenceWorkflowInput:
    """Input for the confidence calibration workflow."""

    user_id: UUID | None = None  # None = process all active users
    days_back: int = 30
    bucket_count: int = 10
    min_samples: int = 50  # Minimum samples for reliable calibration
    apply_calibration: bool = True


@dataclass
class CalibrateConfidenceWorkflowResult:
    """Result of the confidence calibration workflow."""

    success: bool
    samples_analyzed: int
    calibration_error: float
    adjustment_factor: float
    bucket_count: int
    calibration_applied: bool
    errors: list[str]


@workflow.defn
class CalibrateConfidenceWorkflow:
    """Workflow that calibrates confidence predictions based on outcomes.

    This workflow runs periodically to:
    1. Analyze historical prediction confidence vs actual outcomes
    2. Compute Expected Calibration Error (ECE)
    3. Determine adjustment factor for future predictions
    4. Update user calibration settings

    Confidence calibration ensures the system's confidence scores
    match actual accuracy. If predictions with 80% confidence are
    only correct 60% of the time, we're overconfident and need
    to adjust.

    Example usage:
        # Start a single calibration run
        handle = await client.start_workflow(
            CalibrateConfidenceWorkflow.run,
            CalibrateConfidenceWorkflowInput(user_id=user_id, days_back=30),
            id=f"calibrate-confidence-{user_id}",
            task_queue="gardener",
        )

        # Or schedule monthly calibration
        await client.start_workflow(
            CalibrateConfidenceWorkflow.run,
            CalibrateConfidenceWorkflowInput(user_id=user_id),
            id=f"calibrate-confidence-scheduled-{user_id}",
            task_queue="gardener",
            cron_schedule="0 0 1 * *",  # First day of each month
        )
    """

    @workflow.run
    async def run(
        self, input: CalibrateConfidenceWorkflowInput
    ) -> CalibrateConfidenceWorkflowResult:
        """Execute the confidence calibration workflow."""

        workflow.logger.info(
            f"Starting confidence calibration for user {input.user_id}, days_back={input.days_back}"
        )

        errors = []

        # Step 1: Analyze calibration
        try:
            calibration: CalibrationResult = await workflow.execute_activity(
                analyze_confidence_calibration,
                args=[input.user_id, input.days_back, input.bucket_count],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to analyze calibration: {e}")
            return CalibrateConfidenceWorkflowResult(
                success=False,
                samples_analyzed=0,
                calibration_error=0.0,
                adjustment_factor=1.0,
                bucket_count=0,
                calibration_applied=False,
                errors=[f"Failed to analyze calibration: {str(e)}"],
            )

        if not calibration.success:
            return CalibrateConfidenceWorkflowResult(
                success=False,
                samples_analyzed=0,
                calibration_error=0.0,
                adjustment_factor=1.0,
                bucket_count=0,
                calibration_applied=False,
                errors=[calibration.error or "Unknown calibration error"],
            )

        # Calculate total samples
        total_samples = sum(b.total_predictions for b in calibration.buckets)

        workflow.logger.info(
            f"Calibration analysis complete: {total_samples} samples, "
            f"ECE={calibration.overall_calibration_error:.3f}"
        )

        # Check minimum samples
        if total_samples < input.min_samples:
            workflow.logger.info(
                f"Insufficient samples ({total_samples} < {input.min_samples}), "
                "skipping calibration update"
            )
            return CalibrateConfidenceWorkflowResult(
                success=True,
                samples_analyzed=total_samples,
                calibration_error=calibration.overall_calibration_error,
                adjustment_factor=calibration.adjustment_factor,
                bucket_count=len(calibration.buckets),
                calibration_applied=False,
                errors=["Insufficient samples for calibration"],
            )

        # Step 2: Apply calibration if enabled
        calibration_applied = False
        if input.apply_calibration:
            try:
                result = await workflow.execute_activity(
                    update_calibration_settings,
                    args=[
                        input.user_id,
                        calibration.adjustment_factor,
                        total_samples,
                        calibration.overall_calibration_error,
                    ],
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )
                calibration_applied = result
            except Exception as e:
                workflow.logger.error(f"Failed to update calibration: {e}")
                errors.append(f"Failed to update calibration: {str(e)}")

        workflow.logger.info(
            f"Calibration complete: adjustment_factor={calibration.adjustment_factor:.3f}, "
            f"applied={calibration_applied}"
        )

        return CalibrateConfidenceWorkflowResult(
            success=True,
            samples_analyzed=total_samples,
            calibration_error=calibration.overall_calibration_error,
            adjustment_factor=calibration.adjustment_factor,
            bucket_count=len(calibration.buckets),
            calibration_applied=calibration_applied,
            errors=errors,
        )


@dataclass
class ExtractPatternsWorkflowInput:
    """Input for the pattern extraction workflow."""

    user_id: UUID | None = None  # None = process all active users
    days_back: int = 30
    min_outcome_quality: float = 0.6
    sanitize_for_federation: bool = True
    min_users_for_federation: int = 10
    min_observations_for_federation: int = 100


@dataclass
class ExtractPatternsWorkflowResult:
    """Result of the pattern extraction workflow."""

    success: bool
    decisions_analyzed: int
    patterns_extracted: int
    patterns_sanitized: int
    patterns_stored: int
    errors: list[str]


@workflow.defn
class ExtractPatternsWorkflow:
    """Workflow that extracts patterns from successful decisions.

    This workflow runs periodically to:
    1. Find successful decisions from the time period
    2. Extract patterns from decision outcomes
    3. Sanitize patterns with differential privacy
    4. Store patterns for federation (if thresholds met)

    Pattern extraction enables collective learning:
    - Identifies what decision strategies work well
    - Abstracts patterns to categories (no PII)
    - Applies differential privacy before sharing
    - Enables cross-user pattern matching

    Example usage:
        # Start a single extraction run
        handle = await client.start_workflow(
            ExtractPatternsWorkflow.run,
            ExtractPatternsWorkflowInput(user_id=user_id, days_back=30),
            id=f"extract-patterns-{user_id}",
            task_queue="gardener",
        )

        # Or schedule monthly extraction
        await client.start_workflow(
            ExtractPatternsWorkflow.run,
            ExtractPatternsWorkflowInput(user_id=user_id),
            id=f"extract-patterns-scheduled-{user_id}",
            task_queue="gardener",
            cron_schedule="0 2 1 * *",  # First day of each month at 2 AM
        )
    """

    @workflow.run
    async def run(self, input: ExtractPatternsWorkflowInput) -> ExtractPatternsWorkflowResult:
        """Execute the pattern extraction workflow."""

        workflow.logger.info(
            f"Starting pattern extraction for user {input.user_id}, days_back={input.days_back}"
        )

        errors = []

        # Step 1: Find successful decisions
        try:
            decisions: list[DecisionPatternData] = await workflow.execute_activity(
                find_successful_decisions,
                args=[input.user_id, input.days_back, input.min_outcome_quality],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to find decisions: {e}")
            return ExtractPatternsWorkflowResult(
                success=False,
                decisions_analyzed=0,
                patterns_extracted=0,
                patterns_sanitized=0,
                patterns_stored=0,
                errors=[f"Failed to find decisions: {str(e)}"],
            )

        decisions_count = len(decisions)
        workflow.logger.info(f"Found {decisions_count} successful decisions")

        if decisions_count == 0:
            return ExtractPatternsWorkflowResult(
                success=True,
                decisions_analyzed=0,
                patterns_extracted=0,
                patterns_sanitized=0,
                patterns_stored=0,
                errors=[],
            )

        # Step 2: Extract patterns
        try:
            extraction: PatternExtractionResult = await workflow.execute_activity(
                extract_patterns_from_decisions,
                args=[decisions],
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(minutes=1),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to extract patterns: {e}")
            return ExtractPatternsWorkflowResult(
                success=False,
                decisions_analyzed=decisions_count,
                patterns_extracted=0,
                patterns_sanitized=0,
                patterns_stored=0,
                errors=[f"Failed to extract patterns: {str(e)}"],
            )

        if not extraction.success:
            return ExtractPatternsWorkflowResult(
                success=False,
                decisions_analyzed=decisions_count,
                patterns_extracted=0,
                patterns_sanitized=0,
                patterns_stored=0,
                errors=[extraction.error or "Unknown extraction error"],
            )

        workflow.logger.info(f"Extracted {extraction.patterns_found} patterns")

        if extraction.patterns_found == 0:
            return ExtractPatternsWorkflowResult(
                success=True,
                decisions_analyzed=decisions_count,
                patterns_extracted=0,
                patterns_sanitized=0,
                patterns_stored=0,
                errors=[],
            )

        # Step 3: Sanitize patterns (if enabled)
        patterns_sanitized = 0
        patterns_stored = 0

        if input.sanitize_for_federation:
            try:
                sanitization: SanitizationResult = await workflow.execute_activity(
                    sanitize_patterns,
                    args=[
                        extraction.patterns,
                        input.min_users_for_federation,
                        input.min_observations_for_federation,
                    ],
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(minutes=1),
                        maximum_attempts=3,
                    ),
                )

                if not sanitization.success:
                    errors.append(sanitization.error or "Sanitization failed")
                else:
                    patterns_sanitized = sanitization.patterns_sanitized

                    # Step 4: Store sanitized patterns
                    if sanitization.patterns:
                        try:
                            patterns_stored = await workflow.execute_activity(
                                store_federated_patterns,
                                args=[sanitization.patterns],
                                start_to_close_timeout=timedelta(minutes=5),
                                retry_policy=RetryPolicy(
                                    initial_interval=timedelta(seconds=1),
                                    maximum_interval=timedelta(seconds=30),
                                    maximum_attempts=3,
                                ),
                            )
                        except Exception as e:
                            workflow.logger.error(f"Failed to store patterns: {e}")
                            errors.append(f"Failed to store patterns: {str(e)}")

            except Exception as e:
                workflow.logger.error(f"Failed to sanitize patterns: {e}")
                errors.append(f"Failed to sanitize patterns: {str(e)}")

        workflow.logger.info(
            f"Pattern extraction complete: {extraction.patterns_found} extracted, "
            f"{patterns_sanitized} sanitized, {patterns_stored} stored"
        )

        return ExtractPatternsWorkflowResult(
            success=True,
            decisions_analyzed=decisions_count,
            patterns_extracted=extraction.patterns_found,
            patterns_sanitized=patterns_sanitized,
            patterns_stored=patterns_stored,
            errors=errors,
        )


# =============================================================================
# Reindex Embeddings Workflow
# =============================================================================


@dataclass
class ReindexEmbeddingsWorkflowInput:
    """Input for the reindex embeddings workflow."""

    user_id: UUID | None = None  # None = reindex all users
    include_existing: bool = False  # If True, re-embed even if embedding exists
    batch_size: int = 100  # Memories per batch
    max_batches: int = 100  # Maximum batches to process


@dataclass
class ReindexEmbeddingsWorkflowResult:
    """Result of the reindex embeddings workflow."""

    success: bool
    total_memories: int = 0
    memories_processed: int = 0
    memories_updated: int = 0
    memories_failed: int = 0
    batches_completed: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@workflow.defn
class ReindexEmbeddingsWorkflow:
    """Workflow that reindexes memory embeddings.

    This workflow is used when:
    1. Upgrading to a new embedding model
    2. Backfilling embeddings for memories created before embeddings were added
    3. Recovering from embedding generation failures

    The workflow processes memories in batches to:
    - Avoid overwhelming the embedding API
    - Enable progress tracking
    - Allow for graceful handling of failures
    """

    @workflow.run
    async def run(
        self,
        input: ReindexEmbeddingsWorkflowInput,
    ) -> ReindexEmbeddingsWorkflowResult:
        """Execute the reindex embeddings workflow.

        Steps:
        1. Count total memories needing reindex
        2. Process memories in batches:
           a. Find batch of memories
           b. Generate embeddings for batch
           c. Update memories with new embeddings
        3. Return summary of results

        Args:
            input: Workflow configuration

        Returns:
            ReindexEmbeddingsWorkflowResult with statistics
        """
        workflow.logger.info(
            f"Starting reindex workflow (user={input.user_id}, "
            f"include_existing={input.include_existing})"
        )

        errors = []
        total_memories = 0
        memories_processed = 0
        memories_updated = 0
        memories_failed = 0
        batches_completed = 0

        # Step 1: Count total memories needing reindex
        try:
            total_memories = await workflow.execute_activity(
                count_memories_for_reindex,
                args=[input.user_id, input.include_existing],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=30),
                    maximum_attempts=3,
                ),
            )
        except Exception as e:
            workflow.logger.error(f"Failed to count memories: {e}")
            return ReindexEmbeddingsWorkflowResult(
                success=False,
                errors=[f"Failed to count memories: {str(e)}"],
            )

        if total_memories == 0:
            workflow.logger.info("No memories need reindexing")
            return ReindexEmbeddingsWorkflowResult(
                success=True,
                total_memories=0,
            )

        workflow.logger.info(f"Found {total_memories} memories to reindex")

        # Step 2: Process in batches
        offset = 0
        while batches_completed < input.max_batches:
            # Step 2a: Find batch of memories
            try:
                candidates: list[ReindexCandidate] = await workflow.execute_activity(
                    find_memories_for_reindex,
                    args=[
                        input.user_id,
                        input.include_existing,
                        input.batch_size,
                        offset,
                    ],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )
            except Exception as e:
                workflow.logger.error(f"Failed to find memories for batch {batches_completed}: {e}")
                errors.append(f"Batch {batches_completed} find failed: {str(e)}")
                break

            if not candidates:
                workflow.logger.info("No more memories to process")
                break

            # Step 2b: Generate embeddings for batch
            try:
                batch: ReindexBatch = await workflow.execute_activity(
                    generate_embeddings_for_batch,
                    args=[candidates],
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=2),
                        maximum_interval=timedelta(minutes=1),
                        maximum_attempts=3,
                    ),
                )
            except Exception as e:
                workflow.logger.error(
                    f"Failed to generate embeddings for batch {batches_completed}: {e}"
                )
                errors.append(f"Batch {batches_completed} embedding failed: {str(e)}")
                offset += input.batch_size
                batches_completed += 1
                continue

            if batch.errors:
                errors.extend(batch.errors)

            # Step 2c: Update memories with new embeddings
            try:
                result: ReindexResult = await workflow.execute_activity(
                    update_memory_embeddings,
                    args=[batch],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=30),
                        maximum_attempts=3,
                    ),
                )

                memories_processed += len(candidates)
                memories_updated += result.memories_updated
                memories_failed += result.memories_failed

                if result.error:
                    errors.append(result.error)

            except Exception as e:
                workflow.logger.error(
                    f"Failed to update embeddings for batch {batches_completed}: {e}"
                )
                errors.append(f"Batch {batches_completed} update failed: {str(e)}")
                memories_processed += len(candidates)
                memories_failed += len(candidates)

            offset += input.batch_size
            batches_completed += 1

            workflow.logger.info(
                f"Batch {batches_completed} complete: "
                f"{memories_updated}/{memories_processed} updated, {memories_failed} failed"
            )

        workflow.logger.info(
            f"Reindex complete: {memories_updated}/{memories_processed} updated, "
            f"{memories_failed} failed, {batches_completed} batches"
        )

        return ReindexEmbeddingsWorkflowResult(
            success=memories_failed == 0 and len(errors) == 0,
            total_memories=total_memories,
            memories_processed=memories_processed,
            memories_updated=memories_updated,
            memories_failed=memories_failed,
            batches_completed=batches_completed,
            errors=errors,
        )
