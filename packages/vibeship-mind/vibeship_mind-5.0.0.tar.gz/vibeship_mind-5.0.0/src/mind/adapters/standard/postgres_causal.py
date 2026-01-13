"""PostgreSQL causal graph adapter using adjacency tables.

This adapter implements ICausalGraph using simple PostgreSQL tables
for storing causal relationships between nodes.

Limitations compared to FalkorDB (Enterprise):
- Graph traversal is limited to a fixed depth
- No native graph algorithms (PageRank, centrality, etc.)
- Multi-hop queries may be slower

For most single-user use cases, this is sufficient.
"""

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

import asyncpg

from ...core.causal.models import (
    CausalNode,
    CausalRelationship,
    NodeType,
    RelationshipType,
)
from ...ports.graphs import ICausalGraph, CausalPath, CausalNeighbors


class PostgresCausalGraph(ICausalGraph):
    """PostgreSQL implementation of causal graph using adjacency tables.

    Uses two tables:
    - causal_nodes: Stores node information
    - causal_edges: Stores relationships between nodes
    """

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with a connection pool.

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool

    # =========================================================================
    # Node Operations
    # =========================================================================

    async def add_node(self, node: CausalNode) -> CausalNode:
        """Add a node to the causal graph."""
        import json

        await self.pool.execute(
            """
            INSERT INTO causal_nodes (
                node_id, node_type, user_id, properties, created_at
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (node_id) DO NOTHING
            """,
            node.node_id,
            node.node_type.value,
            node.user_id,
            json.dumps(node.properties),
            node.created_at,
        )

        return node

    async def get_node(self, node_id: UUID) -> Optional[CausalNode]:
        """Get a node by ID."""
        row = await self.pool.fetchrow(
            "SELECT * FROM causal_nodes WHERE node_id = $1",
            node_id,
        )

        if row is None:
            return None

        return self._row_to_node(row)

    async def get_nodes_by_type(
        self,
        user_id: UUID,
        node_type: NodeType,
        limit: int = 100,
    ) -> list[CausalNode]:
        """Get nodes of a specific type for a user."""
        rows = await self.pool.fetch(
            """
            SELECT * FROM causal_nodes
            WHERE user_id = $1 AND node_type = $2
            ORDER BY created_at DESC
            LIMIT $3
            """,
            user_id,
            node_type.value,
            limit,
        )

        return [self._row_to_node(row) for row in rows]

    # =========================================================================
    # Edge Operations
    # =========================================================================

    async def add_edge(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: RelationshipType,
        strength: float = 1.0,
        confidence: float = 1.0,
        properties: Optional[dict] = None,
    ) -> CausalRelationship:
        """Add a causal edge between two nodes."""
        import json

        now = datetime.now(UTC)

        await self.pool.execute(
            """
            INSERT INTO causal_edges (
                source_id, target_id, relationship_type,
                strength, confidence, evidence_count,
                properties, created_at
            ) VALUES ($1, $2, $3, $4, $5, 1, $6, $7)
            ON CONFLICT (source_id, target_id) DO UPDATE SET
                strength = $4,
                confidence = $5,
                evidence_count = causal_edges.evidence_count + 1,
                properties = $6
            """,
            source_id,
            target_id,
            relationship_type.value,
            strength,
            confidence,
            json.dumps(properties or {}),
            now,
        )

        return CausalRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength,
            confidence=confidence,
            evidence_count=1,
            properties=properties or {},
            created_at=now,
        )

    async def get_edge(
        self,
        source_id: UUID,
        target_id: UUID,
    ) -> Optional[CausalRelationship]:
        """Get the edge between two nodes."""
        row = await self.pool.fetchrow(
            """
            SELECT * FROM causal_edges
            WHERE source_id = $1 AND target_id = $2
            """,
            source_id,
            target_id,
        )

        if row is None:
            return None

        return self._row_to_edge(row)

    async def update_edge_strength(
        self,
        source_id: UUID,
        target_id: UUID,
        new_strength: float,
    ) -> CausalRelationship:
        """Update the strength of an existing edge."""
        row = await self.pool.fetchrow(
            """
            UPDATE causal_edges
            SET strength = $3,
                evidence_count = evidence_count + 1
            WHERE source_id = $1 AND target_id = $2
            RETURNING *
            """,
            source_id,
            target_id,
            new_strength,
        )

        if row is None:
            raise ValueError(f"Edge {source_id} -> {target_id} not found")

        return self._row_to_edge(row)

    # =========================================================================
    # Traversal Operations
    # =========================================================================

    async def get_causes(
        self,
        node_id: UUID,
        min_strength: float = 0.0,
        limit: int = 50,
    ) -> list[tuple[CausalNode, CausalRelationship]]:
        """Get nodes that causally influence this node (incoming edges)."""
        rows = await self.pool.fetch(
            """
            SELECT
                n.*,
                e.source_id as e_source_id,
                e.target_id as e_target_id,
                e.relationship_type as e_relationship_type,
                e.strength as e_strength,
                e.confidence as e_confidence,
                e.evidence_count as e_evidence_count,
                e.properties as e_properties,
                e.created_at as e_created_at
            FROM causal_edges e
            JOIN causal_nodes n ON e.source_id = n.node_id
            WHERE e.target_id = $1 AND e.strength >= $2
            ORDER BY e.strength DESC
            LIMIT $3
            """,
            node_id,
            min_strength,
            limit,
        )

        return [
            (self._row_to_node(row), self._row_to_edge_from_join(row))
            for row in rows
        ]

    async def get_effects(
        self,
        node_id: UUID,
        min_strength: float = 0.0,
        limit: int = 50,
    ) -> list[tuple[CausalNode, CausalRelationship]]:
        """Get nodes causally influenced by this node (outgoing edges)."""
        rows = await self.pool.fetch(
            """
            SELECT
                n.*,
                e.source_id as e_source_id,
                e.target_id as e_target_id,
                e.relationship_type as e_relationship_type,
                e.strength as e_strength,
                e.confidence as e_confidence,
                e.evidence_count as e_evidence_count,
                e.properties as e_properties,
                e.created_at as e_created_at
            FROM causal_edges e
            JOIN causal_nodes n ON e.target_id = n.node_id
            WHERE e.source_id = $1 AND e.strength >= $2
            ORDER BY e.strength DESC
            LIMIT $3
            """,
            node_id,
            min_strength,
            limit,
        )

        return [
            (self._row_to_node(row), self._row_to_edge_from_join(row))
            for row in rows
        ]

    async def get_neighbors(self, node_id: UUID) -> Optional[CausalNeighbors]:
        """Get all neighbors of a node (both causes and effects)."""
        node = await self.get_node(node_id)
        if node is None:
            return None

        causes = await self.get_causes(node_id)
        effects = await self.get_effects(node_id)

        return CausalNeighbors(
            node=node,
            causes=causes,
            effects=effects,
        )

    async def find_path(
        self,
        source_id: UUID,
        target_id: UUID,
        max_depth: int = 5,
    ) -> Optional[CausalPath]:
        """Find a causal path between two nodes using BFS.

        Limited to max_depth hops for performance.
        """
        if source_id == target_id:
            node = await self.get_node(source_id)
            if node:
                return CausalPath(nodes=[node], edges=[], total_strength=1.0)
            return None

        # BFS with depth limit
        visited = {source_id}
        queue: list[tuple[UUID, list[UUID], list[CausalRelationship]]] = [
            (source_id, [source_id], [])
        ]

        while queue:
            current_id, path_ids, path_edges = queue.pop(0)

            if len(path_edges) >= max_depth:
                continue

            # Get outgoing edges
            effects = await self.get_effects(current_id, min_strength=0.1)

            for effect_node, edge in effects:
                if effect_node.node_id == target_id:
                    # Found the target!
                    new_path_ids = path_ids + [target_id]
                    new_edges = path_edges + [edge]

                    # Fetch all nodes in path
                    nodes = []
                    for nid in new_path_ids:
                        node = await self.get_node(nid)
                        if node:
                            nodes.append(node)

                    # Calculate total strength (product)
                    total_strength = 1.0
                    for e in new_edges:
                        total_strength *= e.strength

                    return CausalPath(
                        nodes=nodes,
                        edges=new_edges,
                        total_strength=total_strength,
                    )

                if effect_node.node_id not in visited:
                    visited.add(effect_node.node_id)
                    queue.append((
                        effect_node.node_id,
                        path_ids + [effect_node.node_id],
                        path_edges + [edge],
                    ))

        return None  # No path found

    # =========================================================================
    # Causal Analysis
    # =========================================================================

    async def get_memory_influence_on_outcome(
        self,
        memory_id: UUID,
        outcome_trace_id: UUID,
    ) -> Optional[float]:
        """Calculate how much a memory influenced an outcome."""
        path = await self.find_path(memory_id, outcome_trace_id, max_depth=3)

        if path is None:
            return None

        return path.total_strength

    async def get_strongest_influences(
        self,
        outcome_trace_id: UUID,
        limit: int = 10,
    ) -> list[tuple[UUID, float]]:
        """Get memories with strongest influence on an outcome.

        For Standard tier, this looks at direct edges only (1-hop).
        """
        rows = await self.pool.fetch(
            """
            SELECT source_id, strength
            FROM causal_edges
            WHERE target_id = $1
              AND relationship_type = 'influenced'
            ORDER BY strength DESC
            LIMIT $2
            """,
            outcome_trace_id,
            limit,
        )

        return [(row["source_id"], row["strength"]) for row in rows]

    # =========================================================================
    # Maintenance
    # =========================================================================

    async def prune_weak_edges(
        self,
        user_id: UUID,
        min_strength: float = 0.1,
        min_evidence: int = 1,
    ) -> int:
        """Remove weak edges from the graph."""
        result = await self.pool.execute(
            """
            DELETE FROM causal_edges
            WHERE source_id IN (
                SELECT node_id FROM causal_nodes WHERE user_id = $1
            )
            AND (strength < $2 OR evidence_count < $3)
            """,
            user_id,
            min_strength,
            min_evidence,
        )

        # Parse "DELETE X" to get count
        try:
            return int(result.split()[-1])
        except (ValueError, IndexError):
            return 0

    async def health_check(self) -> bool:
        """Check if the causal graph tables exist."""
        try:
            result = await self.pool.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'causal_nodes'
                )
                """
            )
            return bool(result)
        except Exception:
            return False

    # =========================================================================
    # Helpers
    # =========================================================================

    def _row_to_node(self, row: asyncpg.Record) -> CausalNode:
        """Convert a database row to a CausalNode."""
        import json

        properties = row["properties"]
        if isinstance(properties, str):
            properties = json.loads(properties)

        return CausalNode(
            node_id=row["node_id"],
            node_type=NodeType(row["node_type"]),
            user_id=row["user_id"],
            properties=properties or {},
            created_at=row["created_at"],
        )

    def _row_to_edge(self, row: asyncpg.Record) -> CausalRelationship:
        """Convert a database row to a CausalRelationship."""
        import json

        properties = row["properties"]
        if isinstance(properties, str):
            properties = json.loads(properties)

        return CausalRelationship(
            source_id=row["source_id"],
            target_id=row["target_id"],
            relationship_type=RelationshipType(row["relationship_type"]),
            strength=row["strength"],
            confidence=row["confidence"],
            evidence_count=row["evidence_count"],
            properties=properties or {},
            created_at=row["created_at"],
        )

    def _row_to_edge_from_join(self, row: asyncpg.Record) -> CausalRelationship:
        """Convert a joined row (with e_ prefix) to CausalRelationship."""
        import json

        properties = row["e_properties"]
        if isinstance(properties, str):
            properties = json.loads(properties)

        return CausalRelationship(
            source_id=row["e_source_id"],
            target_id=row["e_target_id"],
            relationship_type=RelationshipType(row["e_relationship_type"]),
            strength=row["e_strength"],
            confidence=row["e_confidence"],
            evidence_count=row["e_evidence_count"],
            properties=properties or {},
            created_at=row["e_created_at"],
        )
