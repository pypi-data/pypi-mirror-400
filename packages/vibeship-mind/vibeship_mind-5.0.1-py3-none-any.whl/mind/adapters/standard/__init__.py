"""Standard tier adapters using PostgreSQL + APScheduler.

All adapters in this module use PostgreSQL as the backing store,
providing a zero-infrastructure deployment option.

Exports:
    PostgresMemoryStorage: Memory persistence
    PostgresDecisionStorage: Decision trace persistence
    PostgresEventPublisher: Event publishing via PG NOTIFY
    PostgresEventConsumer: Event consumption via PG LISTEN
    PgVectorSearch: Vector similarity via pgvector
    PostgresCausalGraph: Causal graph via adjacency tables
    APSchedulerRunner: Background jobs via APScheduler
"""

from .postgres_storage import PostgresMemoryStorage, PostgresDecisionStorage
from .postgres_events import PostgresEventPublisher, PostgresEventConsumer
from .pgvector_search import PgVectorSearch
from .postgres_causal import PostgresCausalGraph
from .apscheduler_runner import APSchedulerRunner

__all__ = [
    "PostgresMemoryStorage",
    "PostgresDecisionStorage",
    "PostgresEventPublisher",
    "PostgresEventConsumer",
    "PgVectorSearch",
    "PostgresCausalGraph",
    "APSchedulerRunner",
]
