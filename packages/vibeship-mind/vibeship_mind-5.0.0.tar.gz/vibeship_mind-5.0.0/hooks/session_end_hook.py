#!/usr/bin/env python3
"""Mind Session End Hook - Batch Memory Extraction.

This hook runs ONLY when a Claude Code session ends.
It processes the entire conversation to extract meaningful memories.

SAFETY:
- Only runs once at session end (not per-message)
- Read-only: never touches project files
- Fire-and-forget with timeout
- Fail-silent: errors logged externally

This is SAFER than per-message hooks because:
1. No interference during active work
2. Can take more time to analyze (still with limits)
3. Batch processing reduces API calls
4. Single point of failure instead of many

Usage in .claude/settings.json:
{
  "hooks": {
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook.py"
  }
}
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
MIND_API_URL = os.environ.get("MIND_API_URL", "http://127.0.0.1:8000")
USER_ID = os.environ.get("MIND_USER_ID", "550e8400-e29b-41d4-a716-446655440000")
TIMEOUT_SECONDS = 5.0  # Can be slightly longer for end-of-session
LOG_DIR = Path.home() / ".mind" / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "info"):
    """Log to external file."""
    try:
        log_file = LOG_DIR / "session_hook.log"
        timestamp = datetime.now().isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {level.upper()} | {message}\n")
    except Exception:
        pass


def send_memory(content: str, content_type: str, temporal_level: int, salience: float):
    """Send a memory to the Mind API."""
    try:
        import urllib.request
        import urllib.error

        data = json.dumps({
            "user_id": USER_ID,
            "content": content[:2000],
            "content_type": content_type,
            "temporal_level": temporal_level,
            "salience": salience,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{MIND_API_URL}/v1/memories/",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            if resp.status == 201:
                log(f"Memory stored: {content[:50]}...")
                return True
    except Exception as e:
        log(f"Failed to store memory: {e}", "error")

    return False


def extract_session_summary(session_data: dict) -> list[dict]:
    """Extract meaningful memories from session data.

    Returns list of memories to store:
    [{"content": "...", "type": "...", "level": N, "salience": 0.X}, ...]
    """
    memories = []

    # Get conversation summary if available
    summary = session_data.get("summary", "")
    if summary:
        memories.append({
            "content": f"Session summary: {summary}",
            "type": "context",
            "level": 2,  # Situational
            "salience": 0.8,
        })

    # Get user messages for preference extraction
    messages = session_data.get("messages", [])
    user_messages = [m for m in messages if m.get("role") == "user"]

    # Look for preference signals
    preference_keywords = [
        "i prefer", "i like", "i want", "always use", "never use",
        "i hate", "i love", "my preference", "i usually",
    ]

    for msg in user_messages:
        content = msg.get("content", "").lower()
        for keyword in preference_keywords:
            if keyword in content:
                memories.append({
                    "content": msg.get("content", "")[:500],
                    "type": "preference",
                    "level": 4,  # Identity (preferences persist)
                    "salience": 0.9,
                })
                break

    # Track what was worked on
    working_dir = session_data.get("cwd", "")
    if working_dir:
        project_name = Path(working_dir).name
        memories.append({
            "content": f"Worked on project: {project_name}",
            "type": "context",
            "level": 2,
            "salience": 0.6,
        })

    # Track tools used frequently (patterns)
    tool_uses = session_data.get("tool_uses", [])
    if len(tool_uses) > 10:
        # Extract tool usage patterns
        tool_counts = {}
        for tool in tool_uses:
            name = tool.get("name", "unknown")
            tool_counts[name] = tool_counts.get(name, 0) + 1

        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_tools:
            memories.append({
                "content": f"Session tool usage pattern: {dict(top_tools)}",
                "type": "observation",
                "level": 3,  # Seasonal (work patterns)
                "salience": 0.5,
            })

    return memories


def main():
    """Process session end and extract memories."""
    try:
        # Read session data from stdin
        session_input = sys.stdin.read()
        if not session_input.strip():
            log("No session data received")
            return

        session_data = json.loads(session_input)
        log(f"Processing session end")

        # Extract memories from session
        memories = extract_session_summary(session_data)

        if not memories:
            log("No memories to extract from session")
            return

        # Store each memory
        stored = 0
        for memory in memories[:10]:  # Limit to 10 memories per session
            if send_memory(
                memory["content"],
                memory["type"],
                memory["level"],
                memory["salience"],
            ):
                stored += 1

        log(f"Session complete: stored {stored}/{len(memories)} memories")

    except json.JSONDecodeError:
        log("Invalid JSON from session", "error")
    except Exception as e:
        log(f"Session hook error: {e}", "error")

    sys.exit(0)


if __name__ == "__main__":
    main()
