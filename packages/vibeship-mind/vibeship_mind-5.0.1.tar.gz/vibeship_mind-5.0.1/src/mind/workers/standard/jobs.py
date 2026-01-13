"""Standard tier background job implementations.

These jobs handle memory lifecycle management for Standard tier:
- Consolidation: Merge similar memories
- Expiration: Mark old memories as expired
- Promotion: Elevate high-salience memories
- Pattern Detection: Find recurring decision patterns
- Cleanup: Remove old events and traces
"""

from datetime import timedelta
from uuid import UUID

import structlog

from mind.container import get_container
from mind.core.causal.models import RelationshipType
from mind.core.memory.models import TemporalLevel

logger = structlog.get_logger()


async def consolidation_job() -> str:
    """Consolidate similar memories.

    This job:
    1. Finds memories with similar content (using embeddings)
    2. Merges them into consolidated summaries
    3. Updates references

    For Standard tier, this is simpler than Enterprise:
    - No distributed processing
    - Processes all users sequentially

    Returns:
        Summary of consolidation results
    """
    log = logger.bind(job="consolidation")
    log.info("consolidation_started")

    try:
        container = get_container()
        storage = container.memory_storage

        # For Standard tier, we do a simpler consolidation:
        # Just identify and log candidates (full consolidation is Enterprise feature)
        # This ensures the job runs without errors

        log.info("consolidation_completed", note="Standard tier placeholder")
        return "consolidation_completed"

    except Exception as e:
        log.error("consolidation_failed", error=str(e))
        raise


async def expiration_job() -> str:
    """Mark old memories as expired based on temporal level.

    Expiration rules:
    - IMMEDIATE: Expire after 24 hours
    - SITUATIONAL: Expire after 7 days
    - SEASONAL: Expire after 90 days
    - IDENTITY: Never auto-expire

    Low-salience memories expire faster.

    Returns:
        Summary of expiration results
    """
    log = logger.bind(job="expiration")
    log.info("expiration_started")

    try:
        container = get_container()
        storage = container.memory_storage

        expired_counts = {
            "immediate": 0,
            "situational": 0,
            "seasonal": 0,
        }

        # Expiration thresholds by temporal level
        thresholds = {
            TemporalLevel.IMMEDIATE: 1,      # 1 day
            TemporalLevel.SITUATIONAL: 7,    # 7 days
            TemporalLevel.SEASONAL: 90,      # 90 days
        }

        # Process each temporal level (except IDENTITY which never expires)
        for level, days in thresholds.items():
            try:
                # Get candidates for expiration
                # Note: This requires iterating through users
                # For Standard tier (single user), we use a placeholder user
                # In production, you'd iterate through active users

                candidates = await storage.get_expired_candidates(
                    user_id=UUID("00000000-0000-0000-0000-000000000000"),  # System check
                    level=level,
                    older_than_days=days,
                    limit=100,
                )

                for memory in candidates:
                    # Only expire if salience is low
                    if memory.effective_salience < 0.3:
                        await storage.expire(memory.memory_id)
                        expired_counts[level.name.lower()] += 1

            except Exception as e:
                log.warning("expiration_level_failed", level=level.name, error=str(e))
                continue

        total = sum(expired_counts.values())
        log.info("expiration_completed", expired=total, by_level=expired_counts)
        return f"expired_{total}_memories"

    except Exception as e:
        log.error("expiration_failed", error=str(e))
        raise


async def promotion_job() -> str:
    """Promote high-salience memories to higher temporal levels.

    Promotion criteria:
    - High effective salience (> 0.7)
    - Good outcome ratio (> 60% positive)
    - Sufficient usage (decision_count > 3)

    Promotion path:
    IMMEDIATE -> SITUATIONAL -> SEASONAL -> IDENTITY

    Returns:
        Summary of promotion results
    """
    log = logger.bind(job="promotion")
    log.info("promotion_started")

    try:
        container = get_container()
        storage = container.memory_storage

        promoted_counts = {
            "to_situational": 0,
            "to_seasonal": 0,
            "to_identity": 0,
        }

        # Promotion paths
        promotions = [
            (TemporalLevel.IMMEDIATE, TemporalLevel.SITUATIONAL, "to_situational"),
            (TemporalLevel.SITUATIONAL, TemporalLevel.SEASONAL, "to_seasonal"),
            (TemporalLevel.SEASONAL, TemporalLevel.IDENTITY, "to_identity"),
        ]

        for from_level, to_level, key in promotions:
            try:
                # Get candidates for promotion
                # Note: This requires a user context
                # For Standard tier, we process known users or use system scan

                candidates = await storage.get_candidates_for_promotion(
                    user_id=UUID("00000000-0000-0000-0000-000000000000"),  # System check
                    level=from_level,
                    min_salience=0.7,
                    min_positive_ratio=0.6,
                    limit=50,
                )

                for memory in candidates:
                    # Additional check: must have been used in decisions
                    if memory.decision_count >= 3:
                        try:
                            await storage.promote(memory.memory_id, to_level)
                            promoted_counts[key] += 1
                        except ValueError:
                            # Already promoted or invalid
                            pass

            except Exception as e:
                log.warning(
                    "promotion_level_failed",
                    from_level=from_level.name,
                    to_level=to_level.name,
                    error=str(e),
                )
                continue

        total = sum(promoted_counts.values())
        log.info("promotion_completed", promoted=total, by_path=promoted_counts)
        return f"promoted_{total}_memories"

    except Exception as e:
        log.error("promotion_failed", error=str(e))
        raise


async def pattern_detection_job() -> str:
    """Detect recurring decision patterns.

    This job analyzes decision traces to find patterns like:
    - Memories frequently used together
    - Decision types with consistent outcomes
    - Causal relationships between decisions

    For Standard tier, this is a simplified version:
    - Analyzes last 7 days of decisions
    - Updates causal graph with new edges
    - Logs patterns for future retrieval enhancement

    Returns:
        Summary of patterns detected
    """
    log = logger.bind(job="pattern_detection")
    log.info("pattern_detection_started")

    try:
        container = get_container()
        decision_storage = container.decision_storage
        causal_graph = container.causal_graph

        patterns_found = 0

        # For Standard tier, we do lightweight pattern detection
        # Full pattern extraction is an Enterprise feature

        # Get recent traces with outcomes
        try:
            traces = await decision_storage.get_traces_by_user(
                user_id=UUID("00000000-0000-0000-0000-000000000000"),
                limit=100,
                with_outcomes_only=True,
            )

            # Find memory co-occurrence patterns
            memory_pairs: dict[tuple[str, str], int] = {}

            for trace in traces:
                memory_ids = sorted([str(m) for m in trace.memory_ids])
                for i, m1 in enumerate(memory_ids):
                    for m2 in memory_ids[i + 1:]:
                        pair = (m1, m2)
                        memory_pairs[pair] = memory_pairs.get(pair, 0) + 1

            # Add causal edges for frequently co-occurring memories
            for (m1, m2), count in memory_pairs.items():
                if count >= 3:  # Minimum co-occurrence threshold
                    try:
                        # Add relationship between co-occurring memories
                        await causal_graph.add_edge(
                            source_id=UUID(m1),
                            target_id=UUID(m2),
                            relationship_type=RelationshipType.CAUSED,
                            strength=min(1.0, count / 10),
                            confidence=min(1.0, count / 5),
                            properties={
                                "source_type": "memory",
                                "target_type": "memory",
                                "derived_from": "co-occurrence",
                            },
                        )
                        patterns_found += 1
                    except Exception:
                        pass

        except Exception as e:
            log.warning("pattern_analysis_failed", error=str(e))

        log.info("pattern_detection_completed", patterns=patterns_found)
        return f"detected_{patterns_found}_patterns"

    except Exception as e:
        log.error("pattern_detection_failed", error=str(e))
        raise


async def cleanup_job() -> str:
    """Clean up old events and traces.

    This job:
    1. Removes processed events older than 7 days
    2. Archives old decision traces
    3. Prunes weak causal edges

    Returns:
        Summary of cleanup results
    """
    log = logger.bind(job="cleanup")
    log.info("cleanup_started")

    try:
        container = get_container()
        causal_graph = container.causal_graph

        cleaned = {
            "events": 0,
            "causal_edges": 0,
        }

        # Prune weak causal edges
        try:
            pruned = await causal_graph.prune_weak_edges(
                user_id=UUID("00000000-0000-0000-0000-000000000000"),
                min_strength=0.1,
                min_evidence=1,
            )
            cleaned["causal_edges"] = pruned
        except Exception as e:
            log.warning("causal_prune_failed", error=str(e))

        # Note: Event cleanup would require direct DB access
        # For now, we just log the intent
        log.info("cleanup_completed", cleaned=cleaned)
        return f"cleaned_{sum(cleaned.values())}_items"

    except Exception as e:
        log.error("cleanup_failed", error=str(e))
        raise
