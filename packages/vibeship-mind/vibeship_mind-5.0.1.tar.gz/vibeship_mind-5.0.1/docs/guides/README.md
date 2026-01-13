# Mind v5 Documentation

> Complete documentation for the Mind v5 decision intelligence system

---

## Quick Links

| Guide | Description | Best For |
|-------|-------------|----------|
| [Getting Started](./GETTING_STARTED.md) | 15-minute setup guide | First-time users |
| [Core Concepts](./CONCEPTS.md) | Understanding Mind v5 | Learning the system |
| [User Guide](./USER_GUIDE.md) | Step-by-step usage | Daily usage |
| [Installation](./INSTALLATION.md) | Deployment options | DevOps/Production |
| [API Reference](./API_REFERENCE.md) | Endpoint documentation | Developers |
| [Troubleshooting](./TROUBLESHOOTING.md) | Problem solving | When things break |

---

## Learning Path

### Beginner (Start Here)

1. **[Getting Started](./GETTING_STARTED.md)** - Get Mind v5 running
2. **[Core Concepts](./CONCEPTS.md)** - Understand the fundamentals

### Intermediate

3. **[User Guide](./USER_GUIDE.md)** - Learn practical usage
4. **[API Reference](./API_REFERENCE.md)** - Explore all endpoints

### Advanced

5. **[Installation](./INSTALLATION.md)** - Production deployment
6. **Architecture Docs** - See `../architecture/` for ADRs

---

## What is Mind v5?

Mind v5 is a **decision intelligence system** that helps AI agents learn from outcomes. It provides:

### Core Capabilities

| Feature | What It Does |
|---------|--------------|
| **Memory Storage** | Store user context at different temporal levels |
| **Smart Retrieval** | Find relevant memories using semantic search |
| **Decision Tracking** | Record which memories informed each decision |
| **Outcome Learning** | Learn from feedback to improve future retrieval |
| **Causal Analysis** | Understand why decisions worked or didn't |

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Mind v5 API                          │
│                     (FastAPI + Python)                       │
├─────────────────────────────────────────────────────────────┤
│  Memories  │  Decisions  │  Causal  │  Consent  │  Admin   │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                           │
│  RetrievalService │ DecisionService │ CausalService │ ...  │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure                            │
│  PostgreSQL  │  NATS  │  FalkorDB  │  Temporal  │  Qdrant  │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Tasks

### Create a Memory

```bash
curl -X POST http://localhost:8000/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "User prefers Python",
    "temporal_level": 4
  }'
```

### Retrieve Memories

```bash
curl -X POST http://localhost:8000/v1/memories/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "programming language",
    "limit": 5
  }'
```

### Track Decision + Record Outcome

```bash
# Track decision
TRACE=$(curl -s -X POST http://localhost:8000/v1/decisions/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655440001",
    "query": "What language to use?"
  }' | jq -r '.trace_id')

# Record outcome
curl -X POST http://localhost:8000/v1/decisions/outcome \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "'$TRACE'",
    "quality": 0.9,
    "signal": "positive"
  }'
```

---

## Available Interfaces

| Interface | URL | Purpose |
|-----------|-----|---------|
| **API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Admin Dashboard** | http://localhost:8501 | Visual management |
| **Temporal UI** | http://localhost:8088 | Workflow monitoring |
| **Metrics** | http://localhost:8000/metrics | Prometheus metrics |

---

## Additional Resources

### Architecture Decisions

See `../architecture/` for Architecture Decision Records (ADRs):

- ADR-001: Hierarchical Temporal Memory
- ADR-002: Event Sourcing with NATS
- ADR-003: Outcome-Weighted Salience
- ADR-004: Federated Learning Privacy
- ADR-005: Multi-Modal Retrieval

### Runbooks

See `../runbooks/` for operational procedures:

- Database Operations
- Backup and Recovery
- Disaster Recovery
- Capacity Planning
- Incident Response
- Scaling

### Specifications

See `../specs/` for technical specifications:

- Event Catalog
- SLO Definitions

---

## Getting Help

1. **Check Troubleshooting**: [Troubleshooting Guide](./TROUBLESHOOTING.md)
2. **Search Issues**: Look for similar problems on GitHub
3. **Open Issue**: If not found, open a new GitHub issue

---

*Last updated: December 29, 2025*
