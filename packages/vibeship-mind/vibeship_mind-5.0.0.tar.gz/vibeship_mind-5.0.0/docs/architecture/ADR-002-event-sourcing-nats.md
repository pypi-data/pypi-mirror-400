# ADR-002: Event Sourcing with NATS JetStream

## Status
Accepted

## Context
Mind v5 requires:
- Audit trail of all state changes
- Ability to rebuild projections
- Decoupled services for scalability
- Reliable event delivery

## Decision
Use event sourcing as the primary data pattern with NATS JetStream as the event backbone.

**Event Flow:**
1. Commands validated and converted to events
2. Events stored in PostgreSQL (source of truth)
3. Events published to NATS JetStream
4. Consumers process events asynchronously
5. Projections updated from events

**Key Events:**
- MemoryCreated, MemoryUpdated, MemoryPromoted
- DecisionTracked, OutcomeObserved
- PatternExtracted, PatternApplied

## Consequences

### Positive
- Complete audit trail for compliance
- Temporal queries ("what did we know at time X")
- Easy to add new consumers/projections
- Natural fit for causal tracking

### Negative
- Eventual consistency complexity
- Storage growth from event log
- Need for event versioning strategy

### Mitigations
- Idempotent consumers handle redelivery
- Event compaction for old data
- Schema registry for event evolution
