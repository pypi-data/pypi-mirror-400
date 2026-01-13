#!/usr/bin/env python3
"""Mind Hook for Claude Code - Safe Fire-and-Forget Memory Capture.

SAFETY PRINCIPLES:
1. READ-ONLY: Never writes to project files
2. FIRE-AND-FORGET: Async HTTP with 2s timeout
3. FAIL-SILENT: Errors logged externally, never blocks Claude
4. NON-BLOCKING: Returns immediately, processing happens in background

This hook captures conversation context and sends it to the Mind API
for memory extraction. The API decides what's worth remembering.

Usage in .claude/settings.json:
{
  "hooks": {
    "postToolUse": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/mind_hook.py"
  }
}
"""

import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

# Configuration
MIND_API_URL = os.environ.get("MIND_API_URL", "http://127.0.0.1:8000")
USER_ID = os.environ.get("MIND_USER_ID", "550e8400-e29b-41d4-a716-446655440000")
TIMEOUT_SECONDS = 2.0  # Never block longer than this
LOG_DIR = Path.home() / ".mind" / "logs"  # Log outside project directory

# Ensure log directory exists (outside project!)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_error(message: str):
    """Log error to external file (never to project directory)."""
    try:
        log_file = LOG_DIR / "hook_errors.log"
        timestamp = datetime.now().isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {message}\n")
    except Exception:
        pass  # Fail completely silently


def log_activity(message: str):
    """Log activity to external file (never to project directory)."""
    try:
        log_file = LOG_DIR / "hook_activity.log"
        timestamp = datetime.now().isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {message}\n")
    except Exception:
        pass


def send_to_mind_async(content: str, content_type: str = "observation"):
    """Send content to Mind API in background thread with timeout."""
    def _send():
        try:
            import urllib.request
            import urllib.error

            data = json.dumps({
                "user_id": USER_ID,
                "content": content[:2000],  # Limit content size
                "content_type": content_type,
                "temporal_level": 2,  # Situational by default
                "salience": 0.7,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{MIND_API_URL}/v1/memories/",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                if resp.status == 201:
                    log_activity(f"Memory stored: {content[:50]}...")
                else:
                    log_error(f"API returned {resp.status}")

        except urllib.error.URLError as e:
            log_error(f"API unreachable: {e}")
        except Exception as e:
            log_error(f"Send failed: {e}")

    # Run in background thread - don't block
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    # Don't wait for thread - return immediately


def should_capture(hook_data: dict) -> tuple[bool, str, str]:
    """Decide if this hook event should create a memory.

    Returns: (should_capture, content, content_type)

    Filtering logic:
    - Skip routine tool calls (Read, Glob, Grep)
    - Capture significant actions (Write, Edit, Bash commits)
    - Capture user preferences and decisions
    """
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})
    tool_output = hook_data.get("tool_output", "")

    # Skip routine read operations - too noisy
    if tool_name in ["Read", "Glob", "Grep", "LSP"]:
        return False, "", ""

    # Capture file modifications
    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "unknown")
        # Don't log the actual content (privacy), just the action
        return True, f"Modified file: {Path(file_path).name}", "observation"

    # Capture bash commands (especially git operations)
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        # Git commits are significant decisions
        if "git commit" in command:
            return True, f"Git commit made", "event"
        # Other significant commands
        if any(cmd in command for cmd in ["npm install", "pip install", "docker"]):
            return True, f"Environment change: {command[:100]}", "observation"
        return False, "", ""

    # Capture task completions
    if tool_name == "TodoWrite":
        todos = tool_input.get("todos", [])
        completed = [t for t in todos if t.get("status") == "completed"]
        if completed:
            return True, f"Completed tasks: {[t['content'][:50] for t in completed[:3]]}", "event"
        return False, "", ""

    # Skip other tools by default
    return False, "", ""


def main():
    """Main hook entry point - MUST return quickly."""
    try:
        # Read hook data from stdin (Claude passes JSON)
        hook_input = sys.stdin.read()
        if not hook_input.strip():
            return  # No input, exit cleanly

        hook_data = json.loads(hook_input)

        # Decide if we should capture this
        should, content, content_type = should_capture(hook_data)

        if should and content:
            # Fire and forget - don't wait
            send_to_mind_async(content, content_type)

    except json.JSONDecodeError:
        log_error("Invalid JSON from hook")
    except Exception as e:
        log_error(f"Hook error: {e}")

    # Always exit cleanly and quickly
    sys.exit(0)


if __name__ == "__main__":
    main()
