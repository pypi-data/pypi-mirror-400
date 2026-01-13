# Mind v5 - Project Status

> **Last Updated**: December 31, 2024
> **Version**: 5.0.0
> **Status**: Production-Ready Core, Advanced Features In Progress

---

## What is Mind v5?

Mind v5 is a decision intelligence system that helps AI agents make better decisions over time through:

1. **Hierarchical Memory**: Memories organized by temporal persistence (hours → years)
2. **Outcome-Weighted Retrieval**: Memories that led to good decisions rank higher
3. **Causal Inference**: Understanding WHY decisions worked, not just correlation
4. **Federated Learning**: Learning patterns across users with differential privacy

**Core Value Proposition**: AI agents that genuinely improve through experience.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│            SDK | MCP Server | REST API | Dashboard               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MIND v5 API                                 │
│   /memories | /retrieve | /decisions | /causal | /consent        │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  RETRIEVAL    │     │   DECISION    │     │    CAUSAL     │
│   SERVICE     │     │   TRACKING    │     │   SERVICE     │
│ (Multi-Source │     │  (Outcomes)   │     │ (Why it works)│
│    Fusion)    │     │              │     │              │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EVENT BACKBONE (NATS)                       │
│  mind.memory.* | mind.decision.* | mind.causal.* | mind.fed.*    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  CONSUMERS    │     │   GARDENER    │     │  FEDERATION   │
│ (Event-Driven)│     │  (Temporal)   │     │  (Patterns)   │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│   PostgreSQL (pgvector) | Qdrant | FalkorDB | Redis              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Status

### Core Systems (Phase 1) - ✅ Complete

| Component | Status | Description |
|-----------|--------|-------------|
| **Memory System** | ✅ Complete | Hierarchical temporal storage with 4 levels |
| **Decision Tracking** | ✅ Complete | Track decisions with memory attribution |
| **Outcome Recording** | ✅ Complete | Record outcomes with quality scores |
| **Salience Adjustment** | ✅ Complete | Outcome-weighted importance updates |
| **Multi-Source Retrieval** | ✅ Complete | Vector + Keyword + Salience + Recency fusion |
| **Event Sourcing** | ✅ Complete | All state changes through NATS events |
| **REST API** | ✅ Complete | FastAPI with full endpoint coverage |
| **MCP Server** | ✅ Complete | mind_remember, mind_retrieve, mind_decide |
| **SDK Client** | ✅ Complete | Async Python client with context managers |

### Infrastructure (Phase 1) - ✅ Complete

| Component | Status | Description |
|-----------|--------|-------------|
| **PostgreSQL** | ✅ Complete | Primary store with pgvector |
| **Qdrant** | ✅ Complete | Optional dedicated vector DB |
| **FalkorDB** | ✅ Complete | Causal graph storage |
| **NATS JetStream** | ✅ Complete | Event backbone with DLQ |
| **Temporal.io** | ✅ Complete | Workflow orchestration |
| **Redis** | ✅ Complete | Caching and sessions |

### Workers (Phase 1) - ✅ Complete

| Component | Status | Description |
|-----------|--------|-------------|
| **Consumer Runner** | ✅ Complete | Orchestrates all event consumers |
| **Salience Updater** | ✅ Complete | Applies outcome-based adjustments |
| **Causal Updater** | ✅ Complete | Updates causal graph on outcomes |
| **Memory Extractor** | ✅ Complete | Auto-labels memory content types |
| **Qdrant Sync** | ✅ Complete | Syncs vectors to Qdrant |
| **Gardener Worker** | ✅ Complete | Memory lifecycle management |

### Security & Observability - ✅ Complete

| Component | Status | Description |
|-----------|--------|-------------|
| **Authentication** | ✅ Complete | JWT with refresh rotation |
| **Rate Limiting** | ✅ Complete | Per-endpoint rate limits |
| **Request Sanitization** | ✅ Complete | Input validation and cleaning |
| **Security Headers** | ✅ Complete | OWASP recommended headers |
| **Structured Logging** | ✅ Complete | Structlog with context |
| **Metrics** | ✅ Complete | Prometheus metrics |
| **Tracing** | ✅ Complete | OpenTelemetry distributed tracing |
| **Admin Dashboard** | ✅ Complete | Streamlit with VIBESHIP styling |

### Advanced Features (Phase 2+) - ⚠️ In Progress

| Component | Status | Description |
|-----------|--------|-------------|
| **Causal Inference** | ⚠️ Partial | Basic implementation, DoWhy integration pending |
| **Counterfactual Analysis** | ⚠️ Partial | Query structure exists, full implementation pending |
| **Federation Service** | ⚠️ Partial | Pattern extraction works, DP sanitization pending |
| **Shapley Attribution** | ❌ Pending | Precise contribution measurement |
| **Memory Consolidation** | ⚠️ Partial | Basic merging, semantic consolidation pending |
| **User Preferences** | ✅ Complete | Sensitivity levels, retention controls |

---

## The Learning Loop

```
┌──────────────────────────────────────────────────────────────────┐
│                    THE MIND v5 LEARNING LOOP                     │
└──────────────────────────────────────────────────────────────────┘

1. STORE MEMORY
   ────────────────────────────────────────────────────────────────
   mind_remember(
     content="Server actions reduced API calls by 40%",
     content_type="observation",
     temporal_level=2,  # SITUATIONAL
     salience=0.8
   )

2. RETRIEVE RELEVANT MEMORIES (Outcome-Weighted)
   ────────────────────────────────────────────────────────────────
   memories = mind_retrieve(
     query="How should I handle data fetching?",
     limit=10
   )

   Fusion weights:
   • Vector similarity: 1.0 (semantic match)
   • Keyword/BM25: 0.8 (full-text match)
   • Salience: 0.6 (outcome-weighted importance)
   • Recency: 0.4 (time decay)
   • Causal: 0.7 (historical success rate)

3. MAKE DECISION WITH MEMORIES
   ────────────────────────────────────────────────────────────────
   Agent uses retrieved memories to inform decision

4. RECORD OUTCOME
   ────────────────────────────────────────────────────────────────
   mind_decide(
     memory_ids=["mem-123", "mem-456"],
     decision_summary="Used server actions for data fetching",
     outcome_quality=0.9,  # Good outcome!
     outcome_signal="user_accepted"
   )

5. SALIENCE ADJUSTMENT (Automatic)
   ────────────────────────────────────────────────────────────────
   For each memory that influenced the decision:
     delta = outcome_quality × contribution × 0.1
     memory.salience += delta

   Result:
   • Good outcomes → memories gain salience → rank higher
   • Bad outcomes → memories lose salience → rank lower

6. PROMOTION (Via Gardener)
   ────────────────────────────────────────────────────────────────
   Stable, high-salience memories get promoted:
   IMMEDIATE (hours) → SITUATIONAL (weeks) → SEASONAL (months) → IDENTITY (years)
```

---

## Temporal Hierarchy

| Level | Name | Duration | Example |
|-------|------|----------|---------|
| 1 | IMMEDIATE | ~1 day | "User asked about React hooks" |
| 2 | SITUATIONAL | ~14 days | "Project uses Next.js App Router" |
| 3 | SEASONAL | ~90 days | "User prefers functional components" |
| 4 | IDENTITY | ~365 days | "User values clean, minimal code" |

**Promotion Rules:**
- High retrieval count + positive outcomes → promote up
- Low retrieval + negative outcomes → demote or expire
- Gardener runs periodic checks to manage lifecycle

---

## Directory Structure

```
vibeship-mind/
├── src/mind/
│   ├── api/                  # FastAPI HTTP API
│   │   ├── app.py            # Application factory
│   │   ├── routes/           # Endpoint handlers
│   │   │   ├── memories.py
│   │   │   ├── decisions.py
│   │   │   ├── causal.py
│   │   │   ├── consent.py
│   │   │   └── preferences.py
│   │   └── schemas/          # Request/response models
│   │
│   ├── core/                 # Domain logic
│   │   ├── memory/           # Memory system
│   │   │   ├── models.py     # Memory, TemporalLevel
│   │   │   ├── retrieval.py  # RetrievalRequest/Result
│   │   │   └── fusion.py     # Multi-source RRF
│   │   ├── decision/         # Decision tracking
│   │   │   └── models.py     # DecisionTrace, Outcome
│   │   ├── events/           # Event sourcing
│   │   │   ├── base.py       # Event, EventType
│   │   │   ├── memory.py     # Memory events
│   │   │   └── decision.py   # Decision events
│   │   ├── causal/           # Causal inference
│   │   ├── federation/       # Cross-user patterns
│   │   ├── consent/          # Consent management
│   │   ├── retention/        # Memory lifecycle
│   │   └── errors.py         # Error types
│   │
│   ├── infrastructure/       # External integrations
│   │   ├── postgres/         # PostgreSQL + pgvector
│   │   ├── qdrant/           # Vector database
│   │   ├── falkordb/         # Graph database
│   │   ├── nats/             # Event backbone
│   │   ├── temporal/         # Workflow orchestration
│   │   └── embeddings/       # OpenAI embeddings
│   │
│   ├── services/             # Business logic
│   │   ├── retrieval.py      # Multi-source fusion
│   │   ├── embedding.py      # Embedding generation
│   │   └── events.py         # Event publishing
│   │
│   ├── workers/              # Background processing
│   │   ├── consumers/        # Event-driven consumers
│   │   │   ├── runner.py     # Consumer orchestrator
│   │   │   ├── salience_updater.py
│   │   │   ├── causal_updater.py
│   │   │   ├── memory_extractor.py
│   │   │   └── qdrant_sync.py
│   │   └── gardener/         # Memory lifecycle
│   │       ├── worker.py     # Temporal worker
│   │       ├── workflows.py  # Temporal workflows
│   │       └── activities.py # Temporal activities
│   │
│   ├── security/             # Security & privacy
│   │   ├── auth.py           # JWT authentication
│   │   ├── middleware.py     # Security middleware
│   │   ├── encryption.py     # Field encryption
│   │   └── pii.py            # PII detection
│   │
│   ├── observability/        # Monitoring
│   │   ├── logging.py        # Structured logging
│   │   ├── metrics.py        # Prometheus metrics
│   │   └── tracing.py        # OpenTelemetry
│   │
│   ├── mcp/                  # MCP Server
│   │   └── server.py         # FastMCP tools
│   │
│   ├── sdk/                  # Client SDK
│   │   ├── client.py         # MindClient
│   │   └── context.py        # DecisionContext
│   │
│   ├── dashboard/            # Admin UI
│   │   ├── app.py            # Streamlit app
│   │   └── theme.py          # VIBESHIP styling
│   │
│   ├── config.py             # Settings
│   └── cli.py                # CLI commands
│
├── tests/
├── deploy/
├── docs/
└── skills/                   # AI specialist skills
```

---

## API Endpoints

### Memory Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/memories` | POST | Store a new memory |
| `/memories/{id}` | GET | Get memory by ID |
| `/retrieve` | POST | Semantic search with fusion |

### Decision Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/decisions` | POST | Track decision + outcome |
| `/decisions/track` | POST | Track decision (no outcome yet) |
| `/decisions/{id}/outcome` | POST | Record outcome for decision |

### Causal Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/causal/edges` | POST | Record causal relationship |
| `/causal/query` | POST | Query causal paths |
| `/causal/counterfactual` | POST | Counterfactual analysis |

### User Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/consent` | GET/POST | Manage user consent |
| `/preferences` | GET/PUT | User preferences |
| `/preferences/sensitivity` | PUT | Memory sensitivity level |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |

---

## MCP Tools

Mind v5 exposes three MCP tools for AI agents:

```python
# Store a memory
mind_remember(
    user_id: str,
    content: str,
    content_type: str = "observation",  # fact, preference, event, goal, observation
    temporal_level: int = 2,  # 1=immediate, 2=situational, 3=seasonal, 4=identity
    salience: float = 1.0
)

# Retrieve relevant memories (outcome-weighted)
mind_retrieve(
    user_id: str,
    query: str,
    limit: int = 10,
    min_salience: float = 0.0
)

# Track decision and record outcome
mind_decide(
    user_id: str,
    memory_ids: list[str],
    decision_summary: str,
    outcome_quality: float,  # -1.0 (bad) to 1.0 (good)
    outcome_signal: str = "agent_feedback"  # user_accepted, user_rejected, task_completed
)
```

---

## Running Mind v5

### Prerequisites

```bash
# Infrastructure (via docker-compose in deploy/docker/)
docker-compose up -d postgres qdrant falkordb nats temporal redis
```

### Start Services

```bash
# API Server
python -m uvicorn mind.api.app:app --host 0.0.0.0 --port 8080

# Event Consumers
python -m mind.workers.consumers.runner

# Gardener (Memory Lifecycle)
python -m mind.workers.gardener.worker

# Admin Dashboard
streamlit run src/mind/dashboard/app.py

# MCP Server
python -m mind.mcp
```

### Health Check Ports

| Service | Port | Endpoint |
|---------|------|----------|
| API | 8080 | /health |
| Consumers | 9092 | /health |
| Gardener | 9091 | /health |
| Dashboard | 8501 | / |

---

## Environment Variables

### Required
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | For embedding generation |

### Optional (with defaults)
| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_URL` | nats://localhost:4222 | NATS server |
| `QDRANT_URL` | http://localhost:6333 | Qdrant server |
| `FALKORDB_HOST` | localhost | FalkorDB host |
| `TEMPORAL_HOST` | localhost:7233 | Temporal server |
| `REDIS_URL` | redis://localhost:6379 | Redis server |
| `VECTOR_BACKEND` | pgvector | pgvector or qdrant |
| `LOG_LEVEL` | INFO | Logging level |
| `ENABLE_TRACING` | false | OpenTelemetry tracing |

---

## What's Next

### Phase 2: Advanced Causal
- [ ] Full DoWhy integration
- [ ] Shapley value attribution
- [ ] Counterfactual queries
- [ ] Causal discovery from data

### Phase 3: Federation
- [ ] Differential privacy sanitization
- [ ] Cross-user pattern sharing
- [ ] Privacy budget management
- [ ] Federated aggregation

### Phase 4: Scale
- [ ] Horizontal scaling
- [ ] Multi-region deployment
- [ ] Advanced caching
- [ ] Query optimization

---

## Integration with Terrarium

Mind v5 is the intelligence backend for Mind Terrarium:

```
Terrarium Agents → Mind v5 API
                   ├── remember() - Store learnings
                   ├── retrieve() - Get relevant context
                   └── decide() - Learn from outcomes
```

This enables:
- Agents that genuinely improve over time
- Observable decision-making process
- Transparent learning feedback loop

---

## Contributing

See [CLAUDE.md](./CLAUDE.md) for development guidelines.

Key principles:
1. **Events are Sacred** - All state changes through events
2. **Memory Serves Decisions** - Memory exists to improve decisions
3. **Causality Over Correlation** - Store WHY, not just WHAT
4. **Privacy is Non-Negotiable** - No PII leakage
5. **Failure is Expected** - Design for graceful degradation
