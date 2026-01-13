# Installation Guide

> Complete guide for installing Mind v5 in various environments

---

## Table of Contents

1. [Requirements](#requirements)
2. [Quick Install (Docker)](#quick-install-docker)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Configuration Reference](#configuration-reference)
7. [Verification](#verification)

---

## Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB | 50+ GB SSD |
| Python | 3.12+ | 3.12+ |
| Docker | 24.0+ | Latest |

### Required Services

Mind v5 requires these external services:

| Service | Purpose | Required? |
|---------|---------|-----------|
| **PostgreSQL 15+** | Primary database with pgvector | Yes |
| **NATS JetStream** | Event messaging | Yes |
| **FalkorDB** | Causal graph storage | Yes |
| **Temporal** | Workflow orchestration | Yes |
| **Qdrant** | Vector storage (alternative) | No |
| **OpenAI API** | Embeddings | Optional |

---

## Quick Install (Docker)

The fastest way to get Mind v5 running.

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/mind-v5.git
cd mind-v5
```

### Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

**Minimum `.env` configuration:**

```bash
# Database
DATABASE_URL=postgresql://mind:mind@postgres:5432/mind

# NATS
NATS_URL=nats://nats:4222

# FalkorDB
FALKORDB_HOST=falkordb
FALKORDB_PORT=6379

# Temporal
TEMPORAL_HOST=temporal:7233

# Optional: OpenAI for embeddings
# OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 4: Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready
```

### Docker Compose Services

The default `docker-compose.yaml` starts:

| Service | Port | Purpose |
|---------|------|---------|
| `mind-api` | 8000 | Main API |
| `postgres` | 5432 | Database |
| `nats` | 4222, 8222 | Messaging |
| `falkordb` | 6379 | Graph DB |
| `temporal` | 7233 | Workflows |
| `temporal-ui` | 8088 | Workflow UI |

---

## Local Development

For development without Docker for the API.

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Core dependencies
pip install -e .

# Machine learning (embeddings)
pip install -e ".[ml]"

# Vector database (Qdrant)
pip install -e ".[vector]"

# Admin UI
pip install -e ".[ui]"

# Development tools
pip install -e ".[dev]"

# All optional dependencies
pip install -e ".[ml,vector,ui,dev]"
```

### Step 3: Start Infrastructure

```bash
# Start only databases and messaging (not the API)
docker-compose up -d postgres nats falkordb temporal temporal-ui

# Wait for services to be ready
sleep 10
```

### Step 4: Initialize Database

```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize directly
python -c "from mind.infrastructure.postgres.database import init_database; import asyncio; asyncio.run(init_database())"
```

### Step 5: Start API

```bash
# Development mode with hot reload
uvicorn mind.api.app:app --reload --port 8000

# Or using the CLI
python -m mind.cli serve --reload
```

### Step 6: Start Workers (Optional)

```bash
# In a separate terminal
python -m mind.workers.worker
```

### Step 7: Start Dashboard (Optional)

```bash
# In another terminal
streamlit run src/mind/ui/dashboard.py
```

---

## Production Deployment

### Architecture Overview

```
                    Load Balancer
                         │
              ┌──────────┴──────────┐
              │                     │
         ┌────┴────┐           ┌────┴────┐
         │ API Pod │           │ API Pod │
         │   #1    │           │   #2    │
         └────┬────┘           └────┬────┘
              │                     │
    ┌─────────┼─────────────────────┼─────────┐
    │         │                     │         │
    │    ┌────┴─────────────────────┴────┐    │
    │    │       Internal Network         │    │
    │    └───────────────┬───────────────┘    │
    │                    │                     │
    │    ┌───────┬───────┼───────┬───────┐    │
    │    │       │       │       │       │    │
    │  ┌─┴─┐   ┌─┴─┐   ┌─┴─┐   ┌─┴─┐   ┌─┴─┐  │
    │  │PG │   │NAT│   │Fal│   │Tem│   │Qdr│  │
    │  │   │   │S  │   │kor│   │por│   │ant│  │
    │  └───┘   └───┘   └───┘   └───┘   └───┘  │
    │                                         │
    │              Worker Pods                │
    │         (Temporal Workers)              │
    └─────────────────────────────────────────┘
```

### Production Checklist

- [ ] **Security**
  - [ ] Enable JWT authentication
  - [ ] Configure HTTPS/TLS
  - [ ] Set strong database passwords
  - [ ] Enable rate limiting
  - [ ] Configure CORS properly

- [ ] **Reliability**
  - [ ] Set up database replication
  - [ ] Configure NATS clustering
  - [ ] Enable health checks
  - [ ] Set up monitoring

- [ ] **Performance**
  - [ ] Tune PostgreSQL (see below)
  - [ ] Configure connection pooling
  - [ ] Set appropriate resource limits
  - [ ] Enable caching

### Environment Variables (Production)

```bash
# Database
DATABASE_URL=postgresql://mind:${DB_PASSWORD}@db.internal:5432/mind
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# NATS
NATS_URL=nats://nats.internal:4222

# FalkorDB
FALKORDB_HOST=falkordb.internal
FALKORDB_PASSWORD=${FALKORDB_PASSWORD}

# Temporal
TEMPORAL_HOST=temporal.internal:7233
TEMPORAL_NAMESPACE=mind-production

# Security
JWT_SECRET=${JWT_SECRET}
REQUIRE_AUTH=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
LOG_LEVEL=INFO
LOG_FORMAT=json

# Optional
OPENAI_API_KEY=${OPENAI_API_KEY}
QDRANT_URL=http://qdrant.internal:6333
```

### PostgreSQL Tuning

For production workloads, tune PostgreSQL:

```sql
-- Memory (adjust based on available RAM)
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 64MB
maintenance_work_mem = 512MB

-- Connections
max_connections = 200

-- WAL
wal_buffers = 64MB
checkpoint_completion_target = 0.9
max_wal_size = 2GB

-- Planner
random_page_cost = 1.1  -- For SSD
effective_io_concurrency = 200

-- pgvector specific
max_parallel_workers_per_gather = 4
```

---

## Kubernetes Deployment

Mind v5 includes Kubernetes manifests and Helm charts.

### Using Kubectl

```bash
# Create namespace
kubectl create namespace mind

# Apply secrets
kubectl apply -f deploy/k8s/secrets.yaml -n mind

# Apply base manifests
kubectl apply -f deploy/k8s/base/ -n mind

# For staging
kubectl apply -k deploy/k8s/overlays/staging/ -n mind

# For production
kubectl apply -k deploy/k8s/overlays/production/ -n mind
```

### Using Helm

```bash
# Add any required repos
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install with default values
helm install mind deploy/helm/mind -n mind --create-namespace

# Install with custom values
helm install mind deploy/helm/mind -n mind \
  --set api.replicas=3 \
  --set api.resources.limits.memory=2Gi \
  --set postgresql.enabled=true
```

### Scaling

```bash
# Scale API pods
kubectl scale deployment mind-api --replicas=5 -n mind

# Scale workers
kubectl scale deployment mind-worker --replicas=3 -n mind
```

---

## Configuration Reference

### All Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| **Database** |||
| `DATABASE_URL` | (required) | PostgreSQL connection string |
| `DATABASE_POOL_SIZE` | `10` | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | `5` | Extra connections allowed |
| **NATS** |||
| `NATS_URL` | `nats://localhost:4222` | NATS server URL |
| `NATS_CLUSTER_ID` | `mind-cluster` | Cluster identifier |
| **FalkorDB** |||
| `FALKORDB_HOST` | `localhost` | FalkorDB host |
| `FALKORDB_PORT` | `6379` | FalkorDB port |
| `FALKORDB_PASSWORD` | (none) | FalkorDB password |
| **Temporal** |||
| `TEMPORAL_HOST` | `localhost:7233` | Temporal server |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |
| `TEMPORAL_TASK_QUEUE` | `gardener` | Task queue name |
| **Qdrant (Optional)** |||
| `QDRANT_URL` | (none) | Qdrant URL (enables Qdrant) |
| `QDRANT_API_KEY` | (none) | Qdrant API key |
| `VECTOR_BACKEND` | `pgvector` | `pgvector` or `qdrant` |
| **OpenAI (Optional)** |||
| `OPENAI_API_KEY` | (none) | Enables embeddings |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Model to use |
| **Security** |||
| `JWT_SECRET` | (required for auth) | JWT signing secret |
| `REQUIRE_AUTH` | `false` | Enforce authentication |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Window in seconds |
| **Observability** |||
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `text` | `text` or `json` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | (none) | OpenTelemetry collector |
| **API** |||
| `API_HOST` | `0.0.0.0` | Bind address |
| `API_PORT` | `8000` | Bind port |
| `API_WORKERS` | `4` | Uvicorn workers |

---

## Verification

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"5.0.0"}

# Full readiness
curl http://localhost:8000/ready
# Expected: {"ready":true,"database":"connected",...}

# Detailed health
curl http://localhost:8000/health/detailed
```

### Smoke Test

```bash
# Run the smoke test script
python scripts/smoke_test.py

# Or manually test core functionality
python -c "
import httpx

client = httpx.Client(base_url='http://localhost:8000')

# Create memory
resp = client.post('/v1/memories/', json={
    'user_id': '550e8400-e29b-41d4-a716-446655440000',
    'content': 'Test memory',
    'temporal_level': 1
})
print(f'Create: {resp.status_code}')

# Retrieve
resp = client.post('/v1/memories/retrieve', json={
    'user_id': '550e8400-e29b-41d4-a716-446655440000',
    'query': 'test',
    'limit': 5
})
print(f'Retrieve: {resp.status_code}')

print('Smoke test passed!')
"
```

### Run Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests (requires running services)
pytest tests/integration -v

# All tests with coverage
pytest --cov=src/mind --cov-report=html
```

---

## Troubleshooting Installation

### Common Issues

**Database connection failed:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql $DATABASE_URL -c "SELECT 1"

# Check pgvector extension
psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector"
```

**NATS connection failed:**
```bash
# Check NATS is running
docker-compose ps nats

# Check connectivity
curl http://localhost:8222/healthz
```

**Temporal connection failed:**
```bash
# Check Temporal is running
docker-compose ps temporal

# Check namespace exists
tctl namespace describe default
```

**FalkorDB connection failed:**
```bash
# Check FalkorDB is running
docker-compose ps falkordb

# Test connection
redis-cli -h localhost -p 6379 PING
```

See [Troubleshooting Guide](./TROUBLESHOOTING.md) for more solutions.
