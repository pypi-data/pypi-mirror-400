"""Event consumers for Mind v5.

Consumers react to domain events published to NATS JetStream:
- CausalGraphUpdater: Updates causal graph when decisions/outcomes occur
- SalienceUpdater: Updates memory salience based on outcomes
- PatternExtractorConsumer: Extracts patterns from successful decisions
"""

from mind.workers.consumers.causal_updater import CausalGraphUpdater
from mind.workers.consumers.pattern_extractor import PatternExtractorConsumer
from mind.workers.consumers.salience_updater import SalienceUpdater

__all__ = ["CausalGraphUpdater", "SalienceUpdater", "PatternExtractorConsumer"]
