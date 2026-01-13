# ADR-003: Outcome-Weighted Salience

## Status
Accepted

## Context
Traditional memory systems weight by recency or access frequency. This doesn't capture whether a memory actually helped make good decisions.

## Decision
Implement outcome-weighted salience:

```
effective_salience = base_salience + outcome_adjustment
```

Where `outcome_adjustment` is calculated from:
1. Track which memories were used in each decision
2. Observe decision outcomes (positive/negative)
3. Attribute outcome quality to contributing memories
4. Adjust salience based on attribution

**Attribution Algorithm:**
- Memories retrieved for successful decisions: +0.05 to +0.15
- Memories retrieved for failed decisions: -0.05 to -0.15
- Weight by relevance score and recency

## Consequences

### Positive
- Memories that help get promoted naturally
- Misleading memories get demoted
- Self-improving retrieval quality
- Measurable decision improvement over time

### Negative
- Delayed feedback (outcomes take time)
- Attribution is approximate
- Risk of feedback loops

### Mitigations
- Causal inference for better attribution
- Bounded adjustment range
- Decay of adjustment over time
