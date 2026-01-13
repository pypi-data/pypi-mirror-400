# Core Concepts

> Understanding the building blocks of Mind v5

Mind v5 is built on several interconnected concepts. This guide explains each one and how they work together.

---

## Table of Contents

1. [Memories](#memories)
2. [Temporal Levels](#temporal-levels)
3. [Salience](#salience)
4. [Decisions](#decisions)
5. [Outcomes](#outcomes)
6. [Causal Graph](#causal-graph)
7. [Retrieval](#retrieval)
8. [Events](#events)
9. [Workflows](#workflows)
10. [Federation](#federation)

---

## Memories

A **Memory** is a piece of information about a user that helps make better decisions.

### What is a Memory?

```
Memory = Context + Temporal Level + Salience
```

**Examples of memories:**
- "User prefers Python over JavaScript"
- "User is building an e-commerce platform"
- "User asked about authentication 3 times today"
- "User works in healthcare (compliance important)"

### Memory Structure

```json
{
  "memory_id": "uuid-here",
  "user_id": "user-uuid",
  "content": "User prefers detailed explanations with examples",
  "temporal_level": 4,
  "base_salience": 0.8,
  "outcome_adjustment": 0.1,
  "created_at": "2025-01-15T10:30:00Z",
  "valid_until": null
}
```

### Key Properties

| Property | Description |
|----------|-------------|
| `content` | The actual information being stored |
| `temporal_level` | How long this memory should persist (1-4) |
| `base_salience` | Initial importance (0.0 to 1.0) |
| `outcome_adjustment` | Learning adjustment based on feedback |
| `valid_until` | When this memory expires (null = never) |

---

## Temporal Levels

Memories have different lifespans based on their importance and relevance over time.

### The Four Levels

```
Level 4: Identity (Years)
   ↑
Level 3: Reference (Weeks/Months)
   ↑
Level 2: Recent (Days)
   ↑
Level 1: Working (Hours)
```

| Level | Name | Duration | Example |
|-------|------|----------|---------|
| **1** | Working | Hours | "User is debugging a login issue" |
| **2** | Recent | Days | "User deployed to staging yesterday" |
| **3** | Reference | Weeks/Months | "User's project uses React and Node.js" |
| **4** | Identity | Years/Permanent | "User is a senior backend developer" |

### Promotion

Memories can be **promoted** to higher levels based on:
- Repeated access
- Positive outcomes
- Explicit user confirmation

```
Working Memory (Level 1)
    ↓ [accessed 5+ times in a week]
Recent Memory (Level 2)
    ↓ [consistently led to good outcomes]
Reference Memory (Level 3)
    ↓ [fundamental to user identity]
Identity Memory (Level 4)
```

### Expiration

Lower-level memories expire if not reinforced:

| Level | Expires After |
|-------|--------------|
| 1 (Working) | 24 hours |
| 2 (Recent) | 7 days |
| 3 (Reference) | 90 days |
| 4 (Identity) | Never (unless explicitly removed) |

---

## Salience

**Salience** determines how prominently a memory surfaces during retrieval.

### How Salience Works

```
Effective Salience = Base Salience + Outcome Adjustment
```

- **Base Salience**: Initial importance (0.0 to 1.0)
- **Outcome Adjustment**: Learning from feedback (-0.5 to +0.5)
- **Effective Salience**: What's used for ranking (0.0 to 1.0)

### Salience in Action

```
Memory: "User prefers concise responses"
Base Salience: 0.7

Decision 1: Used this memory → User liked response
  → Outcome Adjustment: +0.05

Decision 2: Used this memory → User liked response
  → Outcome Adjustment: +0.10

Decision 3: Used this memory → User liked response
  → Outcome Adjustment: +0.15

Effective Salience: 0.7 + 0.15 = 0.85

Now this memory ranks higher than before!
```

### Why This Matters

Traditional systems treat all stored information equally. Mind v5 learns:

- Helpful information → bubbles up
- Unhelpful information → sinks down
- Misleading information → gets demoted

---

## Decisions

A **Decision** is a tracked moment where the AI used memories to inform an action.

### Decision Tracking

Every time an AI agent consults Mind for context, a decision is tracked:

```json
{
  "trace_id": "decision-uuid",
  "user_id": "user-uuid",
  "session_id": "session-uuid",
  "query": "How should I format this response?",
  "retrieved_memories": ["mem-1", "mem-2", "mem-3"],
  "context": "User asked about code formatting",
  "confidence": 0.85,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Why Track Decisions?

1. **Attribution**: Know which memories influenced each decision
2. **Learning**: Connect outcomes back to the memories used
3. **Debugging**: Understand why the AI behaved a certain way
4. **Improvement**: Identify which memories are actually helpful

---

## Outcomes

An **Outcome** is feedback about how well a decision worked.

### Recording Outcomes

```json
{
  "trace_id": "decision-uuid",
  "quality": 0.9,
  "signal": "positive",
  "feedback": "User said 'perfect, exactly what I needed'"
}
```

### Outcome Signals

| Signal | Quality Range | Meaning |
|--------|--------------|---------|
| `positive` | 0.5 to 1.0 | Decision worked well |
| `neutral` | -0.2 to 0.2 | No clear signal |
| `negative` | -1.0 to -0.5 | Decision didn't work |

### Types of Feedback

**Explicit feedback:**
- User says "thanks, that's perfect"
- User clicks thumbs up/down
- User rates response

**Implicit feedback:**
- User follows the suggestion
- User asks for clarification (neutral/negative)
- User abandons conversation (negative)
- User returns for more help (positive)

### The Learning Loop

```
Decision Made
     ↓
Outcome Recorded (quality: 0.8, signal: positive)
     ↓
Attribution Calculated:
  - Memory A contributed 40% → adjust +0.08
  - Memory B contributed 35% → adjust +0.07
  - Memory C contributed 25% → adjust +0.05
     ↓
Salience Updated for each memory
     ↓
Next retrieval: these memories rank differently
```

---

## Causal Graph

The **Causal Graph** tracks relationships between memories, decisions, and outcomes.

### Graph Structure

```
[Memory A] ──INFLUENCED──> [Decision 1] ──LED_TO──> [Outcome: Good]
     ↑                           ↓
     └── REINFORCED_BY ──────────┘

[Memory B] ──INFLUENCED──> [Decision 1]

[Memory C] ──INFLUENCED──> [Decision 2] ──LED_TO──> [Outcome: Bad]
     ↓
DEMOTED_BY
```

### Relationship Types

| Relationship | Meaning |
|--------------|---------|
| `INFLUENCED` | Memory was used in making a decision |
| `LED_TO` | Decision resulted in an outcome |
| `REINFORCED_BY` | Good outcome strengthened memory |
| `DEMOTED_BY` | Bad outcome weakened memory |
| `SIMILAR_TO` | Memories have related content |

### Causal Capabilities

**Attribution**: "Which memories contributed to this decision?"
```
GET /v1/causal/attribution/{trace_id}
```

**Prediction**: "Based on similar past decisions, what outcome is likely?"
```
POST /v1/causal/predict
```

**Counterfactual**: "What if we hadn't used Memory X?"
```
POST /v1/causal/counterfactual
```

---

## Retrieval

**Retrieval** is the process of finding relevant memories for a given context.

### Multi-Source Retrieval

Mind v5 doesn't just do keyword search. It combines multiple signals:

```
Query: "Help with authentication"
              ↓
    ┌─────────┼─────────┬─────────┬─────────┐
    ↓         ↓         ↓         ↓         ↓
 Vector    Keyword   Salience  Recency   Causal
 Search    Search    Ranking   Boost    Context
    ↓         ↓         ↓         ↓         ↓
    └─────────┴─────────┴─────────┴─────────┘
                        ↓
              RRF Fusion (combine scores)
                        ↓
              Ranked Memory List
```

### Retrieval Signals

| Signal | Weight | Purpose |
|--------|--------|---------|
| **Vector Similarity** | High | Semantic meaning match |
| **Keyword Match** | Medium | Exact term matching |
| **Salience Score** | High | Learned importance |
| **Recency** | Low | Recent memories slightly preferred |
| **Causal Success** | Medium | Past success with similar queries |

### Reciprocal Rank Fusion (RRF)

Different retrieval methods produce different rankings. RRF combines them:

```python
# Simplified RRF formula
rrf_score = sum(1 / (k + rank_in_list) for each list)

# Example: Memory appears in multiple lists
Vector search rank: 3  → 1/(60+3) = 0.0159
Keyword rank: 1        → 1/(60+1) = 0.0164
Salience rank: 2       → 1/(60+2) = 0.0161

RRF Score: 0.0159 + 0.0164 + 0.0161 = 0.0484
```

---

## Events

Mind v5 is **event-driven**. All state changes are published as events.

### Event Types

| Event | When Published |
|-------|---------------|
| `memory.created` | New memory stored |
| `memory.retrieved` | Memories accessed |
| `memory.salience_adjusted` | Learning happened |
| `decision.tracked` | Decision recorded |
| `outcome.observed` | Feedback received |

### Event Flow

```
API Request
     ↓
Service Layer (business logic)
     ↓
Database Write
     ↓
Event Published to NATS
     ↓
┌────────────────────────────────────────┐
│           Event Consumers              │
├──────────────┬─────────────┬───────────┤
│ Causal       │ Salience    │ Pattern   │
│ Updater      │ Updater     │ Extractor │
└──────────────┴─────────────┴───────────┘
```

### Why Events?

1. **Decoupling**: Services don't need to know about each other
2. **Replay**: Can rebuild state from event history
3. **Async**: Heavy processing happens in background
4. **Audit**: Complete history of what happened

---

## Workflows

**Workflows** are long-running background processes managed by Temporal.

### Available Workflows

| Workflow | Purpose | Frequency |
|----------|---------|-----------|
| `MemoryPromotionWorkflow` | Promote memories to higher levels | Daily |
| `MemoryExpirationWorkflow` | Archive expired memories | Hourly |
| `MemoryConsolidationWorkflow` | Merge similar memories | Daily |
| `AnalyzeOutcomesWorkflow` | Batch outcome analysis | Daily |
| `CalibrateConfidenceWorkflow` | Tune prediction accuracy | Weekly |
| `ExtractPatternsWorkflow` | Find decision patterns | Daily |

### Workflow Benefits

1. **Reliability**: Automatically retries on failure
2. **Visibility**: See status in Temporal UI (port 8088)
3. **Scheduling**: Run on configurable schedules
4. **Durability**: Survives service restarts

---

## Federation

**Federation** allows learning across users while preserving privacy.

### How It Works

```
User A's decisions → Pattern extracted → Sanitized
User B's decisions → Pattern extracted → Sanitized
User C's decisions → Pattern extracted → Sanitized
                           ↓
                   Aggregated Pattern
                   (minimum 10 users,
                    100 data points)
                           ↓
              Differential Privacy Applied
                           ↓
              Federated Pattern Available
                           ↓
            New User D can benefit from
            collective learning
```

### Privacy Guarantees

| Protection | Implementation |
|------------|----------------|
| **Anonymization** | User IDs never shared |
| **Aggregation** | Patterns need 10+ users |
| **Differential Privacy** | Noise added to statistics |
| **PII Scrubbing** | Personal info detected and removed |
| **Consent** | Users must opt-in to federation |

### What Gets Federated

**Yes (safe to share):**
- General patterns: "When users ask about X, approach Y works well"
- Abstract strategies: "Concise responses work better for quick questions"

**Never (privacy-sensitive):**
- Specific user content
- Names, emails, personal details
- Individual decision traces
- Raw memory content

---

## Putting It All Together

Here's how everything connects in a real scenario:

```
1. User asks: "How do I add authentication to my React app?"

2. Mind retrieves memories:
   - "User is building an e-commerce site" (Level 3, Salience 0.85)
   - "User prefers JWT over sessions" (Level 4, Salience 0.9)
   - "User uses Next.js" (Level 3, Salience 0.75)

3. Decision tracked:
   - Query: "authentication React"
   - Retrieved memories: [mem-1, mem-2, mem-3]
   - Confidence: 0.82

4. AI responds with JWT + Next.js Auth recommendation

5. User: "Perfect, that's exactly what I needed!"

6. Outcome recorded:
   - Quality: 0.9
   - Signal: positive

7. Salience adjusted:
   - "User prefers JWT" → +0.05 (now 0.95)
   - "User uses Next.js" → +0.04 (now 0.79)
   - "User building e-commerce" → +0.03 (now 0.88)

8. Causal graph updated:
   - [JWT Memory] --REINFORCED_BY--> [This Decision]

9. Next time:
   - These memories rank even higher
   - Similar questions get better answers
```

---

## Next Steps

- **[User Guide](./USER_GUIDE.md)** - Hands-on examples
- **[API Reference](./API_REFERENCE.md)** - Endpoint details
- **[Installation Guide](./INSTALLATION.md)** - Production setup
