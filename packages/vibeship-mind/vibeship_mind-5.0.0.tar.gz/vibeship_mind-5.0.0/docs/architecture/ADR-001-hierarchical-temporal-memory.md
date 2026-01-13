# ADR-001: Hierarchical Temporal Memory Architecture

## Status
Accepted

## Context
Mind v5 needs to store and retrieve memories that vary in their temporal scope and importance. Some memories are transient (today's context), while others persist for years (user identity).

## Decision
Implement a 4-level hierarchical temporal memory system:

1. **Immediate** (hours): Current session context
2. **Situational** (days-weeks): Recent patterns and decisions
3. **Seasonal** (months): Recurring patterns and preferences
4. **Identity** (years): Core values, long-term preferences

Each level has different:
- Retention policies
- Salience decay rates
- Promotion/demotion triggers

## Consequences

### Positive
- Natural alignment with human memory systems
- Efficient retrieval by temporal relevance
- Clear promotion path for important memories
- Optimized storage (most data is transient)

### Negative
- Complexity in determining promotion triggers
- Potential for important memories to decay before promotion
- Need for careful tuning of thresholds

### Mitigations
- Outcome-based salience adjustment prevents premature decay
- Explicit user marking can force promotion
- Gardener worker continuously evaluates promotion candidates
