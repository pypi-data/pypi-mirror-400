# Mind v5

Decision intelligence system for AI agents. Mind helps agents make better decisions over time by learning from outcomes.

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](./docs/guides/GETTING_STARTED.md) | 15-minute setup guide |
| [Core Concepts](./docs/guides/CONCEPTS.md) | Understanding memories, decisions, causality |
| [User Guide](./docs/guides/USER_GUIDE.md) | Step-by-step usage with examples |
| [API Reference](./docs/guides/API_REFERENCE.md) | Complete endpoint documentation |
| [Installation](./docs/guides/INSTALLATION.md) | Production deployment options |
| [Troubleshooting](./docs/guides/TROUBLESHOOTING.md) | Common issues and solutions |

## Core Concepts

- **Hierarchical Temporal Memory**: Memories exist at 4 levels (Working, Recent, Reference, Identity)
- **Outcome-Weighted Salience**: Memories that lead to good decisions become more prominent
- **Decision Tracing**: Every decision is tracked with the context that informed it
- **Causal Learning**: Understanding WHY decisions work, not just correlation
- **Multi-Source Retrieval**: Combines vector search, keywords, salience, recency, and causal signals

## Quick Start

### Option A: One-Command Install (Recommended)

```bash
# Install Mind
pip install vibeship-mind

# Setup and start (downloads PostgreSQL, pgvector automatically)
mind up
```

That's it! Mind will:
1. Download PostgreSQL binaries (no system install needed)
2. Download and install pgvector extension
3. Initialize the database
4. Start the API server on http://localhost:8001

### Option B: With Existing PostgreSQL

```bash
# Install Mind
pip install vibeship-mind

# Configure your database
export MIND_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mind

# Start server (skip automatic PostgreSQL setup)
mind serve
```

### Option C: Docker Compose (Production)

```bash
# Copy environment config
cp .env.example .env

# Start all services (Postgres, NATS, Qdrant, API)
docker-compose up -d

# Check status
docker-compose ps
```

### Verify It Works

```bash
# Run smoke test
pip install httpx
python scripts/smoke_test.py
```

### Use the API

```bash
# Health check
curl http://localhost:8001/health

# Create a memory
curl -X POST http://localhost:8001/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "User prefers concise code examples",
    "content_type": "preference",
    "temporal_level": 3,
    "salience": 0.8
  }'

# Retrieve memories (semantic search)
curl -X POST http://localhost:8001/v1/memories/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "code examples",
    "limit": 5
  }'

# Track a decision
curl -X POST http://localhost:8001/v1/decisions/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655440001",
    "decision_type": "response_style",
    "decision_summary": "Used concise examples",
    "confidence": 0.85
  }'

# Record outcome
curl -X POST http://localhost:8001/v1/decisions/outcome \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "<trace_id_from_track>",
    "quality": 0.9,
    "signal": "explicit_positive",
    "feedback": "User understood quickly"
  }'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/v1/memories/` | Create memory |
| GET | `/v1/memories/{memory_id}` | Get memory by ID |
| POST | `/v1/memories/retrieve` | Retrieve memories (semantic search) |
| POST | `/v1/decisions/track` | Track a decision |
| POST | `/v1/decisions/outcome` | Record decision outcome |
| GET | `/metrics` | Prometheus metrics |

## CLI Commands

| Command | Description |
|---------|-------------|
| `mind up` | One-command start: setup + serve |
| `mind setup` | Download PostgreSQL, pgvector, initialize database |
| `mind serve` | Start the API server |
| `mind serve --reload` | Start with auto-reload (development) |
| `mind db init` | Initialize database tables |
| `mind db migrate` | Run database migrations |
| `mind health` | Check service health |
| `mind version` | Show version information |
| `mind mcp` | Start MCP server for AI agents |

### Setup Options

```bash
mind setup --skip-postgres     # Use existing PostgreSQL
mind setup --skip-pgvector     # Skip pgvector installation
mind setup --skip-db-init      # Skip database initialization
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/unit -v

# Start API in development mode
python -m mind.cli serve --reload

# Run linting
ruff check src/
mypy src/
```

## Architecture

```
                         +------------------+
                         |    API Layer     |
                         |   (FastAPI)      |
                         +--------+---------+
                                  |
        +------------+------------+------------+------------+
        |            |            |            |            |
+-------v----+ +-----v------+ +---v----+ +----v-----+ +-----v------+
|  Memory    | |  Decision  | | Event  | | Causal   | | Retrieval  |
|  Service   | |  Service   | | Service| | Service  | | Service    |
+-------+----+ +-----+------+ +---+----+ +----+-----+ +-----+------+
        |            |            |            |            |
        +------------+------------+------------+------------+
                                  |
     +-------------+--------------+--------------+-------------+
     |             |              |              |             |
+----v----+  +-----v-----+  +-----v-----+  +-----v-----+  +----v----+
|Postgres |  |  Qdrant   |  |   NATS    |  | FalkorDB  |  | Temporal|
|(pgvector)|  | (vectors) |  | (events)  |  | (causal)  |  |(workflows)
+---------+  +-----------+  +-----------+  +-----------+  +---------+
```

## Configuration

See `.env.example` for all configuration options.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [PyPI Package](https://pypi.org/project/vibeship-mind/)
- [GitHub Repository](https://github.com/vibeship/vibeship-mind)
- [Documentation](https://github.com/vibeship/vibeship-mind#readme)
