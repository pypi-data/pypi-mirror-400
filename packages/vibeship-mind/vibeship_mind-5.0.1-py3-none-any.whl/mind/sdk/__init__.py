"""Mind SDK - Python client for Mind v5 decision intelligence.

The SDK provides a type-safe, async interface to Mind v5 with
enforced feedback loop through the DecisionContext.

Quick Start:
    from mind.sdk import MindClient

    async with MindClient() as client:
        # Check health
        health = await client.health()

        # Store a memory
        memory = await client.remember(
            user_id=user_id,
            content="User prefers concise responses",
        )

        # Retrieve with decision tracking (recommended)
        async with client.decision(user_id) as ctx:
            memories = await ctx.retrieve("response preferences")

            # ... use memories to make your decision ...

            # Record outcome (required to complete feedback loop)
            await ctx.outcome(quality=0.9, signal="user_accepted")

The DecisionContext enforces the self-improvement loop:
1. Retrieve memories relevant to your task
2. Use those memories to make a decision
3. Track the decision with ctx.track() or ctx.outcome()
4. Record the outcome so Mind can learn

If you exit a context without recording an outcome, you'll get
a warning. This ensures Mind learns from every decision.
"""

from mind.sdk.client import MindClient, MindError
from mind.sdk.context import DecisionContext, OutcomeNotRecordedError
from mind.sdk.models import (
    DecisionTrace,
    Memory,
    OutcomeResult,
    RetrievalResult,
    TemporalLevel,
    TrackResult,
)

__all__ = [
    # Client
    "MindClient",
    "MindError",
    # Context
    "DecisionContext",
    "OutcomeNotRecordedError",
    # Models
    "Memory",
    "RetrievalResult",
    "DecisionTrace",
    "OutcomeResult",
    "TrackResult",
    "TemporalLevel",
]
