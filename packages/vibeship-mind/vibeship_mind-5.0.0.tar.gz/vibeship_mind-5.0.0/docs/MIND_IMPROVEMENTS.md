# Mind v5 Improvement Tracker

> **Living log of issues found, hypotheses tested, and improvements made.**
>
> Mind is a self-improving system. This document tracks its evolution.

---

## Current Issues

Issues discovered during testing that need resolution.

### ISS-001: Salience Not Updating via MCP

**Status**: FIXED (code applied, requires MCP server restart)
**Discovered**: 2024-12-30
**Fixed**: 2024-12-30
**Severity**: High (blocks core learning loop)

**Description**:
When using `mind_decide` via MCP, the salience adjustment returns `memories_updated: 0` and `salience_changes: {}`.

**Root Cause Analysis**:
The decision tracking flow requires `memory_scores` to calculate attribution:
```python
# In decisions.py line 142-144
total_score = sum(trace.memory_scores.values()) or 1.0
attributions = {mid: score / total_score for mid, score in trace.memory_scores.items()}
```

When `memory_scores` is empty, `attributions` is empty, and no salience updates occur.

**Current Flow**:
```
mind_decide()
  → client.track(memory_ids=..., memory_scores=None)  # ← Problem: no scores
  → client.outcome(trace_id=...)
  → trace.memory_scores is empty
  → attributions is empty
  → no updates
```

**Expected Flow**:
```
mind_decide()
  → Generate default scores (equal weight) if not provided
  → OR: Retrieve scores from last retrieval
  → track(memory_ids=..., memory_scores=calculated)
  → outcome records with proper attribution
  → salience updates correctly
```

**Proposed Fix**:
Option A: Pass retrieval scores when calling mind_decide
Option B: Generate equal-weight scores in MCP server
Option C: Link decision to last retrieval_id and use those scores

**Files Affected**:
- `src/mind/mcp/server.py` (mind_decide function)
- `src/mind/sdk/client.py` (track method)
- `src/mind/api/routes/decisions.py` (track_decision)

---

## Improvement Proposals

### IMP-001: Automatic Score Generation

**Status**: IMPLEMENTED ✅
**Priority**: High
**Related Issue**: ISS-001
**Implemented**: 2024-12-30

**Proposal**:
If `memory_scores` is not provided, generate equal-weight scores:

```python
# In mcp/server.py mind_decide
if not memory_scores:
    # Equal weight for all memories
    memory_scores = {
        str(mid): 1.0 / len(memory_ids)
        for mid in memory_ids
    }
```

**Pros**:
- Simple to implement
- Backwards compatible
- Better than no learning at all

**Cons**:
- Loses information about which memories were most relevant
- Equal attribution may not reflect true contribution

**Decision**: IMPLEMENTED in `src/mind/mcp/server.py` (lines 196-201)

---

### IMP-002: Retrieval-Decision Linking

**Status**: IMPLEMENTED ✅
**Priority**: Medium
**Related Issue**: ISS-001
**Implemented**: 2024-12-30

**Proposal**:
Pass retrieval scores directly to decisions for accurate attribution:

```python
# mind_retrieve returns memories with scores
retrieval = await mind_retrieve(user_id, query)

# Extract scores from response
memory_scores = {
    m["memory_id"]: m["score"]
    for m in retrieval["memories"]
}

# mind_decide accepts memory_scores
await mind_decide(
    user_id=user_id,
    memory_ids=list(memory_scores.keys()),
    memory_scores=memory_scores,  # ← Actual retrieval scores
    decision_summary="...",
    outcome_quality=0.9,
)
```

**Pros**:
- Accurate attribution based on retrieval scores
- Clean data flow
- Enables retrieval quality analysis
- Backwards compatible (falls back to equal weights)

**Implementation**:
- Added `memory_scores` parameter to `mind_decide` in `src/mind/mcp/server.py`
- Scores passed through to `client.track()` for attribution calculation
- If not provided, auto-generates equal weights (IMP-001 behavior)

**Decision**: IMPLEMENTED

---

## Tested Hypotheses

Log of experiments run and their results.

### HYP-001: Hierarchical Temporal Memory

**Tested**: 2024-12-30
**Status**: PASSED

**Hypothesis**: Memories can be stored at 4 distinct temporal levels with correct naming and salience.

**Test**:
```python
# Created memories at each level
Level 1 (Immediate): "debugging production issue" → salience 0.90
Level 2 (Situational): "working on Mind v5" → salience 0.85
Level 3 (Seasonal): "quarterly sprints" → salience 0.70
Level 4 (Identity): "founder of VIBESHIP" → salience 1.00
```

**Result**: All levels stored correctly with proper temporal_level_name.

**Conclusion**: Hierarchical memory structure works as designed.

---

### HYP-002: Outcome-Weighted Salience

**Tested**: 2024-12-30
**Status**: PASSED ✅

**Hypothesis**: Positive outcomes increase memory salience, negative decrease it.

**Test**:
1. Store memory with salience 0.5
2. Track decision with memory_scores
3. Record positive outcome (+0.9)
4. Verify salience increased

**Result (via direct API)**:
```
Memory created: salience = 0.5
Decision tracked with trace_id
Outcome recorded (quality=0.9)
Final salience = 0.59
Delta = +0.09
```

**Formula Verified**:
```
delta = quality × attribution × learning_rate
      = 0.9 × 1.0 × 0.1
      = 0.09 ✓
```

**Conclusion**: Core learning loop works correctly when memory_scores are provided.
MCP fix applied (IMP-001). Requires server restart to take effect.

---

## Architecture Decisions

Significant decisions made about Mind's design.

### ADR-001: Event Sourcing for All State Changes

**Date**: 2024-12-28
**Status**: Accepted

**Context**:
Mind needs to track all changes for learning and debugging.

**Decision**:
All state changes flow through NATS events. No direct database writes for core operations.

**Consequences**:
- Can replay events to rebuild state
- Full audit trail
- Slight latency increase
- More complex write path

---

### ADR-002: Temporal Level as Integer (1-4)

**Date**: 2024-12-28
**Status**: Accepted

**Context**:
Need to represent temporal hierarchy in a way that supports:
- Ordering (immediate < situational < seasonal < identity)
- Dampening calculations (1 / level)
- Clear naming

**Decision**:
Use integers 1-4 with level names as computed property:
```python
class TemporalLevel(Enum):
    IMMEDIATE = 1
    SITUATIONAL = 2
    SEASONAL = 3
    IDENTITY = 4
```

**Consequences**:
- Simple arithmetic for dampening
- Clear ordering
- Must maintain name mapping

---

## Metrics & Baselines

Establish baselines for measuring improvement.

### Baseline Metrics (2024-12-30)

```yaml
Retrieval:
  latency_p50: ~650ms
  latency_p95: TBD
  relevance_score: TBD (need human eval)

Learning:
  salience_update_rate: 0% (broken, ISS-001)
  decision_outcome_rate: TBD

System:
  memory_count: ~20 (test data)
  decision_traces: ~5 (test data)
```

### Target Metrics (Post-Fixes)

```yaml
Retrieval:
  latency_p50: <500ms
  latency_p95: <1000ms
  relevance_score: >0.8 (user-rated)

Learning:
  salience_update_rate: 100% (all decisions with outcomes)
  decision_quality_trend: Positive over 30 days

System:
  uptime: 99.9%
  error_rate: <0.1%
```

---

## Verified Working Features (2024-12-30)

All core Mind v5 features have been verified as operational:

### ✅ Causal Graph Population
- Event consumers running via `docker-compose` consumers service
- `decision.tracked` and `outcome.observed` events processed
- FalkorDB stores Memory→Decision→Outcome paths with INFLUENCED and LED_TO edges

### ✅ Retrieval-Decision Linking (IMP-002)
- `mind_decide` accepts optional `memory_scores` parameter
- Agents can pass actual retrieval scores for accurate attribution
- Falls back to equal weights if scores not provided

### ✅ Gardener Workflows
All Temporal schedules ACTIVE:
- `gardener-daily`: 24h schedule (2 runs completed) - promotion, expiration, consolidation
- `analyze-outcomes-weekly`: 7-day schedule - outcome analysis
- `calibrate-confidence-monthly`: 30-day schedule - confidence calibration
- `extract-patterns-monthly`: 30-day schedule - pattern extraction with differential privacy

### ✅ Deduplication/Consolidation
- Daily `MemoryConsolidationWorkflow` merges similar memories
- Thresholds: 85% semantic similarity, 48h minimum age
- NATS 2-minute duplicate_window prevents exact duplicate events

### ✅ Natural Decay
- Recency decay applied during retrieval: `1.0 / (1.0 + age_hours / 168)`
- Exponential decay over 7-day window

### ✅ Observability Metrics
Prometheus metrics exposed at `/metrics`:
- `mind_retrieval_latency_seconds` - by source (vector, keyword, fusion)
- `mind_retrieval_sources_used_total` - source usage counters
- `mind_gardener_*_succeeded_total` - workflow success counters
- `mind_privacy_budget_spent` - differential privacy tracking
- `mind_http_requests_total` - request counters by endpoint

---

## Next Actions

Prioritized list of what to do next.

1. **[LOW]** Add Prometheus/Grafana to docker-compose for visualization
2. **[LOW]** Configure alerting rules
3. **[LOW]** Run hypothesis experiments
   - H1: Temporal Dampening Rates
   - H2: RRF K-Parameter

**Future (when more users):**
- Intent Graph for collective intelligence
- Cross-user pattern federation

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2024-12-30 | Initial document created | Claude |
| 2024-12-30 | Added ISS-001 (salience not updating) | Claude |
| 2024-12-30 | Added HYP-001 (temporal memory - PASSED) | Claude |
| 2024-12-30 | Added HYP-002 (salience - BLOCKED) | Claude |
| 2024-12-30 | Implemented IMP-001 (auto score generation) | Claude |
| 2024-12-30 | ISS-001 → FIXED (code applied) | Claude |
| 2024-12-30 | HYP-002 → PASSED (verified via E2E API test) | Claude |
| 2024-12-30 | Test 7: Decision Tracking E2E verified | Claude |
| 2024-12-30 | Added consumers service to docker-compose | Claude |
| 2024-12-30 | Fixed NATS DLQ subject overlap | Claude |
| 2024-12-30 | IMP-002 IMPLEMENTED (memory_scores parameter) | Claude |
| 2024-12-30 | Verified all Gardener schedules ACTIVE | Claude |
| 2024-12-30 | Verified consolidation/deduplication working | Claude |
| 2024-12-30 | Verified Prometheus metrics exposed | Claude |

---

*Update this document as Mind evolves.*
