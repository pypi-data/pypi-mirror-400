#!/usr/bin/env python3
"""
Mind v5 Smoke Test

Tests the core loop:
1. Health check
2. Create a memory
3. Get memory by ID
4. Retrieve memories (search)
5. Track a decision
6. Record an outcome

Run: python scripts/smoke_test.py
"""

import httpx
import sys
from uuid import uuid4

BASE_URL = "http://localhost:8080"
TEST_USER_ID = str(uuid4())
TEST_SESSION_ID = str(uuid4())


def main():
    print("=" * 60)
    print("Mind v5 Smoke Test")
    print("=" * 60)
    print(f"API: {BASE_URL}")
    print(f"Test User: {TEST_USER_ID}")
    print()

    # Use follow_redirects to handle 307s
    client = httpx.Client(timeout=30.0, follow_redirects=True)

    tests = [
        ("Health Check", test_health),
        ("Create Memory", test_create_memory),
        ("Get Memory", test_get_memory),
        ("Retrieve Memories", test_retrieve_memories),
        ("Track Decision", test_track_decision),
        ("Record Outcome", test_record_outcome),
    ]

    passed = 0
    failed = 0
    context = {}  # Share data between tests

    for name, test_fn in tests:
        try:
            print(f"[TEST] {name}...", end=" ")
            test_fn(client, context)
            print("PASSED")
            passed += 1
        except AssertionError as e:
            print(f"FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


def test_health(client: httpx.Client, ctx: dict):
    """Test health endpoint."""
    resp = client.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("status") == "healthy", f"Expected healthy, got {data}"


def test_create_memory(client: httpx.Client, ctx: dict):
    """Test creating a memory."""
    resp = client.post(
        f"{BASE_URL}/v1/memories/",
        json={
            "user_id": TEST_USER_ID,
            "content": "User prefers concise explanations over detailed ones",
            "content_type": "preference",
            "temporal_level": 3,  # SEASONAL - stable preference
            "salience": 0.8,
        },
    )
    assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "memory_id" in data, f"Expected memory_id in response: {data}"
    ctx["memory_id"] = data["memory_id"]

    # Create a second memory for retrieval testing
    resp2 = client.post(
        f"{BASE_URL}/v1/memories/",
        json={
            "user_id": TEST_USER_ID,
            "content": "User is working on a Python project with FastAPI",
            "content_type": "context",
            "temporal_level": 2,  # SITUATIONAL
            "salience": 0.6,
        },
    )
    assert resp2.status_code in (200, 201), f"Second memory failed: {resp2.text}"
    ctx["memory_id_2"] = resp2.json()["memory_id"]


def test_get_memory(client: httpx.Client, ctx: dict):
    """Test getting a memory by ID."""
    memory_id = ctx.get("memory_id")
    assert memory_id, "No memory_id from previous test"

    resp = client.get(f"{BASE_URL}/v1/memories/{memory_id}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["memory_id"] == memory_id, f"Memory ID mismatch"
    assert "content" in data, f"Expected content in response"


def test_retrieve_memories(client: httpx.Client, ctx: dict):
    """Test retrieving memories with a query."""
    resp = client.post(
        f"{BASE_URL}/v1/memories/retrieve",
        json={
            "user_id": TEST_USER_ID,
            "query": "explanation preferences",
            "limit": 5,
        },
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "memories" in data, f"Expected memories in response: {data}"
    assert "retrieval_id" in data, f"Expected retrieval_id in response: {data}"


def test_track_decision(client: httpx.Client, ctx: dict):
    """Test tracking a decision."""
    memory_ids = [ctx.get("memory_id")] if ctx.get("memory_id") else []

    resp = client.post(
        f"{BASE_URL}/v1/decisions/track",
        json={
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "memory_ids": memory_ids,
            "memory_scores": {memory_ids[0]: 0.85} if memory_ids else {},
            "decision_type": "response_style",
            "decision_summary": "Provided a concise explanation with example",
            "confidence": 0.85,
            "alternatives_count": 2,
        },
    )
    assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "trace_id" in data, f"Expected trace_id in response: {data}"
    ctx["trace_id"] = data["trace_id"]


def test_record_outcome(client: httpx.Client, ctx: dict):
    """Test recording a decision outcome."""
    trace_id = ctx.get("trace_id")
    assert trace_id, "No trace_id from previous test"

    resp = client.post(
        f"{BASE_URL}/v1/decisions/outcome",
        json={
            "trace_id": trace_id,
            "quality": 0.9,  # Positive outcome
            "signal": "explicit_positive",
            "feedback": "User understood the explanation quickly",
        },
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "outcome_quality" in data, f"Expected outcome_quality in response: {data}"
    assert data.get("memories_updated", 0) >= 0, f"Expected memories_updated"


if __name__ == "__main__":
    sys.exit(main())
