#!/usr/bin/env python3
"""Mind Session End Hook - LLM-Driven Memory Extraction.

This hook uses an LLM to intelligently extract memories from conversations,
similar to how Mem0, Zep, and ChatGPT handle automatic memory capture.

SAFETY:
- Only runs once at session end
- Read-only: never touches project files
- Fire-and-forget with timeout
- Fail-silent: errors logged externally

DIFFERENCE FROM RULE-BASED:
- Rule-based: looks for keywords like "I prefer", "always use"
- LLM-driven: understands context and extracts what matters

Usage in .claude/settings.json:
{
  "hooks": {
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook_llm.py"
  }
}

Requires: ANTHROPIC_API_KEY environment variable
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
MIND_API_URL = os.environ.get("MIND_API_URL", "http://127.0.0.1:8000")
USER_ID = os.environ.get("MIND_USER_ID", "550e8400-e29b-41d4-a716-446655440000")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TIMEOUT_SECONDS = 30.0  # LLM calls need more time
LOG_DIR = Path.home() / ".mind" / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Memory extraction prompt - this is what makes it intelligent
EXTRACTION_PROMPT = """Analyze this Claude Code conversation and extract important memories.

For each memory, categorize it:

TEMPORAL LEVELS:
- 1 (immediate): Current session context, will fade in hours
- 2 (situational): Recent patterns, days to weeks
- 3 (seasonal): Recurring behaviors, months
- 4 (identity): Core preferences, years

MEMORY TYPES:
- preference: User likes/dislikes, coding style choices
- decision: Important choices made and why
- fact: Information about the user/project
- goal: What user is trying to achieve
- observation: Patterns noticed during work
- problem: Issues encountered and solutions found

SALIENCE (0.0 to 1.0):
- 1.0: Critical, always relevant
- 0.8: Important, frequently useful
- 0.5: Useful context
- 0.3: Minor detail

Extract 3-10 memories from this conversation. Focus on:
1. User preferences (coding style, tools, patterns they like)
2. Project decisions and their rationale
3. Problems solved and how
4. Recurring patterns
5. Goals and intentions

Return JSON array:
[
  {
    "content": "Short memory description",
    "type": "preference|decision|fact|goal|observation|problem",
    "temporal_level": 1-4,
    "salience": 0.0-1.0,
    "reason": "Why this is worth remembering"
  }
]

CONVERSATION:
{conversation}

Return ONLY the JSON array, no other text."""


def log(message: str, level: str = "info"):
    """Log to external file."""
    try:
        log_file = LOG_DIR / "session_hook_llm.log"
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

        with urllib.request.urlopen(req, timeout=10.0) as resp:
            if resp.status == 201:
                log(f"Memory stored: {content[:50]}...")
                return True
    except Exception as e:
        log(f"Failed to store memory: {e}", "error")

    return False


def extract_with_llm(conversation_text: str) -> list[dict]:
    """Use Claude to extract memories from conversation.

    This is the key difference from rule-based extraction.
    The LLM understands context and decides what's important.
    """
    if not ANTHROPIC_API_KEY:
        log("No ANTHROPIC_API_KEY, falling back to rule-based extraction", "warn")
        return []

    try:
        import urllib.request
        import urllib.error

        # Truncate conversation to fit in context window
        max_chars = 50000  # ~12k tokens
        if len(conversation_text) > max_chars:
            conversation_text = conversation_text[:max_chars] + "\n... [truncated]"

        prompt = EXTRACTION_PROMPT.format(conversation=conversation_text)

        data = json.dumps({
            "model": "claude-3-5-haiku-20241022",  # Fast and cheap
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            response_text = result["content"][0]["text"]

            # Parse JSON from response
            memories = json.loads(response_text)
            log(f"LLM extracted {len(memories)} memories")
            return memories

    except json.JSONDecodeError as e:
        log(f"Failed to parse LLM response as JSON: {e}", "error")
    except Exception as e:
        log(f"LLM extraction failed: {e}", "error")

    return []


def format_conversation(session_data: dict) -> str:
    """Format session data into readable conversation."""
    lines = []

    messages = session_data.get("messages", [])
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if content:
            lines.append(f"{role.upper()}: {content[:1000]}")

    # Add tool uses summary
    tool_uses = session_data.get("tool_uses", [])
    if tool_uses:
        lines.append("\n--- TOOL USAGE SUMMARY ---")
        for tool in tool_uses[:20]:  # Limit to 20
            name = tool.get("name", "unknown")
            input_data = tool.get("input", {})
            # Only include meaningful tool info
            if name in ["Write", "Edit"]:
                file_path = input_data.get("file_path", "unknown")
                lines.append(f"TOOL: {name} on {file_path}")
            elif name == "Bash":
                cmd = input_data.get("command", "")[:100]
                lines.append(f"TOOL: Bash - {cmd}")

    return "\n".join(lines)


def rule_based_fallback(session_data: dict) -> list[dict]:
    """Fallback to rule-based extraction if LLM unavailable.

    This is the original approach - less intelligent but works without API.
    """
    memories = []

    summary = session_data.get("summary", "")
    if summary:
        memories.append({
            "content": f"Session summary: {summary}",
            "type": "observation",
            "temporal_level": 2,
            "salience": 0.8,
        })

    messages = session_data.get("messages", [])
    user_messages = [m for m in messages if m.get("role") == "user"]

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
                    "temporal_level": 4,
                    "salience": 0.9,
                })
                break

    working_dir = session_data.get("cwd", "")
    if working_dir:
        project_name = Path(working_dir).name
        memories.append({
            "content": f"Worked on project: {project_name}",
            "type": "observation",
            "temporal_level": 2,
            "salience": 0.6,
        })

    return memories


def main():
    """Process session end and extract memories using LLM."""
    try:
        session_input = sys.stdin.read()
        if not session_input.strip():
            log("No session data received")
            return

        session_data = json.loads(session_input)
        log("Processing session end with LLM extraction")

        # Try LLM extraction first
        conversation_text = format_conversation(session_data)
        memories = extract_with_llm(conversation_text)

        # Fall back to rule-based if LLM fails
        if not memories:
            log("Falling back to rule-based extraction")
            memories = rule_based_fallback(session_data)

        if not memories:
            log("No memories to extract from session")
            return

        # Store each memory
        stored = 0
        for memory in memories[:10]:  # Limit to 10
            if send_memory(
                memory.get("content", ""),
                memory.get("type", "observation"),
                memory.get("temporal_level", 2),
                memory.get("salience", 0.7),
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
