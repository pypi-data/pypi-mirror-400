"""Causal inference domain models.

These models represent causal relationships between memories, decisions,
and outcomes. They enable:
- Understanding what context led to what decisions
- Attributing outcomes to specific memories
- Counterfactual reasoning ("what if we used different memories?")
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID


class NodeType(Enum):
    """Types of nodes in the causal graph."""

    MEMORY = "memory"
    DECISION = "decision"
    OUTCOME = "outcome"


class RelationshipType(Enum):
    """Types of causal relationships."""

    INFLUENCED = "influenced"  # Memory -> Decision
    LED_TO = "led_to"  # Decision -> Outcome
    CAUSED = "caused"  # Direct causal link (derived)


@dataclass(frozen=True)
class CausalNode:
    """A node in the causal graph.

    Nodes represent entities that participate in causal chains:
    - Memories: Context that influences decisions
    - Decisions: Actions taken based on context
    - Outcomes: Results of decisions
    """

    node_id: UUID
    node_type: NodeType
    user_id: UUID
    properties: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_memory(cls, memory_id: UUID, user_id: UUID, **props) -> "CausalNode":
        """Create a memory node."""
        return cls(
            node_id=memory_id,
            node_type=NodeType.MEMORY,
            user_id=user_id,
            properties=props,
        )

    @classmethod
    def from_decision(cls, trace_id: UUID, user_id: UUID, **props) -> "CausalNode":
        """Create a decision node."""
        return cls(
            node_id=trace_id,
            node_type=NodeType.DECISION,
            user_id=user_id,
            properties=props,
        )

    @classmethod
    def from_outcome(cls, trace_id: UUID, user_id: UUID, **props) -> "CausalNode":
        """Create an outcome node."""
        return cls(
            node_id=trace_id,
            node_type=NodeType.OUTCOME,
            user_id=user_id,
            properties=props,
        )


@dataclass(frozen=True)
class CausalRelationship:
    """A causal relationship between two nodes.

    Relationships capture the causal influence between nodes:
    - strength: How strong is the causal influence (0-1)
    - confidence: How certain are we about this relationship (0-1)
    - evidence_count: How many observations support this relationship
    """

    source_id: UUID
    target_id: UUID
    relationship_type: RelationshipType
    strength: float = 1.0  # 0.0 - 1.0
    confidence: float = 1.0  # 0.0 - 1.0
    evidence_count: int = 1
    properties: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_updated_strength(self, new_strength: float) -> "CausalRelationship":
        """Create new relationship with updated strength."""
        return CausalRelationship(
            source_id=self.source_id,
            target_id=self.target_id,
            relationship_type=self.relationship_type,
            strength=new_strength,
            confidence=self.confidence,
            evidence_count=self.evidence_count + 1,
            properties=self.properties,
            created_at=self.created_at,
        )


@dataclass
class CausalGraph:
    """A causal graph for a user.

    The graph captures all causal relationships between a user's
    memories, decisions, and outcomes. It enables:
    - Forward inference: What outcomes might this context lead to?
    - Backward inference: What context led to this outcome?
    - Counterfactual: What if we had used different context?
    """

    user_id: UUID
    nodes: dict[UUID, CausalNode] = field(default_factory=dict)
    edges: list[CausalRelationship] = field(default_factory=list)

    def add_node(self, node: CausalNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node

    def add_edge(self, edge: CausalRelationship) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)

    def get_influencers(self, node_id: UUID) -> list[CausalRelationship]:
        """Get all relationships where node_id is the target."""
        return [e for e in self.edges if e.target_id == node_id]

    def get_influenced(self, node_id: UUID) -> list[CausalRelationship]:
        """Get all relationships where node_id is the source."""
        return [e for e in self.edges if e.source_id == node_id]

    def get_path(
        self,
        source_id: UUID,
        target_id: UUID,
        max_depth: int = 5,
    ) -> list[CausalRelationship] | None:
        """Find a causal path between two nodes using BFS."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        # BFS to find shortest path
        visited = {source_id}
        queue = [(source_id, [])]

        while queue:
            current, path = queue.pop(0)

            if len(path) >= max_depth:
                continue

            for edge in self.get_influenced(current):
                if edge.target_id == target_id:
                    return path + [edge]

                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge]))

        return None


@dataclass(frozen=True)
class CounterfactualQuery:
    """A counterfactual query for causal analysis.

    Counterfactual queries ask "what if" questions:
    - What if we had used different memories?
    - What if we had made a different decision?
    - What outcome would we expect with this context?
    """

    user_id: UUID
    original_trace_id: UUID
    hypothetical_memory_ids: list[UUID]
    question: str

    # Optional constraints
    decision_type: str | None = None
    min_confidence: float = 0.5


@dataclass
class CounterfactualResult:
    """Result of a counterfactual analysis.

    Provides the predicted outcome and supporting evidence.
    """

    query: CounterfactualQuery
    predicted_outcome_quality: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    similar_historical_count: int
    average_historical_outcome: float
    reasoning: str
    supporting_traces: list[UUID] = field(default_factory=list)

    @property
    def is_positive_prediction(self) -> bool:
        """Check if the prediction is positive."""
        return self.predicted_outcome_quality > 0

    @property
    def is_confident(self) -> bool:
        """Check if prediction confidence meets threshold."""
        return self.confidence >= self.query.min_confidence


@dataclass(frozen=True)
class CausalAttribution:
    """Attribution of an outcome to contributing factors.

    Quantifies how much each memory contributed to an outcome,
    enabling precise salience updates.
    """

    trace_id: UUID
    outcome_quality: float
    attributions: dict[UUID, float]  # memory_id -> contribution (0-1)
    total_attributed: float  # Sum of attributions (should be ~1.0)
    method: str  # "retrieval_score", "causal_path", "shapley"

    def get_attribution(self, memory_id: UUID) -> float:
        """Get attribution for a specific memory."""
        return self.attributions.get(memory_id, 0.0)

    def top_contributors(self, n: int = 5) -> list[tuple[UUID, float]]:
        """Get top N contributing memories."""
        sorted_attrs = sorted(
            self.attributions.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_attrs[:n]
