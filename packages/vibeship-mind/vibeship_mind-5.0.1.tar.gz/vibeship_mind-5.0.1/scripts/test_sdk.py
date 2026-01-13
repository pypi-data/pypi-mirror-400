#!/usr/bin/env python3
"""Test the Mind SDK.

Run with: python scripts/test_sdk.py
"""

import asyncio
import sys
from uuid import uuid4

# Add src to path for development
sys.path.insert(0, "src")

from mind.sdk import MindClient, TemporalLevel


async def main():
    """Test the SDK end-to-end."""
    print("=" * 60)
    print("Mind SDK Test")
    print("=" * 60)

    user_id = uuid4()
    session_id = uuid4()

    async with MindClient("http://localhost:8080") as client:
        # 1. Health check
        print("\n1. Health check...")
        health = await client.health()
        print(f"   Status: {health.get('status')}")
        print(f"   Version: {health.get('version')}")

        # 2. Store a memory
        print("\n2. Storing memory...")
        memory = await client.remember(
            user_id=user_id,
            content="User prefers detailed technical explanations with code examples",
            content_type="preference",
            temporal_level=TemporalLevel.IDENTITY,
            salience=0.9,
        )
        print(f"   Created: {memory.memory_id}")
        print(f"   Content: {memory.content[:50]}...")

        # 3. Store another memory
        print("\n3. Storing another memory...")
        memory2 = await client.remember(
            user_id=user_id,
            content="User is working on a Python project with FastAPI",
            content_type="observation",
            temporal_level=TemporalLevel.SITUATIONAL,
            salience=0.7,
        )
        print(f"   Created: {memory2.memory_id}")

        # 4. Retrieve memories (simple)
        print("\n4. Retrieving memories (simple)...")
        result = await client.retrieve(
            user_id=user_id,
            query="code examples",
            limit=5,
        )
        print(f"   Found: {len(result.memories)} memories")
        print(f"   Retrieval ID: {result.retrieval_id}")
        for mem in result.memories:
            print(f"   - [{mem.effective_salience:.2f}] {mem.content[:40]}...")

        # 5. Decision context with full feedback loop
        print("\n5. Decision context with feedback loop...")
        async with client.decision(user_id, session_id, "response_style") as ctx:
            # Retrieve memories within context (use matching query)
            memories = await ctx.retrieve("code examples technical explanation")
            print(f"   Retrieved: {len(memories)} memories in context")

            if not memories:
                print("   No memories found, skipping outcome tracking")
                await ctx.skip_outcome("no memories to base decision on")
                return

            # Simulate making a decision based on memories
            print("   Making decision based on memories...")

            # Track the decision explicitly
            track_result = await ctx.track(
                decision_summary="Used detailed explanation style with code",
                confidence=0.85,
                alternatives_count=2,
            )
            print(f"   Tracked: {track_result.trace_id}")

            # Record the outcome
            outcome_result = await ctx.outcome(
                quality=0.9,
                signal="user_thumbs_up",
                feedback="User said it was helpful",
            )
            print(f"   Outcome recorded: quality={outcome_result.outcome_quality}")
            print(f"   Memories updated: {outcome_result.memories_updated}")
            print(f"   Salience changes: {outcome_result.salience_changes}")

        # 6. Verify the decision trace
        print("\n6. Verifying decision trace...")
        trace = await client.get_decision(track_result.trace_id)
        print(f"   Trace ID: {trace.trace_id}")
        print(f"   Decision type: {trace.decision_type}")
        print(f"   Outcome observed: {trace.outcome_observed}")
        print(f"   Outcome quality: {trace.outcome_quality}")

        # 7. Retrieve again to see updated salience
        print("\n7. Retrieving to check salience updates...")
        result2 = await client.retrieve(
            user_id=user_id,
            query="code examples",
            limit=5,
        )
        for mem in result2.memories:
            print(f"   - [{mem.effective_salience:.2f}] {mem.content[:40]}...")

    print("\n" + "=" * 60)
    print("SDK Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
