# Mind v5 - User Onboarding & Distribution Strategy

> How to make Mind easy to install, use, and love.

---

## Current State: Developer Setup

**Today's installation:**
```bash
git clone https://github.com/vibeship/mind
cd mind
docker-compose up -d
# Configure MCP in Claude Desktop
```

**Friction points:**
- Requires Docker knowledge
- Manual MCP configuration
- No visual feedback during learning
- No clear "it's working" moment

---

## Target State: One-Command Install

### Option 1: NPX/UVX for MCP Server Only

```bash
# For users who just want the MCP tools
npx mind-mcp
# or
uvx mind-mcp
```

**What this gives:**
- Instant `mind_remember`, `mind_retrieve`, `mind_decide` tools
- Cloud-hosted backend (Mind Cloud)
- Zero infrastructure needed
- Free tier with limits

**Implementation:**
1. Publish `mind-mcp` to npm/PyPI
2. MCP server connects to Mind Cloud API
3. User signs up via web, gets API key
4. Key stored in `~/.mind/config`

### Option 2: Docker One-Liner (Self-Hosted)

```bash
# For users who want full control
curl -fsSL https://mind.vibeship.ai/install.sh | bash
```

**What this does:**
1. Checks Docker is installed
2. Creates `~/.mind` directory
3. Downloads docker-compose.yml
4. Starts services
5. Configures Claude Desktop MCP automatically
6. Opens welcome page in browser

### Option 3: Homebrew/Chocolatey

```bash
# macOS
brew install vibeship/tap/mind

# Windows
choco install mind

# Linux
curl -fsSL https://mind.vibeship.ai/install.sh | bash
```

---

## The "Aha!" Moments

### Moment 1: First Memory Stored (0-30 seconds)

**Current:** User stores a memory, sees JSON response. Boring.

**Improved:**
```
You: "Remember that I prefer TypeScript over JavaScript"

Mind: Stored! This is now part of your Identity layer.
      I'll use this preference in future recommendations.

      Your Mind now has:
      - 1 identity memory (core preferences)
      - 0 situational memories (recent context)
```

**Implementation:**
- Add friendly response formatting in MCP
- Show memory count by temporal level
- Explain what the memory means

### Moment 2: Memory Affects a Decision (1-5 minutes)

**Current:** User asks something, doesn't know Mind was used.

**Improved:**
```
You: "What tech stack should I use for this API?"

Claude: Based on your preferences, I recommend:
        - TypeScript (you've told me you prefer this)
        - Node.js with Express

        [Mind used: 2 memories influenced this]
        [Click to see which memories]
```

**Implementation:**
- Claude Code integration shows memory attribution
- Link to view contributing memories
- Show confidence score

### Moment 3: Mind Gets Smarter (5-30 minutes)

**Current:** User doesn't see learning happening.

**Improved:**
```
Mind Weekly Digest:

  This week, your Mind:
  - Learned from 12 decisions
  - Improved 3 memory rankings
  - Discovered 1 new pattern

  Top performing memories:
  1. "Prefers TypeScript" - helped 8 decisions
  2. "Likes minimal dependencies" - helped 5 decisions

  Memories that need validation:
  1. "Prefers MongoDB" - mixed results, should I keep?
```

**Implementation:**
- Weekly email/notification digest
- Dashboard showing learning progress
- Memory validation prompts

### Moment 4: Cross-Session Continuity (Days later)

**Current:** User comes back, forgets Mind exists.

**Improved:**
```
[New session starts]

Mind: Welcome back! Since last time:
      - I remember you were working on the API project
      - You prefer TypeScript and minimal dependencies
      - Last session ended with a successful deployment

      Ready to continue?
```

**Implementation:**
- Session summary on reconnect
- Proactive context recall
- "Resume where you left off" feature

---

## The "Wow!" Moments

### Wow 1: Mind Prevents a Mistake

```
You: "Let's add MongoDB to this project"

Claude: Hold on - your Mind indicates you had issues with
        MongoDB in Project X (3 months ago). The outcome
        was negative (-0.7).

        Would you like to:
        1. Proceed anyway (I'll update your preference)
        2. Consider alternatives (PostgreSQL worked well for you)
        3. Tell me more about what's different this time
```

### Wow 2: Pattern Emerges

```
Mind: I noticed something interesting!

      Over the last month, your successful decisions often
      involved:
      - Using typed languages (success rate: 87%)
      - Avoiding ORMs (success rate: 82%)
      - Preferring REST over GraphQL (success rate: 79%)

      Should I factor this into future recommendations?
```

### Wow 3: Mind Explains Itself

```
You: "Why did you recommend Express over Fastify?"

Mind: Here's my reasoning:

      Memories that influenced this:
      1. "Prefers well-documented libraries" (weight: 0.4)
         - Express has more tutorials
      2. "Values stability over speed" (weight: 0.3)
         - Express is more battle-tested
      3. "TypeScript preference" (weight: 0.2)
         - Both support TS, neutral factor

      Historical context:
      - You chose Express in 3 past projects
      - All had positive outcomes

      Confidence: 78%
```

---

## Onboarding Flow

### Step 1: Quick Start (30 seconds)

```
Welcome to Mind!

Mind helps AI remember and learn from your preferences.
Let's set up your first memory.

What's something every AI should know about you?
> [User types: "I'm a backend developer who loves Python"]

Got it! I've stored this as an Identity memory.
This will influence all future interactions.

[Continue] or [Add more]
```

### Step 2: First Retrieval Demo (1 minute)

```
Let's see Mind in action!

Ask me anything, and I'll show you how your memory
influences my response.

> "What language should I use for a CLI tool?"

Based on your memory "backend developer who loves Python",
I recommend Python with Click or Typer.

Did this recommendation help? [Yes] [No] [Skip]
```

### Step 3: Dashboard Tour (2 minutes)

```
Here's your Mind Dashboard:

[Memory Browser] - See all your memories
[Decision History] - Track what Mind influenced
[Learning Graph] - Watch Mind get smarter
[Settings] - Privacy, exports, integrations

Your Mind is now active across all Claude interactions!
```

---

## Distribution Channels

### 1. Claude Code Marketplace
- One-click install from Claude Code
- Auto-configures MCP
- Managed by Anthropic

### 2. GitHub
- Open source core
- Docker-compose for self-hosting
- Contributions welcome

### 3. VS Code Extension
- Integrates with Copilot
- Visual memory browser
- Learning progress sidebar

### 4. Web Dashboard
- mind.vibeship.ai/dashboard
- View memories without CLI
- Share patterns (opt-in)
- Team collaboration

### 5. API for Integrations
- REST API for any AI platform
- SDK for Python, TypeScript, Go
- Webhook notifications

---

## Metrics for Success

### Activation
- % of users who store first memory within 5 min
- % of users who see first retrieval within 10 min
- % of users who record first outcome within 1 hour

### Engagement
- Memories stored per week
- Decisions influenced per day
- Return rate after 7 days

### Value
- Time saved per session
- Decision quality improvement
- User satisfaction (NPS)

### Virality
- Referral rate
- Social shares of learning graphs
- Team adoption rate

---

## Pricing Strategy

### Free Tier
- 100 memories
- 1,000 retrievals/month
- 7-day retention for decisions
- Personal use only

### Pro ($10/month)
- 10,000 memories
- Unlimited retrievals
- Forever retention
- API access
- Priority support

### Team ($25/user/month)
- Everything in Pro
- Shared team patterns
- Admin dashboard
- SSO
- 99.9% SLA

### Enterprise (Custom)
- Self-hosted option
- Private cloud
- Custom integrations
- Dedicated support
- Compliance (SOC2, HIPAA)

---

## Next Steps

1. **Week 1:** Publish `mind-mcp` to npm/PyPI
2. **Week 2:** Build onboarding flow in MCP
3. **Week 3:** Create web dashboard MVP
4. **Week 4:** Launch on Product Hunt / Hacker News

---

*The goal: Make every AI interaction smarter because Mind remembers.*
