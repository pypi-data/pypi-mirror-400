# Memory Capture Strategies for Mind v5

## The Problem

Claude doesn't automatically remember things between sessions. We need a way to:
1. Capture important context during conversations
2. Store it in Mind for future retrieval
3. Do this **safely** without corrupting files or blocking Claude

## Strategy Comparison

| Strategy | Reliability | Safety | Effort | Best For |
|----------|-------------|--------|--------|----------|
| MCP Server | Medium | High | Low | When Claude remembers to use it |
| Per-Message Hook | High | Medium | Medium | Automatic capture, needs careful design |
| Session-End Hook | High | Very High | Medium | Batch processing, safest option |
| CLAUDE.md Reinforcement | Medium | Very High | Low | Reminding Claude to use Mind |
| Polling/Observer | High | Very High | High | Completely decoupled capture |

## Recommended Approach: Layered Strategy

Use **multiple strategies together** for maximum reliability:

```
Layer 1: CLAUDE.md Instructions (always present)
    ↓
Layer 2: Session-End Hook (safe batch processing)
    ↓
Layer 3: MCP Tools (for explicit memory operations)
    ↓
Layer 4: Per-Message Hook (optional, for real-time capture)
```

---

## Strategy 1: Session-End Hook (RECOMMENDED)

**Safest option.** Only runs when Claude exits, processes entire conversation.

### Setup
```json
// .claude/settings.json
{
  "hooks": {
    "stop": ["python", "C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook.py"]
  }
}
```

### How It Works
1. During conversation: Claude works normally
2. When session ends: Hook receives conversation summary
3. Hook extracts meaningful memories (preferences, decisions, patterns)
4. Sends batch to Mind API
5. Exits cleanly

### Why It's Safe
- No interference during active work
- Single point of processing
- Can take more time to analyze
- If it fails, only one session is affected

---

## Strategy 2: Per-Message Hook (USE WITH CAUTION)

**Higher risk.** Runs on every tool call. Must be extremely fast.

### Setup
```json
// .claude/settings.json
{
  "hooks": {
    "postToolUse": ["python", "C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/mind_hook.py"]
  }
}
```

### Safety Rules (CRITICAL)
1. **NEVER write to project files** - only HTTP calls
2. **2-second timeout max** - abandon if slow
3. **Fire-and-forget** - don't wait for response
4. **Fail silently** - log errors externally, never crash
5. **Filter aggressively** - don't capture Read/Glob/Grep

### What Gets Captured
- File modifications (Write, Edit)
- Git commits
- Package installations
- Task completions

### What Gets Ignored
- Read operations (too noisy)
- Search operations (not meaningful)
- LSP calls (internal)

---

## Strategy 3: MCP Server

**Most flexible.** Claude can explicitly store and retrieve memories.

### Setup
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

### Available Tools
- `mind_remember(user_id, content, ...)` - Store a memory
- `mind_retrieve(user_id, query, ...)` - Search memories
- `mind_decide(...)` - Track decision outcomes

### Limitation
Claude must remember to call these tools. Works best with CLAUDE.md reinforcement.

---

## Strategy 4: CLAUDE.md Reinforcement

**Zero risk.** Just instructions that remind Claude to use Mind.

### Add to Project CLAUDE.md
```markdown
## Memory Integration

This project uses Mind v5 for context memory. At session start and end:

1. **Start of session**: Call `mind_retrieve` to get relevant past context
2. **During work**: Note important decisions and preferences
3. **End of session**: Call `mind_remember` to store what was learned

Key things to remember:
- User preferences (coding style, tools, patterns)
- Project decisions and their rationale
- Problems solved and solutions found
- Patterns that work or don't work
```

---

## Strategy 5: Polling/Observer (Advanced)

**Most decoupled.** A separate process that watches for activity.

### Concept
1. Background service runs independently
2. Watches Claude's conversation logs/output
3. Extracts and stores memories
4. Never interferes with Claude

### Implementation
Would require:
- Finding where Claude logs conversations
- Parsing log format
- Running as a Windows service

This is the safest but requires more setup.

---

## My Recommendation

Start with this combination:

1. **CLAUDE.md instructions** (immediate, zero risk)
2. **Session-end hook with LLM** (automatic, intelligent, safe)
3. **MCP server** (for explicit operations)

Skip per-message hooks until you're confident the system is stable.

---

## LLM-Driven vs Rule-Based Extraction

### The Industry Standard: LLM-Driven

Major memory systems (Mem0, Zep, ChatGPT) use **LLM-driven extraction**:

> "When you add a conversation to memory, it automatically extracts the important bits."
> — Mem0 Documentation

> "Classification models identify information that looks important or useful."
> — OpenAI on ChatGPT Memory

### How It Works

**Rule-Based (Original):**
```python
# Looks for keywords
if "i prefer" in content.lower():
    save_as_preference(content)
```

**LLM-Driven (Enhanced):**
```python
# Asks an LLM to understand and extract
memories = claude.analyze(
    "Extract preferences, decisions, and patterns from this conversation"
)
```

### The Difference

| Approach | Catches | Misses |
|----------|---------|--------|
| **Rule-based** | "I prefer tabs" | "Tabs work better for this codebase" |
| **LLM-driven** | Both | (Much less) |

### Setup for LLM-Driven Extraction

```json
// .claude/settings.json
{
  "hooks": {
    "stop": "python C:/Users/USER/Desktop/the-mind/vibeship-mind/hooks/session_end_hook_llm.py"
  }
}
```

**Required:** Set `ANTHROPIC_API_KEY` environment variable.

Uses Claude 3.5 Haiku (fast, cheap ~$0.001/session) to analyze conversations.

### Fallback Behavior

If `ANTHROPIC_API_KEY` is not set, automatically falls back to rule-based extraction.
This ensures the system works even without API access.

### Testing Safely

Before enabling hooks in your main environment:

1. Test with a throwaway project first
2. Monitor `~/.mind/logs/` for errors
3. Check that Mind API is running (`curl http://127.0.0.1:8000/health`)
4. Start with session-end hook only
5. Add per-message hook only if needed

---

## Troubleshooting

### Hook not firing
- Check hook path is absolute
- Check Python is in PATH
- Check `.claude/settings.json` syntax

### Memories not stored
- Check Mind API is running: `curl http://127.0.0.1:8000/health`
- Check logs: `~/.mind/logs/hook_errors.log`
- Check USER_ID matches your dashboard

### Claude slow/hanging
- Hook is taking too long
- Reduce timeout to 1 second
- Check API is responsive

### Files corrupted
- Hook is writing to project (BUG - should never happen)
- Check hook code for any file writes
- Disable hook immediately
