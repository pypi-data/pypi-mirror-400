"""Adapter implementations for Mind ports.

Adapters provide concrete implementations of port interfaces
for different deployment tiers:

Standard Tier (adapters.standard):
    - PostgreSQL for all storage (memories, decisions, events, vectors, causal)
    - APScheduler for background jobs

Enterprise Tier (adapters.enterprise):
    - PostgreSQL for core storage
    - NATS for events
    - Qdrant for vectors
    - FalkorDB for causal graphs
    - Temporal for background jobs

Testing (adapters.testing):
    - In-memory stub implementations for unit tests
"""

from . import standard

__all__ = ["standard"]
