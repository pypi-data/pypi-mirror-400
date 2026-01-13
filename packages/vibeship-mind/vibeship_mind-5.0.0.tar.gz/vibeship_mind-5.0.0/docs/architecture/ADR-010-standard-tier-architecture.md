# ADR-010: Mind Standard Tier Architecture

> **Status**: Accepted
> **Date**: January 4, 2026
> **Decision**: Implement Standard tier in same repo with port-based abstraction

---

## Context

Mind v5 Enterprise requires Docker Compose with 7+ services. This creates barriers:
- Cloud users (Supabase/Neon) don't need local infrastructure
- New users want quick evaluation
- Docker Desktop has reliability issues
- Resource consumption is high

We need a lightweight tier that preserves the learning loop while eliminating infrastructure complexity.

## Decision

### 1. Same Repository (Monorepo)

Keep Standard and Enterprise in the same repository with shared core domain logic.

**Structure:**
```
mind-v5/
├── src/mind/
│   ├── core/                    # Shared domain logic (100%)
│   │   ├── memory/
│   │   ├── decision/
│   │   ├── causal/
│   │   └── events/
│   │
│   ├── ports/                   # NEW: Abstraction interfaces
│   │   ├── storage.py           # IMemoryStorage, IDecisionStorage
│   │   ├── events.py            # IEventPublisher, IEventConsumer
│   │   ├── vectors.py           # IVectorSearch
│   │   ├── graphs.py            # ICausalGraph
│   │   └── scheduler.py         # IBackgroundScheduler
│   │
│   ├── adapters/                # NEW: Tier-specific implementations
│   │   ├── standard/            # Standard tier adapters
│   │   │   ├── postgres_storage.py
│   │   │   ├── postgres_events.py    # PG NOTIFY/LISTEN
│   │   │   ├── pgvector_search.py
│   │   │   ├── postgres_causal.py    # Adjacency tables
│   │   │   └── apscheduler_runner.py
│   │   │
│   │   └── enterprise/          # Enterprise tier adapters
│   │       ├── postgres_storage.py   # Same as standard
│   │       ├── nats_events.py
│   │       ├── qdrant_search.py
│   │       ├── falkordb_causal.py
│   │       └── temporal_scheduler.py
│   │
│   ├── services/                # Business logic (uses ports)
│   │   ├── memory_service.py
│   │   ├── decision_service.py
│   │   ├── learning_service.py  # NEW: Synchronous learning
│   │   ├── retrieval_service.py
│   │   └── extraction_service.py
│   │
│   ├── infrastructure/          # EXISTING: Migrate to adapters
│   │   └── embedded/            # NEW: Embedded PostgreSQL
│   │       ├── __init__.py
│   │       ├── postgres.py
│   │       └── bin/             # Downloaded on first use
│   │
│   ├── api/                     # Unchanged
│   ├── mcp/                     # Unchanged
│   └── cli/                     # Enhanced
│       ├── __init__.py
│       ├── serve.py             # mind serve
│       ├── migrate.py           # mind migrate
│       └── demo.py              # mind demo
```

### 2. Port-Based Abstraction

Define clear interfaces (ports) that both tiers implement:

```python
# src/mind/ports/storage.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..core.memory.models import Memory

class IMemoryStorage(ABC):
    """Port for memory persistence."""

    @abstractmethod
    async def store(self, memory: Memory) -> Memory:
        """Store a memory, return with ID assigned."""
        pass

    @abstractmethod
    async def get(self, memory_id: UUID) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        pass

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 100,
        temporal_level: Optional[int] = None
    ) -> List[Memory]:
        """Get memories for a user."""
        pass

    @abstractmethod
    async def update_salience(
        self,
        memory_id: UUID,
        adjustment: float
    ) -> Memory:
        """Adjust memory salience based on outcome."""
        pass

    @abstractmethod
    async def expire(self, memory_id: UUID) -> None:
        """Mark a memory as expired."""
        pass
```

```python
# src/mind/ports/events.py
from abc import ABC, abstractmethod
from typing import Callable, Any

class IEventPublisher(ABC):
    """Port for publishing domain events."""

    @abstractmethod
    async def publish(self, event_type: str, payload: dict) -> None:
        """Publish an event."""
        pass

class IEventConsumer(ABC):
    """Port for consuming domain events."""

    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[dict], Any]
    ) -> None:
        """Subscribe to events of a type."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start consuming events."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop consuming events."""
        pass
```

```python
# src/mind/ports/vectors.py
from abc import ABC, abstractmethod
from typing import List, Tuple
from uuid import UUID

class IVectorSearch(ABC):
    """Port for vector similarity search."""

    @abstractmethod
    async def index(
        self,
        id: UUID,
        embedding: List[float],
        metadata: dict
    ) -> None:
        """Index a vector."""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter: Optional[dict] = None
    ) -> List[Tuple[UUID, float]]:
        """Search for similar vectors, return (id, score) pairs."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Remove a vector from the index."""
        pass
```

```python
# src/mind/ports/scheduler.py
from abc import ABC, abstractmethod
from typing import Callable
from datetime import timedelta

class IBackgroundScheduler(ABC):
    """Port for background job scheduling."""

    @abstractmethod
    def schedule_interval(
        self,
        job_id: str,
        func: Callable,
        interval: timedelta,
        **kwargs
    ) -> None:
        """Schedule a recurring job."""
        pass

    @abstractmethod
    def schedule_once(
        self,
        job_id: str,
        func: Callable,
        delay: timedelta,
        **kwargs
    ) -> None:
        """Schedule a one-time job."""
        pass

    @abstractmethod
    def cancel(self, job_id: str) -> None:
        """Cancel a scheduled job."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the scheduler."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown."""
        pass
```

### 3. Standard Tier Adapters

#### PostgreSQL Storage (Same as Enterprise)
```python
# src/mind/adapters/standard/postgres_storage.py
class PostgresMemoryStorage(IMemoryStorage):
    """PostgreSQL implementation of memory storage."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def store(self, memory: Memory) -> Memory:
        query = """
            INSERT INTO memories (
                memory_id, user_id, content, content_type,
                temporal_level, base_salience, outcome_adjustment,
                embedding, valid_from, valid_until, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
        """
        row = await self.pool.fetchrow(query, ...)
        return Memory.from_row(row)
```

#### PostgreSQL Events (Replaces NATS)
```python
# src/mind/adapters/standard/postgres_events.py
class PostgresEventPublisher(IEventPublisher):
    """PostgreSQL NOTIFY-based event publishing."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def publish(self, event_type: str, payload: dict) -> None:
        # Also persist to events table for durability
        await self.pool.execute("""
            INSERT INTO events (event_type, payload, created_at)
            VALUES ($1, $2, NOW())
        """, event_type, json.dumps(payload))

        # Notify listeners
        await self.pool.execute(
            f"NOTIFY mind_events, '{event_type}:{json.dumps(payload)}'"
        )

class PostgresEventConsumer(IEventConsumer):
    """PostgreSQL LISTEN-based event consuming."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.handlers: Dict[str, List[Callable]] = {}
        self._running = False

    async def subscribe(self, event_type: str, handler: Callable) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def start(self) -> None:
        self._running = True
        conn = await self.pool.acquire()
        await conn.add_listener('mind_events', self._handle_notification)

    async def _handle_notification(self, conn, pid, channel, payload):
        event_type, data = payload.split(':', 1)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                await handler(json.loads(data))
```

#### pgvector Search (Replaces Qdrant)
```python
# src/mind/adapters/standard/pgvector_search.py
class PgVectorSearch(IVectorSearch):
    """PostgreSQL pgvector implementation."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter: Optional[dict] = None
    ) -> List[Tuple[UUID, float]]:
        # Build filter clause
        where_clause = "WHERE 1=1"
        params = [query_embedding, limit]
        param_idx = 3

        if filter:
            if 'user_id' in filter:
                where_clause += f" AND user_id = ${param_idx}"
                params.append(filter['user_id'])
                param_idx += 1
            if 'temporal_level' in filter:
                where_clause += f" AND temporal_level = ${param_idx}"
                params.append(filter['temporal_level'])
                param_idx += 1

        query = f"""
            SELECT
                memory_id,
                1 - (embedding <=> $1::vector) AS similarity
            FROM memories
            {where_clause}
            AND valid_until IS NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """

        rows = await self.pool.fetch(query, *params)
        return [(row['memory_id'], row['similarity']) for row in rows]
```

#### PostgreSQL Causal (Replaces FalkorDB)
```python
# src/mind/adapters/standard/postgres_causal.py
class PostgresCausalGraph(ICausalGraph):
    """Simple causal graph using PostgreSQL adjacency tables."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_edge(
        self,
        cause_id: UUID,
        effect_id: UUID,
        strength: float,
        evidence: str
    ) -> None:
        await self.pool.execute("""
            INSERT INTO causal_edges (cause_id, effect_id, strength, evidence)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (cause_id, effect_id)
            DO UPDATE SET strength = $3, evidence = $4
        """, cause_id, effect_id, strength, evidence)

    async def get_causes(
        self,
        effect_id: UUID,
        min_strength: float = 0.0
    ) -> List[CausalEdge]:
        rows = await self.pool.fetch("""
            SELECT * FROM causal_edges
            WHERE effect_id = $1 AND strength >= $2
            ORDER BY strength DESC
        """, effect_id, min_strength)
        return [CausalEdge.from_row(r) for r in rows]

    async def get_effects(
        self,
        cause_id: UUID,
        min_strength: float = 0.0
    ) -> List[CausalEdge]:
        rows = await self.pool.fetch("""
            SELECT * FROM causal_edges
            WHERE cause_id = $1 AND strength >= $2
            ORDER BY strength DESC
        """, cause_id, min_strength)
        return [CausalEdge.from_row(r) for r in rows]

    # Note: Complex graph traversal (multi-hop, cycle detection)
    # is limited compared to FalkorDB. Recommend upgrade for
    # advanced causal analysis.
```

#### APScheduler (Replaces Temporal)
```python
# src/mind/adapters/standard/apscheduler_runner.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

class APSchedulerRunner(IBackgroundScheduler):
    """APScheduler implementation for Standard tier."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def schedule_interval(
        self,
        job_id: str,
        func: Callable,
        interval: timedelta,
        **kwargs
    ) -> None:
        self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=interval.total_seconds()),
            id=job_id,
            kwargs=kwargs,
            replace_existing=True
        )

    async def start(self) -> None:
        self.scheduler.start()

    async def shutdown(self) -> None:
        self.scheduler.shutdown(wait=True)
```

### 4. Embedded PostgreSQL

```python
# src/mind/infrastructure/embedded/postgres.py
import subprocess
import platform
import asyncio
from pathlib import Path
from typing import Optional
import asyncpg

class EmbeddedPostgres:
    """
    Embedded PostgreSQL server for zero-config local development.

    Downloads PostgreSQL binaries on first use (lazy loading).
    Data persists in ~/.mind/postgres/ across restarts.
    """

    DEFAULT_PORT = 5433  # Avoid conflict with system PG
    BINARY_VERSION = "16.1"  # PostgreSQL version

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        port: int = DEFAULT_PORT
    ):
        self.data_dir = Path(data_dir or "~/.mind/postgres").expanduser()
        self.bin_dir = self.data_dir / "bin"
        self.pg_data = self.data_dir / "data"
        self.port = port
        self._process: Optional[subprocess.Popen] = None

    @property
    def connection_url(self) -> str:
        """Get the connection URL for this embedded instance."""
        return f"postgresql://mind:mind@localhost:{self.port}/mind"

    async def ensure_binaries(self) -> None:
        """Download PostgreSQL binaries if not present."""
        if (self.bin_dir / "postgres").exists():
            return

        self.bin_dir.mkdir(parents=True, exist_ok=True)

        # Determine platform
        system = platform.system().lower()
        arch = platform.machine().lower()

        # Download appropriate binaries
        # Uses embedded-postgres-binaries project
        url = self._get_binary_url(system, arch)
        await self._download_and_extract(url)

    async def init_db(self) -> None:
        """Initialize the PostgreSQL data directory."""
        if (self.pg_data / "PG_VERSION").exists():
            return

        self.pg_data.mkdir(parents=True, exist_ok=True)

        initdb = self.bin_dir / "initdb"
        proc = await asyncio.create_subprocess_exec(
            str(initdb),
            "-D", str(self.pg_data),
            "-U", "mind",
            "--encoding=UTF8",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"initdb failed: {stderr.decode()}")

        # Configure for local use
        await self._configure_postgres()

    async def start(self) -> str:
        """Start the embedded PostgreSQL server."""
        await self.ensure_binaries()
        await self.init_db()

        postgres = self.bin_dir / "postgres"
        self._process = subprocess.Popen(
            [
                str(postgres),
                "-D", str(self.pg_data),
                "-p", str(self.port),
                "-k", str(self.data_dir),  # Unix socket dir
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

        # Wait for PostgreSQL to be ready
        await self._wait_for_ready()

        # Create database if needed
        await self._ensure_database()

        # Apply pgvector extension
        await self._ensure_pgvector()

        return self.connection_url

    async def stop(self) -> None:
        """Gracefully stop PostgreSQL."""
        if self._process:
            pg_ctl = self.bin_dir / "pg_ctl"
            subprocess.run([
                str(pg_ctl), "stop",
                "-D", str(self.pg_data),
                "-m", "fast"
            ])
            self._process = None

    async def _wait_for_ready(self, timeout: int = 30) -> None:
        """Wait for PostgreSQL to accept connections."""
        for _ in range(timeout * 10):
            try:
                conn = await asyncpg.connect(
                    host="localhost",
                    port=self.port,
                    user="mind",
                    database="postgres"
                )
                await conn.close()
                return
            except:
                await asyncio.sleep(0.1)
        raise RuntimeError("PostgreSQL failed to start")

    async def _ensure_database(self) -> None:
        """Create the mind database if it doesn't exist."""
        conn = await asyncpg.connect(
            host="localhost",
            port=self.port,
            user="mind",
            database="postgres"
        )
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = 'mind'"
            )
            if not exists:
                await conn.execute("CREATE DATABASE mind")
        finally:
            await conn.close()

    async def _ensure_pgvector(self) -> None:
        """Enable pgvector extension."""
        conn = await asyncpg.connect(self.connection_url)
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        finally:
            await conn.close()
```

### 5. Dependency Injection Container

```python
# src/mind/container.py
from dataclasses import dataclass
from typing import Optional
import os

from .ports.storage import IMemoryStorage, IDecisionStorage
from .ports.events import IEventPublisher, IEventConsumer
from .ports.vectors import IVectorSearch
from .ports.graphs import ICausalGraph
from .ports.scheduler import IBackgroundScheduler

@dataclass
class MindContainer:
    """Dependency injection container for Mind services."""

    memory_storage: IMemoryStorage
    decision_storage: IDecisionStorage
    event_publisher: IEventPublisher
    event_consumer: IEventConsumer
    vector_search: IVectorSearch
    causal_graph: ICausalGraph
    scheduler: IBackgroundScheduler

    @classmethod
    async def create_standard(
        cls,
        database_url: Optional[str] = None
    ) -> "MindContainer":
        """Create Standard tier container."""
        from .adapters.standard import (
            PostgresMemoryStorage,
            PostgresDecisionStorage,
            PostgresEventPublisher,
            PostgresEventConsumer,
            PgVectorSearch,
            PostgresCausalGraph,
            APSchedulerRunner
        )
        from .infrastructure.embedded import EmbeddedPostgres

        # Use provided URL or start embedded PostgreSQL
        if database_url:
            pool = await asyncpg.create_pool(database_url)
        else:
            embedded = EmbeddedPostgres()
            url = await embedded.start()
            pool = await asyncpg.create_pool(url)

        return cls(
            memory_storage=PostgresMemoryStorage(pool),
            decision_storage=PostgresDecisionStorage(pool),
            event_publisher=PostgresEventPublisher(pool),
            event_consumer=PostgresEventConsumer(pool),
            vector_search=PgVectorSearch(pool),
            causal_graph=PostgresCausalGraph(pool),
            scheduler=APSchedulerRunner()
        )

    @classmethod
    async def create_enterprise(cls) -> "MindContainer":
        """Create Enterprise tier container."""
        from .adapters.enterprise import (
            PostgresMemoryStorage,
            PostgresDecisionStorage,
            NatsEventPublisher,
            NatsEventConsumer,
            QdrantVectorSearch,
            FalkorDBCausalGraph,
            TemporalScheduler
        )

        # ... Enterprise configuration
        pass
```

### 6. Synchronous Learning Service

The key innovation for Standard tier: move learning from async events to synchronous calls.

```python
# src/mind/services/learning_service.py
class LearningService:
    """
    Synchronous learning loop for Standard tier.

    In Enterprise, salience updates happen via NATS events.
    In Standard, we update immediately after outcome recording.
    This actually provides BETTER consistency for single-user.
    """

    def __init__(
        self,
        memory_storage: IMemoryStorage,
        decision_storage: IDecisionStorage
    ):
        self.memory_storage = memory_storage
        self.decision_storage = decision_storage

    async def record_outcome(
        self,
        decision_id: UUID,
        outcome_quality: float,  # -1.0 to 1.0
        feedback: Optional[str] = None
    ) -> DecisionTrace:
        """
        Record outcome and immediately update saliences.

        This is synchronous (unlike Enterprise's async event flow)
        which provides immediate consistency.
        """
        # 1. Get the decision with its memory attributions
        decision = await self.decision_storage.get(decision_id)
        if not decision:
            raise NotFoundError(f"Decision {decision_id} not found")

        # 2. Record the outcome
        outcome = Outcome(
            decision_id=decision_id,
            quality=outcome_quality,
            feedback=feedback,
            recorded_at=datetime.utcnow()
        )
        await self.decision_storage.record_outcome(outcome)

        # 3. Calculate salience adjustments for each attributed memory
        adjustments = self._calculate_adjustments(
            decision.memory_attributions,
            outcome_quality
        )

        # 4. Apply adjustments SYNCHRONOUSLY
        for memory_id, adjustment in adjustments.items():
            await self.memory_storage.update_salience(
                memory_id,
                adjustment
            )

        # 5. Build and return trace
        return DecisionTrace(
            decision=decision,
            outcome=outcome,
            salience_adjustments=adjustments
        )

    def _calculate_adjustments(
        self,
        attributions: Dict[UUID, float],  # memory_id -> attribution_score
        outcome_quality: float
    ) -> Dict[UUID, float]:
        """
        Calculate how much to adjust each memory's salience.

        Uses attribution-weighted outcome:
        - High attribution + positive outcome = big boost
        - High attribution + negative outcome = big penalty
        - Low attribution = small adjustment either way
        """
        adjustments = {}

        # Normalize attribution scores
        total_attribution = sum(attributions.values()) or 1.0

        for memory_id, attribution in attributions.items():
            normalized = attribution / total_attribution
            adjustment = normalized * outcome_quality * 0.1  # Max 10% per outcome
            adjustments[memory_id] = adjustment

        return adjustments
```

---

## Consequences

### Positive

1. **Zero-config experience**: Users can start in seconds
2. **Cloud-native**: Works with Supabase, Neon out of the box
3. **Maintainable**: Single codebase, shared tests
4. **Clear upgrade path**: Port interfaces make tier migration trivial
5. **Immediate consistency**: Synchronous learning is actually better for single-user

### Negative

1. **Embedded PG binary size**: ~100MB download on first use
2. **Limited graph traversal**: Simple adjacency tables vs FalkorDB
3. **No event replay**: PostgreSQL events don't support replay like NATS
4. **Single instance**: Can't horizontally scale Standard tier

### Neutral

1. **Feature flags**: Need to manage tier-specific behavior
2. **Documentation**: Must clearly document tier differences
3. **Testing**: Need tests for both adapter implementations

---

## References

- ADR-001: Event Sourcing Architecture
- ADR-005: PostgreSQL as Primary Store
- ADR-008: Hierarchical Memory Design
- PRD: Mind Standard Tier
