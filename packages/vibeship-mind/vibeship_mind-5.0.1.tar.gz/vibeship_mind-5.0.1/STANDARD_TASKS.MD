# Mind Standard Tier - Task Tracker

> **Status**: In Progress
> **Started**: January 4, 2026
> **Target**: Production-ready Standard tier
> **Repository**: Same repo (monorepo with port-based abstraction)

---

## Quick Reference

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Port Interfaces | ✅ Complete | 9/9 |
| Phase 2: Standard Adapters | ✅ Complete | 10/10 |
| Phase 3: Synchronous Learning | ✅ Complete | 6/6 |
| Phase 4: Embedded PostgreSQL | ✅ Complete | 10/10 |
| Phase 5: CLI and API Updates | ✅ Complete | 7/7 |
| Phase 6: Testing and Documentation | 🔴 Not Started | 0/8 |
| **TOTAL** | | **42/50** |

**Legend**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Blocked

---

## Phase 1: Port Interfaces

**Goal**: Define clean abstraction boundaries between core logic and infrastructure

**Status**: ✅ Complete (9/9 tasks)

| # | Task | File | Status | Notes |
|---|------|------|:------:|-------|
| 1.1 | Create ports directory structure | `src/mind/ports/` | ✅ | Created with __init__.py |
| 1.2 | Define IMemoryStorage interface | `src/mind/ports/storage.py` | ✅ | Full CRUD + lifecycle |
| 1.3 | Define IDecisionStorage interface | `src/mind/ports/storage.py` | ✅ | Traces + outcomes |
| 1.4 | Define IEventPublisher interface | `src/mind/ports/events.py` | ✅ | Publish + batch |
| 1.5 | Define IEventConsumer interface | `src/mind/ports/events.py` | ✅ | Subscribe + patterns |
| 1.6 | Define IVectorSearch interface | `src/mind/ports/vectors.py` | ✅ | Search + filter |
| 1.7 | Define ICausalGraph interface | `src/mind/ports/graphs.py` | ✅ | Nodes + edges + traversal |
| 1.8 | Define IBackgroundScheduler interface | `src/mind/ports/scheduler.py` | ✅ | Interval + cron + once |
| 1.9 | Create MindContainer base class | `src/mind/container.py` | ✅ | Standard + Enterprise factories |

### Phase 1 Deliverables

- [x] All port interfaces defined with type hints
- [x] MindContainer skeleton ready for adapters
- [ ] Unit tests for interface contracts

---

## Phase 2: Standard Adapters

**Goal**: Implement Standard tier adapters using PostgreSQL + APScheduler

**Status**: ✅ Complete (10/10 tasks)

**Dependencies**: Phase 1 complete

| # | Task | File | Status | Notes |
|---|------|------|:------:|-------|
| 2.1 | Create adapters directory structure | `src/mind/adapters/standard/` | ✅ | With __init__.py exports |
| 2.2 | Implement PostgresMemoryStorage | `adapters/standard/postgres_storage.py` | ✅ | Full CRUD, salience, lifecycle |
| 2.3 | Implement PostgresDecisionStorage | `adapters/standard/postgres_storage.py` | ✅ | Traces + outcomes |
| 2.4 | Implement PostgresEventPublisher | `adapters/standard/postgres_events.py` | ✅ | NOTIFY + events table |
| 2.5 | Implement PostgresEventConsumer | `adapters/standard/postgres_events.py` | ✅ | LISTEN + polling fallback |
| 2.6 | Implement PgVectorSearch | `adapters/standard/pgvector_search.py` | ✅ | Cosine similarity, filters |
| 2.7 | Implement PostgresCausalGraph | `adapters/standard/postgres_causal.py` | ✅ | BFS path finding, neighbors |
| 2.8 | Implement APSchedulerRunner | `adapters/standard/apscheduler_runner.py` | ✅ | Interval, cron, once |
| 2.9 | Create Standard container factory | `src/mind/container.py` | ✅ | In Phase 1 |
| 2.10 | Add causal_edges table migration | `migrations/001_causal_tables.sql` | ✅ | Nodes + edges + functions |

### Phase 2 Deliverables

- [x] All Standard adapters implemented
- [x] Testing stubs for unit tests (`adapters/testing/stubs.py`)
- [x] Database migration for causal tables

---

## Phase 3: Synchronous Learning Service

**Goal**: Implement immediate salience updates without event-driven architecture

**Status**: ✅ Complete (6/6 tasks)

**Dependencies**: Phase 2 complete

| # | Task | File | Status | Notes |
|---|------|------|:------:|-------|
| 3.1 | Create LearningService class | `src/mind/services/learning.py` | ✅ | With container integration |
| 3.2 | Implement record_outcome with sync updates | `services/learning.py` | ✅ | Immediate salience updates |
| 3.3 | Implement attribution-weighted adjustments | `services/learning.py` | ✅ | `_calculate_attribution` method |
| 3.4 | Add salience bounds checking | `services/learning.py` | ✅ | MAX_ADJUSTMENT_DELTA=0.1 |
| 3.5 | Add causal graph updates | `services/learning.py` | ✅ | `_update_causal_graph` method |
| 3.6 | Wire into API with get_learning_service | `services/__init__.py` | ✅ | Factory function |

### Phase 3 Deliverables

- [x] LearningService fully implemented
- [x] Container integration via get_learning_service()
- [x] Causal graph relationship tracking

---

## Phase 4: Embedded PostgreSQL

**Goal**: Bundle PostgreSQL for zero-config local development

**Status**: ✅ Complete (10/10 tasks)

**Dependencies**: Phase 2 complete

| # | Task | File | Status | Notes |
|---|------|------|:------:|-------|
| 4.1 | Create embedded infrastructure module | `src/mind/infrastructure/embedded/` | ✅ | Package with __init__.py |
| 4.2 | Implement binary download logic | `infrastructure/embedded/downloader.py` | ✅ | PostgresBinaryManager |
| 4.3 | Implement EmbeddedPostgres class | `infrastructure/embedded/postgres.py` | ✅ | Full lifecycle management |
| 4.4 | Add initdb and startup logic | `infrastructure/embedded/postgres.py` | ✅ | Auto-init on first start |
| 4.5 | Add graceful shutdown | `infrastructure/embedded/postgres.py` | ✅ | pg_ctl stop + fallback |
| 4.6 | Add pgvector extension handling | `infrastructure/embedded/postgres.py` | ✅ | Auto-install extensions |
| 4.7 | Integrate with MindContainer | `src/mind/container.py` | ✅ | Auto-start if no DATABASE_URL |
| 4.8 | Add Windows support | `infrastructure/embedded/` | ✅ | Platform detection |
| 4.9 | Add macOS support | `infrastructure/embedded/` | ✅ | x64 + arm64 |
| 4.10 | Add Linux support | `infrastructure/embedded/` | ✅ | x64 + arm64 |

### Phase 4 Deliverables

- [x] EmbeddedPostgres works on Windows, macOS, Linux
- [x] Lazy binary download (not bundled in pip package)
- [x] Data persistence across restarts
- [ ] Integration tests (Phase 6)

### Platform Support

| Platform | Architecture | Status |
|----------|--------------|:------:|
| Windows | x64 | ✅ |
| macOS | x64 | ✅ |
| macOS | arm64 | ✅ |
| Linux | x64 | ✅ |
| Linux | arm64 | ✅ |

---

## Phase 5: CLI and API Updates

**Goal**: Polish the developer experience with simple commands

**Status**: ✅ Complete (7/7 tasks)

**Dependencies**: Phase 4 complete

| # | Task | File | Status | Notes |
|---|------|------|:------:|-------|
| 5.1 | Create CLI module structure | `src/mind/cli/` | ✅ | With __init__.py entry point |
| 5.2 | Implement `mind serve` command | `cli/serve.py` | ✅ | Banner, tier detection |
| 5.3 | Implement `mind migrate` command | `cli/migrate.py` | ✅ | Alembic + SQL fallback |
| 5.4 | Implement `mind demo` command | `cli/demo.py` | ✅ | Interactive learning loop |
| 5.5 | Add tier auto-detection | `api/app.py` | ✅ | MIND_TIER or auto-detect |
| 5.6 | Update API startup for Standard tier | `api/app.py` | ✅ | MindContainer integration |
| 5.7 | Add health + version commands | `cli/health.py`, `cli/version.py` | ✅ | Service health checks |

### Phase 5 Deliverables

- [x] `mind serve` starts embedded PG if no DATABASE_URL
- [x] `mind migrate` applies schema to any PostgreSQL
- [x] `mind demo` shows interactive learning loop
- [x] Clear CLI help text

---

## Phase 6: Testing and Documentation

**Goal**: Ensure quality and document the tier

**Status**: 🔴 Not Started (0/8 tasks)

**Dependencies**: Phase 5 complete

| # | Task | File | Status | Notes |
|---|------|------|:------:|-------|
| 6.1 | Add Standard tier unit tests | `tests/unit/adapters/standard/` | ⬜ | |
| 6.2 | Add integration tests | `tests/integration/standard/` | ⬜ | |
| 6.3 | Add learning loop tests | `tests/unit/services/` | ⬜ | |
| 6.4 | Add embedded PG tests | `tests/integration/embedded/` | ⬜ | |
| 6.5 | Write Quick Start guide | `docs/quick-start.md` | ⬜ | |
| 6.6 | Write Cloud Setup guide | `docs/cloud-setup.md` | ⬜ | |
| 6.7 | Write Migration guide | `docs/enterprise-migration.md` | ⬜ | |
| 6.8 | Update README | `README.md` | ⬜ | |

### Phase 6 Deliverables

- [ ] 80%+ test coverage for new code
- [ ] All existing tests pass
- [ ] Clear documentation for all user journeys

---

## Final Acceptance Criteria

| Criteria | Status |
|----------|:------:|
| User can install with `pip install mind-sdk` | ⬜ |
| User can start with `mind serve` (no config) | ⬜ |
| Learning loop demonstrably improves retrieval | ⬜ |
| All existing MCP tools work unchanged | ⬜ |
| Claude hooks work unchanged | ⬜ |
| Cloud PostgreSQL (Supabase) works | ⬜ |

---

## Architecture Summary

```
Mind Standard (CORE)
├── PostgreSQL + pgvector ──────────── Single database for everything
├── APScheduler ────────────────────── Background jobs (replaces Temporal)
├── Synchronous Learning ───────────── Immediate salience updates (replaces NATS)
├── PostgreSQL Causal Tables ───────── Simple adjacency (replaces FalkorDB)
└── Embedded PostgreSQL ────────────── Zero-config local development

vs

Mind Enterprise (adds)
├── NATS JetStream ─────────────────── Event backbone
├── Qdrant ─────────────────────────── Dedicated vector search
├── FalkorDB ───────────────────────── Graph traversal
├── Temporal.io ────────────────────── Durable workflows
└── Federation ─────────────────────── Cross-user patterns
```

---

## Quality Comparison

| Metric | Standard | Enterprise |
|--------|:--------:|:----------:|
| Learning quality | 90% | 100% |
| Retrieval relevance | 95% | 100% |
| Causal accuracy | 70% | 100% |
| Scalability | 1 user | 1000+ users |
| Setup time | < 1 min | ~30 min |

---

## Related Documents

| Document | Path |
|----------|------|
| PRD | `docs/architecture/MIND-STANDARD-PRD.md` |
| Architecture ADR | `docs/architecture/ADR-010-standard-tier-architecture.md` |
| Implementation Plan | `docs/architecture/IMPLEMENTATION-PLAN-STANDARD-TIER.md` |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-04 | Initial task tracker created |
| 2026-01-04 | Phase 1 complete: All port interfaces defined |
| 2026-01-04 | Phase 2 complete: All Standard adapters implemented |
| 2026-01-04 | Phase 3 complete: LearningService with synchronous updates |
| 2026-01-04 | Phase 4 complete: EmbeddedPostgres with cross-platform support |
| 2026-01-04 | Phase 5 complete: CLI commands and tier auto-detection |

---

*Last Updated: January 4, 2026*
