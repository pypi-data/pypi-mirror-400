# Mind Standard Tier - Implementation Plan

> **Status**: Ready for Implementation
> **Priority**: High
> **Target**: Production-ready Standard tier

---

## Overview

This plan implements Mind Standard tier as described in the PRD and ADR-010. The work is organized into 6 phases with clear dependencies and deliverables.

---

## Phase 1: Port Interfaces

**Goal**: Define clean abstraction boundaries between core logic and infrastructure

**Duration**: 2-3 days

### Tasks

| # | Task | File | Dependencies |
|---|------|------|--------------|
| 1.1 | Create ports directory structure | `src/mind/ports/` | None |
| 1.2 | Define IMemoryStorage interface | `src/mind/ports/storage.py` | 1.1 |
| 1.3 | Define IDecisionStorage interface | `src/mind/ports/storage.py` | 1.1 |
| 1.4 | Define IEventPublisher interface | `src/mind/ports/events.py` | 1.1 |
| 1.5 | Define IEventConsumer interface | `src/mind/ports/events.py` | 1.1 |
| 1.6 | Define IVectorSearch interface | `src/mind/ports/vectors.py` | 1.1 |
| 1.7 | Define ICausalGraph interface | `src/mind/ports/graphs.py` | 1.1 |
| 1.8 | Define IBackgroundScheduler interface | `src/mind/ports/scheduler.py` | 1.1 |
| 1.9 | Create MindContainer base class | `src/mind/container.py` | 1.2-1.8 |

### Deliverables

- [ ] All port interfaces defined with type hints
- [ ] MindContainer skeleton ready for adapters
- [ ] Unit tests for interface contracts

### Code Preview

```python
# src/mind/ports/__init__.py
from .storage import IMemoryStorage, IDecisionStorage
from .events import IEventPublisher, IEventConsumer
from .vectors import IVectorSearch
from .graphs import ICausalGraph
from .scheduler import IBackgroundScheduler

__all__ = [
    "IMemoryStorage",
    "IDecisionStorage",
    "IEventPublisher",
    "IEventConsumer",
    "IVectorSearch",
    "ICausalGraph",
    "IBackgroundScheduler",
]
```

---

## Phase 2: Standard Adapters

**Goal**: Implement Standard tier adapters using PostgreSQL + APScheduler

**Duration**: 4-5 days

### Tasks

| # | Task | File | Dependencies |
|---|------|------|--------------|
| 2.1 | Create adapters directory structure | `src/mind/adapters/standard/` | Phase 1 |
| 2.2 | Implement PostgresMemoryStorage | `adapters/standard/postgres_storage.py` | 2.1 |
| 2.3 | Implement PostgresDecisionStorage | `adapters/standard/postgres_storage.py` | 2.1 |
| 2.4 | Implement PostgresEventPublisher | `adapters/standard/postgres_events.py` | 2.1 |
| 2.5 | Implement PostgresEventConsumer | `adapters/standard/postgres_events.py` | 2.1 |
| 2.6 | Implement PgVectorSearch | `adapters/standard/pgvector_search.py` | 2.1 |
| 2.7 | Implement PostgresCausalGraph | `adapters/standard/postgres_causal.py` | 2.1 |
| 2.8 | Implement APSchedulerRunner | `adapters/standard/apscheduler_runner.py` | 2.1 |
| 2.9 | Create Standard container factory | `src/mind/container.py` | 2.2-2.8 |
| 2.10 | Add causal_edges table migration | `migrations/` | 2.7 |

### Deliverables

- [ ] All Standard adapters implemented
- [ ] Integration tests against PostgreSQL
- [ ] Database migration for causal tables

### Database Schema Addition

```sql
-- migrations/0XX_add_causal_edges.sql

CREATE TABLE IF NOT EXISTS causal_edges (
    edge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cause_id UUID NOT NULL,
    effect_id UUID NOT NULL,
    strength FLOAT NOT NULL DEFAULT 0.5,
    evidence TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(cause_id, effect_id),

    CONSTRAINT valid_strength CHECK (strength >= 0 AND strength <= 1)
);

CREATE INDEX idx_causal_edges_cause ON causal_edges(cause_id);
CREATE INDEX idx_causal_edges_effect ON causal_edges(effect_id);

-- Trigger to update timestamp
CREATE TRIGGER update_causal_edges_timestamp
    BEFORE UPDATE ON causal_edges
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

---

## Phase 3: Synchronous Learning Service

**Goal**: Implement immediate salience updates without event-driven architecture

**Duration**: 2-3 days

### Tasks

| # | Task | File | Dependencies |
|---|------|------|--------------|
| 3.1 | Create LearningService class | `src/mind/services/learning_service.py` | Phase 2 |
| 3.2 | Implement record_outcome with sync updates | `services/learning_service.py` | 3.1 |
| 3.3 | Implement attribution-weighted adjustments | `services/learning_service.py` | 3.1 |
| 3.4 | Add salience bounds checking | `services/learning_service.py` | 3.1 |
| 3.5 | Update DecisionService to use LearningService | `services/decision_service.py` | 3.2 |
| 3.6 | Update API endpoints to use new flow | `api/routes/decisions.py` | 3.5 |

### Deliverables

- [ ] LearningService fully implemented
- [ ] Existing tests pass
- [ ] New tests for synchronous learning

### Learning Algorithm

```python
def calculate_salience_adjustment(
    attribution_score: float,  # How much this memory contributed
    outcome_quality: float,    # -1.0 (bad) to 1.0 (good)
    memory_retrieval_rank: int # Position in retrieval results
) -> float:
    """
    Calculate salience adjustment for a memory based on decision outcome.

    Higher attribution + better outcome = bigger positive adjustment.
    Higher attribution + worse outcome = bigger negative adjustment.

    Rank-based decay ensures top-ranked memories get more credit/blame.
    """
    # Rank decay: top result gets full weight, others decay
    rank_weight = 1.0 / (1.0 + 0.3 * memory_retrieval_rank)

    # Attribution normalizes contribution
    weighted_attribution = attribution_score * rank_weight

    # Scale adjustment (max 10% change per outcome)
    adjustment = weighted_attribution * outcome_quality * 0.1

    return adjustment
```

---

## Phase 4: Embedded PostgreSQL

**Goal**: Bundle PostgreSQL for zero-config local development

**Duration**: 3-4 days

### Tasks

| # | Task | File | Dependencies |
|---|------|------|--------------|
| 4.1 | Create embedded infrastructure module | `src/mind/infrastructure/embedded/` | None |
| 4.2 | Implement binary download logic | `infrastructure/embedded/downloader.py` | 4.1 |
| 4.3 | Implement EmbeddedPostgres class | `infrastructure/embedded/postgres.py` | 4.2 |
| 4.4 | Add initdb and startup logic | `infrastructure/embedded/postgres.py` | 4.3 |
| 4.5 | Add graceful shutdown | `infrastructure/embedded/postgres.py` | 4.3 |
| 4.6 | Add pgvector extension handling | `infrastructure/embedded/postgres.py` | 4.4 |
| 4.7 | Integrate with MindContainer | `src/mind/container.py` | 4.5 |
| 4.8 | Add Windows support | `infrastructure/embedded/` | 4.3 |
| 4.9 | Add macOS support | `infrastructure/embedded/` | 4.3 |
| 4.10 | Add Linux support | `infrastructure/embedded/` | 4.3 |

### Deliverables

- [ ] EmbeddedPostgres works on Windows, macOS, Linux
- [ ] Lazy binary download (not bundled in pip package)
- [ ] Data persistence across restarts
- [ ] Integration tests

### Platform Support Matrix

| Platform | Architecture | Binary Source |
|----------|--------------|---------------|
| Windows | x64 | postgresql-binaries |
| macOS | x64 | postgresql-binaries |
| macOS | arm64 | postgresql-binaries |
| Linux | x64 | postgresql-binaries |
| Linux | arm64 | postgresql-binaries |

---

## Phase 5: CLI and API Updates

**Goal**: Polish the developer experience with simple commands

**Duration**: 2-3 days

### Tasks

| # | Task | File | Dependencies |
|---|------|------|--------------|
| 5.1 | Create CLI module structure | `src/mind/cli/` | None |
| 5.2 | Implement `mind serve` command | `cli/serve.py` | Phase 4 |
| 5.3 | Implement `mind migrate` command | `cli/migrate.py` | Phase 2 |
| 5.4 | Implement `mind demo` command | `cli/demo.py` | 5.2 |
| 5.5 | Add tier auto-detection | `cli/serve.py` | 5.2 |
| 5.6 | Update API startup for Standard tier | `api/main.py` | Phase 3 |
| 5.7 | Add configuration documentation | `docs/` | 5.2-5.4 |

### Deliverables

- [ ] `mind serve` starts embedded PG if no DATABASE_URL
- [ ] `mind migrate` applies schema to any PostgreSQL
- [ ] `mind demo` shows interactive learning loop
- [ ] Clear CLI help text

### CLI Commands

```bash
# Start Mind Standard (auto-detects tier)
mind serve
mind serve --port 8080
mind serve --database-url postgresql://...

# Run migrations
mind migrate
mind migrate --database-url postgresql://...

# Demo mode (seeds data, opens dashboard)
mind demo

# Health check
mind health

# Show config
mind config
```

---

## Phase 6: Testing and Documentation

**Goal**: Ensure quality and document the tier

**Duration**: 2-3 days

### Tasks

| # | Task | File | Dependencies |
|---|------|------|--------------|
| 6.1 | Add Standard tier unit tests | `tests/unit/adapters/standard/` | Phase 2 |
| 6.2 | Add integration tests | `tests/integration/standard/` | Phase 5 |
| 6.3 | Add learning loop tests | `tests/unit/services/` | Phase 3 |
| 6.4 | Add embedded PG tests | `tests/integration/embedded/` | Phase 4 |
| 6.5 | Write Quick Start guide | `docs/quick-start.md` | All |
| 6.6 | Write Cloud Setup guide | `docs/cloud-setup.md` | All |
| 6.7 | Write Migration guide | `docs/enterprise-migration.md` | All |
| 6.8 | Update README | `README.md` | All |

### Deliverables

- [ ] 80%+ test coverage for new code
- [ ] All existing tests pass
- [ ] Clear documentation for all user journeys

---

## Dependency Graph

```
Phase 1: Port Interfaces
    │
    ├──► Phase 2: Standard Adapters ──► Phase 3: Learning Service
    │         │                              │
    │         ▼                              │
    │    Phase 4: Embedded PG ◄──────────────┘
    │         │
    │         ▼
    └──► Phase 5: CLI Updates
              │
              ▼
         Phase 6: Testing & Docs
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Embedded PG binary issues | Test on all platforms early (Phase 4) |
| pgvector performance | Benchmark with 100k memories, document limits |
| Sync learning latency | Profile and optimize, add batching if needed |
| Breaking existing tests | Run full test suite after each phase |

---

## Success Criteria

### Phase Gates

| Phase | Gate Criteria |
|-------|---------------|
| 1 | All interfaces defined, type-checked, documented |
| 2 | All adapters pass interface contract tests |
| 3 | Learning loop tests pass, API unchanged |
| 4 | Embedded PG starts on Windows/macOS/Linux |
| 5 | `mind serve` works with zero config |
| 6 | Docs reviewed, 80% coverage achieved |

### Final Acceptance

- [ ] User can install with `pip install mind-sdk`
- [ ] User can start with `mind serve` (no config)
- [ ] Learning loop demonstrably improves retrieval
- [ ] All existing MCP tools work unchanged
- [ ] Claude hooks work unchanged
- [ ] Cloud PostgreSQL (Supabase) works

---

## File Changes Summary

### New Files

```
src/mind/
├── ports/
│   ├── __init__.py
│   ├── storage.py
│   ├── events.py
│   ├── vectors.py
│   ├── graphs.py
│   └── scheduler.py
├── adapters/
│   ├── __init__.py
│   └── standard/
│       ├── __init__.py
│       ├── postgres_storage.py
│       ├── postgres_events.py
│       ├── pgvector_search.py
│       ├── postgres_causal.py
│       └── apscheduler_runner.py
├── services/
│   └── learning_service.py
├── infrastructure/
│   └── embedded/
│       ├── __init__.py
│       ├── postgres.py
│       └── downloader.py
├── cli/
│   ├── __init__.py
│   ├── serve.py
│   ├── migrate.py
│   └── demo.py
└── container.py

docs/
├── quick-start.md
├── cloud-setup.md
└── enterprise-migration.md

tests/
├── unit/
│   ├── adapters/
│   │   └── standard/
│   └── services/
│       └── test_learning_service.py
└── integration/
    ├── standard/
    └── embedded/
```

### Modified Files

```
src/mind/
├── api/
│   ├── main.py              # Tier detection, container init
│   └── routes/
│       └── decisions.py     # Use LearningService
├── services/
│   └── decision_service.py  # Integrate LearningService

migrations/
└── 0XX_add_causal_edges.sql

README.md
pyproject.toml               # Add new dependencies
```

---

## Next Steps

1. **Approve this plan** - Review with stakeholders
2. **Create branch** - `feature/standard-tier`
3. **Begin Phase 1** - Port interfaces
4. **Daily check-ins** - Track progress against phases

---

*Document End*
