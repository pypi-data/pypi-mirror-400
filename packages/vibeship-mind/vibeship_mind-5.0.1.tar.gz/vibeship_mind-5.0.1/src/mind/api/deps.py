"""FastAPI dependencies for accessing Mind services.

These dependencies provide access to the container adapters,
enabling routes to work with both Standard and Enterprise tiers.

Usage:
    from mind.api.deps import get_memory_storage

    @router.post("/")
    async def create_memory(
        request: MemoryCreate,
        storage: IMemoryStorage = Depends(get_memory_storage),
    ):
        await storage.store(memory)
"""

from mind.container import get_container
from mind.ports.storage import IMemoryStorage, IDecisionStorage
from mind.ports.events import IEventPublisher
from mind.ports.vectors import IVectorSearch
from mind.ports.graphs import ICausalGraph


def get_memory_storage() -> IMemoryStorage:
    """Get the memory storage adapter from the container.

    Returns the appropriate adapter for the current tier:
    - Standard: PostgresMemoryStorage (asyncpg)
    - Enterprise: PostgresMemoryStorage (asyncpg)

    Raises:
        RuntimeError: If container not initialized
    """
    return get_container().memory_storage


def get_decision_storage() -> IDecisionStorage:
    """Get the decision storage adapter from the container.

    Returns the appropriate adapter for the current tier:
    - Standard: PostgresDecisionStorage (asyncpg)
    - Enterprise: PostgresDecisionStorage (asyncpg)

    Raises:
        RuntimeError: If container not initialized
    """
    return get_container().decision_storage


def get_event_publisher() -> IEventPublisher:
    """Get the event publisher from the container.

    Returns the appropriate adapter for the current tier:
    - Standard: PostgresEventPublisher
    - Enterprise: NatsEventPublisher

    Raises:
        RuntimeError: If container not initialized
    """
    return get_container().event_publisher


def get_vector_search() -> IVectorSearch:
    """Get the vector search adapter from the container.

    Returns the appropriate adapter for the current tier:
    - Standard: PgVectorSearch
    - Enterprise: QdrantVectorSearch

    Raises:
        RuntimeError: If container not initialized
    """
    return get_container().vector_search


def get_causal_graph() -> ICausalGraph:
    """Get the causal graph adapter from the container.

    Returns the appropriate adapter for the current tier:
    - Standard: PostgresCausalGraph
    - Enterprise: FalkorDBCausalGraph

    Raises:
        RuntimeError: If container not initialized
    """
    return get_container().causal_graph


def is_container_ready() -> bool:
    """Check if the container has been initialized.

    Useful for health checks and graceful startup.

    Returns:
        True if container is initialized and available
    """
    try:
        get_container()
        return True
    except RuntimeError:
        return False
