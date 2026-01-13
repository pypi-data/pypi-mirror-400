# vibeship-mind - Decision Intelligence for AI Agents

> Make every AI interaction smarter because Mind remembers.

Mind is a memory and learning system for AI agents. It helps Claude remember your preferences and learn from decision outcomes to give better recommendations over time.

## Quick Start

### Option 1: Mind Cloud (Recommended - No Setup)

```bash
# Add to Claude - just works!
uvx vibeship-mind
```

Mind Cloud handles everything. No Docker, no database, no configuration.

### Option 2: Self-Hosted

For users who want full control over their data:

```bash
# Clone and run
git clone https://github.com/vibeship/mind
cd mind
docker-compose up -d

# Then run MCP with local flag
uvx vibeship-mind --local
```

## Configuration

### Claude Code (CLI)

Add to your project's `.mcp.json` or global `~/.claude/settings.json`:

```json
{
    "mcpServers": {
        "mind": {
            "command": "uvx",
            "args": ["vibeship-mind"]
        }
    }
}
```

Or add via command:
```bash
claude mcp add mind "uvx vibeship-mind"
```

### Claude Desktop

Add to your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
    "mcpServers": {
        "mind": {
            "command": "uvx",
            "args": ["vibeship-mind"]
        }
    }
}
```

Restart Claude Desktop, and Mind is ready!

### Self-Hosted (Local Docker)

If running Mind locally instead of Mind Cloud:

```json
{
    "mcpServers": {
        "mind": {
            "command": "uvx",
            "args": ["vibeship-mind", "--local"]
        }
    }
}
```

## How It Works

### 1. Mind Remembers

When you tell Claude something important, Mind stores it:

```
You: "I prefer TypeScript over JavaScript"

Mind: Memory stored!

Content: "I prefer TypeScript over JavaScript"
Level: Identity (core preference)
Salience: 100%

This is your first memory! Mind will use this to give better recommendations.
```

### 2. Mind Retrieves

When you ask for recommendations, Mind recalls relevant memories:

```
You: "What language should I use for this API?"

Claude: Based on your preferences, I recommend TypeScript.

[Mind used 2 memories]
- "Prefers TypeScript" (95% relevance)
- "Values type safety" (78% relevance)
```

### 3. Mind Learns

When you give feedback, Mind learns what works:

```
You: "Great suggestion, TypeScript was perfect!"

Mind: Outcome recorded (positive)!

Quality: +90%
Memories updated: 2

The memory "Prefers TypeScript" is now stronger.
It will rank higher in future retrievals.
```

## Tools Available

Once installed, Claude has access to these Mind tools:

| Tool | Purpose |
|------|---------|
| `mind_remember` | Store something important about you |
| `mind_retrieve` | Get relevant memories for a decision |
| `mind_decide` | Record a decision and its outcome |
| `mind_health` | Check Mind status |

## Memory Levels

Mind organizes memories by how long they should persist:

| Level | Duration | Example |
|-------|----------|---------|
| Immediate (1) | Hours | "Working on the checkout feature" |
| Situational (2) | Days-Weeks | "Debugging the auth system" |
| Seasonal (3) | Months | "Building e-commerce features" |
| Identity (4) | Permanent | "Prefers TypeScript" |

## Commands

```bash
# Start MCP server (connects to Mind Cloud)
uvx vibeship-mind

# Use local Mind instance
uvx vibeship-mind --local

# Show setup guide
uvx vibeship-mind --setup

# JSON output instead of friendly messages
uvx vibeship-mind --json

# Show version
uvx vibeship-mind --version
```

## Configuration

Mind stores config in `~/.mind/config.json`:

```json
{
    "api_url": "https://api.mind.vibeship.ai",
    "user_id": "auto-generated-uuid",
    "friendly_mode": true
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MIND_API_URL` | Mind API endpoint | Mind Cloud |
| `MIND_API_KEY` | API key (for cloud) | None |

## Privacy

- Your memories are yours. Mind Cloud encrypts everything.
- Self-hosted option for complete data control.
- No PII in logs or error messages.
- Federated patterns are anonymized with differential privacy.

## Troubleshooting

### "Mind Status: Offline"

1. **Using Cloud?** Check your internet connection.
2. **Using Local?** Is Docker running? Run `docker-compose up -d`
3. **Still stuck?** Run `uvx vibeship-mind --setup` to reconfigure.

### "No relevant memories found"

Mind needs memories to retrieve! Try storing some first:
- Tell Claude your preferences
- Share what you're working on
- Mention your tech stack

### Claude doesn't show Mind tools

1. Check Claude Desktop config has Mind entry
2. Restart Claude Desktop
3. Look for "mind" in the tools list

## Links

- **Website**: https://mind.vibeship.ai
- **Documentation**: https://docs.mind.vibeship.ai
- **GitHub**: https://github.com/vibeship/mind
- **Discord**: https://discord.gg/vibeship

## License

MIT - See [LICENSE](LICENSE) for details.

---

**Made with love by VIBESHIP**

*Mind: Decision Intelligence for AI Agents*
