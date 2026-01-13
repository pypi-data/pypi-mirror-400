#!/usr/bin/env python3
"""Test the Mind MCP tools.

Run with: python scripts/test_mcp.py
"""

import asyncio
import sys
from uuid import uuid4

# Add src to path
sys.path.insert(0, "src")

from mind.mcp.server import (
    mind_health,
    mind_remember,
    mind_retrieve,
    mind_decide,
)


async def main():
    """Test MCP tools end-to-end."""
    print("=" * 60)
    print("Mind MCP Tools Test")
    print("=" * 60)

    user_id = str(uuid4())

    # 1. Health check
    print("\n1. mind_health...")
    health = await mind_health()
    print(f"   Status: {health.get('status')}")

    # 2. Store memories
    print("\n2. mind_remember (storing 2 memories)...")
    mem1 = await mind_remember(
        user_id=user_id,
        content="User prefers Python over JavaScript for backend work",
        content_type="preference",
        temporal_level=4,  # identity
        salience=0.9,
    )
    print(f"   Memory 1: {mem1['memory_id'][:8]}... - {mem1['content'][:30]}...")

    mem2 = await mind_remember(
        user_id=user_id,
        content="User is currently debugging a FastAPI authentication issue",
        content_type="observation",
        temporal_level=2,  # situational
        salience=0.7,
    )
    print(f"   Memory 2: {mem2['memory_id'][:8]}... - {mem2['content'][:30]}...")

    # 3. Retrieve memories (use same keywords as stored content)
    print("\n3. mind_retrieve...")
    result = await mind_retrieve(
        user_id=user_id,
        query="Python backend",
        limit=5,
    )
    print(f"   Found: {len(result['memories'])} memories")
    print(f"   Latency: {result['latency_ms']:.1f}ms")
    for m in result['memories']:
        print(f"   - [{m['effective_salience']:.2f}] {m['content'][:40]}...")

    # 4. Make a decision based on memories
    print("\n4. mind_decide (tracking decision + outcome)...")
    memory_ids = [m['memory_id'] for m in result['memories']]

    if memory_ids:
        decision = await mind_decide(
            user_id=user_id,
            memory_ids=memory_ids,
            decision_summary="Recommended Python/FastAPI solution for auth",
            outcome_quality=0.85,
            outcome_signal="user_accepted",
            decision_type="recommendation",
            confidence=0.9,
            feedback="User said this was helpful",
        )
        print(f"   Trace ID: {decision['trace_id'][:8]}...")
        print(f"   Outcome quality: {decision['outcome_quality']}")
        print(f"   Memories updated: {decision['memories_updated']}")
        print(f"   Salience changes: {decision['salience_changes']}")

    # 5. Retrieve again to see salience changes
    print("\n5. mind_retrieve (checking salience updates)...")
    result2 = await mind_retrieve(
        user_id=user_id,
        query="programming preferences",
        limit=5,
    )
    for m in result2['memories']:
        print(f"   - [{m['effective_salience']:.2f}] {m['content'][:40]}...")

    print("\n" + "=" * 60)
    print("MCP Tools Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
