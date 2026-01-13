"""Memory consolidation worker.

This worker periodically consolidates similar memories to:
1. Merge semantically similar memories into stronger, unified memories
2. Detect and resolve contradictions
3. Promote frequently-reinforced memories to higher temporal levels
4. Decay unused memories over time

The consolidation runs as a scheduled task, not event-driven.
"""

import asyncio
import json
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

import httpx
import structlog
from sqlalchemy import select, func, text

from mind.core.memory.models import Memory, TemporalLevel
from mind.infrastructure.postgres.database import get_database
from mind.infrastructure.postgres.models import MemoryModel
from mind.infrastructure.embeddings.openai import get_embedder

logger = structlog.get_logger()


class MemoryConsolidator:
    """Consolidates and maintains memory health.

    Key operations:
    1. Similarity-based consolidation: Merge similar memories
    2. Contradiction detection: Find and resolve conflicting memories
    3. Temporal promotion: Promote reinforced memories to higher levels
    4. Decay: Reduce salience of unused memories
    """

    SIMILARITY_THRESHOLD = 0.85  # Memories above this similarity are candidates for merge
    CONSOLIDATION_INTERVAL = 3600  # Run every hour

    def __init__(self):
        self._http = httpx.AsyncClient(timeout=30.0)
        self._openai_key = os.environ.get("MIND_OPENAI_API_KEY")
        self._running = False

    async def start(self) -> None:
        """Start the consolidation loop."""
        logger.info("memory_consolidator_starting")
        self._running = True

        while self._running:
            try:
                await self._run_consolidation_cycle()
            except Exception as e:
                logger.error("consolidation_cycle_failed", error=str(e))

            # Wait for next cycle
            await asyncio.sleep(self.CONSOLIDATION_INTERVAL)

    async def stop(self) -> None:
        """Stop the consolidation loop."""
        self._running = False
        await self._http.aclose()
        logger.info("memory_consolidator_stopped")

    async def _run_consolidation_cycle(self) -> None:
        """Run a full consolidation cycle across all users."""
        start_time = time.time()
        logger.info("consolidation_cycle_started")

        db = get_database()
        async with db.session() as session:
            # Get all unique user IDs with memories
            stmt = select(MemoryModel.user_id).distinct()
            result = await session.execute(stmt)
            user_ids = [row[0] for row in result.all()]

        consolidated_count = 0
        for user_id in user_ids:
            count = await self._consolidate_user_memories(user_id)
            consolidated_count += count

        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(
            "consolidation_cycle_completed",
            user_count=len(user_ids),
            consolidated_count=consolidated_count,
            elapsed_ms=elapsed_ms,
        )

    async def _consolidate_user_memories(self, user_id: UUID) -> int:
        """Consolidate memories for a single user.

        Returns the number of memories consolidated.
        """
        log = logger.bind(user_id=str(user_id))

        db = get_database()
        async with db.session() as session:
            # Get all active memories for user with embeddings
            stmt = (
                select(MemoryModel)
                .where(MemoryModel.user_id == user_id)
                .where(MemoryModel.embedding.isnot(None))
                .where(
                    (MemoryModel.valid_until.is_(None)) |
                    (MemoryModel.valid_until > datetime.now(UTC))
                )
                .order_by(MemoryModel.created_at.desc())
                .limit(500)  # Process in batches
            )
            result = await session.execute(stmt)
            memories = list(result.scalars().all())

        if len(memories) < 2:
            return 0

        # Find similar memory pairs
        similar_pairs = await self._find_similar_pairs(memories)

        if not similar_pairs:
            return 0

        # Consolidate each pair
        consolidated = 0
        for mem1, mem2, similarity in similar_pairs:
            try:
                merged = await self._merge_memories(mem1, mem2, similarity)
                if merged:
                    consolidated += 1
                    log.debug(
                        "memories_merged",
                        memory1=str(mem1.memory_id),
                        memory2=str(mem2.memory_id),
                        similarity=similarity,
                    )
            except Exception as e:
                log.warning("merge_failed", error=str(e))

        if consolidated > 0:
            log.info("user_memories_consolidated", count=consolidated)

        return consolidated

    async def _find_similar_pairs(
        self,
        memories: list[MemoryModel]
    ) -> list[tuple[MemoryModel, MemoryModel, float]]:
        """Find pairs of memories that are similar enough to consolidate."""
        similar_pairs = []

        # Compare each pair using cosine similarity
        for i, mem1 in enumerate(memories):
            for mem2 in memories[i + 1:]:
                if mem1.embedding is None or mem2.embedding is None:
                    continue

                similarity = self._cosine_similarity(mem1.embedding, mem2.embedding)

                if similarity >= self.SIMILARITY_THRESHOLD:
                    similar_pairs.append((mem1, mem2, similarity))

        # Sort by similarity (highest first)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)

        return similar_pairs[:10]  # Limit to top 10 pairs per cycle

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def _merge_memories(
        self,
        mem1: MemoryModel,
        mem2: MemoryModel,
        similarity: float,
    ) -> bool:
        """Merge two similar memories into one consolidated memory.

        Strategy:
        - Use LLM to create a consolidated content
        - Keep the higher temporal level
        - Combine salience (boost for reinforcement)
        - Expire the older memory
        """
        if not self._openai_key:
            return False

        # Use LLM to consolidate - escape content for safety
        mem1_safe = mem1.content.replace('"', '\\"').replace('\n', ' ')
        mem2_safe = mem2.content.replace('"', '\\"').replace('\n', ' ')

        prompt = f"""You are consolidating two similar memories into one stronger, unified memory.

Memory 1: {mem1_safe}
Memory 2: {mem2_safe}

Create a single consolidated memory that:
1. Captures all unique information from both memories
2. Is more comprehensive but still concise (1-2 sentences)
3. Uses the most specific/accurate details from either memory
4. Preserves any entity mentions

Return valid JSON only (no markdown, no code blocks):
{{"consolidated_content": "The merged memory content", "entities": ["entity1", "entity2"], "is_contradiction": false, "contradiction_resolution": null}}

If the memories contradict each other, set is_contradiction to true and explain in contradiction_resolution which one is likely more current/accurate."""

        try:
            response = await self._http.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "max_tokens": 256,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            result = response.json()

            response_text = result["choices"][0]["message"]["content"]

            # Parse JSON from response
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()

            merge_result = json.loads(clean_text)

            # Handle contradictions
            if merge_result.get("is_contradiction"):
                logger.info(
                    "contradiction_detected",
                    memory1=str(mem1.memory_id),
                    memory2=str(mem2.memory_id),
                    resolution=merge_result.get("contradiction_resolution"),
                )
                # Keep the newer one, expire the older
                older = mem1 if mem1.created_at < mem2.created_at else mem2
                await self._expire_memory(older)
                return True

            # Create consolidated memory and expire old ones
            consolidated_content = merge_result.get("consolidated_content", mem1.content)

            db = get_database()
            embedder = get_embedder()

            # Generate embedding for consolidated content
            embed_result = await embedder.embed(consolidated_content)
            embedding = embed_result if isinstance(embed_result, list) else None

            async with db.session() as session:
                # Create new consolidated memory
                new_memory = MemoryModel(
                    memory_id=uuid4(),
                    user_id=mem1.user_id,
                    content=consolidated_content,
                    content_type=mem1.content_type,
                    embedding=embedding,
                    temporal_level=max(mem1.temporal_level, mem2.temporal_level),
                    valid_from=min(mem1.valid_from, mem2.valid_from),
                    valid_until=None,
                    # Boost salience for reinforced memory
                    base_salience=min(1.0, max(mem1.base_salience, mem2.base_salience) + 0.1),
                    outcome_adjustment=(mem1.outcome_adjustment + mem2.outcome_adjustment) / 2,
                    retrieval_count=mem1.retrieval_count + mem2.retrieval_count,
                    decision_count=mem1.decision_count + mem2.decision_count,
                    positive_outcomes=mem1.positive_outcomes + mem2.positive_outcomes,
                    negative_outcomes=mem1.negative_outcomes + mem2.negative_outcomes,
                )
                session.add(new_memory)

                # Expire old memories
                now = datetime.now(UTC)
                await session.execute(
                    text("UPDATE memories SET valid_until = :now WHERE memory_id = :id1 OR memory_id = :id2"),
                    {"now": now, "id1": mem1.memory_id, "id2": mem2.memory_id}
                )

                await session.commit()

            return True

        except Exception as e:
            logger.error("merge_llm_failed", error=str(e))
            return False

    async def _expire_memory(self, memory: MemoryModel) -> None:
        """Mark a memory as expired."""
        db = get_database()
        async with db.session() as session:
            await session.execute(
                text("UPDATE memories SET valid_until = :now WHERE memory_id = :id"),
                {"now": datetime.now(UTC), "id": memory.memory_id}
            )
            await session.commit()


async def create_memory_consolidator() -> MemoryConsolidator:
    """Factory to create the memory consolidator."""
    return MemoryConsolidator()
