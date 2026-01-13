# Mind v5 Constitution

> **The Living Architecture of Decision Intelligence**
>
> This document defines how Mind works, how it learns, and how it evolves.
> It is both a specification and a hypothesis - meant to be tested, refined, and improved.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [The Learning Loop](#the-learning-loop)
3. [Architecture Components](#architecture-components)
4. [Schemas & Data Models](#schemas--data-models)
5. [Rulesets](#rulesets)
6. [Self-Improvement Mechanisms](#self-improvement-mechanisms)
7. [Hypotheses & Experiments](#hypotheses--experiments)
8. [Evolution Log](#evolution-log)

---

## Core Philosophy

### The Prime Directive

**Mind exists to help AI agents make better decisions over time.**

Not just store information. Not just retrieve context. But to *learn* from outcomes and continuously improve the quality of decisions.

### The Five Axioms

1. **Memory Serves Decisions**
   - Every memory exists to improve future decision quality
   - If a memory doesn't influence decisions, it should decay
   - The value of a memory is measured by the outcomes it enables

2. **Outcomes Are Truth**
   - We don't assume which memories are valuable
   - We observe which memories lead to good outcomes
   - Reality (outcomes) teaches us what matters

3. **Time Structures Memory**
   - Not all memories are equal in temporal scope
   - Some truths last hours, others last years
   - Temporal hierarchy prevents short-term noise from corrupting long-term wisdom

4. **Causality Over Correlation**
   - We track WHY decisions worked, not just THAT they worked
   - Causal understanding enables counterfactual reasoning
   - "What if we had done X instead?" is a valid question

5. **Privacy Is Inviolable**
   - User memories never leave their Mind without consent
   - Patterns can be shared; personal data cannot
   - Trust is the foundation of memory

### The Ultimate Goal

To create a decision intelligence layer that:
- Learns from every interaction
- Improves with every outcome
- Enables AI agents to make increasingly better decisions
- Evolves toward true understanding, not just pattern matching

---

## The Learning Loop

### The Fundamental Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE MIND LEARNING LOOP                        │
│                                                                   │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│    │  STORE   │────▶│ RETRIEVE │────▶│  DECIDE  │               │
│    │  Memory  │     │  Context │     │  Action  │               │
│    └──────────┘     └──────────┘     └──────────┘               │
│         ▲                                  │                     │
│         │                                  ▼                     │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│    │  ADJUST  │◀────│  LEARN   │◀────│ OBSERVE  │               │
│    │ Salience │     │ Outcome  │     │  Result  │               │
│    └──────────┘     └──────────┘     └──────────┘               │
│                                                                   │
│    Each cycle makes the next cycle better.                       │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Details

#### 1. STORE (Memory Creation)
```yaml
trigger: New information worth remembering
inputs:
  - content: The information to store
  - content_type: fact | preference | event | goal | observation
  - temporal_level: 1-4 (immediate → identity)
  - initial_salience: 0.0 - 1.0 (importance estimate)
outputs:
  - memory_id: Unique identifier
  - embedding: Vector representation
  - timestamp: When stored
rules:
  - Choose temporal_level based on expected relevance duration
  - Set initial_salience based on confidence and importance
  - Never store PII in content directly (encrypt or tokenize)
```

#### 2. RETRIEVE (Context Assembly)
```yaml
trigger: Decision needs to be made
inputs:
  - query: What context is needed
  - user_id: Whose memories to search
  - limit: Max memories to return
outputs:
  - memories: Ranked list of relevant memories
  - scores: Relevance scores for each
  - retrieval_id: For tracking this retrieval
rules:
  - Use multi-modal retrieval (vector + keyword + graph)
  - Apply Reciprocal Rank Fusion for combining results
  - Weight by effective_salience (base + outcome adjustment)
  - Respect temporal validity (don't return expired memories)
```

#### 3. DECIDE (Action Selection)
```yaml
trigger: Context assembled, action needed
inputs:
  - context: Retrieved memories
  - options: Possible actions
  - constraints: Requirements/limitations
outputs:
  - decision: Chosen action
  - trace_id: Links memories to this decision
  - confidence: How certain about the choice
rules:
  - Record which memories influenced the decision
  - Track memory_scores (how much each contributed)
  - Log decision_type (recommendation, action, preference)
  - Capture alternatives_count for decision quality analysis
```

#### 4. OBSERVE (Outcome Detection)
```yaml
trigger: Decision has played out
inputs:
  - trace_id: Which decision this is about
  - signal: How outcome was detected
outputs:
  - outcome_quality: -1.0 (bad) to +1.0 (good)
  - feedback: Optional text explanation
rules:
  - Detect outcomes through multiple signals:
    - user_accepted: User explicitly approved
    - user_rejected: User explicitly rejected
    - task_completed: Task finished successfully
    - task_failed: Task did not complete
    - agent_feedback: Agent's self-assessment
  - Quality should reflect actual impact, not just acceptance
```

#### 5. LEARN (Attribution)
```yaml
trigger: Outcome observed
inputs:
  - outcome: Quality and signal
  - trace: Which memories contributed
outputs:
  - attributions: Credit/blame for each memory
rules:
  - Attribute proportionally to memory_scores
  - Consider confidence in attribution
  - Account for confounding factors
  - Store causal evidence for future analysis
```

#### 6. ADJUST (Salience Update)
```yaml
trigger: Attribution computed
inputs:
  - memory_id: Which memory to update
  - attribution: How much it contributed
  - outcome_quality: Was the decision good or bad
outputs:
  - salience_delta: How much to adjust
  - new_effective_salience: Updated value
rules:
  - Formula: delta = attribution * outcome_quality * learning_rate
  - Clamp effective_salience to [0.0, 1.0]
  - Higher temporal levels adjust more slowly
  - Publish event for downstream systems
```

### The Compound Effect

Each cycle through the loop:
1. Memories that lead to good decisions gain salience
2. Memories that mislead lose salience
3. Future retrievals favor proven-valuable memories
4. Decision quality improves over time

**This is how Mind learns.**

---

## Architecture Components

### 1. Hierarchical Temporal Memory

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEMPORAL HIERARCHY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Level 4: IDENTITY (Years)                                       │
│  ══════════════════════════════════════════════════════════════ │
│  Core beliefs, values, personality, long-term preferences        │
│  Example: "User values clean code and developer experience"      │
│  Decay: Extremely slow, requires major evidence to change        │
│                                                                   │
│  Level 3: SEASONAL (Months)                                      │
│  ────────────────────────────────────────────────────────────── │
│  Recurring patterns, project phases, quarterly rhythms           │
│  Example: "User does major releases before holidays"             │
│  Decay: Slow, refreshed by repeated observation                  │
│                                                                   │
│  Level 2: SITUATIONAL (Days-Weeks)                               │
│  ────────────────────────────────────────────────────────────── │
│  Current projects, recent context, ongoing work                  │
│  Example: "User is working on Mind v5 MCP integration"           │
│  Decay: Moderate, fades when situation changes                   │
│                                                                   │
│  Level 1: IMMEDIATE (Hours)                                      │
│  ────────────────────────────────────────────────────────────── │
│  Current session, active task, momentary context                 │
│  Example: "User is debugging API latency issue"                  │
│  Decay: Fast, typically expires within session                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Temporal Level Rules

| Level | Name | Duration | Salience Adjustment Rate | Use For |
|-------|------|----------|-------------------------|---------|
| 1 | Immediate | Hours | 1.0x (fast) | Current task context |
| 2 | Situational | Days-Weeks | 0.5x (moderate) | Ongoing projects |
| 3 | Seasonal | Months | 0.25x (slow) | Recurring patterns |
| 4 | Identity | Years | 0.1x (very slow) | Core preferences |

#### Level Selection Heuristics

```python
def select_temporal_level(content: str, content_type: str) -> int:
    """Determine appropriate temporal level for a memory."""

    # Identity markers
    if content_type == "fact" and contains_identity_words(content):
        return 4  # "User is founder of...", "User values..."

    # Seasonal patterns
    if contains_recurring_pattern(content):
        return 3  # "User typically...", "Every quarter..."

    # Situational context
    if content_type in ["observation", "goal"] and is_project_related(content):
        return 2  # "Working on...", "Current focus..."

    # Immediate by default
    return 1  # "Currently...", "Right now..."
```

### 2. Outcome-Weighted Salience

The core learning mechanism of Mind.

```python
@dataclass
class Memory:
    memory_id: UUID
    content: str
    temporal_level: int
    base_salience: float      # Initial importance (0.0 - 1.0)
    outcome_adjustment: float  # Cumulative learning (-1.0 to +1.0)

    @property
    def effective_salience(self) -> float:
        """Salience after outcome-based adjustment."""
        return max(0.0, min(1.0, self.base_salience + self.outcome_adjustment))
```

#### Salience Update Algorithm

```python
def compute_salience_delta(
    outcome_quality: float,      # -1.0 to +1.0
    attribution: float,          # 0.0 to 1.0 (how much this memory contributed)
    temporal_level: int,         # 1-4
    learning_rate: float = 0.1,  # Base learning rate
) -> float:
    """
    Compute how much to adjust a memory's salience.

    The formula balances:
    - Outcome quality: Good outcomes increase, bad decrease
    - Attribution: Higher contribution = more credit/blame
    - Temporal level: Higher levels adjust more slowly
    - Learning rate: Controls overall adjustment speed
    """
    # Temporal dampening: higher levels are more stable
    temporal_dampening = 1.0 / temporal_level

    # Core formula
    delta = outcome_quality * attribution * learning_rate * temporal_dampening

    return delta
```

#### Example Scenario

```
Initial State:
  Memory: "User prefers Redis for caching"
  base_salience: 0.6
  outcome_adjustment: 0.0
  effective_salience: 0.6

Decision Made:
  "Suggested Redis for new caching layer"
  Memory contributed with score 0.8 (80% of context)

Outcome Observed:
  User accepted, implementation worked well
  outcome_quality: +0.8

Salience Update:
  attribution = 0.8 / 1.0 = 0.8
  temporal_level = 2 (situational)
  delta = 0.8 * 0.8 * 0.1 * 0.5 = 0.032

New State:
  outcome_adjustment: 0.032
  effective_salience: 0.632

Future Impact:
  This memory now ranks slightly higher in retrieval
  After 10 more positive outcomes, it could reach 0.9+
```

### 3. Multi-Modal Retrieval with RRF

Mind retrieves memories through multiple channels and fuses results.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETRIEVAL ARCHITECTURE                        │
│                                                                   │
│                        Query                                      │
│                          │                                        │
│            ┌─────────────┼─────────────┐                         │
│            ▼             ▼             ▼                         │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│     │  Vector  │  │  Keyword │  │   Graph  │                    │
│     │  Search  │  │  Search  │  │ Traverse │                    │
│     │ (Qdrant) │  │(Postgres)│  │(FalkorDB)│                    │
│     └────┬─────┘  └────┬─────┘  └────┬─────┘                    │
│          │             │             │                           │
│          ▼             ▼             ▼                           │
│     ┌─────────────────────────────────────┐                     │
│     │   Reciprocal Rank Fusion (RRF)      │                     │
│     │   ─────────────────────────────     │                     │
│     │   Combines rankings from all        │                     │
│     │   sources into unified score        │                     │
│     └──────────────────┬──────────────────┘                     │
│                        │                                         │
│                        ▼                                         │
│     ┌─────────────────────────────────────┐                     │
│     │      Salience Weighting             │                     │
│     │   ─────────────────────────────     │                     │
│     │   final_score = rrf_score *         │                     │
│     │                 effective_salience  │                     │
│     └──────────────────┬──────────────────┘                     │
│                        │                                         │
│                        ▼                                         │
│                 Ranked Memories                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Reciprocal Rank Fusion Formula

```python
def reciprocal_rank_fusion(
    rankings: list[list[tuple[str, float]]],  # Multiple ranked lists
    k: int = 60,  # RRF constant
) -> dict[str, float]:
    """
    Combine multiple rankings into a single score.

    RRF is robust to:
    - Different score scales across sources
    - Missing items in some rankings
    - Outlier scores
    """
    fused_scores = defaultdict(float)

    for ranking in rankings:
        for rank, (memory_id, _) in enumerate(ranking, start=1):
            # RRF formula: 1 / (k + rank)
            fused_scores[memory_id] += 1.0 / (k + rank)

    return dict(fused_scores)
```

### 4. Event Sourcing (NATS)

All state changes flow through immutable events.

```yaml
Event Types:
  memory.stored:
    - user_id, memory_id, content_hash, temporal_level
    - Trigger: New memory created

  memory.retrieved:
    - user_id, retrieval_id, memory_ids, query_hash
    - Trigger: Memories fetched for decision

  decision.tracked:
    - user_id, trace_id, memory_ids, decision_type
    - Trigger: Decision made with memory context

  outcome.observed:
    - user_id, trace_id, quality, signal
    - Trigger: Decision outcome detected

  salience.adjusted:
    - user_id, memory_id, previous, new, delta, reason
    - Trigger: Learning applied to memory

Event Guarantees:
  - At-least-once delivery
  - Ordered within user partition
  - Persistent (JetStream)
  - Replayable for rebuilding projections
```

### 5. Causal Inference (FalkorDB)

Track why things work, not just that they work.

```cypher
// Memory → Decision relationship
(memory:Memory)-[:INFLUENCED {score: 0.8}]->(decision:Decision)

// Decision → Outcome relationship
(decision:Decision)-[:RESULTED_IN {quality: 0.8}]->(outcome:Outcome)

// Causal chain
(cause:Memory)-[:CAUSED {confidence: 0.7}]->(effect:Outcome)

// Counterfactual edge
(decision:Decision)-[:ALTERNATIVE {not_chosen: true}]->(alt:Decision)
```

#### Causal Queries

```cypher
// What memories consistently lead to good outcomes?
MATCH (m:Memory)-[:INFLUENCED]->(d:Decision)-[:RESULTED_IN]->(o:Outcome)
WHERE o.quality > 0.5
RETURN m, COUNT(o) as success_count, AVG(o.quality) as avg_quality
ORDER BY success_count DESC

// What would have happened if we chose differently?
MATCH (d:Decision)-[:ALTERNATIVE]->(alt:Decision)
WHERE d.trace_id = $trace_id
RETURN alt, alt.predicted_outcome
```

### 6. Temporal Workflows (Gardener)

Background processes that maintain Mind's health.

```python
@workflow.defn
class GardenerWorkflow:
    """Background maintenance workflows."""

    @workflow.run
    async def run(self, user_id: UUID) -> None:
        # Daily tasks
        await workflow.execute_activity(
            decay_stale_memories,
            args=[user_id],
            schedule_to_close_timeout=timedelta(minutes=30),
        )

        # Weekly tasks
        if is_weekly_run():
            await workflow.execute_activity(
                consolidate_patterns,
                args=[user_id],
                schedule_to_close_timeout=timedelta(hours=1),
            )

            await workflow.execute_activity(
                prune_low_salience_memories,
                args=[user_id, min_salience=0.1],
                schedule_to_close_timeout=timedelta(minutes=30),
            )

        # Monthly tasks
        if is_monthly_run():
            await workflow.execute_activity(
                extract_identity_patterns,
                args=[user_id],
                schedule_to_close_timeout=timedelta(hours=2),
            )
```

---

## Schemas & Data Models

### Memory Schema

```python
@dataclass(frozen=True)
class Memory:
    """A single unit of stored knowledge."""

    # Identity
    memory_id: UUID
    user_id: UUID

    # Content
    content: str                    # The actual information
    content_type: ContentType       # fact, preference, event, goal, observation
    embedding: list[float]          # Vector representation (1536 dims for ada-002)

    # Temporal
    temporal_level: TemporalLevel   # 1-4
    valid_from: datetime            # When this became true
    valid_until: datetime | None    # When this expires (None = indefinite)

    # Salience
    base_salience: float            # Initial importance (0.0 - 1.0)
    outcome_adjustment: float       # Cumulative learning

    # Metadata
    created_at: datetime
    updated_at: datetime
    source: str                     # Where this came from

    @property
    def effective_salience(self) -> float:
        return max(0.0, min(1.0, self.base_salience + self.outcome_adjustment))

    @property
    def is_valid(self) -> bool:
        now = datetime.now(UTC)
        return self.valid_from <= now and (self.valid_until is None or now < self.valid_until)


class ContentType(Enum):
    FACT = "fact"              # Objective truth: "User is CEO of..."
    PREFERENCE = "preference"  # Subjective choice: "User prefers..."
    EVENT = "event"            # Something that happened: "User deployed..."
    GOAL = "goal"              # Desired outcome: "User wants to..."
    OBSERVATION = "observation"  # Pattern noticed: "User typically..."


class TemporalLevel(Enum):
    IMMEDIATE = 1     # Hours
    SITUATIONAL = 2   # Days-Weeks
    SEASONAL = 3      # Months
    IDENTITY = 4      # Years
```

### Decision Trace Schema

```python
@dataclass
class DecisionTrace:
    """Record of a decision and its context."""

    # Identity
    trace_id: UUID
    user_id: UUID
    session_id: UUID

    # Context
    memory_ids: list[UUID]           # Which memories influenced
    memory_scores: dict[str, float]  # How much each contributed

    # Decision
    decision_type: str               # recommendation, action, preference
    decision_summary: str            # What was decided (no PII)
    confidence: float                # How certain (0.0 - 1.0)
    alternatives_count: int          # How many options considered

    # Timing
    created_at: datetime

    # Outcome (filled later)
    outcome_observed: bool = False
    outcome_quality: float | None = None
    outcome_timestamp: datetime | None = None
    outcome_signal: str | None = None
```

### Outcome Schema

```python
@dataclass
class Outcome:
    """Observed result of a decision."""

    trace_id: UUID
    quality: float           # -1.0 (bad) to +1.0 (good)
    signal: str              # How detected: user_accepted, task_completed, etc.
    feedback_text: str | None
    observed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
```

### Salience Update Schema

```python
@dataclass
class SalienceUpdate:
    """A change to a memory's salience."""

    memory_id: UUID
    trace_id: UUID

    delta: float              # How much to change
    reason: str               # Why: "positive_outcome", "negative_outcome"

    previous_adjustment: float
    new_adjustment: float

    @classmethod
    def from_outcome(
        cls,
        memory_id: UUID,
        trace_id: UUID,
        outcome: Outcome,
        contribution: float,
        learning_rate: float = 0.1,
    ) -> "SalienceUpdate":
        delta = outcome.quality * contribution * learning_rate
        return cls(
            memory_id=memory_id,
            trace_id=trace_id,
            delta=delta,
            reason="positive_outcome" if delta > 0 else "negative_outcome",
            previous_adjustment=0.0,  # Filled by caller
            new_adjustment=delta,     # Filled by caller
        )
```

---

## Rulesets

### Memory Storage Rules

```yaml
R1: Temporal Level Selection
  - Level 4 (Identity): Core beliefs, values, permanent preferences
    - Keywords: "always", "never", "is a", "values", "believes"
    - Content types: fact (about identity), preference (permanent)

  - Level 3 (Seasonal): Recurring patterns, project phases
    - Keywords: "typically", "usually", "every [time period]", "pattern"
    - Content types: observation (recurring)

  - Level 2 (Situational): Current projects, recent context
    - Keywords: "working on", "this week", "current", "project"
    - Content types: goal, observation (current)

  - Level 1 (Immediate): Active task, session context
    - Keywords: "right now", "currently", "this session"
    - Content types: event (recent)

R2: Initial Salience Assignment
  - 1.0: Explicit user statements ("I want...", "I prefer...")
  - 0.8: Strong observations with evidence
  - 0.6: Reasonable inferences
  - 0.4: Weak signals or guesses
  - 0.2: Background context, low confidence

R3: Content Validation
  - No PII in raw content (names, emails, addresses)
  - No secrets or credentials
  - No harmful or illegal content
  - Content length: 10-2000 characters

R4: Deduplication
  - Before storing, check for semantic similarity > 0.95
  - If duplicate exists, consider updating existing memory
  - Log duplicate attempts for pattern analysis
```

### Retrieval Rules

```yaml
R5: Query Processing
  - Embed query using same model as memories (text-embedding-ada-002)
  - Extract keywords for full-text search
  - Identify entities for graph traversal

R6: Multi-Source Retrieval
  - Vector search: Top 100 by cosine similarity
  - Keyword search: Top 50 by BM25 score
  - Graph search: 2-hop traversal from query entities

R7: Fusion & Ranking
  - Apply RRF with k=60
  - Multiply RRF score by effective_salience
  - Filter out invalid memories (expired, deleted)
  - Return top N by final score

R8: Retrieval Limits
  - Default limit: 10 memories
  - Maximum limit: 100 memories
  - Include retrieval_id for decision tracking
```

### Decision Tracking Rules

```yaml
R9: What to Track
  - Every decision that uses retrieved memories
  - The memory_ids that influenced the decision
  - The memory_scores (contribution weights)
  - The decision_summary (no PII)

R10: Memory Score Calculation
  - Score = retrieval_score * relevance_to_decision
  - Normalize scores to sum to 1.0
  - Minimum score threshold: 0.01

R11: Confidence Estimation
  - Based on memory quality, coverage, consistency
  - Higher when multiple memories agree
  - Lower when memories conflict or are sparse
```

### Outcome Recording Rules

```yaml
R12: Outcome Signals
  - user_accepted: User explicitly approved the decision
  - user_rejected: User explicitly rejected the decision
  - user_modified: User accepted with modifications
  - task_completed: Task finished successfully
  - task_failed: Task did not complete
  - task_partial: Task partially succeeded
  - agent_feedback: Agent's self-assessment of quality

R13: Quality Scoring
  - +1.0: Perfect outcome, exceeded expectations
  - +0.8: Good outcome, met expectations
  - +0.5: Acceptable outcome, minor issues
  - 0.0: Neutral, no clear signal
  - -0.5: Poor outcome, significant issues
  - -0.8: Bad outcome, failed expectations
  - -1.0: Terrible outcome, caused harm

R14: Outcome Timing
  - Record as soon as outcome is observable
  - Some outcomes are immediate (user acceptance)
  - Some outcomes are delayed (task completion)
  - Maximum tracking window: 7 days
```

### Salience Adjustment Rules

```yaml
R15: Base Formula
  delta = outcome_quality * attribution * learning_rate * temporal_dampening

  Where:
  - outcome_quality: -1.0 to +1.0
  - attribution: 0.0 to 1.0 (memory's contribution)
  - learning_rate: 0.1 (configurable)
  - temporal_dampening: 1.0 / temporal_level

R16: Adjustment Bounds
  - Maximum single adjustment: ±0.1
  - Total outcome_adjustment range: -0.5 to +0.5
  - Effective salience range: 0.0 to 1.0

R17: Temporal Dampening
  - Level 1 (Immediate): 1.0x adjustment rate
  - Level 2 (Situational): 0.5x adjustment rate
  - Level 3 (Seasonal): 0.25x adjustment rate
  - Level 4 (Identity): 0.1x adjustment rate

  Rationale: Higher-level memories should be more stable

R18: Attribution Rules
  - Proportional to memory_score in decision trace
  - Minimum attribution: 0.01 (avoid zero adjustment)
  - Maximum attribution: 1.0 (single memory decisions)
```

### Decay Rules

```yaml
R19: Natural Decay
  - Immediate (Level 1): Decay 10% daily
  - Situational (Level 2): Decay 5% weekly
  - Seasonal (Level 3): Decay 2% monthly
  - Identity (Level 4): Decay 1% yearly

R20: Activity-Based Decay
  - Retrieval resets decay timer
  - Positive outcome extends validity
  - Negative outcome accelerates decay

R21: Pruning Threshold
  - Prune memories with effective_salience < 0.05
  - Archive before deleting (30-day retention)
  - Never prune Level 4 memories automatically
```

---

## Self-Improvement Mechanisms

### 1. Outcome-Driven Learning

The primary learning mechanism: adjust salience based on decision outcomes.

```
Positive Loop:
  Good memories → Good decisions → Positive outcomes → Higher salience → More retrieval

Negative Loop:
  Bad memories → Bad decisions → Negative outcomes → Lower salience → Less retrieval
```

### 2. Pattern Extraction

Periodically analyze successful memories to extract generalizable patterns.

```python
async def extract_patterns(user_id: UUID) -> list[Pattern]:
    """Extract patterns from high-performing memories."""

    # Find memories with consistently positive outcomes
    high_performers = await db.query("""
        SELECT m.* FROM memories m
        JOIN decision_traces dt ON m.memory_id = ANY(dt.memory_ids)
        WHERE m.user_id = $1
          AND dt.outcome_quality > 0.5
        GROUP BY m.memory_id
        HAVING COUNT(*) >= 3
        ORDER BY AVG(dt.outcome_quality) DESC
    """, user_id)

    # Cluster similar memories
    clusters = cluster_by_embedding(high_performers)

    # Extract pattern from each cluster
    patterns = []
    for cluster in clusters:
        pattern = summarize_cluster(cluster)
        patterns.append(pattern)

    return patterns
```

### 3. Counterfactual Analysis

Learn from what didn't happen.

```python
async def analyze_counterfactuals(trace_id: UUID) -> CounterfactualReport:
    """What if we had made a different decision?"""

    trace = await get_trace(trace_id)

    # Find similar past decisions with different outcomes
    similar_decisions = await find_similar_decisions(
        context=trace.memory_ids,
        exclude=trace.trace_id,
    )

    # Compare outcomes
    report = CounterfactualReport(
        actual_decision=trace,
        alternatives=[
            {
                "decision": alt,
                "outcome_difference": alt.outcome_quality - trace.outcome_quality,
                "key_differences": diff_memories(trace, alt),
            }
            for alt in similar_decisions
        ]
    )

    return report
```

### 4. Hypothesis Testing

Systematically test improvements to Mind's algorithms.

```python
class HypothesisTest:
    """Framework for testing Mind improvements."""

    def __init__(
        self,
        name: str,
        control: Callable,   # Current algorithm
        treatment: Callable, # New algorithm
        metric: str,         # What to measure
    ):
        self.name = name
        self.control = control
        self.treatment = treatment
        self.metric = metric
        self.results = {"control": [], "treatment": []}

    async def run_trial(self, user_id: UUID, query: str):
        """Run one trial of A/B test."""

        # Randomly assign
        is_treatment = random.random() < 0.5

        if is_treatment:
            result = await self.treatment(user_id, query)
            self.results["treatment"].append(result)
        else:
            result = await self.control(user_id, query)
            self.results["control"].append(result)

    def analyze(self) -> HypothesisResult:
        """Analyze results with statistical significance."""

        control_mean = mean(self.results["control"])
        treatment_mean = mean(self.results["treatment"])

        # t-test for significance
        t_stat, p_value = ttest_ind(
            self.results["control"],
            self.results["treatment"],
        )

        return HypothesisResult(
            name=self.name,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            improvement=(treatment_mean - control_mean) / control_mean,
            p_value=p_value,
            significant=p_value < 0.05,
        )
```

### 5. Federated Learning

Learn from patterns across users while preserving privacy.

```python
async def federate_pattern(pattern: Pattern) -> FederatedPattern:
    """Share pattern across users with privacy protection."""

    # Ensure pattern meets privacy thresholds
    assert pattern.source_count >= 100  # Minimum instances
    assert pattern.user_count >= 10     # Minimum users

    # Apply differential privacy
    noisy_pattern = add_laplace_noise(
        pattern,
        epsilon=0.1,  # Privacy budget
    )

    # Sanitize any remaining PII
    sanitized = remove_pii(noisy_pattern)

    # Store in federated pool
    await store_federated_pattern(sanitized)

    return sanitized
```

---

## Hypotheses & Experiments

### Active Hypotheses

These are current theories about how to improve Mind. Each should be tested.

```yaml
H1: Temporal Dampening Rates
  Current: [1.0, 0.5, 0.25, 0.1] for levels 1-4
  Hypothesis: Steeper dampening [1.0, 0.3, 0.1, 0.03] prevents identity drift
  Metric: Identity-level memory stability over 30 days
  Status: Not tested

H2: RRF K-Parameter
  Current: k=60 (standard)
  Hypothesis: k=30 favors top results more strongly
  Metric: Decision quality (outcome average)
  Status: Not tested

H3: Learning Rate Decay
  Current: Fixed 0.1 learning rate
  Hypothesis: Decay learning rate over time (0.1 → 0.01)
  Metric: Salience stability, false positive rate
  Status: Not tested

H4: Negative Outcome Weighting
  Current: Symmetric (±1.0 range)
  Hypothesis: Negative outcomes should weight 2x (loss aversion)
  Metric: Harmful memory suppression speed
  Status: Not tested

H5: Retrieval Count Impact
  Current: Default 10 memories
  Hypothesis: Fewer memories (5) lead to more focused decisions
  Metric: Decision confidence, outcome quality
  Status: Not tested

H6: Multi-Modal Fusion Weights
  Current: Equal weight for vector/keyword/graph
  Hypothesis: Vector 0.5, Keyword 0.3, Graph 0.2
  Metric: Retrieval relevance, user satisfaction
  Status: Not tested
```

### Experiment Log

```yaml
Experiment Template:
  id: EXP-XXX
  hypothesis: Which hypothesis being tested
  start_date: When started
  end_date: When concluded
  sample_size: Number of decisions
  control_group: Description
  treatment_group: Description
  results:
    control_mean: X.XX
    treatment_mean: X.XX
    improvement: X.X%
    p_value: X.XXX
    significant: true/false
  conclusion: What we learned
  action: What we changed
```

### Proposed Experiments

1. **EXP-001: Salience Initialization**
   - Test whether ML-based initial salience outperforms heuristics
   - Train model on historical outcome data

2. **EXP-002: Embedding Model Comparison**
   - Compare ada-002 vs text-embedding-3-small vs text-embedding-3-large
   - Measure retrieval quality and cost tradeoff

3. **EXP-003: Causal Attribution**
   - Test causal inference for attribution vs simple proportional
   - Use DoWhy for causal estimation

---

## Evolution Log

Track how Mind's architecture evolves over time.

```yaml
Version: 5.0.0
Date: 2024-12-30
Changes:
  - Initial v5 architecture
  - Hierarchical temporal memory (4 levels)
  - Outcome-weighted salience
  - Multi-modal retrieval with RRF
  - Event sourcing with NATS
  - Causal inference with FalkorDB
  - Temporal workflows with Gardener

Lessons Learned:
  - (To be populated as we learn)

Open Questions:
  - Optimal learning rate for different use cases?
  - How to handle conflicting memories?
  - When should memories be promoted to higher temporal levels?
  - How to balance exploration vs exploitation in retrieval?
```

---

## Appendix: Quick Reference

### The Learning Loop (One Sentence)

> Store memories, retrieve for decisions, observe outcomes, adjust salience, repeat.

### Key Formulas

```
effective_salience = base_salience + outcome_adjustment

salience_delta = outcome_quality × attribution × learning_rate × (1/temporal_level)

rrf_score = Σ(1 / (k + rank)) for each source

final_rank = rrf_score × effective_salience
```

### Key Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| Min salience for retrieval | 0.05 | Filter noise |
| Prune threshold | 0.05 | Clean up dead memories |
| Max single adjustment | 0.1 | Prevent wild swings |
| Semantic similarity for dedup | 0.95 | Avoid duplicates |
| Privacy min instances | 100 | Federated patterns |
| Privacy min users | 10 | Federated patterns |

### Command Cheat Sheet

```bash
# Store a memory
mind_remember(user_id, content, content_type, temporal_level, salience)

# Retrieve context
mind_retrieve(user_id, query, limit)

# Track decision + outcome
mind_decide(user_id, memory_ids, decision_summary, outcome_quality, ...)

# Check health
mind_health()
```

---

*This is a living document. Update it as Mind evolves.*

*Last Updated: 2024-12-30*
*Version: 5.0.0*
