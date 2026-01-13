"""Port interfaces for Mind infrastructure abstraction.

Ports define the boundaries between core domain logic and infrastructure.
Each port has one or more adapters (implementations) for different tiers:

Standard Tier:
    - PostgreSQL for storage, events, vectors, causal
    - APScheduler for background jobs

Enterprise Tier:
    - PostgreSQL for storage
    - NATS for events
    - Qdrant for vectors
    - FalkorDB for causal graphs
    - Temporal for background jobs
"""

from .storage import IMemoryStorage, IDecisionStorage
from .events import IEventPublisher, IEventConsumer
from .vectors import IVectorSearch
from .graphs import ICausalGraph
from .scheduler import IBackgroundScheduler

__all__ = [
    # Storage ports
    "IMemoryStorage",
    "IDecisionStorage",
    # Event ports
    "IEventPublisher",
    "IEventConsumer",
    # Vector port
    "IVectorSearch",
    # Graph port
    "ICausalGraph",
    # Scheduler port
    "IBackgroundScheduler",
]
