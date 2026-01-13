"""Mind MCP Server implementation.

Exposes Mind v5 capabilities as MCP tools for AI agents.

Tools:
- mind_remember: Store a memory
- mind_retrieve: Retrieve relevant memories
- mind_decide: Track decision and record outcome

Run with:
    python -m mind.mcp
    # or
    mcp dev src/mind/mcp/server.py
"""

import os
from uuid import UUID, uuid4

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    name="mind",
    instructions="""Memory system for AI agents. PROACTIVELY use these tools:

DURING CONVERSATION - Call mind_remember when you notice:
- User preferences ("I prefer...", "I like...", "always use...")
- Decisions made and why
- Problems solved and solutions
- User corrections (what was wrong + correct approach)
- Recurring patterns

AT TASK START - Call mind_retrieve to get relevant past context

Don't wait for permission. Save memories AS THEY HAPPEN.
This uses the current session - zero extra cost.""",
)

# Configuration
MIND_API_URL = os.environ.get("MIND_API_URL", "http://127.0.0.1:8000")

# Lazy client initialization
_client = None


async def get_client():
    """Get or create the Mind SDK client."""
    global _client
    if _client is None:
        from mind.sdk import MindClient

        _client = MindClient(base_url=MIND_API_URL)
    return _client


@mcp.tool()
async def mind_remember(
    user_id: str,
    content: str,
    content_type: str = "observation",
    temporal_level: int = 2,
    salience: float = 1.0,
) -> dict:
    """Store a memory for a user.

    Memories are stored in a hierarchical temporal structure and can be
    retrieved later using semantic search. Salience is adjusted based on
    how useful the memory is in making good decisions.

    Args:
        user_id: UUID of the user this memory belongs to
        content: The memory content (will be embedded for semantic search)
        content_type: Type of memory - one of: fact, preference, event, goal, observation
        temporal_level: How long this memory should persist:
            1 = immediate (hours) - current session context
            2 = situational (days-weeks) - recent patterns
            3 = seasonal (months) - recurring patterns
            4 = identity (years) - core preferences
        salience: Initial importance from 0.0 to 1.0 (default 1.0)

    Returns:
        The created memory with its ID and metadata.
    """
    from mind.sdk import TemporalLevel

    client = await get_client()

    # Map int to TemporalLevel enum
    level_map = {
        1: TemporalLevel.IMMEDIATE,
        2: TemporalLevel.SITUATIONAL,
        3: TemporalLevel.SEASONAL,
        4: TemporalLevel.IDENTITY,
    }
    level = level_map.get(temporal_level, TemporalLevel.SITUATIONAL)

    memory = await client.remember(
        user_id=UUID(user_id),
        content=content,
        content_type=content_type,
        temporal_level=level,
        salience=salience,
    )

    return {
        "memory_id": str(memory.memory_id),
        "content": memory.content,
        "temporal_level": memory.temporal_level,
        "temporal_level_name": memory.temporal_level_name,
        "effective_salience": memory.effective_salience,
        "created_at": memory.created_at.isoformat(),
    }


@mcp.tool()
async def mind_retrieve(
    user_id: str,
    query: str,
    limit: int = 10,
    min_salience: float = 0.0,
) -> dict:
    """Retrieve relevant memories for a query.

    Uses multi-source fusion (vector similarity, keywords, salience, recency)
    to find the most relevant memories. Memories with better past outcomes
    will rank higher due to outcome-weighted salience.

    Args:
        user_id: UUID of the user whose memories to search
        query: Natural language query describing what you need
        limit: Maximum number of memories to return (1-100, default 10)
        min_salience: Minimum effective salience threshold (0.0-1.0)

    Returns:
        Retrieved memories with their content and relevance scores.
        Also returns a retrieval_id for decision tracking.
    """
    client = await get_client()

    result = await client.retrieve(
        user_id=UUID(user_id),
        query=query,
        limit=limit,
        min_salience=min_salience,
    )

    return {
        "retrieval_id": str(result.retrieval_id),
        "latency_ms": result.latency_ms,
        "memories": [
            {
                "memory_id": str(m.memory_id),
                "content": m.content,
                "content_type": m.content_type,
                "temporal_level": m.temporal_level,
                "temporal_level_name": m.temporal_level_name,
                "effective_salience": m.effective_salience,
                "score": result.scores.get(str(m.memory_id), 0.0),
            }
            for m in result.memories
        ],
    }


@mcp.tool()
async def mind_decide(
    user_id: str,
    memory_ids: list[str],
    decision_summary: str,
    outcome_quality: float,
    outcome_signal: str = "agent_feedback",
    session_id: str | None = None,
    decision_type: str = "recommendation",
    confidence: float = 0.8,
    feedback: str | None = None,
    memory_scores: dict[str, float] | None = None,
) -> dict:
    """Track a decision and record its outcome in one call.

    This is the feedback loop that enables learning. When you make a decision
    based on retrieved memories, call this tool to:
    1. Track which memories influenced the decision
    2. Record whether the outcome was good or bad

    Good outcomes (+quality) increase memory salience, making those memories
    more likely to be retrieved in similar future situations.
    Bad outcomes (-quality) decrease salience.

    Args:
        user_id: UUID of the user
        memory_ids: List of memory IDs that influenced this decision
        decision_summary: Short summary of what was decided (no PII)
        outcome_quality: How well did it work? -1.0 (bad) to 1.0 (good)
        outcome_signal: How was outcome detected? Examples:
            - "user_accepted" - user explicitly approved
            - "user_rejected" - user explicitly rejected
            - "task_completed" - task finished successfully
            - "agent_feedback" - agent's own assessment
        session_id: Optional session UUID (auto-generated if not provided)
        decision_type: Type of decision: recommendation, action, preference
        confidence: How confident was the decision? 0.0-1.0
        feedback: Optional text feedback about the outcome
        memory_scores: Optional dict mapping memory_id to retrieval score.
            Pass the scores from mind_retrieve for accurate attribution.
            If not provided, uses equal weights for all memories.

    Returns:
        Decision trace and salience changes applied to memories.
    """
    client = await get_client()

    # Use provided scores or generate equal weights
    # Best practice: pass scores from mind_retrieve for accurate attribution
    if memory_scores is None:
        memory_scores = {
            mid: 1.0 / len(memory_ids) for mid in memory_ids
        }

    # Track the decision
    track_result = await client.track(
        user_id=UUID(user_id),
        session_id=UUID(session_id) if session_id else uuid4(),
        memory_ids=[UUID(m) for m in memory_ids],
        memory_scores=memory_scores,  # Now passes scores for attribution
        decision_type=decision_type,
        decision_summary=decision_summary,
        confidence=confidence,
    )

    # Record the outcome
    outcome_result = await client.outcome(
        trace_id=track_result.trace_id,
        quality=outcome_quality,
        signal=outcome_signal,
        feedback=feedback,
    )

    return {
        "trace_id": str(track_result.trace_id),
        "created_at": track_result.created_at.isoformat(),
        "outcome_quality": outcome_result.outcome_quality,
        "memories_updated": outcome_result.memories_updated,
        "salience_changes": outcome_result.salience_changes,
    }


@mcp.tool()
async def mind_health() -> dict:
    """Check Mind API health status.

    Returns:
        Health status including API version.
    """
    client = await get_client()
    return await client.health()


def run_server():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run_server()
