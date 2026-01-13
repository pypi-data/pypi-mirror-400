#!/usr/bin/env python3
"""Mind Session Save Hook - Save session for next-session extraction.

This hook runs when Claude Code exits and saves the session data
to a file. The NEXT session will extract memories using Claude itself,
so there's no extra API cost - it uses your existing Claude subscription.

FLOW:
1. Session ends → This hook saves session to ~/.mind/pending_sessions/
2. Next session starts → Claude reads pending sessions
3. Claude extracts memories using mind_remember (uses your Claude Max)
4. Pending session file is deleted

SAFETY:
- Only writes to ~/.mind/ (never project files)
- Fail-silent
- Quick execution (just file write)

Usage in .claude/settings.json:
{
  "hooks": {
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_save_hook.py"
  }
}
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Configuration
PENDING_DIR = Path.home() / ".mind" / "pending_sessions"
LOG_DIR = Path.home() / ".mind" / "logs"
MAX_PENDING = 10  # Keep last 10 sessions max

# Ensure directories exist
PENDING_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "info"):
    """Log to external file."""
    try:
        log_file = LOG_DIR / "session_save.log"
        timestamp = datetime.now().isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {level.upper()} | {message}\n")
    except Exception:
        pass


def clean_old_sessions():
    """Remove old pending sessions if too many."""
    try:
        sessions = sorted(PENDING_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
        while len(sessions) > MAX_PENDING:
            oldest = sessions.pop(0)
            oldest.unlink()
            log(f"Cleaned old session: {oldest.name}")
    except Exception as e:
        log(f"Failed to clean old sessions: {e}", "error")


def extract_key_content(session_data: dict) -> dict:
    """Extract just the important parts to keep file small."""
    result = {
        "session_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "cwd": session_data.get("cwd", ""),
    }

    # Extract user messages (most important for preferences)
    messages = session_data.get("messages", [])
    user_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if content and len(content) > 10:  # Skip very short messages
                user_messages.append(content[:1000])  # Limit each message

    result["user_messages"] = user_messages[:20]  # Max 20 messages

    # Extract summary if available
    if session_data.get("summary"):
        result["summary"] = session_data["summary"][:2000]

    # Extract significant tool uses
    tool_uses = session_data.get("tool_uses", [])
    significant_tools = []
    for tool in tool_uses:
        name = tool.get("name", "")
        if name in ["Write", "Edit", "Bash"]:
            tool_input = tool.get("input", {})
            if name == "Bash":
                cmd = tool_input.get("command", "")
                if any(x in cmd for x in ["git commit", "npm install", "pip install"]):
                    significant_tools.append({"name": name, "cmd": cmd[:200]})
            else:
                file_path = tool_input.get("file_path", "")
                significant_tools.append({"name": name, "file": Path(file_path).name})

    result["significant_tools"] = significant_tools[:10]

    return result


def main():
    """Save session data for next-session extraction."""
    try:
        session_input = sys.stdin.read()
        if not session_input.strip():
            log("No session data received")
            return

        session_data = json.loads(session_input)

        # Extract key content (keep it small)
        key_content = extract_key_content(session_data)

        # Skip if nothing meaningful
        if not key_content.get("user_messages") and not key_content.get("summary"):
            log("Session has no meaningful content to save")
            return

        # Save to pending directory
        session_file = PENDING_DIR / f"{key_content['session_id']}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(key_content, f, indent=2)

        log(f"Session saved: {session_file.name}")

        # Clean old sessions
        clean_old_sessions()

    except json.JSONDecodeError:
        log("Invalid JSON from session", "error")
    except Exception as e:
        log(f"Session save error: {e}", "error")

    sys.exit(0)


if __name__ == "__main__":
    main()
