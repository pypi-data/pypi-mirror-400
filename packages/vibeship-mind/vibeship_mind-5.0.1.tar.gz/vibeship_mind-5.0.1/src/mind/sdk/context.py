"""Decision context manager.

Enforces the self-improvement feedback loop by requiring
outcome recording before the context exits.
"""

import warnings
from typing import TYPE_CHECKING
from uuid import UUID

from mind.sdk.models import (
    Memory,
    OutcomeResult,
    TemporalLevel,
    TrackResult,
)

if TYPE_CHECKING:
    from mind.sdk.client import MindClient


class OutcomeNotRecordedError(Exception):
    """Raised when exiting a DecisionContext without recording an outcome."""

    def __init__(self, trace_id: UUID):
        super().__init__(
            f"Decision {trace_id} was tracked but no outcome was recorded. "
            "Call ctx.outcome() before exiting the context to complete the feedback loop."
        )
        self.trace_id = trace_id


class DecisionContext:
    """Context manager for decision tracking with enforced feedback loop.

    Usage:
        async with client.decision(user_id) as ctx:
            # Retrieve relevant memories
            memories = await ctx.retrieve("user preferences")

            # Use memories to make your decision...
            decision = make_decision(memories)

            # Track what you decided (optional, called automatically if not)
            await ctx.track("Used preference X", confidence=0.85)

            # Record the outcome (REQUIRED)
            await ctx.outcome(quality=0.9, signal="user_accepted")

    The context enforces the feedback loop:
    - If you retrieve memories and exit without recording an outcome,
      a warning is issued (in development) or error raised (in strict mode).
    - This ensures Mind can learn from every decision.
    """

    def __init__(
        self,
        client: "MindClient",
        user_id: UUID,
        session_id: UUID,
        decision_type: str = "recommendation",
        strict: bool = False,
    ):
        """Initialize decision context.

        Args:
            client: MindClient instance
            user_id: User making decisions
            session_id: Current session ID
            decision_type: Type of decisions in this context
            strict: If True, raise error on missing outcome. If False, warn.
        """
        self._client = client
        self._user_id = user_id
        self._session_id = session_id
        self._decision_type = decision_type
        self._strict = strict

        # State tracking
        self._retrieved_memories: list[Memory] = []
        self._memory_scores: dict[str, float] = {}
        self._trace_id: UUID | None = None
        self._decision_tracked: bool = False
        self._outcome_recorded: bool = False
        self._decision_summary: str | None = None

    @property
    def user_id(self) -> UUID:
        """Get the user ID for this context."""
        return self._user_id

    @property
    def session_id(self) -> UUID:
        """Get the session ID for this context."""
        return self._session_id

    @property
    def trace_id(self) -> UUID | None:
        """Get the trace ID (available after track() is called)."""
        return self._trace_id

    @property
    def memories(self) -> list[Memory]:
        """Get all memories retrieved in this context."""
        return self._retrieved_memories

    async def __aenter__(self) -> "DecisionContext":
        """Enter the decision context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the decision context.

        If memories were retrieved but no outcome was recorded,
        this will warn or raise depending on strict mode.
        """
        # If there was an exception, don't add another
        if exc_type is not None:
            return

        # If no memories were retrieved, nothing to track
        if not self._retrieved_memories:
            return

        # If decision was tracked but no outcome recorded
        if self._decision_tracked and not self._outcome_recorded:
            if self._strict:
                raise OutcomeNotRecordedError(self._trace_id)
            else:
                warnings.warn(
                    f"Decision {self._trace_id} was tracked but no outcome was recorded. "
                    "The feedback loop is incomplete. Call ctx.outcome() to help Mind learn.",
                    UserWarning,
                    stacklevel=2,
                )

    async def retrieve(
        self,
        query: str,
        limit: int = 10,
        temporal_levels: list[TemporalLevel] | None = None,
        min_salience: float = 0.0,
    ) -> list[Memory]:
        """Retrieve relevant memories.

        Memories retrieved through this method are automatically
        tracked for the decision trace.

        Args:
            query: Natural language query
            limit: Maximum memories to return
            temporal_levels: Filter to specific levels
            min_salience: Minimum effective salience

        Returns:
            List of relevant memories.
        """
        result = await self._client.retrieve(
            user_id=self._user_id,
            query=query,
            limit=limit,
            temporal_levels=temporal_levels,
            min_salience=min_salience,
        )

        # Track these memories for the decision
        self._retrieved_memories.extend(result.memories)
        self._memory_scores.update(result.scores)

        return result.memories

    async def remember(
        self,
        content: str,
        content_type: str = "observation",
        temporal_level: TemporalLevel = TemporalLevel.SITUATIONAL,
        salience: float = 1.0,
    ) -> Memory:
        """Store a new memory within this context.

        Args:
            content: Memory content
            content_type: Type of memory
            temporal_level: Persistence level
            salience: Initial importance

        Returns:
            The created Memory.
        """
        return await self._client.remember(
            user_id=self._user_id,
            content=content,
            content_type=content_type,
            temporal_level=temporal_level,
            salience=salience,
        )

    async def track(
        self,
        decision_summary: str,
        confidence: float = 0.8,
        alternatives_count: int = 0,
    ) -> TrackResult:
        """Track the decision made using retrieved memories.

        This is called automatically when you call outcome() if not
        called explicitly. Call this if you want to customize the
        decision metadata before recording the outcome.

        Args:
            decision_summary: Short summary of the decision (no PII)
            confidence: Confidence in the decision (0.0 to 1.0)
            alternatives_count: Number of alternatives considered

        Returns:
            TrackResult with trace_id.
        """
        if not self._retrieved_memories:
            raise ValueError("No memories retrieved. Call retrieve() first.")

        memory_ids = [m.memory_id for m in self._retrieved_memories]

        result = await self._client.track(
            user_id=self._user_id,
            session_id=self._session_id,
            memory_ids=memory_ids,
            decision_type=self._decision_type,
            decision_summary=decision_summary,
            confidence=confidence,
            memory_scores=self._memory_scores,
            alternatives_count=alternatives_count,
        )

        self._trace_id = result.trace_id
        self._decision_tracked = True
        self._decision_summary = decision_summary

        return result

    async def outcome(
        self,
        quality: float,
        signal: str = "explicit_feedback",
        feedback: str | None = None,
        decision_summary: str | None = None,
        confidence: float = 0.8,
    ) -> OutcomeResult:
        """Record the outcome of the decision.

        This completes the feedback loop, allowing Mind to learn
        from the decision's success or failure.

        If track() wasn't called explicitly, it will be called
        automatically with the provided or default decision_summary.

        Args:
            quality: Outcome quality (-1.0 bad to 1.0 good)
            signal: How detected: explicit_feedback, implicit_success, etc.
            feedback: Optional textual feedback
            decision_summary: Summary if track() wasn't called (defaults to auto-generated)
            confidence: Confidence if track() wasn't called

        Returns:
            OutcomeResult showing salience changes.
        """
        # Auto-track if not already done
        if not self._decision_tracked:
            if not self._retrieved_memories:
                raise ValueError("No memories retrieved. Call retrieve() first.")

            summary = (
                decision_summary or f"Decision based on {len(self._retrieved_memories)} memories"
            )
            await self.track(decision_summary=summary, confidence=confidence)

        result = await self._client.outcome(
            trace_id=self._trace_id,
            quality=quality,
            signal=signal,
            feedback=feedback,
        )

        self._outcome_recorded = True
        return result

    async def skip_outcome(self, reason: str = "not applicable") -> None:
        """Explicitly skip recording an outcome.

        Use this when the decision context is used for retrieval
        but no actionable decision was made (e.g., just browsing).

        This prevents the warning/error on context exit.

        Args:
            reason: Why outcome tracking is being skipped.
        """
        self._outcome_recorded = True  # Mark as handled
        # We could log this for analytics, but keep it simple for now
