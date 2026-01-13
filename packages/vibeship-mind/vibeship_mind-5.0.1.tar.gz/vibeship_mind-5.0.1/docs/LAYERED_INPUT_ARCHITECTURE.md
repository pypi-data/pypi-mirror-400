# Layered Input Architecture for Mind v5

## The Problem

No single input method is 100% reliable:
- **MCP tools**: Claude sometimes forgets to call them
- **Hooks**: Can miss context if session ends abnormally
- **API extraction**: Costs money

## The Solution: Layered Redundancy

Use ALL input methods together. If one fails, others catch it.

```
                     USER CONVERSATION
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Layer 1 │        │ Layer 2 │        │ Layer 3 │
   │   MCP   │        │  Hooks  │        │   API   │
   │ (live)  │        │ (auto)  │        │ (opt)   │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    ┌─────────────┐
                    │ Deduplication │
                    │   Layer     │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │  Mind API   │
                    └─────────────┘
```

---

## Layer 1: MCP Tools (Real-Time)

**How it works**: Claude calls `mind_remember` during conversation.

**When it fires**: Whenever Claude notices something important.

**Reliability**: ~70% (Claude sometimes forgets)

**Setup**:
```json
// claude_desktop_config.json or .claude/settings.json
{
  "mcpServers": {
    "mind": {
      "command": "python",
      "args": ["-m", "mind.mcp"],
      "cwd": "C:\\Users\\USER\\Desktop\\the-mind\\vibeship-mind",
      "env": {
        "MIND_API_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

**Plus CLAUDE.md instructions**:
```markdown
## Memory System

PROACTIVELY call mind_remember when you notice:
- User preferences ("I prefer...", "I like...")
- Decisions made and why
- Problems solved and solutions
- User corrections
- Recurring patterns

Don't wait for permission. Save memories AS THEY HAPPEN.
```

---

## Layer 2: Hooks (Automatic Backup)

**How it works**: Hooks fire automatically on events.

**When it fires**:
- Per-message hook: After significant tool uses (Write, Edit, Bash)
- Session-end hook: When conversation ends

**Reliability**: ~95% (fails only if process crashes)

**Setup**:
```json
// .claude/settings.json
{
  "hooks": {
    "postToolUse": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/mind_hook.py",
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook.py"
  }
}
```

### Hook Files

**Per-message hook** (`hooks/mind_hook.py`):
- Captures file modifications, git commits, package installs
- Fire-and-forget (2s timeout)
- Filters out noise (Read, Glob, Grep ignored)

**Session-end hook** (`hooks/session_end_hook.py`):
- Runs once when Claude exits
- Extracts preferences from user messages
- Tracks project worked on
- Captures tool usage patterns

---

## Layer 3: LLM API Extraction (Optional, Highest Quality)

**How it works**: Sends session to an LLM for intelligent extraction.

**When it fires**: At session end (if enabled).

**Reliability**: ~99% (depends on API availability)

**Cost**: ~$0.001/session with Claude 3.5 Haiku

**Setup**:
```json
// .claude/settings.json (use INSTEAD of basic session hook)
{
  "hooks": {
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook_llm.py"
  }
}
```

**Requires**: `ANTHROPIC_API_KEY` environment variable.

**Fallback**: If no API key, automatically uses rule-based extraction.

---

## Deduplication

When multiple layers capture the same memory, Mind v5 deduplicates:

1. **Content hashing**: Similar memories merged
2. **Temporal proximity**: Same memory within 5 minutes = dedupe
3. **Salience boost**: If captured by multiple layers, salience increases

---

## Recommended Configuration

### For Maximum Reliability (Free)

Use Layers 1 + 2:

```json
// .claude/settings.json
{
  "hooks": {
    "postToolUse": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/mind_hook.py",
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook.py"
  }
}
```

Plus MCP server configured and CLAUDE.md instructions.

### For Maximum Quality (Paid)

Use all three layers:

```json
// .claude/settings.json
{
  "hooks": {
    "postToolUse": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/mind_hook.py",
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook_llm.py"
  }
}
```

Plus MCP server and CLAUDE.md.

---

## What Gets Captured

| Input Source | Captures | Temporal Level |
|--------------|----------|----------------|
| MCP (Claude calls) | Preferences, decisions, patterns | 3-4 (long-term) |
| Per-message hook | File changes, git commits | 2 (situational) |
| Session-end hook | Session summary, preferences | 2-4 (varies) |
| LLM extraction | Everything intelligent | 2-4 (contextual) |

---

## Testing Your Setup

1. **Check Mind API**: `curl http://127.0.0.1:8000/health`
2. **Check logs**: `~/.mind/logs/hook_activity.log`
3. **Check dashboard**: `http://127.0.0.1:8501`
4. **Verify memories**: Look for new memories after a session
