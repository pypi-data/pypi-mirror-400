"""NATS JetStream infrastructure for event backbone."""

from mind.infrastructure.nats.client import NatsClient, get_nats_client
from mind.infrastructure.nats.consumer import EventConsumer
from mind.infrastructure.nats.publisher import EventPublisher

__all__ = [
    "NatsClient",
    "get_nats_client",
    "EventPublisher",
    "EventConsumer",
]
