# Mind Memory Instructions for CLAUDE.md

Add this to your project's CLAUDE.md to enable real-time memory capture.

---

## Memory Integration (Copy this to your CLAUDE.md)

```markdown
## Memory System

This project uses Mind v5 for persistent memory. YOU are the memory worker.

### Real-Time Memory Capture

As you work, AUTOMATICALLY call `mind_remember` when you notice:

| Trigger | What to Save | Temporal Level |
|---------|--------------|----------------|
| User says "I prefer...", "I like...", "always use..." | The preference | 4 (identity) |
| User makes a decision with rationale | Decision + why | 3 (seasonal) |
| You solve a problem | Problem + solution | 3 (seasonal) |
| User corrects you | What was wrong + correct approach | 4 (identity) |
| Pattern emerges (user does X repeatedly) | The pattern | 3 (seasonal) |
| Project-specific fact learned | The fact | 2 (situational) |

### How to Call

```
mind_remember(
  user_id="550e8400-e29b-41d4-a716-446655440000",
  content="User prefers tabs over spaces for Python",
  content_type="preference",
  temporal_level=4,
  salience=0.9
)
```

### When to Retrieve

At the START of significant tasks, call:
```
mind_retrieve(
  user_id="550e8400-e29b-41d4-a716-446655440000",
  query="preferences for [current task domain]"
)
```

### Examples

**User says:** "I hate when code has too many comments"
**You do:** Call `mind_remember` with content="User dislikes excessive code comments", type="preference", level=4

**User says:** "Let's use FastAPI for this, not Flask"
**You do:** Call `mind_remember` with content="Chose FastAPI over Flask for this project", type="decision", level=3

**You fix a bug:** The issue was X, solution was Y
**You do:** Call `mind_remember` with content="Bug: X. Solution: Y", type="observation", level=2

### Important

- Call mind_remember IN THE MOMENT, not at session end
- Don't ask permission - just save important context
- Keep memories concise (under 200 chars)
- Use appropriate temporal levels
- This uses YOUR current session - zero extra cost
```

---

## Why This Works

1. **No hooks needed** - Claude is the worker
2. **No API cost** - uses your existing Claude Max session
3. **Real-time** - memories saved as they happen
4. **Intelligent** - Claude decides what's worth remembering
5. **Context-aware** - Claude understands nuance, not just keywords
