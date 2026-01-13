"""Causal graph port interface for causal relationships.

This port abstracts causal graph storage and traversal:
- Standard: PostgreSQL adjacency tables (limited traversal)
- Enterprise: FalkorDB (full graph traversal, Cypher queries)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ..core.causal.models import (
    CausalNode,
    CausalRelationship,
    NodeType,
    RelationshipType,
)


@dataclass
class CausalPath:
    """A path through the causal graph."""

    nodes: list[CausalNode]
    edges: list[CausalRelationship]
    total_strength: float  # Product of edge strengths

    @property
    def length(self) -> int:
        """Number of edges in the path."""
        return len(self.edges)

    @property
    def source(self) -> CausalNode:
        """First node in the path."""
        return self.nodes[0]

    @property
    def target(self) -> CausalNode:
        """Last node in the path."""
        return self.nodes[-1]


@dataclass
class CausalNeighbors:
    """Neighbors of a node in the causal graph."""

    node: CausalNode
    causes: list[tuple[CausalNode, CausalRelationship]]  # Incoming edges
    effects: list[tuple[CausalNode, CausalRelationship]]  # Outgoing edges


class ICausalGraph(ABC):
    """Port for causal graph operations.

    The causal graph tracks relationships between:
    - Memories (context that influences decisions)
    - Decisions (actions taken based on context)
    - Outcomes (results of decisions)

    Implementations:
        - PostgresCausalGraph (Standard): Adjacency tables, limited depth
        - FalkorDBCausalGraph (Enterprise): Full graph DB, unlimited depth
    """

    # =========================================================================
    # Node Operations
    # =========================================================================

    @abstractmethod
    async def add_node(self, node: CausalNode) -> CausalNode:
        """Add a node to the causal graph.

        Args:
            node: The node to add

        Returns:
            The added node (may have server-assigned fields)

        Note:
            If node already exists, this is a no-op.
        """
        pass

    @abstractmethod
    async def get_node(self, node_id: UUID) -> Optional[CausalNode]:
        """Get a node by ID.

        Args:
            node_id: The node's unique identifier

        Returns:
            The node if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_nodes_by_type(
        self,
        user_id: UUID,
        node_type: NodeType,
        limit: int = 100,
    ) -> list[CausalNode]:
        """Get nodes of a specific type for a user.

        Args:
            user_id: The user's identifier
            node_type: Type of nodes to retrieve
            limit: Maximum nodes to return

        Returns:
            List of matching nodes
        """
        pass

    # =========================================================================
    # Edge Operations
    # =========================================================================

    @abstractmethod
    async def add_edge(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: RelationshipType,
        strength: float = 1.0,
        confidence: float = 1.0,
        properties: Optional[dict] = None,
    ) -> CausalRelationship:
        """Add a causal edge between two nodes.

        Args:
            source_id: ID of the source node (cause)
            target_id: ID of the target node (effect)
            relationship_type: Type of causal relationship
            strength: Strength of the causal influence (0.0 - 1.0)
            confidence: Confidence in this relationship (0.0 - 1.0)
            properties: Optional additional properties

        Returns:
            The created relationship

        Note:
            If edge already exists, strength and confidence are updated.
        """
        pass

    @abstractmethod
    async def get_edge(
        self,
        source_id: UUID,
        target_id: UUID,
    ) -> Optional[CausalRelationship]:
        """Get the edge between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            The relationship if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_edge_strength(
        self,
        source_id: UUID,
        target_id: UUID,
        new_strength: float,
    ) -> CausalRelationship:
        """Update the strength of an existing edge.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            new_strength: New strength value

        Returns:
            The updated relationship

        Raises:
            ValueError: If edge doesn't exist
        """
        pass

    # =========================================================================
    # Traversal Operations
    # =========================================================================

    @abstractmethod
    async def get_causes(
        self,
        node_id: UUID,
        min_strength: float = 0.0,
        limit: int = 50,
    ) -> list[tuple[CausalNode, CausalRelationship]]:
        """Get nodes that causally influence this node (incoming edges).

        Args:
            node_id: The target node
            min_strength: Minimum edge strength to include
            limit: Maximum results

        Returns:
            List of (cause_node, relationship) tuples
        """
        pass

    @abstractmethod
    async def get_effects(
        self,
        node_id: UUID,
        min_strength: float = 0.0,
        limit: int = 50,
    ) -> list[tuple[CausalNode, CausalRelationship]]:
        """Get nodes causally influenced by this node (outgoing edges).

        Args:
            node_id: The source node
            min_strength: Minimum edge strength to include
            limit: Maximum results

        Returns:
            List of (effect_node, relationship) tuples
        """
        pass

    @abstractmethod
    async def get_neighbors(self, node_id: UUID) -> Optional[CausalNeighbors]:
        """Get all neighbors of a node (both causes and effects).

        Args:
            node_id: The node to get neighbors for

        Returns:
            CausalNeighbors with causes and effects, None if node not found
        """
        pass

    @abstractmethod
    async def find_path(
        self,
        source_id: UUID,
        target_id: UUID,
        max_depth: int = 5,
    ) -> Optional[CausalPath]:
        """Find a causal path between two nodes.

        Args:
            source_id: Starting node
            target_id: Ending node
            max_depth: Maximum path length

        Returns:
            The shortest path if one exists, None otherwise

        Note:
            Standard tier uses BFS with depth limit.
            Enterprise tier uses graph database algorithms.
        """
        pass

    # =========================================================================
    # Causal Analysis (Advanced - Enterprise may have richer implementations)
    # =========================================================================

    @abstractmethod
    async def get_memory_influence_on_outcome(
        self,
        memory_id: UUID,
        outcome_trace_id: UUID,
    ) -> Optional[float]:
        """Calculate how much a memory influenced an outcome.

        Args:
            memory_id: The memory node ID
            outcome_trace_id: The outcome/decision trace ID

        Returns:
            Influence score (0.0 - 1.0) if path exists, None otherwise

        Note:
            Standard tier: Simple path strength product
            Enterprise tier: Can use Shapley values, graph centrality
        """
        pass

    @abstractmethod
    async def get_strongest_influences(
        self,
        outcome_trace_id: UUID,
        limit: int = 10,
    ) -> list[tuple[UUID, float]]:
        """Get memories with strongest influence on an outcome.

        Args:
            outcome_trace_id: The outcome to analyze
            limit: Maximum memories to return

        Returns:
            List of (memory_id, influence_score) tuples
        """
        pass

    # =========================================================================
    # Maintenance
    # =========================================================================

    @abstractmethod
    async def prune_weak_edges(
        self,
        user_id: UUID,
        min_strength: float = 0.1,
        min_evidence: int = 1,
    ) -> int:
        """Remove weak edges from the graph.

        Args:
            user_id: User whose graph to prune
            min_strength: Edges below this are removed
            min_evidence: Edges with less evidence are removed

        Returns:
            Number of edges removed
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the causal graph backend is healthy.

        Returns:
            True if healthy, False otherwise
        """
        pass
