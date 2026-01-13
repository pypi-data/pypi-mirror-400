"""Dependency injection container for Mind services.

The container provides a unified way to access all Mind services
with the correct adapters for the current tier (Standard/Enterprise).

Usage:
    # Standard tier with embedded PostgreSQL
    container = await MindContainer.create_standard()

    # Standard tier with cloud PostgreSQL
    container = await MindContainer.create_standard(
        database_url="postgresql://..."
    )

    # Enterprise tier (requires Docker services)
    container = await MindContainer.create_enterprise()

    # Access services
    memory = await container.memory_storage.get(memory_id)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TYPE_CHECKING
import os

from .ports.storage import IMemoryStorage, IDecisionStorage
from .ports.events import IEventPublisher, IEventConsumer
from .ports.vectors import IVectorSearch
from .ports.graphs import ICausalGraph
from .ports.scheduler import IBackgroundScheduler

if TYPE_CHECKING:
    from .workers.standard.runner import StandardWorkerRunner


class Tier(Enum):
    """Mind deployment tiers."""

    STANDARD = "standard"  # PostgreSQL + APScheduler
    ENTERPRISE = "enterprise"  # Full Docker stack


@dataclass
class MindContainer:
    """Dependency injection container for Mind services.

    All infrastructure dependencies are injected through this container,
    allowing easy swapping between tiers and testing with mocks.

    Attributes:
        tier: The current deployment tier
        memory_storage: Memory persistence operations
        decision_storage: Decision trace persistence
        event_publisher: Domain event publishing
        event_consumer: Domain event consumption
        vector_search: Vector similarity search
        causal_graph: Causal relationship graph
        scheduler: Background job scheduling
    """

    tier: Tier
    memory_storage: IMemoryStorage
    decision_storage: IDecisionStorage
    event_publisher: IEventPublisher
    event_consumer: IEventConsumer
    vector_search: IVectorSearch
    causal_graph: ICausalGraph
    scheduler: IBackgroundScheduler

    # Internal state
    _pool: Optional[object] = None  # Database connection pool
    _embedded_pg: Optional[object] = None  # Embedded PostgreSQL instance
    _worker_runner: Optional["StandardWorkerRunner"] = None  # Standard tier job runner

    @classmethod
    async def create_standard(
        cls,
        database_url: Optional[str] = None,
    ) -> "MindContainer":
        """Create a Standard tier container.

        Args:
            database_url: PostgreSQL connection string.
                         If None, starts embedded PostgreSQL.

        Returns:
            Configured MindContainer for Standard tier

        Example:
            # Zero-config local development
            container = await MindContainer.create_standard()

            # Cloud PostgreSQL (Supabase, Neon, etc.)
            container = await MindContainer.create_standard(
                database_url="postgresql://user:pass@host:5432/mind"
            )
        """
        # Import adapters (deferred to avoid circular imports)
        from .adapters.standard import (
            PostgresMemoryStorage,
            PostgresDecisionStorage,
            PostgresEventPublisher,
            PostgresEventConsumer,
            PgVectorSearch,
            PostgresCausalGraph,
            APSchedulerRunner,
        )

        embedded_pg = None
        pool = None

        # Determine database URL
        if database_url is None:
            database_url = os.environ.get("MIND_DATABASE_URL")

        if database_url is None:
            # Start embedded PostgreSQL for zero-config local development
            from .infrastructure.embedded import EmbeddedPostgres

            embedded_pg = EmbeddedPostgres()
            await embedded_pg.start()
            database_url = embedded_pg.sync_connection_url

        # Create connection pool
        import asyncpg

        # Strip SQLAlchemy driver prefix if present
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        asyncpg_url = asyncpg_url.replace("postgresql+psycopg2://", "postgresql://")

        pool = await asyncpg.create_pool(
            asyncpg_url,
            min_size=2,
            max_size=10,
        )

        # Initialize Standard tier schema
        from .infrastructure.embedded.schema import init_standard_schema
        await init_standard_schema(pool)

        # Create adapters
        memory_storage = PostgresMemoryStorage(pool)
        decision_storage = PostgresDecisionStorage(pool)
        event_publisher = PostgresEventPublisher(pool)
        event_consumer = PostgresEventConsumer(pool)
        vector_search = PgVectorSearch(pool)
        causal_graph = PostgresCausalGraph(pool)
        scheduler = APSchedulerRunner()

        # Create worker runner for Standard tier background jobs
        from .workers.standard.runner import StandardWorkerRunner
        worker_runner = StandardWorkerRunner()

        container = cls(
            tier=Tier.STANDARD,
            memory_storage=memory_storage,
            decision_storage=decision_storage,
            event_publisher=event_publisher,
            event_consumer=event_consumer,
            vector_search=vector_search,
            causal_graph=causal_graph,
            scheduler=scheduler,
        )
        container._pool = pool
        container._embedded_pg = embedded_pg
        container._worker_runner = worker_runner

        return container

    @classmethod
    async def create_enterprise(
        cls,
        *,
        postgres_url: Optional[str] = None,
        nats_url: Optional[str] = None,
        qdrant_url: Optional[str] = None,
        falkordb_url: Optional[str] = None,
        temporal_url: Optional[str] = None,
    ) -> "MindContainer":
        """Create an Enterprise tier container.

        Args:
            postgres_url: PostgreSQL connection string
            nats_url: NATS server URL
            qdrant_url: Qdrant server URL
            falkordb_url: FalkorDB server URL
            temporal_url: Temporal server URL

        Returns:
            Configured MindContainer for Enterprise tier

        Note:
            Enterprise tier requires Docker services to be running.
            Use docker-compose up to start all required services.
        """
        # Import enterprise adapters
        from .adapters.enterprise import (
            PostgresMemoryStorage,
            PostgresDecisionStorage,
            NatsEventPublisher,
            NatsEventConsumer,
            QdrantVectorSearch,
            FalkorDBCausalGraph,
            TemporalScheduler,
        )

        # Get URLs from environment if not provided
        postgres_url = postgres_url or os.environ.get(
            "MIND_POSTGRES_URL",
            "postgresql://mind:mind@localhost:5432/mind",
        )
        nats_url = nats_url or os.environ.get(
            "MIND_NATS_URL",
            "nats://localhost:4222",
        )
        qdrant_url = qdrant_url or os.environ.get(
            "MIND_QDRANT_URL",
            "http://localhost:6333",
        )
        falkordb_url = falkordb_url or os.environ.get(
            "MIND_FALKORDB_URL",
            "redis://localhost:6379",
        )
        temporal_url = temporal_url or os.environ.get(
            "MIND_TEMPORAL_URL",
            "localhost:7233",
        )

        # Create connection pool
        import asyncpg

        # Strip SQLAlchemy driver prefix if present
        asyncpg_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
        asyncpg_url = asyncpg_url.replace("postgresql+psycopg2://", "postgresql://")

        pool = await asyncpg.create_pool(
            asyncpg_url,
            min_size=5,
            max_size=20,
        )

        # Create enterprise adapters
        memory_storage = PostgresMemoryStorage(pool)
        decision_storage = PostgresDecisionStorage(pool)
        event_publisher = await NatsEventPublisher.connect(nats_url)
        event_consumer = await NatsEventConsumer.connect(nats_url)
        vector_search = await QdrantVectorSearch.connect(qdrant_url)
        causal_graph = await FalkorDBCausalGraph.connect(falkordb_url)
        scheduler = await TemporalScheduler.connect(temporal_url)

        container = cls(
            tier=Tier.ENTERPRISE,
            memory_storage=memory_storage,
            decision_storage=decision_storage,
            event_publisher=event_publisher,
            event_consumer=event_consumer,
            vector_search=vector_search,
            causal_graph=causal_graph,
            scheduler=scheduler,
        )
        container._pool = pool

        return container

    @classmethod
    async def create_for_testing(
        cls,
        *,
        memory_storage: Optional[IMemoryStorage] = None,
        decision_storage: Optional[IDecisionStorage] = None,
        event_publisher: Optional[IEventPublisher] = None,
        event_consumer: Optional[IEventConsumer] = None,
        vector_search: Optional[IVectorSearch] = None,
        causal_graph: Optional[ICausalGraph] = None,
        scheduler: Optional[IBackgroundScheduler] = None,
    ) -> "MindContainer":
        """Create a container with mock/test implementations.

        Args:
            Provide mock implementations for any ports needed in tests.
            Ports not provided will use a no-op stub.

        Returns:
            Container configured for testing
        """
        from .adapters.testing import (
            StubMemoryStorage,
            StubDecisionStorage,
            StubEventPublisher,
            StubEventConsumer,
            StubVectorSearch,
            StubCausalGraph,
            StubScheduler,
        )

        return cls(
            tier=Tier.STANDARD,
            memory_storage=memory_storage or StubMemoryStorage(),
            decision_storage=decision_storage or StubDecisionStorage(),
            event_publisher=event_publisher or StubEventPublisher(),
            event_consumer=event_consumer or StubEventConsumer(),
            vector_search=vector_search or StubVectorSearch(),
            causal_graph=causal_graph or StubCausalGraph(),
            scheduler=scheduler or StubScheduler(),
        )

    async def start(self) -> None:
        """Start all services that need explicit startup.

        Call this after creating the container to:
        - Start the event consumer
        - Start the background scheduler (with jobs for Standard tier)
        """
        await self.event_consumer.start()

        # For Standard tier, use the worker runner to register and start jobs
        if self._worker_runner is not None:
            await self._worker_runner.start()
            print("Scheduler started")  # Match existing output
        else:
            # Enterprise tier: scheduler started separately (Temporal)
            await self.scheduler.start()

    async def shutdown(self) -> None:
        """Gracefully shutdown all services.

        Call this before application exit to:
        - Stop the event consumer
        - Stop the scheduler
        - Close database connections
        - Stop embedded PostgreSQL (if used)
        """
        await self.event_consumer.stop()

        # For Standard tier, use the worker runner to stop jobs
        if self._worker_runner is not None:
            await self._worker_runner.stop()
        else:
            await self.scheduler.shutdown(wait=True)

        await self.event_publisher.close()

        if self._pool is not None:
            await self._pool.close()

        if self._embedded_pg is not None:
            await self._embedded_pg.stop()

    async def health_check(self) -> dict[str, bool]:
        """Check health of all services.

        Returns:
            Dictionary mapping service name to health status
        """
        # Get scheduler health from worker runner for Standard tier
        if self._worker_runner is not None:
            scheduler_healthy = await self._worker_runner.health_check()
        else:
            scheduler_healthy = await self.scheduler.health_check()

        return {
            "vector_search": await self.vector_search.health_check(),
            "causal_graph": await self.causal_graph.health_check(),
            "scheduler": scheduler_healthy,
        }

    @property
    def is_standard(self) -> bool:
        """Check if running in Standard tier."""
        return self.tier == Tier.STANDARD

    @property
    def is_enterprise(self) -> bool:
        """Check if running in Enterprise tier."""
        return self.tier == Tier.ENTERPRISE


# Global container instance (set during app startup)
_container: Optional[MindContainer] = None


def get_container() -> MindContainer:
    """Get the global container instance.

    Returns:
        The configured MindContainer

    Raises:
        RuntimeError: If container not initialized
    """
    if _container is None:
        raise RuntimeError(
            "MindContainer not initialized. "
            "Call set_container() during app startup."
        )
    return _container


def set_container(container: MindContainer) -> None:
    """Set the global container instance.

    Args:
        container: The container to use globally

    Note:
        Typically called once during application startup.
    """
    global _container
    _container = container
