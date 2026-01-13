# Mind Standard (CORE) - Product Requirements Document

> **Version**: 1.0
> **Status**: Draft
> **Author**: Claude Code
> **Date**: January 4, 2026

---

## Executive Summary

Mind Standard is a lightweight, zero-infrastructure version of Mind v5 that delivers 90% of Enterprise capabilities with 0% infrastructure complexity. It targets cloud-first users (Supabase, Neon, Railway) while providing embedded PostgreSQL for local development.

**One-command installation:**
```bash
pip install mind-sdk && mind serve
```

---

## Problem Statement

### Current Pain Points

1. **Docker Complexity**: Mind Enterprise requires Docker Compose with 7+ services (PostgreSQL, NATS, Qdrant, FalkorDB, Temporal, API, Workers)
2. **Unreliable Startup**: Docker Desktop issues cause frequent startup failures
3. **Resource Heavy**: Full stack consumes 4GB+ RAM
4. **Cloud User Friction**: Users with managed PostgreSQL (Supabase/Neon) shouldn't need local Docker
5. **Barrier to Entry**: New users want to try Mind before committing to infrastructure

### Target Users

| User Type | Setup Preference | Database |
|-----------|------------------|----------|
| **Cloud Developer** | `pip install` + connection string | Supabase, Neon, Railway |
| **Local Developer** | `pip install` only | Embedded PostgreSQL |
| **Evaluator** | One command, zero config | Embedded PostgreSQL |
| **Enterprise** | Full Docker stack | Self-managed |

---

## Product Requirements

### Functional Requirements

#### FR-1: Zero-Config Installation
- **FR-1.1**: Single pip install: `pip install mind-sdk`
- **FR-1.2**: Single command to start: `mind serve`
- **FR-1.3**: Embedded PostgreSQL starts automatically if no connection string provided
- **FR-1.4**: Data persists in `~/.mind/` across restarts

#### FR-2: Cloud PostgreSQL Support
- **FR-2.1**: Accept standard PostgreSQL connection strings
- **FR-2.2**: Support Supabase pooled connections (PgBouncer compatible)
- **FR-2.3**: Support Neon serverless driver
- **FR-2.4**: Auto-run migrations on first connect

#### FR-3: Full Memory System
- **FR-3.1**: Hierarchical temporal memory (4 levels)
- **FR-3.2**: Vector similarity search via pgvector
- **FR-3.3**: Multi-source retrieval fusion (RRF algorithm)
- **FR-3.4**: Memory promotion/demotion lifecycle

#### FR-4: Complete Learning Loop
- **FR-4.1**: Decision tracking with memory attribution
- **FR-4.2**: Outcome recording (positive/negative feedback)
- **FR-4.3**: Salience adjustment based on outcomes
- **FR-4.4**: Memory consolidation on schedule

#### FR-5: Background Processing
- **FR-5.1**: Memory extraction from conversations
- **FR-5.2**: Scheduled consolidation (hourly)
- **FR-5.3**: Expiration checks (daily)
- **FR-5.4**: Pattern detection (weekly)

#### FR-6: API Compatibility
- **FR-6.1**: Same REST API as Enterprise
- **FR-6.2**: Same MCP tool interface
- **FR-6.3**: Claude Code hooks work unchanged
- **FR-6.4**: SDK clients work unchanged

### Non-Functional Requirements

#### NFR-1: Performance
- **NFR-1.1**: API startup < 3 seconds (with embedded PG)
- **NFR-1.2**: Memory retrieval < 100ms (p95)
- **NFR-1.3**: Memory storage < 50ms (p95)
- **NFR-1.4**: RAM usage < 500MB (excluding embedded PG)

#### NFR-2: Reliability
- **NFR-2.1**: Graceful degradation if background tasks fail
- **NFR-2.2**: No data loss on unexpected shutdown
- **NFR-2.3**: Automatic recovery from PG connection loss

#### NFR-3: Maintainability
- **NFR-3.1**: Share 90%+ code with Enterprise tier
- **NFR-3.2**: Single test suite covers both tiers
- **NFR-3.3**: Feature flags control tier-specific behavior

---

## Architecture Overview

### Tier Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MIND STANDARD (CORE)                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   REST API   │  │   MCP Tools  │  │     CLI      │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         └─────────────────┼─────────────────┘                       │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    CORE SERVICES                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │
│  │  │   Memory    │  │  Decision   │  │   Causal    │          │   │
│  │  │   Service   │  │   Tracker   │  │   Service   │          │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │   │
│  │  │  Learning   │  │  Retrieval  │  │ Extraction  │          │   │
│  │  │   Service   │  │   Fusion    │  │   Service   │          │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           │                                         │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   INFRASTRUCTURE                             │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │              PostgreSQL + pgvector                   │    │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │    │   │
│  │  │  │memories │ │decisions│ │ causal  │ │ events  │   │    │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │              APScheduler (Background)                │    │   │
│  │  │  • Consolidation  • Expiration  • Pattern Mining    │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      MIND ENTERPRISE (adds)                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │    NATS     │  │   Qdrant    │  │  FalkorDB   │                 │
│  │ (Events)    │  │  (Vectors)  │  │  (Graph)    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Temporal   │  │ Federation  │  │  Advanced   │                 │
│  │ (Workflows) │  │  (Privacy)  │  │   Causal    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Standard Approach | Enterprise Approach |
|----------|-------------------|---------------------|
| **Event handling** | Synchronous in-process | NATS JetStream |
| **Vector search** | pgvector in PostgreSQL | Qdrant (dedicated) |
| **Graph/Causal** | PostgreSQL adjacency tables | FalkorDB |
| **Background jobs** | APScheduler (in-process) | Temporal.io |
| **Memory extraction** | Synchronous Claude call | Worker queue |

---

## Feature Matrix

### Core Features (Both Tiers)

| Feature | Standard | Enterprise | Notes |
|---------|:--------:|:----------:|-------|
| Hierarchical memory (4 levels) | ✅ | ✅ | Identical |
| Vector similarity search | ✅ | ✅ | pgvector vs Qdrant |
| Multi-source retrieval fusion | ✅ | ✅ | Same RRF algorithm |
| Decision tracking | ✅ | ✅ | Same schema |
| Outcome-based learning | ✅ | ✅ | Synchronous vs async |
| Salience adjustment | ✅ | ✅ | Same algorithm |
| Memory lifecycle | ✅ | ✅ | Promotion/demotion |
| REST API | ✅ | ✅ | Same endpoints |
| MCP tools | ✅ | ✅ | Same interface |
| Claude hooks | ✅ | ✅ | Same hook system |

### Advanced Features

| Feature | Standard | Enterprise | Notes |
|---------|:--------:|:----------:|-------|
| Basic causal edges | ✅ | ✅ | PG tables |
| Advanced causal inference | ⚠️ 70% | ✅ | No graph traversal |
| Counterfactual reasoning | ⚠️ 50% | ✅ | Limited depth |
| Pattern federation | ❌ | ✅ | Privacy-preserving |
| Multi-user pooling | ⚠️ | ✅ | Single-user optimized |
| Durable workflows | ❌ | ✅ | Temporal required |
| Event replay | ❌ | ✅ | NATS required |
| Horizontal scaling | ❌ | ✅ | Single instance |

### Quality Metrics

| Metric | Standard | Enterprise |
|--------|----------|------------|
| Learning quality | 90% | 100% |
| Retrieval relevance | 95% | 100% |
| Causal accuracy | 70% | 100% |
| Scalability | 1 user | 1000+ users |

---

## User Journeys

### Journey 1: Cloud Developer (Supabase)

```
1. pip install mind-sdk
2. Set MIND_DATABASE_URL to Supabase connection string
3. mind migrate (auto-applies schema + pgvector)
4. mind serve
5. Configure Claude hooks
6. Start using Mind with existing cloud database
```

### Journey 2: Local Developer (Zero Config)

```
1. pip install mind-sdk
2. mind serve
   → Detects no DATABASE_URL
   → Starts embedded PostgreSQL at ~/.mind/postgres/
   → Applies migrations
   → Starts API server
3. Configure Claude hooks
4. Mind is ready, data persists locally
```

### Journey 3: Evaluator (Try It Out)

```
1. pip install mind-sdk
2. mind demo
   → Starts embedded PostgreSQL
   → Seeds with example memories
   → Opens browser to dashboard
   → Shows live learning loop
3. Decide whether to continue with Standard or upgrade to Enterprise
```

---

## API Specification

### Endpoints (Same as Enterprise)

```
POST   /v1/memories/store       # Store a memory
POST   /v1/memories/retrieve    # Retrieve with fusion
GET    /v1/memories/{id}        # Get specific memory
DELETE /v1/memories/{id}        # Mark memory expired

POST   /v1/decisions/track      # Track a decision
POST   /v1/decisions/outcome    # Record outcome
GET    /v1/decisions/{id}       # Get decision with trace

POST   /v1/interactions/record  # Record interaction for extraction

GET    /health                  # Health check
GET    /metrics                 # Prometheus metrics
```

### MCP Tools (Same as Enterprise)

```
mind_remember    # Store a memory
mind_retrieve    # Retrieve relevant memories
mind_decide      # Track decision + record outcome
mind_health      # Check API status
```

---

## Success Metrics

### Installation Success
- **Target**: 95% of users complete install in < 2 minutes
- **Measure**: Time from `pip install` to first successful API call

### Learning Quality
- **Target**: 90% of Enterprise learning quality
- **Measure**: A/B test on decision outcome improvement over time

### Adoption
- **Target**: 70% of new Mind users start with Standard
- **Measure**: Tier selection tracking

### Upgrade Path
- **Target**: 30% of Standard users upgrade to Enterprise within 90 days
- **Measure**: Tier migration tracking

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Embedded PG binary size | Large pip package (100MB+) | Lazy download on first use |
| pgvector performance at scale | Slow retrieval >100k memories | Document scaling limits, upgrade path |
| Synchronous learning latency | Slow API responses | Batch updates, async option |
| Feature drift between tiers | Maintenance burden | Shared core code, feature flags |
| Cloud connection security | Data exposure | TLS required, connection pooling docs |

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Port interfaces for storage abstraction
- Embedded PostgreSQL wrapper
- Basic APScheduler integration

### Phase 2: Core Services (Week 3-4)
- Synchronous learning service
- PostgreSQL causal tables
- Memory lifecycle without Temporal

### Phase 3: API Parity (Week 5)
- Verify all endpoints work
- MCP tool compatibility
- Hook system unchanged

### Phase 4: Polish (Week 6)
- CLI improvements (`mind serve`, `mind demo`)
- Documentation
- Migration guide from Enterprise

---

## Appendix: Technical Specifications

### Embedded PostgreSQL

- **Binary source**: postgresql-binaries (prebuilt, trusted)
- **Bundled extensions**: pgvector
- **Data directory**: `~/.mind/postgres/data/`
- **Default port**: 5433 (avoid conflict with system PG)
- **Auto-start**: On `mind serve` if no DATABASE_URL
- **Auto-stop**: On process exit (graceful shutdown)

### pgvector Configuration

```sql
-- Index for vector similarity
CREATE INDEX memories_embedding_idx
ON memories USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Retrieval query
SELECT *, 1 - (embedding <=> $1) AS similarity
FROM memories
WHERE user_id = $2
ORDER BY embedding <=> $1
LIMIT $3;
```

### APScheduler Jobs

| Job | Schedule | Function |
|-----|----------|----------|
| consolidate_memories | Every 1 hour | Merge similar memories |
| expire_memories | Every 24 hours | Mark old immediate memories |
| promote_memories | Every 24 hours | Elevate high-salience memories |
| detect_patterns | Every 7 days | Find recurring patterns |

---

*Document End*
