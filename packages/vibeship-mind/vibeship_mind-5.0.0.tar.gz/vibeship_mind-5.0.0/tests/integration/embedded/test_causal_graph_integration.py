"""Integration tests for PostgreSQL causal graph adapter (Embedded).

These tests verify PostgresCausalGraph works correctly against
an embedded PostgreSQL database.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.integration.embedded.conftest import requires_embedded_pg


pytestmark = [pytest.mark.integration, requires_embedded_pg]


class TestPostgresCausalGraphEmbedded:
    """Integration tests for PostgresCausalGraph using embedded PostgreSQL."""

    @pytest_asyncio.fixture
    async def causal_graph(self, clean_db):
        """Create a PostgresCausalGraph instance."""
        from mind.adapters.standard.postgres_causal import PostgresCausalGraph
        return PostgresCausalGraph(pool=clean_db)

    @pytest.mark.asyncio
    async def test_add_and_get_node(self, causal_graph, test_user):
        """Test adding and retrieving a causal node."""
        from mind.core.causal.models import CausalNode, NodeType

        node = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={"content_type": "preference"},
            created_at=datetime.now(UTC),
        )

        saved = await causal_graph.add_node(node)

        assert saved.node_id == node.node_id

        retrieved = await causal_graph.get_node(node.node_id)

        assert retrieved is not None
        assert retrieved.node_id == node.node_id
        assert retrieved.node_type == NodeType.MEMORY
        assert retrieved.properties == {"content_type": "preference"}

    @pytest.mark.asyncio
    async def test_add_edge_between_nodes(self, causal_graph, test_user):
        """Test adding an edge between two nodes."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create two nodes
        source = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        target = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.DECISION,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )

        await causal_graph.add_node(source)
        await causal_graph.add_node(target)

        # Add edge
        edge = await causal_graph.add_edge(
            source_id=source.node_id,
            target_id=target.node_id,
            relationship_type=RelationshipType.INFLUENCED,
            strength=0.8,
            confidence=0.9,
        )

        assert edge.source_id == source.node_id
        assert edge.target_id == target.node_id
        assert edge.strength == 0.8
        assert edge.confidence == 0.9

    @pytest.mark.asyncio
    async def test_get_edge(self, causal_graph, test_user):
        """Test retrieving an edge."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        source = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        target = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.OUTCOME,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )

        await causal_graph.add_node(source)
        await causal_graph.add_node(target)
        await causal_graph.add_edge(
            source.node_id, target.node_id,
            RelationshipType.LED_TO, 0.7, 0.85
        )

        edge = await causal_graph.get_edge(source.node_id, target.node_id)

        assert edge is not None
        assert edge.strength == 0.7
        assert edge.confidence == 0.85

    @pytest.mark.asyncio
    async def test_update_edge_strength(self, causal_graph, test_user):
        """Test updating edge strength."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        source = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        target = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.DECISION,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )

        await causal_graph.add_node(source)
        await causal_graph.add_node(target)
        await causal_graph.add_edge(
            source.node_id, target.node_id,
            RelationshipType.INFLUENCED, 0.5, 0.5
        )

        # Update strength
        updated = await causal_graph.update_edge_strength(
            source.node_id, target.node_id,
            new_strength=0.9,
        )

        assert updated.strength == 0.9

        # Verify persistence
        edge = await causal_graph.get_edge(source.node_id, target.node_id)
        assert edge.strength == 0.9

    @pytest.mark.asyncio
    async def test_get_causes(self, causal_graph, test_user):
        """Test getting causes (incoming edges) of a node."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create target node
        target = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.DECISION,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(target)

        # Create multiple cause nodes
        causes = []
        for i in range(3):
            cause = CausalNode(
                node_id=uuid4(),
                node_type=NodeType.MEMORY,
                user_id=test_user,
                properties={"index": i},
                created_at=datetime.now(UTC),
            )
            await causal_graph.add_node(cause)
            await causal_graph.add_edge(
                cause.node_id, target.node_id,
                RelationshipType.INFLUENCED,
                strength=0.5 + (i * 0.1),
                confidence=0.8,
            )
            causes.append(cause)

        # Get causes
        result = await causal_graph.get_causes(target.node_id)

        assert len(result) == 3

        # Verify all cause nodes are present
        cause_ids = {node.node_id for node, _ in result}
        for cause in causes:
            assert cause.node_id in cause_ids

    @pytest.mark.asyncio
    async def test_get_effects(self, causal_graph, test_user):
        """Test getting effects (outgoing edges) of a node."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create source node
        source = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(source)

        # Create multiple effect nodes
        effects = []
        for i in range(2):
            effect = CausalNode(
                node_id=uuid4(),
                node_type=NodeType.DECISION if i == 0 else NodeType.OUTCOME,
                user_id=test_user,
                properties={},
                created_at=datetime.now(UTC),
            )
            await causal_graph.add_node(effect)
            await causal_graph.add_edge(
                source.node_id, effect.node_id,
                RelationshipType.LED_TO,
                strength=0.7,
                confidence=0.85,
            )
            effects.append(effect)

        # Get effects
        result = await causal_graph.get_effects(source.node_id)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_neighbors(self, causal_graph, test_user):
        """Test getting all neighbors of a node."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create center node
        center = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.DECISION,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(center)

        # Add incoming edge (cause)
        cause = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(cause)
        await causal_graph.add_edge(
            cause.node_id, center.node_id,
            RelationshipType.INFLUENCED, 0.8, 0.9
        )

        # Add outgoing edge (effect)
        effect = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.OUTCOME,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(effect)
        await causal_graph.add_edge(
            center.node_id, effect.node_id,
            RelationshipType.LED_TO, 0.7, 0.85
        )

        # Get neighbors
        result = await causal_graph.get_neighbors(center.node_id)

        assert result is not None
        assert result.node.node_id == center.node_id
        assert len(result.causes) == 1
        assert len(result.effects) == 1

    @pytest.mark.asyncio
    async def test_find_path_direct(self, causal_graph, test_user):
        """Test finding a direct path between two nodes."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create nodes
        source = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        target = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.OUTCOME,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )

        await causal_graph.add_node(source)
        await causal_graph.add_node(target)
        await causal_graph.add_edge(
            source.node_id, target.node_id,
            RelationshipType.LED_TO, 0.8, 0.9
        )

        # Find path
        path = await causal_graph.find_path(source.node_id, target.node_id)

        assert path is not None
        assert path.total_strength == 0.8

    @pytest.mark.asyncio
    async def test_find_path_multi_hop(self, causal_graph, test_user):
        """Test finding a multi-hop path."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create chain: A -> B -> C
        node_a = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        node_b = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.DECISION,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        node_c = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.OUTCOME,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )

        await causal_graph.add_node(node_a)
        await causal_graph.add_node(node_b)
        await causal_graph.add_node(node_c)

        await causal_graph.add_edge(
            node_a.node_id, node_b.node_id,
            RelationshipType.INFLUENCED, 0.9, 0.9
        )
        await causal_graph.add_edge(
            node_b.node_id, node_c.node_id,
            RelationshipType.LED_TO, 0.8, 0.85
        )

        # Find path
        path = await causal_graph.find_path(
            node_a.node_id,
            node_c.node_id,
            max_depth=3,
        )

        assert path is not None
        assert len(path.nodes) == 3
        assert len(path.edges) == 2
        # Total strength is product of edge strengths
        assert abs(path.total_strength - (0.9 * 0.8)) < 0.01

    @pytest.mark.asyncio
    async def test_get_nodes_by_type(self, causal_graph, test_user):
        """Test getting nodes by type."""
        from mind.core.causal.models import CausalNode, NodeType

        # Create nodes of different types
        for node_type in [NodeType.MEMORY, NodeType.MEMORY, NodeType.DECISION]:
            node = CausalNode(
                node_id=uuid4(),
                node_type=node_type,
                user_id=test_user,
                properties={},
                created_at=datetime.now(UTC),
            )
            await causal_graph.add_node(node)

        # Get memory nodes
        memories = await causal_graph.get_nodes_by_type(
            test_user,
            NodeType.MEMORY,
        )

        assert len(memories) == 2
        assert all(n.node_type == NodeType.MEMORY for n in memories)

    @pytest.mark.asyncio
    async def test_get_strongest_influences(self, causal_graph, test_user):
        """Test getting strongest influences on a node."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create target
        target = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.OUTCOME,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(target)

        # Create influencing nodes with different strengths
        strengths = [0.9, 0.5, 0.7, 0.3]
        for strength in strengths:
            source = CausalNode(
                node_id=uuid4(),
                node_type=NodeType.MEMORY,
                user_id=test_user,
                properties={},
                created_at=datetime.now(UTC),
            )
            await causal_graph.add_node(source)
            await causal_graph.add_edge(
                source.node_id, target.node_id,
                RelationshipType.INFLUENCED, strength, 0.8
            )

        # Get strongest influences
        result = await causal_graph.get_strongest_influences(
            target.node_id,
            limit=3,
        )

        assert len(result) == 3
        # Should be sorted by strength descending
        assert result[0][1] == 0.9
        assert result[1][1] == 0.7
        assert result[2][1] == 0.5

    @pytest.mark.asyncio
    async def test_prune_weak_edges(self, causal_graph, test_user):
        """Test pruning weak edges."""
        from mind.core.causal.models import CausalNode, NodeType, RelationshipType

        # Create nodes
        source = CausalNode(
            node_id=uuid4(),
            node_type=NodeType.MEMORY,
            user_id=test_user,
            properties={},
            created_at=datetime.now(UTC),
        )
        await causal_graph.add_node(source)

        # Create edges with varying strengths
        for strength in [0.05, 0.15, 0.5, 0.8]:
            target = CausalNode(
                node_id=uuid4(),
                node_type=NodeType.DECISION,
                user_id=test_user,
                properties={},
                created_at=datetime.now(UTC),
            )
            await causal_graph.add_node(target)
            await causal_graph.add_edge(
                source.node_id, target.node_id,
                RelationshipType.INFLUENCED, strength, 0.5
            )

        # Prune edges with strength < 0.1
        pruned = await causal_graph.prune_weak_edges(
            test_user,
            min_strength=0.1,
        )

        assert pruned == 1  # Only the 0.05 edge

        # Verify remaining edges
        effects = await causal_graph.get_effects(source.node_id)
        assert len(effects) == 3  # 0.15, 0.5, 0.8 remain

    @pytest.mark.asyncio
    async def test_health_check(self, causal_graph):
        """Test causal graph health check."""
        result = await causal_graph.health_check()
        assert result is True
