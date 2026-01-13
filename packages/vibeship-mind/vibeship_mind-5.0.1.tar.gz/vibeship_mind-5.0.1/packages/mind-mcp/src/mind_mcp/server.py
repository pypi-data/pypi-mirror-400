"""Mind MCP Server with friendly responses.

This is the user-facing MCP server that connects to either:
- Mind Cloud (default, no setup needed)
- Local Mind instance (for self-hosted users)
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel

# Configuration
MIND_CLOUD_URL = "https://api.mind.vibeship.ai"
MIND_LOCAL_URL = "http://localhost:8080"
CONFIG_DIR = Path.home() / ".mind"
CONFIG_FILE = CONFIG_DIR / "config.json"

console = Console()

# Session ID for tracking interactions within a session
_session_id: Optional[str] = None


def get_session_id() -> str:
    """Get or create session ID for this MCP session."""
    global _session_id
    if _session_id is None:
        _session_id = str(uuid4())
    return _session_id


# Initialize FastMCP server
mcp = FastMCP(
    name="mind",
    instructions="""Mind - Decision Intelligence for AI Agents.

Mind helps you remember user preferences and learn from decision outcomes.

Tools:
- mind_remember: Store something important about the user
- mind_retrieve: Get relevant memories for a decision
- mind_decide: Record a decision and its outcome (for learning)
- mind_record_interaction: Record user message for automatic memory extraction
- mind_health: Check Mind API health status

Best Practice:
1. Call mind_record_interaction with the user's message at the start
2. Use mind_retrieve before making recommendations
3. Use mind_decide after user gives feedback
4. Mind automatically extracts memories from recorded interactions
""",
)


class Config(BaseModel):
    """Mind configuration."""
    api_key: Optional[str] = None
    api_url: str = MIND_CLOUD_URL
    user_id: Optional[str] = None
    friendly_mode: bool = True
    first_run: bool = True


def load_config() -> Config:
    """Load config from ~/.mind/config.json"""
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return Config(**data)
        except Exception:
            pass
    return Config()


def save_config(config: Config) -> None:
    """Save config to ~/.mind/config.json"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(config.model_dump_json(indent=2))


def get_api_url() -> str:
    """Get the Mind API URL."""
    # Check environment first
    if os.environ.get("MIND_API_URL"):
        return os.environ["MIND_API_URL"]

    # Check config
    config = load_config()
    return config.api_url


def get_user_id() -> str:
    """Get or create user ID."""
    config = load_config()
    if not config.user_id:
        config.user_id = str(uuid4())
        save_config(config)
    return config.user_id


# Friendly response formatters
def format_memory_stored(memory: dict, is_first: bool = False) -> str:
    """Format memory creation response."""
    level_names = {1: "Immediate", 2: "Situational", 3: "Seasonal", 4: "Identity"}
    level_desc = {
        1: "short-term context",
        2: "recent patterns",
        3: "recurring themes",
        4: "core preference"
    }

    level = memory.get("temporal_level", 2)
    level_name = level_names.get(level, "Situational")
    level_info = level_desc.get(level, "general memory")

    response = f"""Memory stored!

Content: "{memory.get('content', '')[:100]}..."
Level: {level_name} ({level_info})
Salience: {memory.get('effective_salience', 1.0):.0%}

"""

    if is_first:
        response += """This is your first memory! Mind will use this to give better recommendations.

Tip: Store preferences at the Identity level (4) for permanent memories.
"""

    return response


def format_retrieval(result: dict) -> str:
    """Format retrieval response."""
    memories = result.get("memories", [])
    latency = result.get("latency_ms", 0)

    if not memories:
        return "No relevant memories found. Try storing some memories first!"

    response = f"Found {len(memories)} relevant memories ({latency:.0f}ms):\n\n"

    for i, mem in enumerate(memories, 1):
        score = result.get("scores", {}).get(mem["memory_id"], 0)
        response += f"{i}. \"{mem['content'][:80]}...\"\n"
        response += f"   Relevance: {score:.0%} | Level: {mem.get('temporal_level_name', 'unknown')}\n\n"

    response += "\nUse these memories to inform your response."

    return response


def format_decision(result: dict) -> str:
    """Format decision outcome response."""
    memories_updated = result.get("memories_updated", 0)
    changes = result.get("salience_changes", {})
    quality = result.get("outcome_quality", 0)

    if quality > 0:
        emoji = "positive"
        direction = "increased"
    elif quality < 0:
        emoji = "negative"
        direction = "decreased"
    else:
        emoji = "neutral"
        direction = "unchanged"

    response = f"""Outcome recorded ({emoji})!

Quality: {quality:+.0%}
Memories updated: {memories_updated}

"""

    if changes:
        response += "Salience changes:\n"
        for mid, delta in changes.items():
            response += f"  Memory {mid[:8]}...: {delta:+.2f}\n"
        response += f"\nThese memories will rank {'higher' if quality > 0 else 'lower'} in future retrievals."

    return response


# HTTP client for Mind API
async def mind_api(method: str, path: str, data: dict = None) -> dict:
    """Make request to Mind API."""
    url = f"{get_api_url()}{path}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        else:
            raise ValueError(f"Unknown method: {method}")

        response.raise_for_status()
        return response.json()


@mcp.tool()
async def mind_remember(
    content: str,
    content_type: str = "observation",
    temporal_level: int = 2,
    salience: float = 1.0,
) -> str:
    """Store a memory for the user.

    Use this to remember important information about the user that should
    influence future recommendations.

    Args:
        content: What to remember (e.g., "User prefers TypeScript")
        content_type: Type of memory - fact, preference, event, goal, observation
        temporal_level: How long to remember:
            1 = Immediate (hours) - current session context
            2 = Situational (days) - recent patterns
            3 = Seasonal (months) - recurring themes
            4 = Identity (permanent) - core preferences
        salience: Importance from 0.0 to 1.0 (default 1.0)

    Returns:
        Confirmation with memory details
    """
    user_id = get_user_id()
    config = load_config()
    is_first = config.first_run

    result = await mind_api("POST", "/v1/memories/", {
        "user_id": user_id,
        "content": content,
        "content_type": content_type,
        "temporal_level": temporal_level,
        "salience": salience,
    })

    if is_first:
        config.first_run = False
        save_config(config)

    if config.friendly_mode:
        return format_memory_stored(result, is_first)

    return json.dumps(result, indent=2)


@mcp.tool()
async def mind_retrieve(
    query: str,
    limit: int = 5,
    min_salience: float = 0.0,
) -> str:
    """Retrieve relevant memories for a decision.

    Use this before making recommendations to get context about the user.

    Args:
        query: What you're trying to decide (e.g., "What tech stack to recommend?")
        limit: Maximum memories to return (default 5)
        min_salience: Minimum importance threshold (0.0-1.0)

    Returns:
        Relevant memories with scores
    """
    user_id = get_user_id()
    config = load_config()

    result = await mind_api("POST", "/v1/memories/retrieve", {
        "user_id": user_id,
        "query": query,
        "limit": limit,
        "min_salience": min_salience,
    })

    if config.friendly_mode:
        return format_retrieval(result)

    return json.dumps(result, indent=2)


@mcp.tool()
async def mind_decide(
    memory_ids: list[str],
    decision_summary: str,
    outcome_quality: float,
    outcome_signal: str = "agent_feedback",
    feedback: str = None,
) -> str:
    """Record a decision and its outcome for learning.

    Call this after the user gives feedback on a recommendation.
    Positive outcomes make memories rank higher, negative lower.

    Args:
        memory_ids: IDs of memories that influenced the decision
        decision_summary: Short summary of what was decided
        outcome_quality: How well it worked (-1.0 to 1.0)
            1.0 = User loved it
            0.5 = User liked it
            0.0 = Neutral
            -0.5 = User disliked it
            -1.0 = User hated it
        outcome_signal: How outcome was detected:
            - user_accepted: User explicitly approved
            - user_rejected: User explicitly rejected
            - task_completed: Task finished successfully
            - agent_feedback: Your assessment
        feedback: Optional text feedback

    Returns:
        Learning confirmation with salience changes
    """
    user_id = get_user_id()
    config = load_config()

    # Track decision
    track_result = await mind_api("POST", "/v1/decisions/track", {
        "user_id": user_id,
        "session_id": str(uuid4()),
        "memory_ids": memory_ids,
        "memory_scores": {mid: 1.0 / len(memory_ids) for mid in memory_ids},
        "decision_type": "recommendation",
        "decision_summary": decision_summary,
        "confidence": 0.8,
    })

    # Record outcome
    outcome_result = await mind_api("POST", "/v1/decisions/outcome", {
        "trace_id": track_result["trace_id"],
        "quality": outcome_quality,
        "signal": outcome_signal,
        "feedback": feedback,
    })

    if config.friendly_mode:
        return format_decision(outcome_result)

    return json.dumps(outcome_result, indent=2)


@mcp.tool()
async def mind_record_interaction(
    content: str,
    interaction_type: str = "text",
    context: dict = None,
    skip_extraction: bool = False,
) -> str:
    """Record a user interaction for automatic memory extraction.

    Call this at the start of processing a user message. Mind will
    automatically extract relevant memories from the interaction content.

    Args:
        content: The user's message or interaction content
        interaction_type: Type of interaction:
            - text: Regular text message (default)
            - voice_transcript: Transcribed voice
            - action: User action (clicked, selected, etc.)
            - feedback: Explicit feedback (thumbs up/down)
            - command: System command
        context: Additional context for extraction:
            - previous_turns: List of recent conversation turns
            - current_task: What the user is working on
        skip_extraction: Set to true to skip memory extraction

    Returns:
        Confirmation that interaction was recorded
    """
    user_id = get_user_id()
    session_id = get_session_id()
    config = load_config()

    try:
        result = await mind_api("POST", "/v1/interactions/record", {
            "user_id": user_id,
            "session_id": session_id,
            "content": content,
            "interaction_type": interaction_type,
            "context": context or {},
            "extraction_priority": "normal",
            "skip_extraction": skip_extraction,
        })

        if config.friendly_mode:
            queued = result.get("extraction_queued", False)
            if queued:
                return f"Interaction recorded. Memory extraction queued."
            else:
                return f"Interaction recorded (extraction skipped)."

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Failed to record interaction: {str(e)}"


@mcp.tool()
async def mind_health() -> str:
    """Check Mind API health status.

    Returns:
        Health status including API version
    """
    user_id = get_user_id()
    config = load_config()

    try:
        health = await mind_api("GET", "/health")

        # Get memory count
        retrieve = await mind_api("POST", "/v1/memories/retrieve", {
            "user_id": user_id,
            "query": "*",
            "limit": 100,
        })

        memory_count = len(retrieve.get("memories", []))

        return f"""Mind Status: Online

API: {get_api_url()}
User ID: {user_id[:8]}...
Memories: {memory_count}
Mode: {'Friendly' if config.friendly_mode else 'JSON'}

Mind is ready to help you make better decisions!
"""

    except Exception as e:
        return f"""Mind Status: Offline

Error: {str(e)}

Troubleshooting:
1. If using local: Is Docker running? Run `docker-compose up -d`
2. If using cloud: Check your internet connection
3. Run `uvx vibeship-mind --setup` to reconfigure
"""


def show_welcome():
    """Show welcome message on first run."""
    console.print(Panel(
        """[bold green]Welcome to Mind![/bold green]

Mind helps AI agents remember and learn from decisions.

[bold]Quick Start:[/bold]
1. Add Mind to Claude Code or Claude Desktop
2. Start chatting - Mind works automatically
3. Give feedback - Mind learns and improves

[bold]Claude Code:[/bold]
  claude mcp add mind "uvx vibeship-mind"

[bold]Claude Desktop:[/bold]
Add to config (macOS: ~/Library/Application Support/Claude/claude_desktop_config.json):

{
    "mcpServers": {
        "mind": {
            "command": "uvx",
            "args": ["vibeship-mind"]
        }
    }
}

[bold]Commands:[/bold]
  uvx vibeship-mind          Start MCP server (Mind Cloud)
  uvx vibeship-mind --local  Use local Docker instance
  uvx vibeship-mind --setup  Show this guide

[dim]Learn more: https://mind.vibeship.ai[/dim]
""",
        title="Mind v0.1.0",
        border_style="green",
    ))


def run_server():
    """Run the MCP server."""
    mcp.run()


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Mind MCP Server")
    parser.add_argument("--setup", action="store_true", help="Configure Mind")
    parser.add_argument("--local", action="store_true", help="Use local Mind instance")
    parser.add_argument("--json", action="store_true", help="Use JSON responses (not friendly)")
    parser.add_argument("--version", action="store_true", help="Show version")

    args = parser.parse_args()

    if args.version:
        print("vibeship-mind v0.1.0")
        return

    if args.setup:
        show_welcome()
        return

    config = load_config()

    if args.local:
        config.api_url = MIND_LOCAL_URL
        save_config(config)
        console.print(f"[green]Using local Mind instance: {MIND_LOCAL_URL}[/green]")

    if args.json:
        config.friendly_mode = False
        save_config(config)

    if config.first_run:
        show_welcome()
        config.first_run = False
        save_config(config)

    run_server()


if __name__ == "__main__":
    main()
