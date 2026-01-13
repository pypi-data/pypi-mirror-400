# Getting Started with Mind v5

> **Time to complete**: 15-20 minutes
> **Prerequisites**: Docker, Python 3.12+

Welcome to Mind v5, the decision intelligence system that helps AI agents learn from outcomes. This guide will get you from zero to a working system.

---

## What is Mind v5?

Mind v5 is a **memory and learning system** for AI agents. Think of it as giving your AI a brain that:

1. **Remembers** important context about users
2. **Learns** which information leads to good decisions
3. **Improves** over time based on feedback
4. **Understands** cause and effect relationships

### The Core Loop

```
User interacts with AI
        ↓
AI retrieves relevant memories from Mind
        ↓
AI makes a decision using those memories
        ↓
User gives feedback (explicit or implicit)
        ↓
Mind learns: good feedback → boost those memories
             bad feedback → demote those memories
        ↓
Next time, better memories surface first
```

---

## Quick Start (5 minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/mind-v5.git
cd mind-v5

# Copy environment config
cp .env.example .env
```

### Step 2: Start Everything with Docker

```bash
# Start all services
docker-compose up -d

# Verify everything is running
docker-compose ps
```

You should see these services:
- `postgres` - Main database with vector support
- `nats` - Event messaging system
- `falkordb` - Graph database for causal relationships
- `temporal` - Workflow orchestration
- `mind-api` - The Mind v5 API

### Step 3: Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "5.0.0"}
```

### Step 4: Create Your First Memory

```bash
curl -X POST http://localhost:8000/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "User prefers Python code examples over pseudocode",
    "temporal_level": 4
  }'
```

**Congratulations!** You've just created your first memory in Mind v5.

---

## Running Locally (Development Mode)

If you prefer running the API outside Docker:

### Step 1: Create Virtual Environment

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Core dependencies
pip install -e .

# Optional: ML features (embeddings)
pip install -e ".[ml]"

# Optional: Admin UI
pip install -e ".[ui]"

# Development tools
pip install -e ".[dev]"
```

### Step 3: Start Infrastructure Only

```bash
# Start databases and messaging (not the API)
docker-compose up -d postgres nats falkordb temporal temporal-ui
```

### Step 4: Run the API

```bash
# Start API with hot-reload
uvicorn mind.api.app:app --reload --port 8000
```

### Step 5: (Optional) Start Admin Dashboard

```bash
streamlit run src/mind/ui/dashboard.py
```

Open http://localhost:8501 for the visual dashboard.

---

## Available UIs

Mind v5 comes with several interfaces:

| Interface | URL | Purpose |
|-----------|-----|---------|
| **API Docs** | http://localhost:8000/docs | Interactive API explorer (Swagger) |
| **Admin Dashboard** | http://localhost:8501 | Visual management UI |
| **Temporal UI** | http://localhost:8088 | Workflow monitoring |
| **Health Check** | http://localhost:8000/health | System status |

---

## What's Next?

Now that Mind v5 is running, learn how to use it effectively:

1. **[Core Concepts](./CONCEPTS.md)** - Understand memories, decisions, and causality
2. **[User Guide](./USER_GUIDE.md)** - Step-by-step usage with real examples
3. **[API Reference](./API_REFERENCE.md)** - Complete endpoint documentation
4. **[Installation Guide](./INSTALLATION.md)** - Production deployment options

---

## Quick Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `NATS_URL` | `nats://localhost:4222` | NATS server |
| `FALKORDB_HOST` | `localhost` | FalkorDB host |
| `TEMPORAL_HOST` | `localhost:7233` | Temporal server |
| `OPENAI_API_KEY` | (none) | For embeddings (optional) |

### Common Commands

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f mind-api

# Stop everything
docker-compose down

# Run tests
pytest tests/unit -v

# Check linting
ruff check src/
```

---

## Getting Help

- **Issues**: Open a GitHub issue
- **Logs**: Check `docker-compose logs`
- **Health**: Visit `/ready` endpoint for detailed status
- **Troubleshooting**: See [Troubleshooting Guide](./TROUBLESHOOTING.md)
