"""Mind SDK client.

Provides a type-safe, async client for the Mind v5 API.
Enforces the self-improvement feedback loop through the DecisionContext.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import httpx

if TYPE_CHECKING:
    from mind.sdk.context import DecisionContext

from mind.sdk.models import (
    DecisionTrace,
    Memory,
    OutcomeResult,
    RetrievalResult,
    TemporalLevel,
    TrackResult,
)


class MindError(Exception):
    """Error from Mind API."""

    def __init__(self, message: str, status_code: int = 0, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class MindClient:
    """Async client for the Mind v5 API.

    Usage:
        client = MindClient("http://localhost:8080")

        # Simple usage
        memory = await client.remember(user_id, "User prefers dark mode")
        memories = await client.retrieve(user_id, "theme preferences")

        # With decision tracking (recommended)
        async with client.decision(user_id, session_id) as ctx:
            memories = await ctx.retrieve("user preferences")
            # ... use memories to make a decision ...
            await ctx.outcome(quality=0.9, signal="user_accepted")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 30.0,
        api_key: str | None = None,
    ):
        """Initialize the Mind client.

        Args:
            base_url: Mind API base URL
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> MindClient:
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an HTTP request and return JSON response."""
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)

        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = {"message": response.text}
            raise MindError(
                message=detail.get("detail", detail.get("message", "Unknown error")),
                status_code=response.status_code,
                details=detail,
            )

        if response.status_code == 204:
            return {}
        return response.json()

    # ========== Health ==========

    async def health(self) -> dict:
        """Check API health.

        Returns:
            Health status dict with 'status' and 'version' keys.
        """
        return await self._request("GET", "/health")

    # ========== Memory Operations ==========

    async def remember(
        self,
        user_id: UUID,
        content: str,
        content_type: str = "observation",
        temporal_level: TemporalLevel = TemporalLevel.SITUATIONAL,
        salience: float = 1.0,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
    ) -> Memory:
        """Store a new memory.

        Args:
            user_id: User this memory belongs to
            content: Memory content text
            content_type: Type: fact, preference, event, goal, observation
            temporal_level: How long this memory should persist
            salience: Initial importance (0.0 to 1.0)
            valid_from: When memory becomes valid
            valid_until: When memory expires

        Returns:
            The created Memory object.
        """
        payload = {
            "user_id": str(user_id),
            "content": content,
            "content_type": content_type,
            "temporal_level": temporal_level.value,
            "salience": salience,
        }
        if valid_from:
            payload["valid_from"] = valid_from.isoformat()
        if valid_until:
            payload["valid_until"] = valid_until.isoformat()

        data = await self._request("POST", "/v1/memories/", json=payload)
        return Memory.from_dict(data)

    async def get_memory(self, memory_id: UUID) -> Memory:
        """Get a memory by ID.

        Args:
            memory_id: The memory's UUID

        Returns:
            The Memory object.
        """
        data = await self._request("GET", f"/v1/memories/{memory_id}")
        return Memory.from_dict(data)

    async def retrieve(
        self,
        user_id: UUID,
        query: str,
        limit: int = 10,
        temporal_levels: list[TemporalLevel] | None = None,
        min_salience: float = 0.0,
    ) -> RetrievalResult:
        """Retrieve relevant memories for a query.

        Uses multi-source fusion (vector, keyword, salience, recency)
        to find the most relevant memories.

        Args:
            user_id: User whose memories to search
            query: Natural language query
            limit: Maximum memories to return (1-100)
            temporal_levels: Filter to specific levels
            min_salience: Minimum effective salience

        Returns:
            RetrievalResult with memories and scores.
        """
        payload = {
            "user_id": str(user_id),
            "query": query,
            "limit": limit,
            "min_salience": min_salience,
        }
        if temporal_levels:
            payload["temporal_levels"] = [t.value for t in temporal_levels]

        data = await self._request("POST", "/v1/memories/retrieve", json=payload)
        return RetrievalResult.from_dict(data)

    # ========== Decision Tracking ==========

    async def track(
        self,
        user_id: UUID,
        session_id: UUID,
        memory_ids: list[UUID],
        decision_type: str,
        decision_summary: str,
        confidence: float,
        memory_scores: dict[str, float] | None = None,
        alternatives_count: int = 0,
    ) -> TrackResult:
        """Track a decision made using memories.

        Creates a trace linking memories to the decision.
        Use outcome() later to record how the decision worked out.

        Args:
            user_id: User making the decision
            session_id: Current session ID
            memory_ids: IDs of memories that influenced the decision
            decision_type: Type: recommendation, action, preference, etc.
            decision_summary: Short summary (no PII)
            confidence: Confidence in the decision (0.0 to 1.0)
            memory_scores: Optional memory_id -> retrieval score mapping
            alternatives_count: Number of alternatives considered

        Returns:
            TrackResult with trace_id for later outcome tracking.
        """
        payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "memory_ids": [str(m) for m in memory_ids],
            "decision_type": decision_type,
            "decision_summary": decision_summary,
            "confidence": confidence,
            "alternatives_count": alternatives_count,
        }
        if memory_scores:
            payload["memory_scores"] = memory_scores

        data = await self._request("POST", "/v1/decisions/track", json=payload)
        return TrackResult.from_dict(data)

    async def outcome(
        self,
        trace_id: UUID,
        quality: float,
        signal: str,
        feedback: str | None = None,
    ) -> OutcomeResult:
        """Record the outcome of a tracked decision.

        This is the feedback loop that enables learning.
        Positive outcomes increase memory salience,
        negative outcomes decrease it.

        Args:
            trace_id: The decision trace to update
            quality: Outcome quality (-1.0 bad to 1.0 good)
            signal: How detected: explicit_feedback, implicit_success, etc.
            feedback: Optional textual feedback

        Returns:
            OutcomeResult showing salience changes.
        """
        payload = {
            "trace_id": str(trace_id),
            "quality": quality,
            "signal": signal,
        }
        if feedback:
            payload["feedback"] = feedback

        data = await self._request("POST", "/v1/decisions/outcome", json=payload)
        return OutcomeResult.from_dict(data)

    async def get_decision(self, trace_id: UUID) -> DecisionTrace:
        """Get a decision trace by ID.

        Args:
            trace_id: The trace's UUID

        Returns:
            The DecisionTrace object.
        """
        data = await self._request("GET", f"/v1/decisions/{trace_id}")
        return DecisionTrace.from_dict(data)

    # ========== Decision Context ==========

    def decision(
        self,
        user_id: UUID,
        session_id: UUID | None = None,
        decision_type: str = "recommendation",
    ) -> DecisionContext:
        """Create a decision context for tracking.

        The context manager enforces the feedback loop:
        you must call outcome() before exiting.

        Usage:
            async with client.decision(user_id) as ctx:
                memories = await ctx.retrieve("query")
                # ... use memories ...
                await ctx.outcome(quality=0.9)

        Args:
            user_id: User making the decision
            session_id: Optional session ID (auto-generated if not provided)
            decision_type: Type of decision being made

        Returns:
            DecisionContext manager.
        """
        from mind.sdk.context import DecisionContext

        return DecisionContext(
            client=self,
            user_id=user_id,
            session_id=session_id or uuid4(),
            decision_type=decision_type,
        )
