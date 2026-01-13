"""Unit tests for PostgreSQL causal graph adapter.

These tests mock the asyncpg pool to test causal graph operations
without requiring a real database.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from mind.adapters.standard.postgres_causal import PostgresCausalGraph
from mind.core.causal.models import (
    CausalNode,
    CausalRelationship,
    NodeType,
    RelationshipType,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_pool():
    """Create a mock asyncpg pool."""
    pool = AsyncMock()
    pool.execute = AsyncMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock()
    pool.fetchval = AsyncMock()
    return pool


@pytest.fixture
def causal_graph(mock_pool):
    """Create a PostgresCausalGraph with mocked pool."""
    return PostgresCausalGraph(pool=mock_pool)


@pytest.fixture
def sample_node():
    """Create a sample causal node."""
    return CausalNode(
        node_id=uuid4(),
        node_type=NodeType.MEMORY,
        user_id=uuid4(),
        properties={"content_type": "observation"},
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_edge():
    """Create a sample causal relationship."""
    return CausalRelationship(
        source_id=uuid4(),
        target_id=uuid4(),
        relationship_type=RelationshipType.INFLUENCED,
        strength=0.8,
        confidence=0.9,
        evidence_count=5,
        properties={"context": "test"},
        created_at=datetime.now(UTC),
    )


def create_mock_node_row(node: CausalNode) -> MagicMock:
    """Create a mock row from a CausalNode."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: getattr(self, key)
    row.node_id = node.node_id
    row.node_type = node.node_type.value
    row.user_id = node.user_id
    row.properties = json.dumps(node.properties)
    row.created_at = node.created_at
    return row


def create_mock_edge_row(edge: CausalRelationship) -> MagicMock:
    """Create a mock row from a CausalRelationship."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: getattr(self, key)
    row.source_id = edge.source_id
    row.target_id = edge.target_id
    row.relationship_type = edge.relationship_type.value
    row.strength = edge.strength
    row.confidence = edge.confidence
    row.evidence_count = edge.evidence_count
    row.properties = json.dumps(edge.properties)
    row.created_at = edge.created_at
    return row


def create_mock_join_row(node: CausalNode, edge: CausalRelationship) -> MagicMock:
    """Create a mock row from joined node and edge data."""
    row = MagicMock()
    row.__getitem__ = lambda self, key: getattr(self, key)
    # Node fields
    row.node_id = node.node_id
    row.node_type = node.node_type.value
    row.user_id = node.user_id
    row.properties = json.dumps(node.properties)
    row.created_at = node.created_at
    # Edge fields (with e_ prefix)
    row.e_source_id = edge.source_id
    row.e_target_id = edge.target_id
    row.e_relationship_type = edge.relationship_type.value
    row.e_strength = edge.strength
    row.e_confidence = edge.confidence
    row.e_evidence_count = edge.evidence_count
    row.e_properties = json.dumps(edge.properties)
    row.e_created_at = edge.created_at
    return row


# =============================================================================
# Node Operations Tests
# =============================================================================


class TestCausalGraphNodes:
    """Tests for causal graph node operations."""

    @pytest.mark.asyncio
    async def test_add_node(self, causal_graph, mock_pool, sample_node):
        """Test adding a node to the graph."""
        result = await causal_graph.add_node(sample_node)

        assert result.node_id == sample_node.node_id
        mock_pool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_node_found(self, causal_graph, mock_pool, sample_node):
        """Test getting an existing node."""
        mock_row = create_mock_node_row(sample_node)
        mock_pool.fetchrow.return_value = mock_row

        result = await causal_graph.get_node(sample_node.node_id)

        assert result is not None
        assert result.node_id == sample_node.node_id
        assert result.node_type == sample_node.node_type

    @pytest.mark.asyncio
    async def test_get_node_not_found(self, causal_graph, mock_pool):
        """Test getting a non-existent node."""
        mock_pool.fetchrow.return_value = None

        result = await causal_graph.get_node(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_nodes_by_type(self, causal_graph, mock_pool, sample_node):
        """Test getting nodes by type."""
        mock_row = create_mock_node_row(sample_node)
        mock_pool.fetch.return_value = [mock_row, mock_row]

        result = await causal_graph.get_nodes_by_type(
            sample_node.user_id,
            NodeType.MEMORY,
            limit=100,
        )

        assert len(result) == 2
        assert all(n.node_type == NodeType.MEMORY for n in result)


# =============================================================================
# Edge Operations Tests
# =============================================================================


class TestCausalGraphEdges:
    """Tests for causal graph edge operations."""

    @pytest.mark.asyncio
    async def test_add_edge(self, causal_graph, mock_pool):
        """Test adding an edge between nodes."""
        source_id = uuid4()
        target_id = uuid4()

        result = await causal_graph.add_edge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=RelationshipType.INFLUENCED,
            strength=0.8,
            confidence=0.9,
        )

        assert result.source_id == source_id
        assert result.target_id == target_id
        assert result.strength == 0.8
        mock_pool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_edge_with_properties(self, causal_graph, mock_pool):
        """Test adding an edge with properties."""
        source_id = uuid4()
        target_id = uuid4()
        props = {"context": "test", "weight": 1.0}

        result = await causal_graph.add_edge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=RelationshipType.LED_TO,
            properties=props,
        )

        assert result.properties == props

    @pytest.mark.asyncio
    async def test_get_edge_found(self, causal_graph, mock_pool, sample_edge):
        """Test getting an existing edge."""
        mock_row = create_mock_edge_row(sample_edge)
        mock_pool.fetchrow.return_value = mock_row

        result = await causal_graph.get_edge(
            sample_edge.source_id,
            sample_edge.target_id,
        )

        assert result is not None
        assert result.strength == sample_edge.strength

    @pytest.mark.asyncio
    async def test_get_edge_not_found(self, causal_graph, mock_pool):
        """Test getting a non-existent edge."""
        mock_pool.fetchrow.return_value = None

        result = await causal_graph.get_edge(uuid4(), uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_update_edge_strength(self, causal_graph, mock_pool, sample_edge):
        """Test updating edge strength."""
        updated_edge = CausalRelationship(
            source_id=sample_edge.source_id,
            target_id=sample_edge.target_id,
            relationship_type=sample_edge.relationship_type,
            strength=0.95,  # Updated
            confidence=sample_edge.confidence,
            evidence_count=sample_edge.evidence_count + 1,
            properties=sample_edge.properties,
            created_at=sample_edge.created_at,
        )
        mock_row = create_mock_edge_row(updated_edge)
        mock_pool.fetchrow.return_value = mock_row

        result = await causal_graph.update_edge_strength(
            sample_edge.source_id,
            sample_edge.target_id,
            new_strength=0.95,
        )

        assert result.strength == 0.95

    @pytest.mark.asyncio
    async def test_update_edge_strength_not_found(self, causal_graph, mock_pool):
        """Test updating non-existent edge."""
        mock_pool.fetchrow.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await causal_graph.update_edge_strength(uuid4(), uuid4(), 0.9)


# =============================================================================
# Traversal Operations Tests
# =============================================================================


class TestCausalGraphTraversal:
    """Tests for causal graph traversal operations."""

    @pytest.mark.asyncio
    async def test_get_causes(self, causal_graph, mock_pool, sample_node, sample_edge):
        """Test getting causes of a node."""
        mock_row = create_mock_join_row(sample_node, sample_edge)
        mock_pool.fetch.return_value = [mock_row]

        result = await causal_graph.get_causes(uuid4())

        assert len(result) == 1
        node, edge = result[0]
        assert node.node_id == sample_node.node_id
        assert edge.strength == sample_edge.strength

    @pytest.mark.asyncio
    async def test_get_causes_with_min_strength(
        self, causal_graph, mock_pool, sample_node, sample_edge
    ):
        """Test getting causes with minimum strength filter."""
        mock_row = create_mock_join_row(sample_node, sample_edge)
        mock_pool.fetch.return_value = [mock_row]

        await causal_graph.get_causes(uuid4(), min_strength=0.5)

        call_args = mock_pool.fetch.call_args[0][0]
        assert "strength >= $2" in call_args

    @pytest.mark.asyncio
    async def test_get_effects(self, causal_graph, mock_pool, sample_node, sample_edge):
        """Test getting effects of a node."""
        mock_row = create_mock_join_row(sample_node, sample_edge)
        mock_pool.fetch.return_value = [mock_row]

        result = await causal_graph.get_effects(uuid4())

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_neighbors(self, causal_graph, mock_pool, sample_node, sample_edge):
        """Test getting all neighbors of a node."""
        mock_node_row = create_mock_node_row(sample_node)
        mock_join_row = create_mock_join_row(sample_node, sample_edge)

        mock_pool.fetchrow.return_value = mock_node_row
        mock_pool.fetch.return_value = [mock_join_row]

        result = await causal_graph.get_neighbors(sample_node.node_id)

        assert result is not None
        assert result.node.node_id == sample_node.node_id

    @pytest.mark.asyncio
    async def test_get_neighbors_not_found(self, causal_graph, mock_pool):
        """Test getting neighbors of non-existent node."""
        mock_pool.fetchrow.return_value = None

        result = await causal_graph.get_neighbors(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_find_path_same_node(self, causal_graph, mock_pool, sample_node):
        """Test finding path when source equals target."""
        mock_node_row = create_mock_node_row(sample_node)
        mock_pool.fetchrow.return_value = mock_node_row

        result = await causal_graph.find_path(
            sample_node.node_id,
            sample_node.node_id,
        )

        assert result is not None
        assert len(result.nodes) == 1
        assert len(result.edges) == 0
        assert result.total_strength == 1.0

    @pytest.mark.asyncio
    async def test_find_path_no_path(self, causal_graph, mock_pool):
        """Test finding path when no path exists."""
        mock_pool.fetch.return_value = []

        result = await causal_graph.find_path(uuid4(), uuid4(), max_depth=3)

        assert result is None

    @pytest.mark.asyncio
    async def test_find_path_direct_connection(
        self, causal_graph, mock_pool, sample_node, sample_edge
    ):
        """Test finding path with direct connection."""
        source_id = uuid4()
        target_id = uuid4()

        target_node = CausalNode(
            node_id=target_id,
            node_type=NodeType.DECISION,
            user_id=sample_node.user_id,
            properties={},
            created_at=datetime.now(UTC),
        )

        edge = CausalRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=RelationshipType.INFLUENCED,
            strength=0.8,
            confidence=0.9,
            evidence_count=1,
            properties={},
            created_at=datetime.now(UTC),
        )

        mock_join_row = create_mock_join_row(target_node, edge)
        mock_pool.fetch.return_value = [mock_join_row]

        # Also mock get_node for path reconstruction
        mock_pool.fetchrow.side_effect = [
            create_mock_node_row(sample_node),
            create_mock_node_row(target_node),
        ]

        result = await causal_graph.find_path(source_id, target_id)

        assert result is not None
        assert result.total_strength == 0.8


# =============================================================================
# Causal Analysis Tests
# =============================================================================


class TestCausalAnalysis:
    """Tests for causal analysis operations."""

    @pytest.mark.asyncio
    async def test_get_memory_influence_on_outcome(self, causal_graph, mock_pool):
        """Test calculating memory influence on outcome."""
        memory_id = uuid4()
        outcome_id = uuid4()

        # No path found
        mock_pool.fetch.return_value = []

        result = await causal_graph.get_memory_influence_on_outcome(
            memory_id,
            outcome_id,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_strongest_influences(self, causal_graph, mock_pool):
        """Test getting strongest influences on outcome."""
        mock_pool.fetch.return_value = [
            MagicMock(
                __getitem__=lambda self, k: {"source_id": uuid4(), "strength": 0.9}[k]
            ),
            MagicMock(
                __getitem__=lambda self, k: {"source_id": uuid4(), "strength": 0.7}[k]
            ),
        ]

        result = await causal_graph.get_strongest_influences(uuid4(), limit=10)

        assert len(result) == 2
        assert result[0][1] == 0.9  # First should be strongest


# =============================================================================
# Maintenance Tests
# =============================================================================


class TestCausalGraphMaintenance:
    """Tests for causal graph maintenance operations."""

    @pytest.mark.asyncio
    async def test_prune_weak_edges(self, causal_graph, mock_pool):
        """Test pruning weak edges."""
        mock_pool.execute.return_value = "DELETE 5"

        result = await causal_graph.prune_weak_edges(
            user_id=uuid4(),
            min_strength=0.1,
            min_evidence=1,
        )

        assert result == 5

    @pytest.mark.asyncio
    async def test_prune_weak_edges_none_deleted(self, causal_graph, mock_pool):
        """Test pruning when no edges deleted."""
        mock_pool.execute.return_value = "DELETE 0"

        result = await causal_graph.prune_weak_edges(uuid4())

        assert result == 0

    @pytest.mark.asyncio
    async def test_prune_weak_edges_parse_error(self, causal_graph, mock_pool):
        """Test pruning with unparseable result."""
        mock_pool.execute.return_value = "SOMETHING UNEXPECTED"

        result = await causal_graph.prune_weak_edges(uuid4())

        assert result == 0

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, causal_graph, mock_pool):
        """Test health check when tables exist."""
        mock_pool.fetchval.return_value = True

        result = await causal_graph.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, causal_graph, mock_pool):
        """Test health check when tables don't exist."""
        mock_pool.fetchval.return_value = False

        result = await causal_graph.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_error(self, causal_graph, mock_pool):
        """Test health check on database error."""
        mock_pool.fetchval.side_effect = Exception("Connection failed")

        result = await causal_graph.health_check()

        assert result is False
