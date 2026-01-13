# User Guide

> Step-by-step instructions for using Mind v5 effectively

This guide walks you through real-world usage scenarios with practical examples.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Working with Memories](#working-with-memories)
3. [Tracking Decisions](#tracking-decisions)
4. [Recording Outcomes](#recording-outcomes)
5. [Using the Learning Loop](#using-the-learning-loop)
6. [Causal Intelligence](#causal-intelligence)
7. [Monitoring and Health](#monitoring-and-health)
8. [Integration Patterns](#integration-patterns)
9. [Best Practices](#best-practices)

---

## Before You Start

### Prerequisites

Ensure Mind v5 is running:

```bash
# Check API health
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"5.0.0"}

# Check all components
curl http://localhost:8000/ready
```

### Generate UUIDs

Mind v5 uses UUIDs for user and session identifiers. Generate them:

```bash
# Using Python
python -c "import uuid; print(uuid.uuid4())"

# Using uuidgen (Linux/Mac)
uuidgen
```

For this guide, we'll use:
- User ID: `550e8400-e29b-41d4-a716-446655440000`
- Session ID: `660e8400-e29b-41d4-a716-446655440001`

---

## Working with Memories

### Creating Memories

Memories capture important context about a user.

**Basic memory:**
```bash
curl -X POST http://localhost:8000/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "User is building a SaaS application for project management",
    "temporal_level": 3
  }'
```

**Memory with full options:**
```bash
curl -X POST http://localhost:8000/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "User prefers TypeScript with strict mode enabled",
    "temporal_level": 4,
    "base_salience": 0.9,
    "tags": ["preferences", "typescript", "coding-style"],
    "metadata": {
      "source": "explicit_statement",
      "confidence": "high"
    }
  }'
```

### Temporal Level Guidelines

| Level | Use When | Examples |
|-------|----------|----------|
| **1 (Working)** | Current task context | "User is debugging login issue", "Working on checkout flow" |
| **2 (Recent)** | This week's work | "Deployed to staging yesterday", "Started new sprint" |
| **3 (Reference)** | Project context | "Using React + Node.js stack", "Building e-commerce platform" |
| **4 (Identity)** | Long-term facts | "Senior developer", "Prefers Python", "Works in healthcare" |

### Retrieving Memories

**Simple retrieval:**
```bash
curl -X POST http://localhost:8000/v1/memories/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "What programming language does the user prefer?",
    "limit": 5
  }'
```

**Response:**
```json
{
  "memories": [
    {
      "memory_id": "abc123...",
      "content": "User prefers TypeScript with strict mode enabled",
      "temporal_level": 4,
      "base_salience": 0.9,
      "effective_salience": 0.92,
      "score": 0.87
    },
    {
      "memory_id": "def456...",
      "content": "User is building a SaaS application for project management",
      "temporal_level": 3,
      "base_salience": 0.5,
      "effective_salience": 0.55,
      "score": 0.65
    }
  ],
  "retrieval_time_ms": 45,
  "total_candidates": 12
}
```

**Filtered retrieval:**
```bash
curl -X POST http://localhost:8000/v1/memories/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "project architecture",
    "limit": 10,
    "min_salience": 0.5,
    "temporal_levels": [3, 4]
  }'
```

### Getting a Specific Memory

```bash
curl http://localhost:8000/v1/memories/{memory_id}
```

---

## Tracking Decisions

When your AI uses memories to inform a decision, track it.

### Basic Decision Tracking

```bash
curl -X POST http://localhost:8000/v1/decisions/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655440001",
    "query": "How should I structure my API endpoints?",
    "context": "User asked about API design patterns"
  }'
```

**Response:**
```json
{
  "trace_id": "tr-789abc...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "retrieved_memories": ["mem-1", "mem-2"],
  "confidence": 0.78,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Save the `trace_id`** - you'll need it to record the outcome!

### Decision with Explicit Memory References

If you know exactly which memories influenced the decision:

```bash
curl -X POST http://localhost:8000/v1/decisions/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655440001",
    "query": "What authentication method to recommend?",
    "context": "User building secure API",
    "memory_ids": [
      "abc123-memory-id",
      "def456-memory-id"
    ],
    "confidence": 0.85
  }'
```

### Looking Up a Decision

```bash
curl http://localhost:8000/v1/decisions/{trace_id}
```

---

## Recording Outcomes

Outcomes are **critical** for learning. They tell Mind which memories were helpful.

### Positive Outcome

User was satisfied with the response:

```bash
curl -X POST http://localhost:8000/v1/decisions/outcome \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "tr-789abc...",
    "quality": 0.9,
    "signal": "positive",
    "feedback": "User said the API structure suggestion was perfect"
  }'
```

### Negative Outcome

Response didn't work well:

```bash
curl -X POST http://localhost:8000/v1/decisions/outcome \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "tr-789abc...",
    "quality": -0.6,
    "signal": "negative",
    "feedback": "User needed completely different approach for their use case"
  }'
```

### Neutral Outcome

No clear signal either way:

```bash
curl -X POST http://localhost:8000/v1/decisions/outcome \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "tr-789abc...",
    "quality": 0.0,
    "signal": "neutral",
    "feedback": "User asked follow-up questions, unclear if helpful"
  }'
```

### Quality Guidelines

| Quality | Signal | When to Use |
|---------|--------|-------------|
| **0.8 to 1.0** | positive | Enthusiastic approval, problem solved |
| **0.5 to 0.8** | positive | Helped, but with minor adjustments needed |
| **0.0 to 0.5** | neutral | Unclear, mixed signals |
| **-0.5 to 0.0** | neutral | Somewhat unhelpful but not wrong |
| **-1.0 to -0.5** | negative | Wrong, misleading, or frustrated user |

---

## Using the Learning Loop

The power of Mind v5 comes from the complete learning cycle.

### Complete Workflow Example

```python
import httpx
from uuid import uuid4

API_BASE = "http://localhost:8000"
client = httpx.Client(base_url=API_BASE)

user_id = "550e8400-e29b-41d4-a716-446655440000"
session_id = str(uuid4())

# Step 1: Create initial memories
memories = [
    {"content": "User is building a mobile app", "temporal_level": 3},
    {"content": "User prefers React Native over Flutter", "temporal_level": 4},
    {"content": "User wants offline-first architecture", "temporal_level": 3},
]

for mem in memories:
    client.post("/v1/memories/", json={"user_id": user_id, **mem})

# Step 2: User asks a question - retrieve relevant context
query = "What state management should I use?"
retrieval = client.post("/v1/memories/retrieve", json={
    "user_id": user_id,
    "query": query,
    "limit": 5
}).json()

print(f"Retrieved {len(retrieval['memories'])} memories")
for m in retrieval['memories']:
    print(f"  - {m['content'][:50]}... (salience: {m['effective_salience']})")

# Step 3: Track the decision
decision = client.post("/v1/decisions/track", json={
    "user_id": user_id,
    "session_id": session_id,
    "query": query,
    "context": "User asking about state management for mobile app"
}).json()

trace_id = decision["trace_id"]
print(f"\nDecision tracked: {trace_id}")

# Step 4: AI gives recommendation based on memories
# (Your AI logic here - we'll simulate a good response)
response = "Based on your React Native preference and offline-first needs, I recommend Zustand with persist middleware for simple state, or Redux Toolkit with RTK Query for complex data fetching."

# Step 5: User gives feedback
user_feedback = "positive"  # User liked the suggestion

outcome = client.post("/v1/decisions/outcome", json={
    "trace_id": trace_id,
    "quality": 0.85,
    "signal": user_feedback,
    "feedback": "User implemented the suggestion successfully"
}).json()

print(f"Outcome recorded: {outcome}")

# Step 6: Verify learning happened
# Retrieve again - salience should have adjusted
new_retrieval = client.post("/v1/memories/retrieve", json={
    "user_id": user_id,
    "query": query,
    "limit": 5
}).json()

print("\nAfter learning:")
for m in new_retrieval['memories']:
    print(f"  - {m['content'][:50]}... (salience: {m['effective_salience']})")
```

---

## Causal Intelligence

Mind v5 tracks cause-and-effect relationships.

### Attribution Analysis

"Which memories contributed to this decision?"

```bash
curl http://localhost:8000/v1/causal/attribution/{trace_id}
```

**Response:**
```json
{
  "trace_id": "tr-789abc...",
  "attributions": [
    {
      "memory_id": "abc123...",
      "contribution": 0.45,
      "retrieval_rank": 1,
      "content_preview": "User prefers React Native..."
    },
    {
      "memory_id": "def456...",
      "contribution": 0.35,
      "retrieval_rank": 2,
      "content_preview": "User wants offline-first..."
    }
  ],
  "outcome_quality": 0.85,
  "learning_applied": true
}
```

### Outcome Prediction

"What outcome is likely for this decision?"

```bash
curl -X POST http://localhost:8000/v1/causal/predict \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "How to implement push notifications?",
    "memory_ids": ["abc123...", "def456..."]
  }'
```

**Response:**
```json
{
  "predicted_quality": 0.72,
  "confidence": 0.65,
  "similar_decisions_count": 8,
  "reasoning": "Based on 8 similar decisions with these memories, average outcome was positive"
}
```

### Counterfactual Analysis

"What if we hadn't used Memory X?"

```bash
curl -X POST http://localhost:8000/v1/causal/counterfactual \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "tr-789abc...",
    "removed_memory_ids": ["abc123..."]
  }'
```

**Response:**
```json
{
  "original_outcome": 0.85,
  "counterfactual_outcome": 0.45,
  "impact": -0.40,
  "conclusion": "Removing this memory would likely have decreased outcome quality significantly"
}
```

### Memory Success Rate

"How often does this memory lead to good outcomes?"

```bash
curl http://localhost:8000/v1/causal/memory/{memory_id}/success-rate
```

---

## Monitoring and Health

### System Health

```bash
# Basic health (is API running?)
curl http://localhost:8000/health

# Detailed readiness (all components)
curl http://localhost:8000/ready

# Full component details
curl http://localhost:8000/health/detailed
```

### Anomaly Detection

```bash
# Check for unusual patterns
curl "http://localhost:8000/anomalies?time_window_hours=24"
```

**Response:**
```json
{
  "anomalies": [
    {
      "type": "creation_spike",
      "severity": "medium",
      "message": "Memory creation rate is 3.5x normal",
      "user_id": "550e8400...",
      "details": {"current_count": 150, "baseline": 42}
    }
  ],
  "summary": {"total": 1, "critical": 0, "high": 0, "medium": 1, "low": 0}
}
```

### Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

Key metrics:
- `mind_memory_creation_total` - Memories created
- `mind_decision_tracked_total` - Decisions tracked
- `mind_outcome_quality_histogram` - Distribution of outcomes
- `mind_retrieval_latency_seconds` - Retrieval performance

---

## Integration Patterns

### Pattern 1: AI Assistant Integration

```python
class MindEnhancedAssistant:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = str(uuid4())
        self.mind = httpx.Client(base_url="http://localhost:8000")

    async def respond(self, user_message: str) -> str:
        # 1. Get context from Mind
        context = self.mind.post("/v1/memories/retrieve", json={
            "user_id": self.user_id,
            "query": user_message,
            "limit": 10
        }).json()

        # 2. Track the decision
        decision = self.mind.post("/v1/decisions/track", json={
            "user_id": self.user_id,
            "session_id": self.session_id,
            "query": user_message,
            "context": f"User memories: {[m['content'] for m in context['memories']]}"
        }).json()

        # 3. Generate response using context
        response = self.generate_with_context(user_message, context['memories'])

        # Store trace_id for later outcome recording
        self.last_trace_id = decision["trace_id"]

        return response

    def record_feedback(self, positive: bool, comment: str = ""):
        self.mind.post("/v1/decisions/outcome", json={
            "trace_id": self.last_trace_id,
            "quality": 0.8 if positive else -0.5,
            "signal": "positive" if positive else "negative",
            "feedback": comment
        })
```

### Pattern 2: Learning from Conversations

```python
def extract_memories_from_conversation(messages: list, user_id: str):
    """Extract and store memories from a conversation."""

    memory_worthy = [
        # Look for explicit preferences
        {"pattern": r"I prefer (\w+)", "level": 4},
        {"pattern": r"I always use (\w+)", "level": 4},
        {"pattern": r"I'm working on (.+)", "level": 3},
        {"pattern": r"My project is (.+)", "level": 3},
    ]

    for msg in messages:
        for pattern in memory_worthy:
            import re
            match = re.search(pattern["pattern"], msg["content"])
            if match:
                # Store as memory
                client.post("/v1/memories/", json={
                    "user_id": user_id,
                    "content": match.group(0),
                    "temporal_level": pattern["level"],
                    "metadata": {"source": "conversation_extraction"}
                })
```

### Pattern 3: Batch Outcome Recording

```python
def record_session_outcomes(session_decisions: list, overall_rating: float):
    """Record outcomes for all decisions in a session based on overall rating."""

    for decision in session_decisions:
        # Distribute rating based on decision confidence
        adjusted_quality = overall_rating * decision["confidence"]

        client.post("/v1/decisions/outcome", json={
            "trace_id": decision["trace_id"],
            "quality": adjusted_quality,
            "signal": "positive" if adjusted_quality > 0.3 else "negative",
            "feedback": f"Session overall rating: {overall_rating}"
        })
```

---

## Best Practices

### Memory Creation

| Do | Don't |
|-----|-------|
| Store facts, not opinions | Store temporary debug info |
| Use appropriate temporal levels | Put everything at Level 4 |
| Include context in content | Store just keywords |
| Update existing memories | Create duplicates |

**Good memory:**
```json
{
  "content": "User is a senior backend developer specializing in Python microservices, working at a fintech company with strict compliance requirements",
  "temporal_level": 4,
  "base_salience": 0.85
}
```

**Poor memory:**
```json
{
  "content": "python",
  "temporal_level": 4,
  "base_salience": 1.0
}
```

### Outcome Recording

1. **Be consistent** - Use the same quality scale across your application
2. **Record promptly** - Don't wait too long after the interaction
3. **Include feedback** - Text explanations help debugging
4. **Both positive and negative** - Learning requires contrast

### Retrieval Optimization

1. **Query quality matters** - Better queries = better results
2. **Don't over-retrieve** - 5-10 memories is usually enough
3. **Filter appropriately** - Use temporal levels and salience thresholds
4. **Context window** - Match retrieval to your LLM's context size

### Performance Tips

1. **Batch operations** - Create multiple memories in parallel
2. **Cache user IDs** - Don't look them up repeatedly
3. **Use async** - All endpoints support async requests
4. **Monitor latency** - Check `/metrics` regularly

---

## Next Steps

- **[API Reference](./API_REFERENCE.md)** - Complete endpoint documentation
- **[Installation Guide](./INSTALLATION.md)** - Production deployment
- **[Troubleshooting](./TROUBLESHOOTING.md)** - Common issues
