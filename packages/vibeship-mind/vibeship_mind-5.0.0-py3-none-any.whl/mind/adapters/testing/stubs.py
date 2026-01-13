"""Stub implementations for testing.

These in-memory stubs allow unit testing without databases.
"""

from datetime import datetime, timedelta, UTC
from typing import Any, Optional
from uuid import UUID

from ...core.memory.models import Memory, TemporalLevel
from ...core.decision.models import DecisionTrace, Outcome, SalienceUpdate
from ...core.causal.models import CausalNode, CausalRelationship, NodeType, RelationshipType
from ...ports.storage import IMemoryStorage, IDecisionStorage
from ...ports.events import IEventPublisher, IEventConsumer, EventHandler
from ...ports.vectors import IVectorSearch, VectorSearchResult, VectorFilter
from ...ports.graphs import ICausalGraph, CausalPath, CausalNeighbors
from ...ports.scheduler import IBackgroundScheduler, JobFunc, JobInfo, JobStatus


class StubMemoryStorage(IMemoryStorage):
    """In-memory stub for memory storage."""

    def __init__(self):
        self.memories: dict[UUID, Memory] = {}

    async def store(self, memory: Memory) -> Memory:
        self.memories[memory.memory_id] = memory
        return memory

    async def get(self, memory_id: UUID) -> Optional[Memory]:
        return self.memories.get(memory_id)

    async def get_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
        temporal_level: Optional[TemporalLevel] = None,
        min_salience: float = 0.0,
        valid_only: bool = True,
    ) -> list[Memory]:
        results = [m for m in self.memories.values() if m.user_id == user_id]
        if temporal_level:
            results = [m for m in results if m.temporal_level == temporal_level]
        if min_salience > 0:
            results = [m for m in results if m.effective_salience >= min_salience]
        return results[offset:offset + limit]

    async def update_salience(self, memory_id: UUID, adjustment: float) -> Memory:
        memory = self.memories.get(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")
        updated = memory.with_outcome_adjustment(adjustment)
        self.memories[memory_id] = updated
        return updated

    async def increment_retrieval_count(self, memory_id: UUID) -> None:
        memory = self.memories.get(memory_id)
        if memory:
            self.memories[memory_id] = memory.with_retrieval()

    async def increment_decision_count(self, memory_id: UUID, positive: bool) -> None:
        pass  # Simplified for testing

    async def expire(self, memory_id: UUID) -> None:
        memory = self.memories.get(memory_id)
        if memory:
            # Create expired version
            self.memories[memory_id] = Memory(
                memory_id=memory.memory_id,
                user_id=memory.user_id,
                content=memory.content,
                content_type=memory.content_type,
                temporal_level=memory.temporal_level,
                valid_from=memory.valid_from,
                valid_until=datetime.now(UTC),
                base_salience=memory.base_salience,
                outcome_adjustment=memory.outcome_adjustment,
            )

    async def promote(self, memory_id: UUID, new_level: TemporalLevel) -> Memory:
        memory = self.memories.get(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")
        # Create promoted version (simplified)
        return memory

    async def get_candidates_for_promotion(
        self, user_id: UUID, level: TemporalLevel,
        min_salience: float = 0.7, min_positive_ratio: float = 0.6, limit: int = 50
    ) -> list[Memory]:
        return []

    async def get_expired_candidates(
        self, user_id: UUID, level: TemporalLevel,
        older_than_days: int, limit: int = 100
    ) -> list[Memory]:
        return []


class StubDecisionStorage(IDecisionStorage):
    """In-memory stub for decision storage."""

    def __init__(self):
        self.traces: dict[UUID, DecisionTrace] = {}
        self.salience_updates: list[SalienceUpdate] = []

    async def store_trace(self, trace: DecisionTrace) -> DecisionTrace:
        self.traces[trace.trace_id] = trace
        return trace

    async def get_trace(self, trace_id: UUID) -> Optional[DecisionTrace]:
        return self.traces.get(trace_id)

    async def record_outcome(self, trace_id: UUID, outcome: Outcome) -> DecisionTrace:
        trace = self.traces.get(trace_id)
        if not trace:
            raise ValueError(f"Trace {trace_id} not found")
        # Create updated trace
        updated = DecisionTrace(
            trace_id=trace.trace_id,
            user_id=trace.user_id,
            session_id=trace.session_id,
            memory_ids=trace.memory_ids,
            memory_scores=trace.memory_scores,
            decision_type=trace.decision_type,
            decision_summary=trace.decision_summary,
            confidence=trace.confidence,
            outcome_observed=True,
            outcome_quality=outcome.quality,
            outcome_timestamp=outcome.observed_at,
            outcome_signal=outcome.signal,
        )
        self.traces[trace_id] = updated
        return updated

    async def get_traces_by_user(
        self, user_id: UUID, *, limit: int = 100, offset: int = 0,
        with_outcomes_only: bool = False, decision_type: Optional[str] = None
    ) -> list[DecisionTrace]:
        results = [t for t in self.traces.values() if t.user_id == user_id]
        return results[offset:offset + limit]

    async def get_traces_for_memory(
        self, memory_id: UUID, *, limit: int = 50, with_outcomes_only: bool = True
    ) -> list[DecisionTrace]:
        return [t for t in self.traces.values() if memory_id in t.memory_ids][:limit]

    async def get_pending_outcomes(
        self, user_id: UUID, older_than_hours: int = 24, limit: int = 50
    ) -> list[DecisionTrace]:
        return []

    async def store_salience_update(self, update: SalienceUpdate) -> None:
        self.salience_updates.append(update)

    async def get_salience_updates_for_memory(
        self, memory_id: UUID, limit: int = 50
    ) -> list[SalienceUpdate]:
        return [u for u in self.salience_updates if u.memory_id == memory_id][:limit]


class StubEventPublisher(IEventPublisher):
    """In-memory stub for event publishing."""

    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    async def publish(
        self, event_type: str, payload: dict[str, Any], *, user_id: Optional[str] = None
    ) -> str:
        event_id = f"evt_{len(self.events)}"
        self.events.append((event_type, {**payload, "_event_id": event_id}))
        return event_id

    async def publish_batch(
        self, events: list[tuple[str, dict[str, Any]]], *, user_id: Optional[str] = None
    ) -> list[str]:
        ids = []
        for event_type, payload in events:
            event_id = await self.publish(event_type, payload, user_id=user_id)
            ids.append(event_id)
        return ids

    async def close(self) -> None:
        pass


class StubEventConsumer(IEventConsumer):
    """In-memory stub for event consumption."""

    def __init__(self):
        self.handlers: dict[str, list[EventHandler]] = {}

    async def subscribe(
        self, event_type: str, handler: EventHandler, *, consumer_name: Optional[str] = None
    ) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def subscribe_pattern(
        self, pattern: str, handler: EventHandler, *, consumer_name: Optional[str] = None
    ) -> None:
        pass

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def acknowledge(self, event_id: str) -> None:
        pass

    async def reject(
        self, event_id: str, *, requeue: bool = True, reason: Optional[str] = None
    ) -> None:
        pass


class StubVectorSearch(IVectorSearch):
    """In-memory stub for vector search."""

    def __init__(self):
        self.vectors: dict[UUID, tuple[list[float], dict]] = {}

    async def index(self, id: UUID, embedding: list[float], metadata: dict[str, Any]) -> None:
        self.vectors[id] = (embedding, metadata)

    async def index_batch(self, items: list[tuple[UUID, list[float], dict[str, Any]]]) -> None:
        for id, embedding, metadata in items:
            self.vectors[id] = (embedding, metadata)

    async def search(
        self, query_embedding: list[float], limit: int = 10, filter: Optional[VectorFilter] = None
    ) -> list[VectorSearchResult]:
        # Simple cosine similarity
        results = []
        for id, (embedding, metadata) in self.vectors.items():
            score = self._cosine_similarity(query_embedding, embedding)
            results.append(VectorSearchResult(id=id, score=score, metadata=metadata))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def search_by_id(
        self, id: UUID, limit: int = 10, filter: Optional[VectorFilter] = None
    ) -> list[VectorSearchResult]:
        if id not in self.vectors:
            return []
        embedding, _ = self.vectors[id]
        results = await self.search(embedding, limit + 1, filter)
        return [r for r in results if r.id != id][:limit]

    async def delete(self, id: UUID) -> None:
        self.vectors.pop(id, None)

    async def delete_batch(self, ids: list[UUID]) -> None:
        for id in ids:
            self.vectors.pop(id, None)

    async def get_embedding(self, id: UUID) -> Optional[list[float]]:
        if id in self.vectors:
            return self.vectors[id][0]
        return None

    async def count(self, filter: Optional[VectorFilter] = None) -> int:
        return len(self.vectors)

    async def health_check(self) -> bool:
        return True

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class StubCausalGraph(ICausalGraph):
    """In-memory stub for causal graph."""

    def __init__(self):
        self.nodes: dict[UUID, CausalNode] = {}
        self.edges: list[CausalRelationship] = []

    async def add_node(self, node: CausalNode) -> CausalNode:
        self.nodes[node.node_id] = node
        return node

    async def get_node(self, node_id: UUID) -> Optional[CausalNode]:
        return self.nodes.get(node_id)

    async def get_nodes_by_type(
        self, user_id: UUID, node_type: NodeType, limit: int = 100
    ) -> list[CausalNode]:
        return [n for n in self.nodes.values()
                if n.user_id == user_id and n.node_type == node_type][:limit]

    async def add_edge(
        self, source_id: UUID, target_id: UUID, relationship_type: RelationshipType,
        strength: float = 1.0, confidence: float = 1.0, properties: Optional[dict] = None
    ) -> CausalRelationship:
        edge = CausalRelationship(
            source_id=source_id, target_id=target_id,
            relationship_type=relationship_type,
            strength=strength, confidence=confidence,
            properties=properties or {},
        )
        self.edges.append(edge)
        return edge

    async def get_edge(self, source_id: UUID, target_id: UUID) -> Optional[CausalRelationship]:
        for e in self.edges:
            if e.source_id == source_id and e.target_id == target_id:
                return e
        return None

    async def update_edge_strength(
        self, source_id: UUID, target_id: UUID, new_strength: float
    ) -> CausalRelationship:
        for i, e in enumerate(self.edges):
            if e.source_id == source_id and e.target_id == target_id:
                updated = e.with_updated_strength(new_strength)
                self.edges[i] = updated
                return updated
        raise ValueError(f"Edge {source_id} -> {target_id} not found")

    async def get_causes(
        self, node_id: UUID, min_strength: float = 0.0, limit: int = 50
    ) -> list[tuple[CausalNode, CausalRelationship]]:
        results = []
        for e in self.edges:
            if e.target_id == node_id and e.strength >= min_strength:
                node = self.nodes.get(e.source_id)
                if node:
                    results.append((node, e))
        return results[:limit]

    async def get_effects(
        self, node_id: UUID, min_strength: float = 0.0, limit: int = 50
    ) -> list[tuple[CausalNode, CausalRelationship]]:
        results = []
        for e in self.edges:
            if e.source_id == node_id and e.strength >= min_strength:
                node = self.nodes.get(e.target_id)
                if node:
                    results.append((node, e))
        return results[:limit]

    async def get_neighbors(self, node_id: UUID) -> Optional[CausalNeighbors]:
        node = self.nodes.get(node_id)
        if not node:
            return None
        causes = await self.get_causes(node_id)
        effects = await self.get_effects(node_id)
        return CausalNeighbors(node=node, causes=causes, effects=effects)

    async def find_path(
        self, source_id: UUID, target_id: UUID, max_depth: int = 5
    ) -> Optional[CausalPath]:
        return None  # Simplified

    async def get_memory_influence_on_outcome(
        self, memory_id: UUID, outcome_trace_id: UUID
    ) -> Optional[float]:
        return None

    async def get_strongest_influences(
        self, outcome_trace_id: UUID, limit: int = 10
    ) -> list[tuple[UUID, float]]:
        return []

    async def prune_weak_edges(
        self, user_id: UUID, min_strength: float = 0.1, min_evidence: int = 1
    ) -> int:
        return 0

    async def health_check(self) -> bool:
        return True


class StubScheduler(IBackgroundScheduler):
    """In-memory stub for background scheduler."""

    def __init__(self):
        self.jobs: dict[str, JobInfo] = {}

    async def schedule_interval(
        self, job_id: str, func: JobFunc, interval: timedelta, *,
        name: Optional[str] = None, start_immediately: bool = False,
        kwargs: Optional[dict[str, Any]] = None
    ) -> JobInfo:
        info = JobInfo(
            job_id=job_id, name=name or job_id, status=JobStatus.PENDING,
            next_run=datetime.now(UTC) + interval, last_run=None,
            last_result=None, run_count=0, error_count=0,
        )
        self.jobs[job_id] = info
        return info

    async def schedule_cron(
        self, job_id: str, func: JobFunc, cron_expression: str, *,
        name: Optional[str] = None, timezone: str = "UTC",
        kwargs: Optional[dict[str, Any]] = None
    ) -> JobInfo:
        info = JobInfo(
            job_id=job_id, name=name or job_id, status=JobStatus.PENDING,
            next_run=None, last_run=None, last_result=None, run_count=0, error_count=0,
        )
        self.jobs[job_id] = info
        return info

    async def schedule_once(
        self, job_id: str, func: JobFunc, run_at: datetime, *,
        name: Optional[str] = None, kwargs: Optional[dict[str, Any]] = None
    ) -> JobInfo:
        info = JobInfo(
            job_id=job_id, name=name or job_id, status=JobStatus.PENDING,
            next_run=run_at, last_run=None, last_result=None, run_count=0, error_count=0,
        )
        self.jobs[job_id] = info
        return info

    async def schedule_delayed(
        self, job_id: str, func: JobFunc, delay: timedelta, *,
        name: Optional[str] = None, kwargs: Optional[dict[str, Any]] = None
    ) -> JobInfo:
        return await self.schedule_once(job_id, func, datetime.now(UTC) + delay, name=name, kwargs=kwargs)

    async def cancel(self, job_id: str) -> bool:
        return self.jobs.pop(job_id, None) is not None

    async def pause(self, job_id: str) -> bool:
        return job_id in self.jobs

    async def resume(self, job_id: str) -> bool:
        return job_id in self.jobs

    async def run_now(self, job_id: str) -> bool:
        return job_id in self.jobs

    async def get_job(self, job_id: str) -> Optional[JobInfo]:
        return self.jobs.get(job_id)

    async def list_jobs(self) -> list[JobInfo]:
        return list(self.jobs.values())

    async def get_failed_jobs(self, limit: int = 50) -> list[JobInfo]:
        return []

    async def start(self) -> None:
        pass

    async def shutdown(self, wait: bool = True) -> None:
        pass

    async def health_check(self) -> bool:
        return True
