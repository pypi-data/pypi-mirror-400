"""Tests for Temporal gardener workflows.

These tests prove that the Temporal workflow orchestration works correctly.
Uses Temporal's testing framework with mocked activities.
"""

import pytest
from datetime import UTC, datetime, timedelta
from uuid import uuid4, UUID

from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from mind.core.memory.models import TemporalLevel
from mind.workers.gardener.workflows import (
    MemoryPromotionWorkflow,
    MemoryExpirationWorkflow,
    MemoryConsolidationWorkflow,
    PromotionWorkflowInput,
    PromotionWorkflowResult,
    ExpirationWorkflowInput,
    ExpirationWorkflowResult,
    ConsolidationWorkflowInput,
    ConsolidationWorkflowResult,
)
from mind.workers.gardener.activities import (
    PromotionCandidate,
    PromotionResult,
    ExpirationCandidate,
    ExpirationResult,
    ConsolidationCandidate,
    ConsolidationResult,
)


# Mock activities for testing (replaces real database/event operations)
@activity.defn(name="find_promotion_candidates")
async def mock_find_candidates(
    user_id, batch_size: int = 100
) -> list[PromotionCandidate]:
    """Mock activity that returns test candidates."""
    return [
        PromotionCandidate(
            memory_id=uuid4(),
            user_id=user_id,
            current_level=TemporalLevel.IMMEDIATE,
            target_level=TemporalLevel.SITUATIONAL,
            score=0.85,
            reason="Test candidate - high retrieval count",
        ),
        PromotionCandidate(
            memory_id=uuid4(),
            user_id=user_id,
            current_level=TemporalLevel.SITUATIONAL,
            target_level=TemporalLevel.SEASONAL,
            score=0.72,
            reason="Test candidate - stable over time",
        ),
    ]


@activity.defn(name="promote_memory")
async def mock_promote_memory(candidate: PromotionCandidate) -> PromotionResult:
    """Mock activity that simulates memory promotion."""
    return PromotionResult(
        memory_id=candidate.memory_id,
        success=True,
        from_level=candidate.current_level,
        to_level=candidate.target_level,
    )


@activity.defn(name="notify_promotion")
async def mock_notify_promotion(result: PromotionResult, user_id) -> bool:
    """Mock activity that simulates event publishing."""
    return True


class TestMemoryPromotionWorkflow:
    """Tests for the MemoryPromotionWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_finds_and_promotes_candidates(self):
        """Workflow should find candidates and promote them successfully."""
        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-test",
                workflows=[MemoryPromotionWorkflow],
                activities=[
                    mock_find_candidates,
                    mock_promote_memory,
                    mock_notify_promotion,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryPromotionWorkflow.run,
                    PromotionWorkflowInput(user_id=user_id, batch_size=10),
                    id=f"test-promotion-{user_id}",
                    task_queue="gardener-test",
                )

                assert isinstance(result, PromotionWorkflowResult)
                assert result.candidates_found == 2
                assert result.promotions_attempted == 2
                assert result.promotions_succeeded == 2
                assert result.promotions_failed == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_no_candidates(self):
        """Workflow should handle empty candidate list gracefully."""

        @activity.defn(name="find_promotion_candidates")
        async def mock_no_candidates(user_id, batch_size: int = 100) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-test-empty",
                workflows=[MemoryPromotionWorkflow],
                activities=[mock_no_candidates],
            ):
                result = await env.client.execute_workflow(
                    MemoryPromotionWorkflow.run,
                    PromotionWorkflowInput(user_id=user_id),
                    id=f"test-promotion-empty-{user_id}",
                    task_queue="gardener-test-empty",
                )

                assert result.candidates_found == 0
                assert result.promotions_attempted == 0
                assert result.promotions_succeeded == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_promotion_failure(self):
        """Workflow should handle failed promotions and continue."""

        call_count = 0

        @activity.defn(name="find_promotion_candidates")
        async def mock_find_two(user_id, batch_size: int = 100) -> list:
            return [
                PromotionCandidate(
                    memory_id=uuid4(),
                    user_id=user_id,
                    current_level=TemporalLevel.IMMEDIATE,
                    target_level=TemporalLevel.SITUATIONAL,
                    score=0.85,
                    reason="Will fail",
                ),
                PromotionCandidate(
                    memory_id=uuid4(),
                    user_id=user_id,
                    current_level=TemporalLevel.IMMEDIATE,
                    target_level=TemporalLevel.SITUATIONAL,
                    score=0.72,
                    reason="Will succeed",
                ),
            ]

        @activity.defn(name="promote_memory")
        async def mock_partial_failure(candidate: PromotionCandidate) -> PromotionResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return PromotionResult(
                    memory_id=candidate.memory_id,
                    success=False,
                    error="Simulated failure",
                )
            return PromotionResult(
                memory_id=candidate.memory_id,
                success=True,
                from_level=candidate.current_level,
                to_level=candidate.target_level,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-test-partial",
                workflows=[MemoryPromotionWorkflow],
                activities=[
                    mock_find_two,
                    mock_partial_failure,
                    mock_notify_promotion,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryPromotionWorkflow.run,
                    PromotionWorkflowInput(user_id=user_id),
                    id=f"test-promotion-partial-{user_id}",
                    task_queue="gardener-test-partial",
                )

                assert result.candidates_found == 2
                assert result.promotions_attempted == 2
                assert result.promotions_succeeded == 1
                assert result.promotions_failed == 1
                assert len(result.errors) == 1
                assert "Simulated failure" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_respects_max_promotions_limit(self):
        """Workflow should not process more than max_promotions_per_run."""

        @activity.defn(name="find_promotion_candidates")
        async def mock_find_many(user_id, batch_size: int = 100) -> list:
            return [
                PromotionCandidate(
                    memory_id=uuid4(),
                    user_id=user_id,
                    current_level=TemporalLevel.IMMEDIATE,
                    target_level=TemporalLevel.SITUATIONAL,
                    score=0.8,
                    reason=f"Candidate {i}",
                )
                for i in range(10)
            ]

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-test-limit",
                workflows=[MemoryPromotionWorkflow],
                activities=[
                    mock_find_many,
                    mock_promote_memory,
                    mock_notify_promotion,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryPromotionWorkflow.run,
                    PromotionWorkflowInput(
                        user_id=user_id,
                        max_promotions_per_run=3,  # Limit to 3
                    ),
                    id=f"test-promotion-limit-{user_id}",
                    task_queue="gardener-test-limit",
                )

                assert result.candidates_found == 10
                assert result.promotions_attempted == 3  # Limited
                assert result.promotions_succeeded == 3


class TestPromotionCandidate:
    """Tests for the PromotionCandidate data class."""

    def test_candidate_creation(self):
        """PromotionCandidate should store all required fields."""
        user_id = uuid4()
        memory_id = uuid4()

        candidate = PromotionCandidate(
            memory_id=memory_id,
            user_id=user_id,
            current_level=TemporalLevel.IMMEDIATE,
            target_level=TemporalLevel.SITUATIONAL,
            score=0.85,
            reason="High retrieval count",
        )

        assert candidate.memory_id == memory_id
        assert candidate.user_id == user_id
        assert candidate.current_level == TemporalLevel.IMMEDIATE
        assert candidate.target_level == TemporalLevel.SITUATIONAL
        assert candidate.score == 0.85


class TestPromotionResult:
    """Tests for the PromotionResult data class."""

    def test_successful_result(self):
        """PromotionResult should correctly represent success."""
        memory_id = uuid4()

        result = PromotionResult(
            memory_id=memory_id,
            success=True,
            from_level=TemporalLevel.IMMEDIATE,
            to_level=TemporalLevel.SITUATIONAL,
        )

        assert result.success is True
        assert result.error is None
        assert result.from_level == TemporalLevel.IMMEDIATE
        assert result.to_level == TemporalLevel.SITUATIONAL

    def test_failed_result(self):
        """PromotionResult should correctly represent failure."""
        memory_id = uuid4()

        result = PromotionResult(
            memory_id=memory_id,
            success=False,
            error="Memory not found",
        )

        assert result.success is False
        assert result.error == "Memory not found"
        assert result.from_level is None
        assert result.to_level is None


# Mock activities for expiration workflow testing
@activity.defn(name="find_expired_memories")
async def mock_find_expired(
    user_id, batch_size: int = 100
) -> list[ExpirationCandidate]:
    """Mock activity that returns test expiration candidates."""
    return [
        ExpirationCandidate(
            memory_id=uuid4(),
            user_id=user_id,
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_until=datetime.now(UTC) - timedelta(hours=1),
            reason="valid_until_passed",
        ),
        ExpirationCandidate(
            memory_id=uuid4(),
            user_id=user_id,
            temporal_level=TemporalLevel.SITUATIONAL,
            valid_until=datetime.now(UTC) - timedelta(days=1),
            reason="low_salience",
        ),
    ]


@activity.defn(name="archive_memory")
async def mock_archive_memory(candidate: ExpirationCandidate) -> ExpirationResult:
    """Mock activity that simulates memory archival."""
    return ExpirationResult(
        memory_id=candidate.memory_id,
        success=True,
        archived=True,
    )


@activity.defn(name="notify_expiration")
async def mock_notify_expiration(result: ExpirationResult, candidate: ExpirationCandidate) -> bool:
    """Mock activity that simulates expiration event publishing."""
    return True


class TestMemoryExpirationWorkflow:
    """Tests for the MemoryExpirationWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_finds_and_archives_expired(self):
        """Workflow should find expired memories and archive them."""
        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-expire-test",
                workflows=[MemoryExpirationWorkflow],
                activities=[
                    mock_find_expired,
                    mock_archive_memory,
                    mock_notify_expiration,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryExpirationWorkflow.run,
                    ExpirationWorkflowInput(user_id=user_id, batch_size=10),
                    id=f"test-expiration-{user_id}",
                    task_queue="gardener-expire-test",
                )

                assert isinstance(result, ExpirationWorkflowResult)
                assert result.candidates_found == 2
                assert result.expirations_attempted == 2
                assert result.expirations_succeeded == 2
                assert result.expirations_failed == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_no_expired(self):
        """Workflow should handle empty expired list gracefully."""

        @activity.defn(name="find_expired_memories")
        async def mock_no_expired(user_id, batch_size: int = 100) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-expire-empty",
                workflows=[MemoryExpirationWorkflow],
                activities=[mock_no_expired],
            ):
                result = await env.client.execute_workflow(
                    MemoryExpirationWorkflow.run,
                    ExpirationWorkflowInput(user_id=user_id),
                    id=f"test-expiration-empty-{user_id}",
                    task_queue="gardener-expire-empty",
                )

                assert result.candidates_found == 0
                assert result.expirations_attempted == 0
                assert result.expirations_succeeded == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_archival_failure(self):
        """Workflow should handle failed archivals and continue."""

        call_count = 0

        @activity.defn(name="find_expired_memories")
        async def mock_find_two_expired(user_id, batch_size: int = 100) -> list:
            return [
                ExpirationCandidate(
                    memory_id=uuid4(),
                    user_id=user_id,
                    temporal_level=TemporalLevel.IMMEDIATE,
                    valid_until=datetime.now(UTC) - timedelta(hours=1),
                    reason="will_fail",
                ),
                ExpirationCandidate(
                    memory_id=uuid4(),
                    user_id=user_id,
                    temporal_level=TemporalLevel.IMMEDIATE,
                    valid_until=datetime.now(UTC) - timedelta(hours=2),
                    reason="will_succeed",
                ),
            ]

        @activity.defn(name="archive_memory")
        async def mock_partial_archive_failure(candidate: ExpirationCandidate) -> ExpirationResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return ExpirationResult(
                    memory_id=candidate.memory_id,
                    success=False,
                    error="Simulated archival failure",
                )
            return ExpirationResult(
                memory_id=candidate.memory_id,
                success=True,
                archived=True,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-expire-partial",
                workflows=[MemoryExpirationWorkflow],
                activities=[
                    mock_find_two_expired,
                    mock_partial_archive_failure,
                    mock_notify_expiration,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryExpirationWorkflow.run,
                    ExpirationWorkflowInput(user_id=user_id),
                    id=f"test-expiration-partial-{user_id}",
                    task_queue="gardener-expire-partial",
                )

                assert result.candidates_found == 2
                assert result.expirations_attempted == 2
                assert result.expirations_succeeded == 1
                assert result.expirations_failed == 1
                assert len(result.errors) == 1
                assert "Simulated archival failure" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_respects_max_expirations_limit(self):
        """Workflow should not process more than max_expirations_per_run."""

        @activity.defn(name="find_expired_memories")
        async def mock_find_many_expired(user_id, batch_size: int = 100) -> list:
            return [
                ExpirationCandidate(
                    memory_id=uuid4(),
                    user_id=user_id,
                    temporal_level=TemporalLevel.IMMEDIATE,
                    valid_until=datetime.now(UTC) - timedelta(hours=i),
                    reason=f"expired_{i}",
                )
                for i in range(10)
            ]

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-expire-limit",
                workflows=[MemoryExpirationWorkflow],
                activities=[
                    mock_find_many_expired,
                    mock_archive_memory,
                    mock_notify_expiration,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryExpirationWorkflow.run,
                    ExpirationWorkflowInput(
                        user_id=user_id,
                        max_expirations_per_run=3,  # Limit to 3
                    ),
                    id=f"test-expiration-limit-{user_id}",
                    task_queue="gardener-expire-limit",
                )

                assert result.candidates_found == 10
                assert result.expirations_attempted == 3  # Limited
                assert result.expirations_succeeded == 3


class TestExpirationCandidate:
    """Tests for the ExpirationCandidate data class."""

    def test_candidate_creation(self):
        """ExpirationCandidate should store all required fields."""
        user_id = uuid4()
        memory_id = uuid4()
        valid_until = datetime.now(UTC) - timedelta(hours=1)

        candidate = ExpirationCandidate(
            memory_id=memory_id,
            user_id=user_id,
            temporal_level=TemporalLevel.IMMEDIATE,
            valid_until=valid_until,
            reason="valid_until_passed",
        )

        assert candidate.memory_id == memory_id
        assert candidate.user_id == user_id
        assert candidate.temporal_level == TemporalLevel.IMMEDIATE
        assert candidate.valid_until == valid_until
        assert candidate.reason == "valid_until_passed"


class TestExpirationResult:
    """Tests for the ExpirationResult data class."""

    def test_successful_result(self):
        """ExpirationResult should correctly represent success."""
        memory_id = uuid4()

        result = ExpirationResult(
            memory_id=memory_id,
            success=True,
            archived=True,
        )

        assert result.success is True
        assert result.archived is True
        assert result.error is None

    def test_failed_result(self):
        """ExpirationResult should correctly represent failure."""
        memory_id = uuid4()

        result = ExpirationResult(
            memory_id=memory_id,
            success=False,
            error="Memory not found",
        )

        assert result.success is False
        assert result.archived is False
        assert result.error == "Memory not found"


# =============================================================================
# Memory Consolidation Workflow Tests
# =============================================================================


# Mock activities for consolidation workflow testing
@activity.defn(name="find_consolidation_candidates")
async def mock_find_consolidation(
    user_id, batch_size: int = 50
) -> list[ConsolidationCandidate]:
    """Mock activity that returns test consolidation candidates."""
    return [
        ConsolidationCandidate(
            primary_memory_id=uuid4(),
            similar_memory_ids=[uuid4(), uuid4()],
            user_id=user_id,
            temporal_level=TemporalLevel.IMMEDIATE,
            similarity_scores=[0.92, 0.88],
            reason="Found 2 similar memories (avg similarity: 0.90)",
        ),
        ConsolidationCandidate(
            primary_memory_id=uuid4(),
            similar_memory_ids=[uuid4()],
            user_id=user_id,
            temporal_level=TemporalLevel.SITUATIONAL,
            similarity_scores=[0.95],
            reason="Found 1 similar memory (avg similarity: 0.95)",
        ),
    ]


@activity.defn(name="consolidate_memories")
async def mock_consolidate_memories(candidate: ConsolidationCandidate) -> ConsolidationResult:
    """Mock activity that simulates memory consolidation."""
    return ConsolidationResult(
        consolidated_memory_id=uuid4(),
        source_memory_ids=[candidate.primary_memory_id] + candidate.similar_memory_ids,
        success=True,
        memories_merged=len(candidate.similar_memory_ids) + 1,
    )


@activity.defn(name="notify_consolidation")
async def mock_notify_consolidation(result: ConsolidationResult, user_id) -> bool:
    """Mock activity that simulates consolidation event publishing."""
    return True


class TestMemoryConsolidationWorkflow:
    """Tests for the MemoryConsolidationWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_finds_and_consolidates_candidates(self):
        """Workflow should find candidates and consolidate them successfully."""
        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-consolidate-test",
                workflows=[MemoryConsolidationWorkflow],
                activities=[
                    mock_find_consolidation,
                    mock_consolidate_memories,
                    mock_notify_consolidation,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryConsolidationWorkflow.run,
                    ConsolidationWorkflowInput(user_id=user_id, batch_size=10),
                    id=f"test-consolidation-{user_id}",
                    task_queue="gardener-consolidate-test",
                )

                assert isinstance(result, ConsolidationWorkflowResult)
                assert result.candidates_found == 2
                assert result.consolidations_attempted == 2
                assert result.consolidations_succeeded == 2
                assert result.consolidations_failed == 0
                # First group: 3 memories merged, second group: 2 memories merged
                assert result.memories_merged == 5
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_no_candidates(self):
        """Workflow should handle empty candidate list gracefully."""

        @activity.defn(name="find_consolidation_candidates")
        async def mock_no_consolidation(user_id, batch_size: int = 50) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-consolidate-empty",
                workflows=[MemoryConsolidationWorkflow],
                activities=[mock_no_consolidation],
            ):
                result = await env.client.execute_workflow(
                    MemoryConsolidationWorkflow.run,
                    ConsolidationWorkflowInput(user_id=user_id),
                    id=f"test-consolidation-empty-{user_id}",
                    task_queue="gardener-consolidate-empty",
                )

                assert result.candidates_found == 0
                assert result.consolidations_attempted == 0
                assert result.consolidations_succeeded == 0
                assert result.memories_merged == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_consolidation_failure(self):
        """Workflow should handle failed consolidations and continue."""

        call_count = 0

        @activity.defn(name="find_consolidation_candidates")
        async def mock_find_two_groups(user_id, batch_size: int = 50) -> list:
            return [
                ConsolidationCandidate(
                    primary_memory_id=uuid4(),
                    similar_memory_ids=[uuid4()],
                    user_id=user_id,
                    temporal_level=TemporalLevel.IMMEDIATE,
                    similarity_scores=[0.90],
                    reason="Will fail",
                ),
                ConsolidationCandidate(
                    primary_memory_id=uuid4(),
                    similar_memory_ids=[uuid4()],
                    user_id=user_id,
                    temporal_level=TemporalLevel.IMMEDIATE,
                    similarity_scores=[0.92],
                    reason="Will succeed",
                ),
            ]

        @activity.defn(name="consolidate_memories")
        async def mock_partial_consolidation_failure(candidate: ConsolidationCandidate) -> ConsolidationResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return ConsolidationResult(
                    consolidated_memory_id=None,
                    source_memory_ids=[candidate.primary_memory_id] + candidate.similar_memory_ids,
                    success=False,
                    error="Simulated consolidation failure",
                )
            return ConsolidationResult(
                consolidated_memory_id=uuid4(),
                source_memory_ids=[candidate.primary_memory_id] + candidate.similar_memory_ids,
                success=True,
                memories_merged=2,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-consolidate-partial",
                workflows=[MemoryConsolidationWorkflow],
                activities=[
                    mock_find_two_groups,
                    mock_partial_consolidation_failure,
                    mock_notify_consolidation,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryConsolidationWorkflow.run,
                    ConsolidationWorkflowInput(user_id=user_id),
                    id=f"test-consolidation-partial-{user_id}",
                    task_queue="gardener-consolidate-partial",
                )

                assert result.candidates_found == 2
                assert result.consolidations_attempted == 2
                assert result.consolidations_succeeded == 1
                assert result.consolidations_failed == 1
                assert result.memories_merged == 2
                assert len(result.errors) == 1
                assert "Simulated consolidation failure" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_respects_max_consolidations_limit(self):
        """Workflow should not process more than max_consolidations_per_run."""

        @activity.defn(name="find_consolidation_candidates")
        async def mock_find_many_groups(user_id, batch_size: int = 50) -> list:
            return [
                ConsolidationCandidate(
                    primary_memory_id=uuid4(),
                    similar_memory_ids=[uuid4()],
                    user_id=user_id,
                    temporal_level=TemporalLevel.IMMEDIATE,
                    similarity_scores=[0.90],
                    reason=f"Group {i}",
                )
                for i in range(10)
            ]

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-consolidate-limit",
                workflows=[MemoryConsolidationWorkflow],
                activities=[
                    mock_find_many_groups,
                    mock_consolidate_memories,
                    mock_notify_consolidation,
                ],
            ):
                result = await env.client.execute_workflow(
                    MemoryConsolidationWorkflow.run,
                    ConsolidationWorkflowInput(
                        user_id=user_id,
                        max_consolidations_per_run=3,  # Limit to 3
                    ),
                    id=f"test-consolidation-limit-{user_id}",
                    task_queue="gardener-consolidate-limit",
                )

                assert result.candidates_found == 10
                assert result.consolidations_attempted == 3  # Limited
                assert result.consolidations_succeeded == 3


class TestConsolidationCandidate:
    """Tests for the ConsolidationCandidate data class."""

    def test_candidate_creation(self):
        """ConsolidationCandidate should store all required fields."""
        user_id = uuid4()
        primary_id = uuid4()
        similar_ids = [uuid4(), uuid4()]

        candidate = ConsolidationCandidate(
            primary_memory_id=primary_id,
            similar_memory_ids=similar_ids,
            user_id=user_id,
            temporal_level=TemporalLevel.IMMEDIATE,
            similarity_scores=[0.92, 0.88],
            reason="Found 2 similar memories",
        )

        assert candidate.primary_memory_id == primary_id
        assert candidate.similar_memory_ids == similar_ids
        assert candidate.user_id == user_id
        assert candidate.temporal_level == TemporalLevel.IMMEDIATE
        assert len(candidate.similarity_scores) == 2
        assert candidate.similarity_scores[0] == 0.92


class TestConsolidationResult:
    """Tests for the ConsolidationResult data class."""

    def test_successful_result(self):
        """ConsolidationResult should correctly represent success."""
        consolidated_id = uuid4()
        source_ids = [uuid4(), uuid4(), uuid4()]

        result = ConsolidationResult(
            consolidated_memory_id=consolidated_id,
            source_memory_ids=source_ids,
            success=True,
            memories_merged=3,
        )

        assert result.success is True
        assert result.consolidated_memory_id == consolidated_id
        assert result.memories_merged == 3
        assert result.error is None

    def test_failed_result(self):
        """ConsolidationResult should correctly represent failure."""
        source_ids = [uuid4(), uuid4()]

        result = ConsolidationResult(
            consolidated_memory_id=None,
            source_memory_ids=source_ids,
            success=False,
            error="Not enough valid memories",
        )

        assert result.success is False
        assert result.consolidated_memory_id is None
        assert result.memories_merged == 0
        assert result.error == "Not enough valid memories"


# =============================================================================
# Outcome Analysis Workflow Tests
# =============================================================================


from mind.workers.gardener.workflows import (
    AnalyzeOutcomesWorkflow,
    AnalyzeOutcomesWorkflowInput,
    AnalyzeOutcomesWorkflowResult,
)
from mind.workers.gardener.activities import (
    OutcomeAnalysis,
    OutcomeAnalysisResult,
    SalienceAdjustmentBatch,
)


# Mock activities for outcome analysis workflow testing
@activity.defn(name="analyze_user_outcomes")
async def mock_analyze_outcomes(
    user_id, days_back: int = 7
) -> OutcomeAnalysisResult:
    """Mock activity that returns test outcome analysis."""
    return OutcomeAnalysisResult(
        success=True,
        analysis=OutcomeAnalysis(
            user_id=user_id,
            period_start=datetime.now(UTC) - timedelta(days=days_back),
            period_end=datetime.now(UTC),
            total_decisions=25,
            positive_outcomes=18,
            negative_outcomes=4,
            neutral_outcomes=3,
            success_rate=0.72,
            top_performing_memories=[
                (uuid4(), 0.85),
                (uuid4(), 0.78),
            ],
            underperforming_memories=[
                (uuid4(), 0.22),
                (uuid4(), 0.15),
            ],
            decision_type_breakdown={
                "recommendation": {"total": 15, "positive": 12, "negative": 2},
                "classification": {"total": 10, "positive": 6, "negative": 2},
            },
        ),
    )


@activity.defn(name="apply_salience_adjustments")
async def mock_apply_adjustments(
    adjustments: list[SalienceAdjustmentBatch],
) -> int:
    """Mock activity that simulates salience adjustments."""
    return len(adjustments)


class TestAnalyzeOutcomesWorkflow:
    """Tests for the AnalyzeOutcomesWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_analyzes_and_applies_adjustments(self):
        """Workflow should analyze outcomes and apply salience adjustments."""
        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-analyze-test",
                workflows=[AnalyzeOutcomesWorkflow],
                activities=[
                    mock_analyze_outcomes,
                    mock_apply_adjustments,
                ],
            ):
                result = await env.client.execute_workflow(
                    AnalyzeOutcomesWorkflow.run,
                    AnalyzeOutcomesWorkflowInput(user_id=user_id, days_back=7),
                    id=f"test-analyze-{user_id}",
                    task_queue="gardener-analyze-test",
                )

                assert isinstance(result, AnalyzeOutcomesWorkflowResult)
                assert result.success is True
                assert result.total_decisions_analyzed == 25
                assert result.success_rate == 0.72
                assert len(result.top_memories) == 2
                assert len(result.underperforming_memories) == 2
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_no_decisions(self):
        """Workflow should handle empty decision history gracefully."""

        @activity.defn(name="analyze_user_outcomes")
        async def mock_no_decisions(user_id, days_back: int = 7) -> OutcomeAnalysisResult:
            return OutcomeAnalysisResult(
                success=True,
                analysis=OutcomeAnalysis(
                    user_id=user_id,
                    period_start=datetime.now(UTC) - timedelta(days=days_back),
                    period_end=datetime.now(UTC),
                    total_decisions=0,
                    positive_outcomes=0,
                    negative_outcomes=0,
                    neutral_outcomes=0,
                    success_rate=0.0,
                    top_performing_memories=[],
                    underperforming_memories=[],
                    decision_type_breakdown={},
                ),
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-analyze-empty",
                workflows=[AnalyzeOutcomesWorkflow],
                activities=[mock_no_decisions],
            ):
                result = await env.client.execute_workflow(
                    AnalyzeOutcomesWorkflow.run,
                    AnalyzeOutcomesWorkflowInput(user_id=user_id),
                    id=f"test-analyze-empty-{user_id}",
                    task_queue="gardener-analyze-empty",
                )

                assert result.success is True
                assert result.total_decisions_analyzed == 0
                assert result.success_rate == 0.0
                assert result.adjustments_applied == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_analysis_failure(self):
        """Workflow should handle analysis failures gracefully."""

        @activity.defn(name="analyze_user_outcomes")
        async def mock_failed_analysis(user_id, days_back: int = 7) -> OutcomeAnalysisResult:
            return OutcomeAnalysisResult(
                success=False,
                error="Database connection failed",
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-analyze-fail",
                workflows=[AnalyzeOutcomesWorkflow],
                activities=[mock_failed_analysis],
            ):
                result = await env.client.execute_workflow(
                    AnalyzeOutcomesWorkflow.run,
                    AnalyzeOutcomesWorkflowInput(user_id=user_id),
                    id=f"test-analyze-fail-{user_id}",
                    task_queue="gardener-analyze-fail",
                )

                assert result.success is False
                assert result.total_decisions_analyzed == 0
                assert len(result.errors) == 1
                assert "Database connection failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_respects_apply_adjustments_flag(self):
        """Workflow should skip adjustments when apply_adjustments is False."""

        adjustments_applied = False

        @activity.defn(name="apply_salience_adjustments")
        async def mock_track_adjustments(adjustments: list) -> int:
            nonlocal adjustments_applied
            adjustments_applied = True
            return len(adjustments)

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-analyze-no-adjust",
                workflows=[AnalyzeOutcomesWorkflow],
                activities=[
                    mock_analyze_outcomes,
                    mock_track_adjustments,
                ],
            ):
                result = await env.client.execute_workflow(
                    AnalyzeOutcomesWorkflow.run,
                    AnalyzeOutcomesWorkflowInput(
                        user_id=user_id,
                        apply_adjustments=False,  # Skip adjustments
                    ),
                    id=f"test-analyze-no-adjust-{user_id}",
                    task_queue="gardener-analyze-no-adjust",
                )

                assert result.success is True
                assert result.adjustments_applied == 0
                assert not adjustments_applied  # Activity not called

    @pytest.mark.asyncio
    async def test_workflow_applies_adjustments_based_on_thresholds(self):
        """Workflow should only adjust memories that exceed thresholds."""

        applied_adjustments = []

        @activity.defn(name="analyze_user_outcomes")
        async def mock_mixed_performers(user_id, days_back: int = 7) -> OutcomeAnalysisResult:
            return OutcomeAnalysisResult(
                success=True,
                analysis=OutcomeAnalysis(
                    user_id=user_id,
                    period_start=datetime.now(UTC) - timedelta(days=days_back),
                    period_end=datetime.now(UTC),
                    total_decisions=20,
                    positive_outcomes=12,
                    negative_outcomes=5,
                    neutral_outcomes=3,
                    success_rate=0.6,
                    top_performing_memories=[
                        (uuid4(), 0.85),  # Above boost threshold (0.7)
                        (uuid4(), 0.65),  # Below boost threshold
                    ],
                    underperforming_memories=[
                        (uuid4(), 0.45),  # Above penalize threshold (0.3)
                        (uuid4(), 0.20),  # Below penalize threshold
                    ],
                    decision_type_breakdown={},
                ),
            )

        @activity.defn(name="apply_salience_adjustments")
        async def mock_capture_adjustments(adjustments: list[SalienceAdjustmentBatch]) -> int:
            nonlocal applied_adjustments
            applied_adjustments = adjustments
            return len(adjustments)

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-analyze-thresholds",
                workflows=[AnalyzeOutcomesWorkflow],
                activities=[
                    mock_mixed_performers,
                    mock_capture_adjustments,
                ],
            ):
                result = await env.client.execute_workflow(
                    AnalyzeOutcomesWorkflow.run,
                    AnalyzeOutcomesWorkflowInput(
                        user_id=user_id,
                        boost_threshold=0.7,
                        penalize_threshold=0.3,
                    ),
                    id=f"test-analyze-thresholds-{user_id}",
                    task_queue="gardener-analyze-thresholds",
                )

                assert result.success is True
                # Only 1 top performer above 0.7, only 1 underperformer below 0.3
                assert result.adjustments_applied == 2

    @pytest.mark.asyncio
    async def test_workflow_handles_adjustment_failure(self):
        """Workflow should handle adjustment failures gracefully."""

        @activity.defn(name="apply_salience_adjustments")
        async def mock_failed_adjustments(adjustments: list) -> int:
            raise Exception("Failed to update database")

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-analyze-adj-fail",
                workflows=[AnalyzeOutcomesWorkflow],
                activities=[
                    mock_analyze_outcomes,
                    mock_failed_adjustments,
                ],
            ):
                result = await env.client.execute_workflow(
                    AnalyzeOutcomesWorkflow.run,
                    AnalyzeOutcomesWorkflowInput(user_id=user_id),
                    id=f"test-analyze-adj-fail-{user_id}",
                    task_queue="gardener-analyze-adj-fail",
                )

                # Workflow should still succeed, but report adjustment error
                assert result.success is True
                assert result.total_decisions_analyzed == 25
                assert result.adjustments_applied == 0
                assert len(result.errors) == 1
                assert "Failed to apply adjustments" in result.errors[0]


class TestOutcomeAnalysis:
    """Tests for the OutcomeAnalysis data class."""

    def test_analysis_creation(self):
        """OutcomeAnalysis should store all required fields."""
        user_id = uuid4()
        now = datetime.now(UTC)
        period_start = now - timedelta(days=7)

        analysis = OutcomeAnalysis(
            user_id=user_id,
            period_start=period_start,
            period_end=now,
            total_decisions=100,
            positive_outcomes=70,
            negative_outcomes=20,
            neutral_outcomes=10,
            success_rate=0.70,
            top_performing_memories=[(uuid4(), 0.9)],
            underperforming_memories=[(uuid4(), 0.1)],
            decision_type_breakdown={"recommendation": {"total": 50, "positive": 40}},
        )

        assert analysis.user_id == user_id
        assert analysis.total_decisions == 100
        assert analysis.success_rate == 0.70
        assert len(analysis.top_performing_memories) == 1
        assert len(analysis.underperforming_memories) == 1


class TestSalienceAdjustmentBatch:
    """Tests for the SalienceAdjustmentBatch data class."""

    def test_adjustment_creation(self):
        """SalienceAdjustmentBatch should store all required fields."""
        memory_id = uuid4()

        adjustment = SalienceAdjustmentBatch(
            memory_id=memory_id,
            adjustment=0.05,
            reason="Top performer",
        )

        assert adjustment.memory_id == memory_id
        assert adjustment.adjustment == 0.05
        assert adjustment.reason == "Top performer"

    def test_negative_adjustment(self):
        """SalienceAdjustmentBatch should allow negative adjustments."""
        memory_id = uuid4()

        adjustment = SalienceAdjustmentBatch(
            memory_id=memory_id,
            adjustment=-0.03,
            reason="Underperformer",
        )

        assert adjustment.adjustment == -0.03


# =============================================================================
# Confidence Calibration Workflow Tests
# =============================================================================


from mind.workers.gardener.workflows import (
    CalibrateConfidenceWorkflow,
    CalibrateConfidenceWorkflowInput,
    CalibrateConfidenceWorkflowResult,
)
from mind.workers.gardener.activities import (
    CalibrationBucket,
    CalibrationResult,
)


# Mock activities for calibration workflow testing
@activity.defn(name="analyze_confidence_calibration")
async def mock_analyze_calibration(
    user_id, days_back: int = 30, bucket_count: int = 10
) -> CalibrationResult:
    """Mock activity that returns test calibration analysis."""
    return CalibrationResult(
        success=True,
        buckets=[
            CalibrationBucket(
                confidence_min=0.6,
                confidence_max=0.7,
                total_predictions=30,
                correct_predictions=20,
                expected_accuracy=0.65,
                actual_accuracy=0.67,
            ),
            CalibrationBucket(
                confidence_min=0.7,
                confidence_max=0.8,
                total_predictions=40,
                correct_predictions=32,
                expected_accuracy=0.75,
                actual_accuracy=0.80,
            ),
            CalibrationBucket(
                confidence_min=0.8,
                confidence_max=0.9,
                total_predictions=30,
                correct_predictions=25,
                expected_accuracy=0.85,
                actual_accuracy=0.83,
            ),
        ],
        overall_calibration_error=0.05,
        adjustment_factor=1.02,
    )


@activity.defn(name="update_calibration_settings")
async def mock_update_calibration(
    user_id, adjustment_factor: float, sample_count: int, calibration_error: float
) -> bool:
    """Mock activity that simulates calibration update."""
    return True


class TestCalibrateConfidenceWorkflow:
    """Tests for the CalibrateConfidenceWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_analyzes_and_applies_calibration(self):
        """Workflow should analyze calibration and update settings."""
        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-calibrate-test",
                workflows=[CalibrateConfidenceWorkflow],
                activities=[
                    mock_analyze_calibration,
                    mock_update_calibration,
                ],
            ):
                result = await env.client.execute_workflow(
                    CalibrateConfidenceWorkflow.run,
                    CalibrateConfidenceWorkflowInput(user_id=user_id, days_back=30),
                    id=f"test-calibrate-{user_id}",
                    task_queue="gardener-calibrate-test",
                )

                assert isinstance(result, CalibrateConfidenceWorkflowResult)
                assert result.success is True
                assert result.samples_analyzed == 100  # 30+40+30
                assert result.calibration_error == 0.05
                assert result.adjustment_factor == 1.02
                assert result.bucket_count == 3
                assert result.calibration_applied is True
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_no_data(self):
        """Workflow should handle empty calibration data gracefully."""

        @activity.defn(name="analyze_confidence_calibration")
        async def mock_no_data(user_id, days_back: int = 30, bucket_count: int = 10) -> CalibrationResult:
            return CalibrationResult(
                success=True,
                buckets=[],
                overall_calibration_error=0.0,
                adjustment_factor=1.0,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-calibrate-empty",
                workflows=[CalibrateConfidenceWorkflow],
                activities=[mock_no_data],
            ):
                result = await env.client.execute_workflow(
                    CalibrateConfidenceWorkflow.run,
                    CalibrateConfidenceWorkflowInput(user_id=user_id),
                    id=f"test-calibrate-empty-{user_id}",
                    task_queue="gardener-calibrate-empty",
                )

                assert result.success is True
                assert result.samples_analyzed == 0
                assert result.calibration_applied is False
                assert "Insufficient samples" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_handles_analysis_failure(self):
        """Workflow should handle analysis failures gracefully."""

        @activity.defn(name="analyze_confidence_calibration")
        async def mock_failed_analysis(user_id, days_back: int = 30, bucket_count: int = 10) -> CalibrationResult:
            return CalibrationResult(
                success=False,
                error="Database connection failed",
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-calibrate-fail",
                workflows=[CalibrateConfidenceWorkflow],
                activities=[mock_failed_analysis],
            ):
                result = await env.client.execute_workflow(
                    CalibrateConfidenceWorkflow.run,
                    CalibrateConfidenceWorkflowInput(user_id=user_id),
                    id=f"test-calibrate-fail-{user_id}",
                    task_queue="gardener-calibrate-fail",
                )

                assert result.success is False
                assert result.samples_analyzed == 0
                assert len(result.errors) == 1
                assert "Database connection failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_respects_apply_calibration_flag(self):
        """Workflow should skip calibration update when apply_calibration is False."""

        calibration_applied = False

        @activity.defn(name="update_calibration_settings")
        async def mock_track_calibration(user_id, adjustment_factor, sample_count, calibration_error) -> bool:
            nonlocal calibration_applied
            calibration_applied = True
            return True

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-calibrate-no-apply",
                workflows=[CalibrateConfidenceWorkflow],
                activities=[
                    mock_analyze_calibration,
                    mock_track_calibration,
                ],
            ):
                result = await env.client.execute_workflow(
                    CalibrateConfidenceWorkflow.run,
                    CalibrateConfidenceWorkflowInput(
                        user_id=user_id,
                        apply_calibration=False,  # Skip calibration update
                    ),
                    id=f"test-calibrate-no-apply-{user_id}",
                    task_queue="gardener-calibrate-no-apply",
                )

                assert result.success is True
                assert result.calibration_applied is False
                assert not calibration_applied  # Activity not called

    @pytest.mark.asyncio
    async def test_workflow_respects_min_samples(self):
        """Workflow should skip calibration when samples < min_samples."""

        @activity.defn(name="analyze_confidence_calibration")
        async def mock_few_samples(user_id, days_back: int = 30, bucket_count: int = 10) -> CalibrationResult:
            return CalibrationResult(
                success=True,
                buckets=[
                    CalibrationBucket(
                        confidence_min=0.7,
                        confidence_max=0.8,
                        total_predictions=20,  # Only 20 samples
                        correct_predictions=15,
                        expected_accuracy=0.75,
                        actual_accuracy=0.75,
                    ),
                ],
                overall_calibration_error=0.0,
                adjustment_factor=1.0,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-calibrate-few",
                workflows=[CalibrateConfidenceWorkflow],
                activities=[mock_few_samples],
            ):
                result = await env.client.execute_workflow(
                    CalibrateConfidenceWorkflow.run,
                    CalibrateConfidenceWorkflowInput(
                        user_id=user_id,
                        min_samples=50,  # Require 50 samples
                    ),
                    id=f"test-calibrate-few-{user_id}",
                    task_queue="gardener-calibrate-few",
                )

                assert result.success is True
                assert result.samples_analyzed == 20
                assert result.calibration_applied is False
                assert "Insufficient samples" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_handles_update_failure(self):
        """Workflow should handle update failures gracefully."""

        @activity.defn(name="update_calibration_settings")
        async def mock_failed_update(user_id, adjustment_factor, sample_count, calibration_error) -> bool:
            raise Exception("Failed to update settings")

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-calibrate-update-fail",
                workflows=[CalibrateConfidenceWorkflow],
                activities=[
                    mock_analyze_calibration,
                    mock_failed_update,
                ],
            ):
                result = await env.client.execute_workflow(
                    CalibrateConfidenceWorkflow.run,
                    CalibrateConfidenceWorkflowInput(user_id=user_id),
                    id=f"test-calibrate-update-fail-{user_id}",
                    task_queue="gardener-calibrate-update-fail",
                )

                # Workflow should still succeed, but report update error
                assert result.success is True
                assert result.samples_analyzed == 100
                assert result.calibration_applied is False
                assert len(result.errors) == 1
                assert "Failed to update calibration" in result.errors[0]


class TestCalibrationBucket:
    """Tests for the CalibrationBucket data class."""

    def test_bucket_creation(self):
        """CalibrationBucket should store all required fields."""
        bucket = CalibrationBucket(
            confidence_min=0.7,
            confidence_max=0.8,
            total_predictions=100,
            correct_predictions=75,
            expected_accuracy=0.75,
            actual_accuracy=0.75,
        )

        assert bucket.confidence_min == 0.7
        assert bucket.confidence_max == 0.8
        assert bucket.total_predictions == 100
        assert bucket.correct_predictions == 75
        assert bucket.expected_accuracy == 0.75
        assert bucket.actual_accuracy == 0.75


class TestCalibrationResult:
    """Tests for the CalibrationResult data class."""

    def test_successful_result(self):
        """CalibrationResult should correctly represent success."""
        result = CalibrationResult(
            success=True,
            buckets=[
                CalibrationBucket(0.7, 0.8, 100, 75, 0.75, 0.75)
            ],
            overall_calibration_error=0.02,
            adjustment_factor=1.05,
        )

        assert result.success is True
        assert len(result.buckets) == 1
        assert result.overall_calibration_error == 0.02
        assert result.adjustment_factor == 1.05
        assert result.error is None

    def test_failed_result(self):
        """CalibrationResult should correctly represent failure."""
        result = CalibrationResult(
            success=False,
            error="Database error",
        )

        assert result.success is False
        assert len(result.buckets) == 0
        assert result.error == "Database error"


# =============================================================================
# Pattern Extraction Workflow Tests
# =============================================================================


from mind.workers.gardener.workflows import (
    ExtractPatternsWorkflow,
    ExtractPatternsWorkflowInput,
    ExtractPatternsWorkflowResult,
)
from mind.workers.gardener.activities import (
    DecisionPatternData,
    ExtractedPattern,
    PatternExtractionResult,
    SanitizedPatternData,
    SanitizationResult,
)


# Mock activities for pattern extraction workflow testing
@activity.defn(name="find_successful_decisions")
async def mock_find_decisions(
    user_id, days_back: int = 30, min_outcome_quality: float = 0.6
) -> list[DecisionPatternData]:
    """Mock activity that returns test decision data."""
    return [
        DecisionPatternData(
            trace_id=uuid4(),
            user_id=user_id,
            decision_type="recommendation",
            outcome_quality=0.85,
            memory_contents=["User prefers detailed explanations", "User likes examples"],
            memory_ids=[uuid4(), uuid4()],
            created_at=datetime.now(UTC) - timedelta(days=5),
        ),
        DecisionPatternData(
            trace_id=uuid4(),
            user_id=user_id,
            decision_type="recommendation",
            outcome_quality=0.78,
            memory_contents=["User prefers step-by-step guides"],
            memory_ids=[uuid4()],
            created_at=datetime.now(UTC) - timedelta(days=3),
        ),
    ]


@activity.defn(name="extract_patterns_from_decisions")
async def mock_extract_patterns(
    decisions: list[DecisionPatternData],
) -> PatternExtractionResult:
    """Mock activity that returns extracted patterns."""
    return PatternExtractionResult(
        success=True,
        patterns_found=2,
        patterns=[
            ExtractedPattern(
                pattern_key="recommendation:preference",
                pattern_type="decision_strategy",
                trigger_category="recommendation",
                response_strategy="preference+context",
                observation_count=5,
                user_count=1,
                average_outcome=0.82,
                first_observed=datetime.now(UTC) - timedelta(days=10),
                last_observed=datetime.now(UTC),
            ),
            ExtractedPattern(
                pattern_key="recommendation:goal",
                pattern_type="decision_strategy",
                trigger_category="recommendation",
                response_strategy="goal+preference",
                observation_count=3,
                user_count=1,
                average_outcome=0.75,
                first_observed=datetime.now(UTC) - timedelta(days=5),
                last_observed=datetime.now(UTC),
            ),
        ],
    )


@activity.defn(name="sanitize_patterns")
async def mock_sanitize_patterns(
    patterns: list[ExtractedPattern], min_users: int = 10, min_observations: int = 100
) -> SanitizationResult:
    """Mock activity that returns sanitization results."""
    # By default, patterns don't meet federation thresholds (single user)
    return SanitizationResult(
        success=True,
        patterns_sanitized=0,
        patterns=[],
        patterns_rejected=len(patterns),
    )


@activity.defn(name="store_federated_patterns")
async def mock_store_patterns(
    patterns: list[SanitizedPatternData],
) -> int:
    """Mock activity that simulates pattern storage."""
    return len(patterns)


class TestExtractPatternsWorkflow:
    """Tests for the ExtractPatternsWorkflow."""

    @pytest.mark.asyncio
    async def test_workflow_extracts_patterns(self):
        """Workflow should find decisions and extract patterns."""
        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-test",
                workflows=[ExtractPatternsWorkflow],
                activities=[
                    mock_find_decisions,
                    mock_extract_patterns,
                    mock_sanitize_patterns,
                    mock_store_patterns,
                ],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(user_id=user_id, days_back=30),
                    id=f"test-patterns-{user_id}",
                    task_queue="gardener-patterns-test",
                )

                assert isinstance(result, ExtractPatternsWorkflowResult)
                assert result.success is True
                assert result.decisions_analyzed == 2
                assert result.patterns_extracted == 2
                # Patterns rejected because they don't meet federation thresholds
                assert result.patterns_sanitized == 0
                assert result.patterns_stored == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_no_decisions(self):
        """Workflow should handle empty decision history gracefully."""

        @activity.defn(name="find_successful_decisions")
        async def mock_no_decisions(user_id, days_back: int = 30, min_outcome_quality: float = 0.6) -> list:
            return []

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-empty",
                workflows=[ExtractPatternsWorkflow],
                activities=[mock_no_decisions],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(user_id=user_id),
                    id=f"test-patterns-empty-{user_id}",
                    task_queue="gardener-patterns-empty",
                )

                assert result.success is True
                assert result.decisions_analyzed == 0
                assert result.patterns_extracted == 0
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_extraction_failure(self):
        """Workflow should handle extraction failures gracefully."""

        @activity.defn(name="extract_patterns_from_decisions")
        async def mock_failed_extraction(decisions: list) -> PatternExtractionResult:
            return PatternExtractionResult(
                success=False,
                error="Pattern extraction failed",
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-fail",
                workflows=[ExtractPatternsWorkflow],
                activities=[
                    mock_find_decisions,
                    mock_failed_extraction,
                ],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(user_id=user_id),
                    id=f"test-patterns-fail-{user_id}",
                    task_queue="gardener-patterns-fail",
                )

                assert result.success is False
                assert result.decisions_analyzed == 2
                assert result.patterns_extracted == 0
                assert len(result.errors) == 1
                assert "Pattern extraction failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_respects_sanitize_flag(self):
        """Workflow should skip sanitization when flag is False."""

        sanitize_called = False

        @activity.defn(name="sanitize_patterns")
        async def mock_track_sanitize(patterns: list, min_users: int = 10, min_observations: int = 100) -> SanitizationResult:
            nonlocal sanitize_called
            sanitize_called = True
            return SanitizationResult(success=True, patterns_sanitized=0)

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-no-sanitize",
                workflows=[ExtractPatternsWorkflow],
                activities=[
                    mock_find_decisions,
                    mock_extract_patterns,
                    mock_track_sanitize,
                ],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(
                        user_id=user_id,
                        sanitize_for_federation=False,  # Skip sanitization
                    ),
                    id=f"test-patterns-no-sanitize-{user_id}",
                    task_queue="gardener-patterns-no-sanitize",
                )

                assert result.success is True
                assert result.patterns_extracted == 2
                assert result.patterns_sanitized == 0
                assert not sanitize_called  # Sanitization skipped

    @pytest.mark.asyncio
    async def test_workflow_stores_patterns_meeting_thresholds(self):
        """Workflow should store patterns that meet federation thresholds."""

        @activity.defn(name="sanitize_patterns")
        async def mock_successful_sanitize(patterns: list, min_users: int = 10, min_observations: int = 100) -> SanitizationResult:
            return SanitizationResult(
                success=True,
                patterns_sanitized=1,
                patterns=[
                    SanitizedPatternData(
                        pattern_id=uuid4(),
                        pattern_type="decision_strategy",
                        trigger_category="recommendation",
                        response_strategy="preference+context",
                        outcome_improvement=0.15,
                        confidence=0.85,
                        source_count=150,
                        user_count=15,
                        epsilon=0.1,
                    ),
                ],
                patterns_rejected=1,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-store",
                workflows=[ExtractPatternsWorkflow],
                activities=[
                    mock_find_decisions,
                    mock_extract_patterns,
                    mock_successful_sanitize,
                    mock_store_patterns,
                ],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(user_id=user_id),
                    id=f"test-patterns-store-{user_id}",
                    task_queue="gardener-patterns-store",
                )

                assert result.success is True
                assert result.patterns_extracted == 2
                assert result.patterns_sanitized == 1
                assert result.patterns_stored == 1
                assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_handles_sanitization_failure(self):
        """Workflow should handle sanitization failures gracefully."""

        @activity.defn(name="sanitize_patterns")
        async def mock_failed_sanitize(patterns: list, min_users: int = 10, min_observations: int = 100) -> SanitizationResult:
            return SanitizationResult(
                success=False,
                error="Sanitization failed",
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-sanitize-fail",
                workflows=[ExtractPatternsWorkflow],
                activities=[
                    mock_find_decisions,
                    mock_extract_patterns,
                    mock_failed_sanitize,
                ],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(user_id=user_id),
                    id=f"test-patterns-sanitize-fail-{user_id}",
                    task_queue="gardener-patterns-sanitize-fail",
                )

                # Workflow should still succeed, but report sanitization error
                assert result.success is True
                assert result.patterns_extracted == 2
                assert result.patterns_sanitized == 0
                assert len(result.errors) == 1
                assert "Sanitization failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_handles_storage_failure(self):
        """Workflow should handle storage failures gracefully."""

        @activity.defn(name="sanitize_patterns")
        async def mock_sanitize_one(patterns: list, min_users: int = 10, min_observations: int = 100) -> SanitizationResult:
            return SanitizationResult(
                success=True,
                patterns_sanitized=1,
                patterns=[
                    SanitizedPatternData(
                        pattern_id=uuid4(),
                        pattern_type="decision_strategy",
                        trigger_category="recommendation",
                        response_strategy="preference",
                        outcome_improvement=0.1,
                        confidence=0.8,
                        source_count=100,
                        user_count=10,
                        epsilon=0.1,
                    ),
                ],
            )

        @activity.defn(name="store_federated_patterns")
        async def mock_failed_store(patterns: list) -> int:
            raise Exception("Failed to store patterns")

        async with await WorkflowEnvironment.start_time_skipping() as env:
            user_id = uuid4()

            async with Worker(
                env.client,
                task_queue="gardener-patterns-store-fail",
                workflows=[ExtractPatternsWorkflow],
                activities=[
                    mock_find_decisions,
                    mock_extract_patterns,
                    mock_sanitize_one,
                    mock_failed_store,
                ],
            ):
                result = await env.client.execute_workflow(
                    ExtractPatternsWorkflow.run,
                    ExtractPatternsWorkflowInput(user_id=user_id),
                    id=f"test-patterns-store-fail-{user_id}",
                    task_queue="gardener-patterns-store-fail",
                )

                # Workflow should still succeed, but report storage error
                assert result.success is True
                assert result.patterns_extracted == 2
                assert result.patterns_sanitized == 1
                assert result.patterns_stored == 0
                assert len(result.errors) == 1
                assert "Failed to store patterns" in result.errors[0]


class TestDecisionPatternData:
    """Tests for the DecisionPatternData data class."""

    def test_data_creation(self):
        """DecisionPatternData should store all required fields."""
        user_id = uuid4()
        trace_id = uuid4()
        memory_ids = [uuid4(), uuid4()]
        now = datetime.now(UTC)

        data = DecisionPatternData(
            trace_id=trace_id,
            user_id=user_id,
            decision_type="recommendation",
            outcome_quality=0.85,
            memory_contents=["Content 1", "Content 2"],
            memory_ids=memory_ids,
            created_at=now,
        )

        assert data.trace_id == trace_id
        assert data.user_id == user_id
        assert data.decision_type == "recommendation"
        assert data.outcome_quality == 0.85
        assert len(data.memory_contents) == 2
        assert len(data.memory_ids) == 2


class TestExtractedPattern:
    """Tests for the ExtractedPattern data class."""

    def test_pattern_creation(self):
        """ExtractedPattern should store all required fields."""
        now = datetime.now(UTC)

        pattern = ExtractedPattern(
            pattern_key="recommendation:preference",
            pattern_type="decision_strategy",
            trigger_category="recommendation",
            response_strategy="preference+context",
            observation_count=10,
            user_count=3,
            average_outcome=0.78,
            first_observed=now - timedelta(days=7),
            last_observed=now,
        )

        assert pattern.pattern_key == "recommendation:preference"
        assert pattern.pattern_type == "decision_strategy"
        assert pattern.observation_count == 10
        assert pattern.user_count == 3
        assert pattern.average_outcome == 0.78


class TestSanitizedPatternData:
    """Tests for the SanitizedPatternData data class."""

    def test_pattern_creation(self):
        """SanitizedPatternData should store all required fields."""
        pattern_id = uuid4()

        pattern = SanitizedPatternData(
            pattern_id=pattern_id,
            pattern_type="decision_strategy",
            trigger_category="recommendation",
            response_strategy="preference+context",
            outcome_improvement=0.15,
            confidence=0.85,
            source_count=150,
            user_count=15,
            epsilon=0.1,
        )

        assert pattern.pattern_id == pattern_id
        assert pattern.pattern_type == "decision_strategy"
        assert pattern.outcome_improvement == 0.15
        assert pattern.confidence == 0.85
        assert pattern.epsilon == 0.1


# =============================================================================
# Reindex Embeddings Workflow Tests
# =============================================================================


from mind.workers.gardener.activities import (
    ReindexCandidate,
    ReindexBatch,
    ReindexResult,
    ReindexProgress,
)
from mind.workers.gardener.workflows import (
    ReindexEmbeddingsWorkflow,
    ReindexEmbeddingsWorkflowInput,
    ReindexEmbeddingsWorkflowResult,
)


class TestReindexEmbeddingsWorkflow:
    """Tests for the ReindexEmbeddingsWorkflow."""

    @pytest.mark.asyncio
    async def test_reindex_workflow_basic(self):
        """Workflow should process memories and update embeddings."""
        user_id = uuid4()
        memory_id = uuid4()
        task_queue = f"gardener-reindex-{uuid4()}"

        # Mock activities
        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            return 1

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            if offset == 0:
                return [
                    ReindexCandidate(
                        memory_id=memory_id,
                        user_id=user_id,
                        content="Test memory content",
                        has_embedding=False,
                    )
                ]
            return []

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate(candidates: list) -> ReindexBatch:
            # Temporal serializes dataclasses as dicts
            memory_ids = [UUID(c["memory_id"]) if isinstance(c, dict) else c.memory_id for c in candidates]
            return ReindexBatch(
                memory_ids=memory_ids,
                embeddings=[[0.1] * 1536 for _ in candidates],
            )

        @activity.defn(name="update_memory_embeddings")
        async def mock_update(batch) -> ReindexResult:
            # Temporal serializes dataclasses as dicts
            memory_ids = batch["memory_ids"] if isinstance(batch, dict) else batch.memory_ids
            return ReindexResult(
                success=True,
                memories_updated=len(memory_ids),
                memories_failed=0,
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate, mock_update],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(user_id=user_id),
                    id=f"test-reindex-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.success
                assert result.total_memories == 1
                assert result.memories_updated == 1
                assert result.memories_failed == 0
                assert result.batches_completed == 1

    @pytest.mark.asyncio
    async def test_reindex_workflow_no_memories(self):
        """Workflow should handle case with no memories to reindex."""
        user_id = uuid4()
        task_queue = f"gardener-reindex-empty-{uuid4()}"

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            return 0

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(user_id=user_id),
                    id=f"test-reindex-empty-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.success
                assert result.total_memories == 0
                assert result.memories_processed == 0

    @pytest.mark.asyncio
    async def test_reindex_workflow_multiple_batches(self):
        """Workflow should process multiple batches correctly."""
        user_id = uuid4()
        task_queue = f"gardener-reindex-multi-{uuid4()}"
        batch_count = [0]

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            return 5

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            if offset < 4:  # Return 2 batches of 2, then empty
                return [
                    ReindexCandidate(
                        memory_id=uuid4(),
                        user_id=user_id if user_id else uuid4(),
                        content=f"Memory {offset + i}",
                        has_embedding=False,
                    )
                    for i in range(min(2, 5 - offset))
                ]
            return []

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate(candidates: list) -> ReindexBatch:
            batch_count[0] += 1
            memory_ids = [UUID(c["memory_id"]) if isinstance(c, dict) else c.memory_id for c in candidates]
            return ReindexBatch(
                memory_ids=memory_ids,
                embeddings=[[0.1] * 1536 for _ in candidates],
            )

        @activity.defn(name="update_memory_embeddings")
        async def mock_update(batch) -> ReindexResult:
            memory_ids = batch["memory_ids"] if isinstance(batch, dict) else batch.memory_ids
            return ReindexResult(
                success=True,
                memories_updated=len(memory_ids),
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate, mock_update],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(
                        user_id=user_id,
                        batch_size=2,
                    ),
                    id=f"test-reindex-multi-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.success
                assert result.total_memories == 5
                assert result.batches_completed >= 2

    @pytest.mark.asyncio
    async def test_reindex_workflow_embedding_failure(self):
        """Workflow should handle embedding generation failures gracefully."""
        user_id = uuid4()
        task_queue = f"gardener-reindex-fail-{uuid4()}"

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            return 1

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            if offset == 0:
                return [
                    ReindexCandidate(
                        memory_id=uuid4(),
                        user_id=user_id,
                        content="Test",
                        has_embedding=False,
                    )
                ]
            return []

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate_fail(candidates: list) -> ReindexBatch:
            raise Exception("Embedding API error")

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate_fail],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(user_id=user_id),
                    id=f"test-reindex-fail-{uuid4()}",
                    task_queue=task_queue,
                )

                # Workflow continues but records the error
                assert len(result.errors) > 0
                assert "embedding failed" in result.errors[0].lower()

    @pytest.mark.asyncio
    async def test_reindex_workflow_partial_failure(self):
        """Workflow should track partial failures in update."""
        user_id = uuid4()
        task_queue = f"gardener-reindex-partial-{uuid4()}"

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            return 3

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            if offset == 0:
                return [
                    ReindexCandidate(
                        memory_id=uuid4(),
                        user_id=user_id if user_id else uuid4(),
                        content=f"Memory {i}",
                        has_embedding=False,
                    )
                    for i in range(3)
                ]
            return []

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate(candidates: list) -> ReindexBatch:
            memory_ids = [UUID(c["memory_id"]) if isinstance(c, dict) else c.memory_id for c in candidates]
            return ReindexBatch(
                memory_ids=memory_ids,
                embeddings=[[0.1] * 1536 for _ in candidates],
            )

        @activity.defn(name="update_memory_embeddings")
        async def mock_update_partial(batch) -> ReindexResult:
            return ReindexResult(
                success=False,
                memories_updated=2,
                memories_failed=1,
                error="One memory failed to update",
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate, mock_update_partial],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(user_id=user_id),
                    id=f"test-reindex-partial-{uuid4()}",
                    task_queue=task_queue,
                )

                assert not result.success  # Has failures
                assert result.memories_updated == 2
                assert result.memories_failed == 1
                assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_reindex_workflow_include_existing(self):
        """Workflow should support re-embedding existing embeddings."""
        user_id = uuid4()
        task_queue = f"gardener-reindex-existing-{uuid4()}"

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            # Return more when including existing
            return 5 if include_existing else 2

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            if offset == 0:
                count = 5 if include_existing else 2
                return [
                    ReindexCandidate(
                        memory_id=uuid4(),
                        user_id=user_id if user_id else uuid4(),
                        content=f"Memory {i}",
                        has_embedding=include_existing,
                    )
                    for i in range(count)
                ]
            return []

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate(candidates: list) -> ReindexBatch:
            memory_ids = [UUID(c["memory_id"]) if isinstance(c, dict) else c.memory_id for c in candidates]
            return ReindexBatch(
                memory_ids=memory_ids,
                embeddings=[[0.1] * 1536 for _ in candidates],
            )

        @activity.defn(name="update_memory_embeddings")
        async def mock_update(batch) -> ReindexResult:
            memory_ids = batch["memory_ids"] if isinstance(batch, dict) else batch.memory_ids
            return ReindexResult(
                success=True,
                memories_updated=len(memory_ids),
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate, mock_update],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(
                        user_id=user_id,
                        include_existing=True,
                    ),
                    id=f"test-reindex-existing-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.success
                assert result.total_memories == 5  # All memories
                assert result.memories_updated == 5

    @pytest.mark.asyncio
    async def test_reindex_workflow_max_batches_limit(self):
        """Workflow should respect max_batches limit."""
        user_id = uuid4()
        task_queue = f"gardener-reindex-limit-{uuid4()}"
        batches_processed = [0]

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            return 1000  # Many memories

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            # Always return memories
            return [
                ReindexCandidate(
                    memory_id=uuid4(),
                    user_id=user_id if user_id else uuid4(),
                    content=f"Memory {offset}",
                    has_embedding=False,
                )
            ]

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate(candidates: list) -> ReindexBatch:
            batches_processed[0] += 1
            memory_ids = [UUID(c["memory_id"]) if isinstance(c, dict) else c.memory_id for c in candidates]
            return ReindexBatch(
                memory_ids=memory_ids,
                embeddings=[[0.1] * 1536 for _ in candidates],
            )

        @activity.defn(name="update_memory_embeddings")
        async def mock_update(batch) -> ReindexResult:
            memory_ids = batch["memory_ids"] if isinstance(batch, dict) else batch.memory_ids
            return ReindexResult(
                success=True,
                memories_updated=len(memory_ids),
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate, mock_update],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(
                        user_id=user_id,
                        max_batches=3,  # Limit to 3 batches
                    ),
                    id=f"test-reindex-limit-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.batches_completed == 3
                assert batches_processed[0] == 3

    @pytest.mark.asyncio
    async def test_reindex_workflow_all_users(self):
        """Workflow should support reindexing all users."""
        task_queue = f"gardener-reindex-all-{uuid4()}"

        @activity.defn(name="count_memories_for_reindex")
        async def mock_count(user_id, include_existing) -> int:
            # user_id should be None for all users
            assert user_id is None
            return 10

        @activity.defn(name="find_memories_for_reindex")
        async def mock_find(user_id, include_existing, batch_size, offset) -> list:
            assert user_id is None
            if offset == 0:
                # Return memories from multiple users
                return [
                    ReindexCandidate(
                        memory_id=uuid4(),
                        user_id=uuid4(),  # Different users
                        content=f"Memory {i}",
                        has_embedding=False,
                    )
                    for i in range(3)
                ]
            return []

        @activity.defn(name="generate_embeddings_for_batch")
        async def mock_generate(candidates: list) -> ReindexBatch:
            memory_ids = [UUID(c["memory_id"]) if isinstance(c, dict) else c.memory_id for c in candidates]
            return ReindexBatch(
                memory_ids=memory_ids,
                embeddings=[[0.1] * 1536 for _ in candidates],
            )

        @activity.defn(name="update_memory_embeddings")
        async def mock_update(batch) -> ReindexResult:
            memory_ids = batch["memory_ids"] if isinstance(batch, dict) else batch.memory_ids
            return ReindexResult(
                success=True,
                memories_updated=len(memory_ids),
            )

        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue=task_queue,
                workflows=[ReindexEmbeddingsWorkflow],
                activities=[mock_count, mock_find, mock_generate, mock_update],
            ):
                result = await env.client.execute_workflow(
                    ReindexEmbeddingsWorkflow.run,
                    ReindexEmbeddingsWorkflowInput(
                        user_id=None,  # All users
                    ),
                    id=f"test-reindex-all-{uuid4()}",
                    task_queue=task_queue,
                )

                assert result.success
                assert result.total_memories == 10


class TestReindexCandidate:
    """Tests for the ReindexCandidate data class."""

    def test_candidate_creation(self):
        """ReindexCandidate should store all required fields."""
        memory_id = uuid4()
        user_id = uuid4()

        candidate = ReindexCandidate(
            memory_id=memory_id,
            user_id=user_id,
            content="Test memory content",
            has_embedding=False,
        )

        assert candidate.memory_id == memory_id
        assert candidate.user_id == user_id
        assert candidate.content == "Test memory content"
        assert candidate.has_embedding is False


class TestReindexBatch:
    """Tests for the ReindexBatch data class."""

    def test_batch_creation(self):
        """ReindexBatch should store memory IDs and embeddings."""
        memory_ids = [uuid4(), uuid4()]
        embeddings = [[0.1] * 1536, [0.2] * 1536]

        batch = ReindexBatch(
            memory_ids=memory_ids,
            embeddings=embeddings,
        )

        assert batch.memory_ids == memory_ids
        assert batch.embeddings == embeddings
        assert batch.errors == []

    def test_batch_with_errors(self):
        """ReindexBatch should track errors."""
        batch = ReindexBatch(
            memory_ids=[uuid4()],
            embeddings=[[0.1] * 1536],
            errors=["Error 1", "Error 2"],
        )

        assert len(batch.errors) == 2


class TestReindexResult:
    """Tests for the ReindexResult data class."""

    def test_result_success(self):
        """ReindexResult should track success."""
        result = ReindexResult(
            success=True,
            memories_updated=10,
            memories_failed=0,
        )

        assert result.success
        assert result.memories_updated == 10
        assert result.memories_failed == 0
        assert result.error is None

    def test_result_failure(self):
        """ReindexResult should track failures."""
        result = ReindexResult(
            success=False,
            memories_updated=5,
            memories_failed=5,
            error="Some memories failed",
        )

        assert not result.success
        assert result.memories_updated == 5
        assert result.memories_failed == 5
        assert result.error == "Some memories failed"
