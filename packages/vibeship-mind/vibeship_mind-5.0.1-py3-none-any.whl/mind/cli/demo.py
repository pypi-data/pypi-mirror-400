"""Mind demo command - Interactive learning loop demonstration.

Shows how Mind's outcome-based learning improves memory retrieval over time.

The demo:
1. Creates sample memories about a user's preferences
2. Makes decisions using those memories
3. Records outcomes (positive/negative)
4. Shows how salience adjusts based on outcomes
5. Demonstrates improved retrieval after learning

Usage:
    mind demo
"""

import asyncio
import sys
from datetime import datetime, UTC
from uuid import uuid4


async def demo_command() -> None:
    """Run an interactive learning loop demo."""
    print(_get_banner())
    print()

    print("This demo shows how Mind learns from decision outcomes.")
    print()
    print("The learning loop:")
    print("  1. Store memories about user preferences")
    print("  2. Retrieve memories to make decisions")
    print("  3. Record decision outcomes (good/bad)")
    print("  4. Watch salience adjust based on outcomes")
    print("  5. See improved retrieval over time")
    print()
    print("-" * 60)
    print()

    try:
        await _run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure the Mind server is running:")
        print("  mind serve")
        sys.exit(1)


async def _run_demo() -> None:
    """Run the actual demo."""
    import httpx

    base_url = "http://127.0.0.1:8000"
    user_id = str(uuid4())

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        # Check server health
        print("Checking server health...")
        try:
            resp = await client.get("/health")
            if resp.status_code != 200:
                raise Exception("Server not healthy")
            print("  Server is healthy!\n")
        except httpx.ConnectError:
            raise Exception(
                "Cannot connect to Mind server at http://127.0.0.1:8000\n"
                "Start the server with: mind serve"
            )

        # Step 1: Create sample memories
        print("Step 1: Creating memories about user preferences")
        print("-" * 60)

        memories = [
            {
                "content": "User prefers concise, direct answers without unnecessary explanation",
                "content_type": "preference",
                "temporal_level": 4,  # Identity level
            },
            {
                "content": "User likes to see code examples when learning new concepts",
                "content_type": "preference",
                "temporal_level": 4,
            },
            {
                "content": "User gets frustrated with overly verbose responses",
                "content_type": "observation",
                "temporal_level": 3,  # Seasonal
            },
            {
                "content": "User appreciates when I acknowledge their expertise level",
                "content_type": "observation",
                "temporal_level": 2,  # Situational
            },
        ]

        created_memories = []
        for mem in memories:
            resp = await client.post(
                "/v1/remember",
                json={
                    "user_id": user_id,
                    **mem,
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                created_memories.append(data)
                print(f"  Created: {mem['content'][:50]}...")

        print()
        print(f"  Created {len(created_memories)} memories\n")

        # Step 2: Retrieve memories for a decision
        print("Step 2: Retrieving memories for a decision")
        print("-" * 60)

        query = "How should I format my response to this user?"
        print(f"  Query: \"{query}\"\n")

        resp = await client.post(
            "/v1/retrieve",
            json={
                "user_id": user_id,
                "query": query,
                "limit": 5,
            }
        )

        if resp.status_code == 200:
            data = resp.json()
            print("  Retrieved memories:")
            for i, mem in enumerate(data.get("memories", [])[:3]):
                salience = mem.get("effective_salience", 1.0)
                print(f"    {i+1}. [{salience:.2f}] {mem['content'][:50]}...")
            print()

        # Step 3: Make a decision and record outcome
        print("Step 3: Making a decision and recording outcome")
        print("-" * 60)

        memory_ids = [m["memory_id"] for m in created_memories[:2]]
        memory_scores = {mid: 0.8 for mid in memory_ids}

        resp = await client.post(
            "/v1/decide",
            json={
                "user_id": user_id,
                "memory_ids": memory_ids,
                "memory_scores": memory_scores,
                "decision_type": "response_format",
                "decision_summary": "Provide concise response with code example",
                "confidence": 0.85,
            }
        )

        if resp.status_code == 200:
            trace_data = resp.json()
            trace_id = trace_data.get("trace_id")
            print(f"  Decision recorded: {trace_id[:8]}...")
            print(f"  Summary: Provide concise response with code example")
            print()

            # Simulate positive outcome
            print("  Recording positive outcome (user was satisfied)...")
            resp = await client.post(
                f"/v1/decide/{trace_id}/outcome",
                json={
                    "user_id": user_id,
                    "quality": 0.9,
                    "signal": "user_satisfied",
                    "feedback": "User thanked for the helpful response",
                }
            )

            if resp.status_code == 200:
                outcome_data = resp.json()
                print(f"  Outcome recorded!")
                print(f"  Memories updated: {outcome_data.get('memories_updated', 0)}")
                print()

        # Step 4: Show salience changes
        print("Step 4: Checking salience adjustments")
        print("-" * 60)

        resp = await client.post(
            "/v1/retrieve",
            json={
                "user_id": user_id,
                "query": query,
                "limit": 5,
            }
        )

        if resp.status_code == 200:
            data = resp.json()
            print("  After positive outcome, saliences adjusted:")
            for i, mem in enumerate(data.get("memories", [])[:3]):
                salience = mem.get("effective_salience", 1.0)
                base = mem.get("base_salience", 1.0)
                adjustment = mem.get("outcome_adjustment", 0.0)
                print(f"    {i+1}. [{salience:.2f}] (base: {base:.2f}, adj: {adjustment:+.2f})")
                print(f"       {mem['content'][:45]}...")
            print()

        # Step 5: Summary
        print("Step 5: Summary")
        print("-" * 60)
        print()
        print("  The learning loop demonstrated:")
        print("    - Memories were retrieved based on relevance to the query")
        print("    - A decision was made using those memories")
        print("    - When the outcome was positive, memory salience increased")
        print("    - Future retrievals will rank these memories higher")
        print()
        print("  Over time, Mind learns which memories lead to good outcomes")
        print("  and prioritizes them in future retrievals.")
        print()
        print("  Try the negative outcome scenario:")
        print("    - Memories that lead to bad outcomes get demoted")
        print("    - This prevents repeating mistakes")
        print()
        print("-" * 60)
        print("Demo complete!")


def _get_banner() -> str:
    """Get the demo banner."""
    return """
╔══════════════════════════════════════════════════════════════════╗
║                     Mind Learning Loop Demo                      ║
╚══════════════════════════════════════════════════════════════════╝
"""
