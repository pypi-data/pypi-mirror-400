"""FalkorDB repository for causal graph operations.

This repository provides graph-based operations for:
- Storing causal relationships between memories and decisions
- Querying causal paths (what led to what)
- Counterfactual analysis (what if different memories were used)
- Attribution (which memories contributed to outcomes)
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import structlog
from falkordb import FalkorDB

from mind.core.errors import ErrorCode, MindError, Result
from mind.observability.tracing import get_tracer

logger = structlog.get_logger()

# Tracer for causal graph operations
_tracer = get_tracer("mind.causal")

GRAPH_NAME = "mind_causal"


@dataclass
class CausalEdge:
    """A causal relationship between nodes."""

    source_id: UUID
    target_id: UUID
    relationship: str  # INFLUENCED, CAUSED, LED_TO
    strength: float  # 0.0 - 1.0
    context: dict
    created_at: datetime


@dataclass
class CausalPath:
    """A path through the causal graph."""

    nodes: list[dict]  # List of node properties
    edges: list[CausalEdge]
    total_strength: float  # Product of edge strengths


@dataclass
class Attribution:
    """Attribution of an outcome to a memory."""

    memory_id: UUID
    outcome_trace_id: UUID
    contribution: float  # 0.0 - 1.0
    path_count: int  # Number of causal paths
    average_path_length: float


class CausalGraphRepository:
    """Repository for causal graph operations.

    The causal graph represents:
    - Memory -> Decision: INFLUENCED relationship
    - Decision -> Outcome: LED_TO relationship
    - Memory -> Outcome: CAUSED relationship (derived)

    This enables answering questions like:
    - Which memories led to good outcomes?
    - What decisions were influenced by a specific memory?
    - What would have happened with different context?
    """

    def __init__(self, client: FalkorDB, graph_name: str = GRAPH_NAME):
        self._client = client
        self._graph_name = graph_name
        self._graph = client.select_graph(graph_name)

    async def add_memory_node(
        self,
        memory_id: UUID,
        user_id: UUID,
        content_hash: str,
        temporal_level: int,
        salience: float,
    ) -> Result[None]:
        """Add a memory node to the causal graph.

        Args:
            memory_id: Unique memory identifier
            user_id: User who owns the memory
            content_hash: Hash of content (no PII in graph)
            temporal_level: Temporal hierarchy level
            salience: Current effective salience

        Returns:
            Result indicating success or failure
        """
        try:
            query = """
            MERGE (m:Memory {memory_id: $memory_id})
            ON CREATE SET
                m.user_id = $user_id,
                m.content_hash = $content_hash,
                m.temporal_level = $temporal_level,
                m.salience = $salience,
                m.created_at = $created_at
            ON MATCH SET
                m.salience = $salience
            """
            self._graph.query(
                query,
                {
                    "memory_id": str(memory_id),
                    "user_id": str(user_id),
                    "content_hash": content_hash,
                    "temporal_level": temporal_level,
                    "salience": salience,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )

            logger.debug(
                "falkordb_memory_added",
                memory_id=str(memory_id),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "falkordb_memory_add_failed",
                memory_id=str(memory_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to add memory node: {e}",
                    context={"memory_id": str(memory_id)},
                )
            )

    async def add_decision_node(
        self,
        trace_id: UUID,
        user_id: UUID,
        decision_type: str,
        confidence: float,
    ) -> Result[None]:
        """Add a decision node to the causal graph."""
        try:
            query = """
            MERGE (d:Decision {trace_id: $trace_id})
            ON CREATE SET
                d.user_id = $user_id,
                d.decision_type = $decision_type,
                d.confidence = $confidence,
                d.created_at = $created_at
            """
            self._graph.query(
                query,
                {
                    "trace_id": str(trace_id),
                    "user_id": str(user_id),
                    "decision_type": decision_type,
                    "confidence": confidence,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )

            logger.debug(
                "falkordb_decision_added",
                trace_id=str(trace_id),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "falkordb_decision_add_failed",
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to add decision node: {e}",
                    context={"trace_id": str(trace_id)},
                )
            )

    async def add_outcome_node(
        self,
        trace_id: UUID,
        quality: float,
        signal: str,
    ) -> Result[None]:
        """Add an outcome node to the causal graph."""
        try:
            query = """
            MERGE (o:Outcome {trace_id: $trace_id})
            ON CREATE SET
                o.quality = $quality,
                o.signal = $signal,
                o.created_at = $created_at
            ON MATCH SET
                o.quality = $quality,
                o.signal = $signal
            """
            self._graph.query(
                query,
                {
                    "trace_id": str(trace_id),
                    "quality": quality,
                    "signal": signal,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )

            logger.debug(
                "falkordb_outcome_added",
                trace_id=str(trace_id),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "falkordb_outcome_add_failed",
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to add outcome node: {e}",
                    context={"trace_id": str(trace_id)},
                )
            )

    async def link_memory_to_decision(
        self,
        memory_id: UUID,
        trace_id: UUID,
        influence_score: float,
        rank: int,
    ) -> Result[None]:
        """Create INFLUENCED relationship between memory and decision.

        Args:
            memory_id: The memory that influenced the decision
            trace_id: The decision trace
            influence_score: How much the memory influenced (0-1)
            rank: Retrieval rank of the memory

        Returns:
            Result indicating success or failure
        """
        try:
            query = """
            MATCH (m:Memory {memory_id: $memory_id})
            MATCH (d:Decision {trace_id: $trace_id})
            MERGE (m)-[r:INFLUENCED]->(d)
            SET r.score = $score,
                r.rank = $rank,
                r.created_at = $created_at
            """
            self._graph.query(
                query,
                {
                    "memory_id": str(memory_id),
                    "trace_id": str(trace_id),
                    "score": influence_score,
                    "rank": rank,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )

            logger.debug(
                "falkordb_influence_linked",
                memory_id=str(memory_id),
                trace_id=str(trace_id),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "falkordb_link_failed",
                memory_id=str(memory_id),
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to link memory to decision: {e}",
                )
            )

    async def link_decision_to_outcome(
        self,
        trace_id: UUID,
    ) -> Result[None]:
        """Create LED_TO relationship between decision and outcome."""
        try:
            query = """
            MATCH (d:Decision {trace_id: $trace_id})
            MATCH (o:Outcome {trace_id: $trace_id})
            MERGE (d)-[r:LED_TO]->(o)
            SET r.created_at = $created_at
            """
            self._graph.query(
                query,
                {
                    "trace_id": str(trace_id),
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )

            logger.debug(
                "falkordb_outcome_linked",
                trace_id=str(trace_id),
            )

            return Result.ok(None)

        except Exception as e:
            logger.error(
                "falkordb_outcome_link_failed",
                trace_id=str(trace_id),
                error=str(e),
            )
            return Result.err(
                MindError(
                    code=ErrorCode.DATABASE_ERROR,
                    message=f"Failed to link decision to outcome: {e}",
                )
            )

    async def get_memory_outcomes(
        self,
        memory_id: UUID,
        limit: int = 100,
    ) -> Result[list[dict]]:
        """Get all outcomes influenced by a memory.

        Traverses: Memory -[INFLUENCED]-> Decision -[LED_TO]-> Outcome

        Args:
            memory_id: Memory to trace outcomes for
            limit: Maximum outcomes to return

        Returns:
            List of outcome dictionaries with quality scores
        """
        with _tracer.start_as_current_span("get_memory_outcomes") as span:
            span.set_attribute("memory_id", str(memory_id))
            span.set_attribute("limit", limit)

            try:
                query = """
                MATCH (m:Memory {memory_id: $memory_id})
                      -[i:INFLUENCED]->(d:Decision)
                      -[l:LED_TO]->(o:Outcome)
                RETURN d.trace_id as trace_id,
                       d.decision_type as decision_type,
                       i.score as influence_score,
                       o.quality as outcome_quality,
                       o.signal as outcome_signal
                ORDER BY o.created_at DESC
                LIMIT $limit
                """

                with _tracer.start_as_current_span("falkordb_query") as query_span:
                    query_span.set_attribute("query_type", "memory_outcomes")
                    result = self._graph.query(
                        query,
                        {
                            "memory_id": str(memory_id),
                            "limit": limit,
                        },
                    )

                outcomes = []
                for row in result.result_set:
                    outcomes.append(
                        {
                            "trace_id": row[0],
                            "decision_type": row[1],
                            "influence_score": row[2],
                            "outcome_quality": row[3],
                            "outcome_signal": row[4],
                        }
                    )

                span.set_attribute("outcome_count", len(outcomes))

                logger.debug(
                    "falkordb_outcomes_retrieved",
                    memory_id=str(memory_id),
                    count=len(outcomes),
                )

                return Result.ok(outcomes)

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "falkordb_outcomes_query_failed",
                    memory_id=str(memory_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Failed to query memory outcomes: {e}",
                    )
                )

    async def get_causal_attribution(
        self,
        trace_id: UUID,
    ) -> Result[list[Attribution]]:
        """Get causal attribution for an outcome.

        Returns which memories contributed to the outcome and how much.

        Args:
            trace_id: The decision/outcome trace

        Returns:
            List of attributions for each contributing memory
        """
        with _tracer.start_as_current_span("get_causal_attribution") as span:
            span.set_attribute("trace_id", str(trace_id))

            try:
                query = """
                MATCH (m:Memory)-[i:INFLUENCED]->(d:Decision {trace_id: $trace_id})
                      -[l:LED_TO]->(o:Outcome)
                RETURN m.memory_id as memory_id,
                       i.score as influence_score,
                       o.quality as outcome_quality
                """

                with _tracer.start_as_current_span("falkordb_query") as query_span:
                    query_span.set_attribute("query_type", "causal_attribution")
                    result = self._graph.query(
                        query,
                        {"trace_id": str(trace_id)},
                    )

                attributions = []
                for row in result.result_set:
                    memory_id = UUID(row[0])
                    influence_score = row[1] or 0.0

                    attributions.append(
                        Attribution(
                            memory_id=memory_id,
                            outcome_trace_id=trace_id,
                            contribution=influence_score,
                            path_count=1,  # Direct path
                            average_path_length=2.0,  # Memory -> Decision -> Outcome
                        )
                    )

                span.set_attribute("attribution_count", len(attributions))

                logger.debug(
                    "falkordb_attribution_retrieved",
                    trace_id=str(trace_id),
                    count=len(attributions),
                )

                return Result.ok(attributions)

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "falkordb_attribution_query_failed",
                    trace_id=str(trace_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Failed to query causal attribution: {e}",
                    )
                )

    async def get_memory_success_rate(
        self,
        memory_id: UUID,
    ) -> Result[dict]:
        """Calculate success rate for a memory.

        Returns statistics about how often this memory led to positive outcomes.

        Args:
            memory_id: The memory to analyze

        Returns:
            Dict with total_outcomes, positive_outcomes, success_rate
        """
        with _tracer.start_as_current_span("get_memory_success_rate") as span:
            span.set_attribute("memory_id", str(memory_id))

            try:
                query = """
                MATCH (m:Memory {memory_id: $memory_id})
                      -[i:INFLUENCED]->(d:Decision)
                      -[l:LED_TO]->(o:Outcome)
                RETURN count(o) as total,
                       sum(CASE WHEN o.quality > 0 THEN 1 ELSE 0 END) as positive,
                       avg(o.quality) as avg_quality
                """

                with _tracer.start_as_current_span("falkordb_query") as query_span:
                    query_span.set_attribute("query_type", "success_rate")
                    result = self._graph.query(
                        query,
                        {"memory_id": str(memory_id)},
                    )

                if result.result_set:
                    row = result.result_set[0]
                    total = row[0] or 0
                    positive = row[1] or 0
                    avg_quality = row[2] or 0.0

                    success_rate = positive / total if total > 0 else 0.0

                    span.set_attribute("total_outcomes", total)
                    span.set_attribute("success_rate", success_rate)

                    return Result.ok(
                        {
                            "memory_id": str(memory_id),
                            "total_outcomes": total,
                            "positive_outcomes": positive,
                            "success_rate": success_rate,
                            "average_quality": avg_quality,
                        }
                    )

                span.set_attribute("total_outcomes", 0)
                return Result.ok(
                    {
                        "memory_id": str(memory_id),
                        "total_outcomes": 0,
                        "positive_outcomes": 0,
                        "success_rate": 0.0,
                        "average_quality": 0.0,
                    }
                )

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "falkordb_success_rate_failed",
                    memory_id=str(memory_id),
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Failed to calculate success rate: {e}",
                    )
                )

    async def find_similar_outcomes(
        self,
        memory_ids: list[UUID],
        limit: int = 10,
    ) -> Result[list[dict]]:
        """Find historical decisions with similar context.

        Given a set of memories, find past decisions that used similar memories
        and what outcomes they had. Useful for prediction.

        Args:
            memory_ids: Current context memories
            limit: Maximum results

        Returns:
            List of similar past decisions with outcomes
        """
        with _tracer.start_as_current_span("find_similar_outcomes") as span:
            span.set_attribute("memory_count", len(memory_ids))
            span.set_attribute("limit", limit)

            try:
                query = """
                MATCH (m:Memory)-[i:INFLUENCED]->(d:Decision)-[l:LED_TO]->(o:Outcome)
                WHERE m.memory_id IN $memory_ids
                WITH d, o, count(m) as overlap_count, collect(i.score) as scores
                WHERE overlap_count >= 2
                RETURN d.trace_id as trace_id,
                       d.decision_type as decision_type,
                       overlap_count,
                       reduce(s = 0.0, x IN scores | s + x) as total_score,
                       o.quality as outcome_quality
                ORDER BY overlap_count DESC, total_score DESC
                LIMIT $limit
                """

                with _tracer.start_as_current_span("falkordb_query") as query_span:
                    query_span.set_attribute("query_type", "similar_outcomes")
                    result = self._graph.query(
                        query,
                        {
                            "memory_ids": [str(mid) for mid in memory_ids],
                            "limit": limit,
                        },
                    )

                similar = []
                for row in result.result_set:
                    similar.append(
                        {
                            "trace_id": row[0],
                            "decision_type": row[1],
                            "overlap_count": row[2],
                            "total_score": row[3],
                            "outcome_quality": row[4],
                        }
                    )

                span.set_attribute("similar_count", len(similar))

                return Result.ok(similar)

            except Exception as e:
                span.record_exception(e)
                logger.error(
                    "falkordb_similar_outcomes_failed",
                    error=str(e),
                )
                return Result.err(
                    MindError(
                        code=ErrorCode.DATABASE_ERROR,
                        message=f"Failed to find similar outcomes: {e}",
                    )
                )
