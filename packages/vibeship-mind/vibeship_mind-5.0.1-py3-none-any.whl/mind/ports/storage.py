"""Storage port interfaces for memories and decisions.

These ports abstract the persistence layer, allowing different
implementations for Standard (PostgreSQL) and Enterprise tiers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..core.memory.models import Memory, TemporalLevel
from ..core.decision.models import DecisionTrace, Outcome, SalienceUpdate


class IMemoryStorage(ABC):
    """Port for memory persistence operations.

    Implementations:
        - PostgresMemoryStorage (Standard/Enterprise)
    """

    @abstractmethod
    async def store(self, memory: Memory) -> Memory:
        """Store a memory, returning it with any server-assigned fields.

        Args:
            memory: The memory to store

        Returns:
            The stored memory with memory_id assigned
        """
        pass

    @abstractmethod
    async def get(self, memory_id: UUID) -> Optional[Memory]:
        """Retrieve a memory by ID.

        Args:
            memory_id: The memory's unique identifier

        Returns:
            The memory if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
        temporal_level: Optional[TemporalLevel] = None,
        min_salience: float = 0.0,
        valid_only: bool = True,
    ) -> list[Memory]:
        """Get memories for a user with filtering.

        Args:
            user_id: The user's unique identifier
            limit: Maximum number of memories to return
            offset: Number of memories to skip (for pagination)
            temporal_level: Filter by temporal level (None = all levels)
            min_salience: Minimum effective salience threshold
            valid_only: If True, only return currently valid memories

        Returns:
            List of memories matching the criteria
        """
        pass

    @abstractmethod
    async def update_salience(
        self,
        memory_id: UUID,
        adjustment: float,
    ) -> Memory:
        """Adjust a memory's outcome_adjustment (salience modifier).

        The adjustment is added to the existing outcome_adjustment.
        Effective salience is clamped to [0.0, 1.0].

        Args:
            memory_id: The memory to update
            adjustment: Delta to add to outcome_adjustment

        Returns:
            The updated memory

        Raises:
            ValueError: If memory not found
        """
        pass

    @abstractmethod
    async def increment_retrieval_count(self, memory_id: UUID) -> None:
        """Increment a memory's retrieval count.

        Called each time a memory is retrieved for context.

        Args:
            memory_id: The memory that was retrieved
        """
        pass

    @abstractmethod
    async def increment_decision_count(
        self,
        memory_id: UUID,
        positive: bool,
    ) -> None:
        """Increment a memory's decision and outcome counts.

        Args:
            memory_id: The memory used in a decision
            positive: Whether the outcome was positive
        """
        pass

    @abstractmethod
    async def expire(self, memory_id: UUID) -> None:
        """Mark a memory as expired (set valid_until to now).

        Expired memories are not returned by get_by_user with valid_only=True.

        Args:
            memory_id: The memory to expire
        """
        pass

    @abstractmethod
    async def promote(
        self,
        memory_id: UUID,
        new_level: TemporalLevel,
    ) -> Memory:
        """Promote a memory to a higher temporal level.

        Args:
            memory_id: The memory to promote
            new_level: The new temporal level (must be higher)

        Returns:
            The updated memory

        Raises:
            ValueError: If new_level is not higher than current
        """
        pass

    @abstractmethod
    async def get_candidates_for_promotion(
        self,
        user_id: UUID,
        level: TemporalLevel,
        min_salience: float = 0.7,
        min_positive_ratio: float = 0.6,
        limit: int = 50,
    ) -> list[Memory]:
        """Get memories that are candidates for promotion to next level.

        Args:
            user_id: The user's identifier
            level: Current level to find promotion candidates
            min_salience: Minimum effective salience required
            min_positive_ratio: Minimum positive outcome ratio
            limit: Maximum candidates to return

        Returns:
            List of memories eligible for promotion
        """
        pass

    @abstractmethod
    async def get_expired_candidates(
        self,
        user_id: UUID,
        level: TemporalLevel,
        older_than_days: int,
        limit: int = 100,
    ) -> list[Memory]:
        """Get memories that should be expired based on age.

        Args:
            user_id: The user's identifier
            level: Temporal level to check
            older_than_days: Expire if older than this many days
            limit: Maximum candidates to return

        Returns:
            List of memories to expire
        """
        pass


class IDecisionStorage(ABC):
    """Port for decision trace persistence operations.

    Implementations:
        - PostgresDecisionStorage (Standard/Enterprise)
    """

    @abstractmethod
    async def store_trace(self, trace: DecisionTrace) -> DecisionTrace:
        """Store a new decision trace.

        Args:
            trace: The decision trace to store

        Returns:
            The stored trace with any server-assigned fields
        """
        pass

    @abstractmethod
    async def get_trace(self, trace_id: UUID) -> Optional[DecisionTrace]:
        """Retrieve a decision trace by ID.

        Args:
            trace_id: The trace's unique identifier

        Returns:
            The trace if found, None otherwise
        """
        pass

    @abstractmethod
    async def record_outcome(
        self,
        trace_id: UUID,
        outcome: Outcome,
    ) -> DecisionTrace:
        """Record an outcome for a decision trace.

        Args:
            trace_id: The trace to update
            outcome: The observed outcome

        Returns:
            The updated trace with outcome recorded

        Raises:
            ValueError: If trace not found
        """
        pass

    @abstractmethod
    async def get_traces_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
        with_outcomes_only: bool = False,
        decision_type: Optional[str] = None,
    ) -> list[DecisionTrace]:
        """Get decision traces for a user.

        Args:
            user_id: The user's identifier
            limit: Maximum traces to return
            offset: Number to skip (pagination)
            with_outcomes_only: If True, only return traces with outcomes
            decision_type: Filter by decision type

        Returns:
            List of matching decision traces
        """
        pass

    @abstractmethod
    async def get_traces_for_memory(
        self,
        memory_id: UUID,
        *,
        limit: int = 50,
        with_outcomes_only: bool = True,
    ) -> list[DecisionTrace]:
        """Get decision traces that used a specific memory.

        Useful for understanding a memory's influence on decisions.

        Args:
            memory_id: The memory to find traces for
            limit: Maximum traces to return
            with_outcomes_only: If True, only return traces with outcomes

        Returns:
            List of traces that included this memory
        """
        pass

    @abstractmethod
    async def get_pending_outcomes(
        self,
        user_id: UUID,
        older_than_hours: int = 24,
        limit: int = 50,
    ) -> list[DecisionTrace]:
        """Get traces that don't have outcomes yet.

        Used for prompting users to provide feedback.

        Args:
            user_id: The user's identifier
            older_than_hours: Only include traces older than this
            limit: Maximum traces to return

        Returns:
            List of traces awaiting outcomes
        """
        pass

    @abstractmethod
    async def store_salience_update(self, update: SalienceUpdate) -> None:
        """Store a salience update record.

        Used for auditing and debugging the learning loop.

        Args:
            update: The salience update to record
        """
        pass

    @abstractmethod
    async def get_salience_updates_for_memory(
        self,
        memory_id: UUID,
        limit: int = 50,
    ) -> list[SalienceUpdate]:
        """Get salience update history for a memory.

        Args:
            memory_id: The memory to get updates for
            limit: Maximum updates to return

        Returns:
            List of salience updates, most recent first
        """
        pass
