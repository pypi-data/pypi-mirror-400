"""Pattern extractor consumer for federation.

This consumer reacts to outcome events to extract learnable patterns
that can be shared across users after sanitization.
"""

from uuid import UUID

import structlog

from mind.core.decision.models import Outcome
from mind.core.events.base import EventEnvelope, EventType
from mind.core.federation.extractor import (
    CategoryMapper,
    ExtractionContext,
    PatternExtractor,
)
from mind.core.federation.sanitizer import DifferentialPrivacySanitizer
from mind.infrastructure.nats.client import NatsClient
from mind.infrastructure.nats.consumer import EventConsumer
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.repositories import (
    DecisionRepository,
    MemoryRepository,
)

logger = structlog.get_logger()


class PatternExtractorConsumer:
    """Extracts patterns from successful outcomes for federation.

    This consumer listens for:
    - outcome.observed: Extract patterns from positive outcomes

    Patterns are extracted by:
    1. Filtering for positive outcomes (quality >= 0.3)
    2. Categorizing memories used in the decision
    3. Building pattern candidates from abstracted categories
    4. Checking if patterns meet privacy thresholds
    5. Sanitizing and storing ready patterns

    Privacy is preserved by:
    - Only using abstract categories, never content
    - Requiring minimum user counts before sharing
    - Applying differential privacy to aggregated data
    """

    CONSUMER_NAME = "pattern-extractor"

    # Minimum outcome quality for pattern extraction
    MIN_QUALITY_THRESHOLD = 0.3

    # How often to check for ready patterns (in events processed)
    CHECK_READY_INTERVAL = 100

    def __init__(self, client: NatsClient):
        self._client = client
        self._consumer = EventConsumer(client, self.CONSUMER_NAME)
        self._extractor = PatternExtractor()
        self._sanitizer = DifferentialPrivacySanitizer()
        self._category_mapper = CategoryMapper()
        self._events_processed = 0
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Register event handlers."""
        self._consumer.on(EventType.OUTCOME_OBSERVED, self._handle_outcome)

    async def start(self) -> None:
        """Start the consumer."""
        logger.info("pattern_extractor_starting")
        await self._consumer.start(subjects=["mind.*.outcome.observed"])

    async def stop(self) -> None:
        """Stop the consumer."""
        await self._consumer.stop()
        logger.info("pattern_extractor_stopped")

    async def _handle_outcome(self, envelope: EventEnvelope) -> None:
        """Handle outcome.observed events.

        Extracts patterns from positive outcomes by:
        1. Getting the decision trace
        2. Categorizing the memories used
        3. Adding observation to pattern extractor
        4. Periodically checking for ready patterns
        """
        log = logger.bind(
            event_id=str(envelope.event_id),
            user_id=str(envelope.user_id),
        )

        try:
            payload = envelope.payload
            trace_id = UUID(payload["trace_id"])
            outcome_quality = payload.get("outcome_quality", 0.0)
            outcome_signal = payload.get("outcome_signal", "unknown")

            log = log.bind(
                trace_id=str(trace_id),
                outcome_quality=outcome_quality,
            )

            # Skip low-quality outcomes
            if outcome_quality < self.MIN_QUALITY_THRESHOLD:
                log.debug("outcome_below_threshold")
                return

            # Get decision trace from database
            db = get_database()
            async with db.session() as session:
                decision_repo = DecisionRepository(session)
                memory_repo = MemoryRepository(session)

                # Fetch the decision trace
                trace_result = await decision_repo.get(trace_id)
                if not trace_result.is_ok:
                    log.warning("decision_trace_not_found")
                    return

                trace = trace_result.value

                # Get memories used in the decision
                memory_contents = []
                for memory_id in trace.memory_ids[:10]:  # Limit to top 10
                    mem_result = await memory_repo.get(memory_id)
                    if mem_result.is_ok:
                        memory_contents.append(mem_result.value.content)

            # Categorize memories for privacy
            memory_categories = self._category_mapper.categorize_memories(memory_contents)

            # Create outcome object
            outcome = Outcome(
                trace_id=trace_id,
                quality=outcome_quality,
                signal=outcome_signal,
            )

            # Extract pattern
            context = ExtractionContext(
                trace=trace,
                outcome=outcome,
                memory_categories=memory_categories,
            )

            result = self._extractor.extract_from_outcome(context)
            if result.is_ok and result.value:
                log.info(
                    "pattern_observation_recorded",
                    observation_count=result.value.observation_count,
                    user_count=result.value.user_count,
                )

            # Periodically check for ready patterns
            self._events_processed += 1
            if self._events_processed % self.CHECK_READY_INTERVAL == 0:
                await self._process_ready_patterns()

        except Exception as e:
            log.error("pattern_extraction_failed", error=str(e))
            raise  # Let consumer handle retry

    async def _process_ready_patterns(self) -> None:
        """Process patterns that meet privacy thresholds.

        Sanitizes and stores patterns that are ready for federation.
        """
        log = logger.bind(events_processed=self._events_processed)

        try:
            ready_patterns = self._extractor.get_ready_patterns()
            if not ready_patterns:
                log.debug("no_patterns_ready")
                return

            log.info("patterns_ready", count=len(ready_patterns))

            for pattern in ready_patterns:
                # Sanitize the pattern
                sanitized = self._sanitizer.sanitize_pattern(pattern)

                if sanitized is not None:
                    # Store the sanitized pattern
                    await self._store_pattern(sanitized)

                    log.info(
                        "pattern_sanitized_and_stored",
                        pattern_id=str(pattern.pattern_id),
                    )

        except Exception as e:
            log.error("pattern_processing_failed", error=str(e))

    async def _store_pattern(self, pattern) -> None:
        """Store a sanitized pattern for federation.

        In production, this would store to a federation database.
        For now, we log the pattern.
        """
        logger.info(
            "federated_pattern_stored",
            pattern_id=str(pattern.pattern_id) if hasattr(pattern, "pattern_id") else "unknown",
            trigger_category=getattr(pattern, "trigger_category", "unknown"),
            observation_count=getattr(pattern, "observation_count", 0),
            user_count=getattr(pattern, "user_count", 0),
        )


async def create_pattern_extractor() -> PatternExtractorConsumer:
    """Factory to create and initialize the pattern extractor."""
    from mind.infrastructure.nats.client import get_nats_client

    client = await get_nats_client()
    return PatternExtractorConsumer(client)
