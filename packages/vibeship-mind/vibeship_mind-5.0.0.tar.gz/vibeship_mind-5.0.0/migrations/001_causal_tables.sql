-- Migration 001: Causal Tables for Standard Tier
-- Date: 2025-01-04
-- Purpose: Add causal graph tables for PostgreSQL-only causal tracking

-- ============================================================================
-- Causal Nodes Table
-- ============================================================================
-- Stores nodes in the causal graph (memories, decisions, outcomes)

CREATE TABLE IF NOT EXISTS causal_nodes (
    node_id UUID PRIMARY KEY,
    node_type VARCHAR(50) NOT NULL,  -- 'memory', 'decision', 'outcome', 'context'
    user_id UUID NOT NULL REFERENCES users(user_id),
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user-scoped queries
CREATE INDEX IF NOT EXISTS idx_causal_nodes_user ON causal_nodes (user_id);

-- Index for type-based filtering
CREATE INDEX IF NOT EXISTS idx_causal_nodes_type ON causal_nodes (user_id, node_type);

-- Index for temporal queries
CREATE INDEX IF NOT EXISTS idx_causal_nodes_created ON causal_nodes (created_at DESC);

COMMENT ON TABLE causal_nodes IS 'Nodes in the causal graph. Standard tier uses adjacency tables instead of FalkorDB.';

-- ============================================================================
-- Causal Edges Table
-- ============================================================================
-- Stores directed edges between nodes with strength/confidence

CREATE TABLE IF NOT EXISTS causal_edges (
    source_id UUID NOT NULL REFERENCES causal_nodes(node_id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES causal_nodes(node_id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,  -- 'influenced', 'caused', 'led_to', 'preceded'
    strength FLOAT NOT NULL DEFAULT 1.0 CHECK (strength BETWEEN 0 AND 1),
    confidence FLOAT NOT NULL DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
    evidence_count INT NOT NULL DEFAULT 1,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (source_id, target_id)
);

-- Index for forward traversal (get effects of a node)
CREATE INDEX IF NOT EXISTS idx_causal_edges_source ON causal_edges (source_id);

-- Index for backward traversal (get causes of a node)
CREATE INDEX IF NOT EXISTS idx_causal_edges_target ON causal_edges (target_id);

-- Index for filtering by relationship type
CREATE INDEX IF NOT EXISTS idx_causal_edges_type ON causal_edges (relationship_type);

-- Index for finding strong edges
CREATE INDEX IF NOT EXISTS idx_causal_edges_strength ON causal_edges (strength DESC);

COMMENT ON TABLE causal_edges IS 'Directed edges in the causal graph with strength and confidence.';

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to add or update an edge (upsert pattern)
CREATE OR REPLACE FUNCTION upsert_causal_edge(
    p_source_id UUID,
    p_target_id UUID,
    p_relationship_type VARCHAR(50),
    p_strength FLOAT DEFAULT 1.0,
    p_confidence FLOAT DEFAULT 1.0,
    p_properties JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO causal_edges (
        source_id, target_id, relationship_type,
        strength, confidence, evidence_count, properties
    ) VALUES (
        p_source_id, p_target_id, p_relationship_type,
        p_strength, p_confidence, 1, p_properties
    )
    ON CONFLICT (source_id, target_id) DO UPDATE SET
        strength = EXCLUDED.strength,
        confidence = EXCLUDED.confidence,
        evidence_count = causal_edges.evidence_count + 1,
        properties = EXCLUDED.properties;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION upsert_causal_edge IS 'Add or update a causal edge, incrementing evidence count on update.';

-- Function to get direct causes of a node
CREATE OR REPLACE FUNCTION get_causes(
    p_node_id UUID,
    p_min_strength FLOAT DEFAULT 0.0,
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    node_id UUID,
    node_type VARCHAR(50),
    user_id UUID,
    properties JSONB,
    edge_strength FLOAT,
    edge_confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.node_id,
        n.node_type,
        n.user_id,
        n.properties,
        e.strength AS edge_strength,
        e.confidence AS edge_confidence
    FROM causal_edges e
    JOIN causal_nodes n ON e.source_id = n.node_id
    WHERE e.target_id = p_node_id
      AND e.strength >= p_min_strength
    ORDER BY e.strength DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_causes IS 'Get nodes that causally influence the given node (incoming edges).';

-- Function to get direct effects of a node
CREATE OR REPLACE FUNCTION get_effects(
    p_node_id UUID,
    p_min_strength FLOAT DEFAULT 0.0,
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    node_id UUID,
    node_type VARCHAR(50),
    user_id UUID,
    properties JSONB,
    edge_strength FLOAT,
    edge_confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.node_id,
        n.node_type,
        n.user_id,
        n.properties,
        e.strength AS edge_strength,
        e.confidence AS edge_confidence
    FROM causal_edges e
    JOIN causal_nodes n ON e.target_id = n.node_id
    WHERE e.source_id = p_node_id
      AND e.strength >= p_min_strength
    ORDER BY e.strength DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_effects IS 'Get nodes causally influenced by the given node (outgoing edges).';

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'causal_nodes') THEN
        RAISE EXCEPTION 'Table causal_nodes not created';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'causal_edges') THEN
        RAISE EXCEPTION 'Table causal_edges not created';
    END IF;
    RAISE NOTICE 'Migration 001: Causal tables created successfully';
END $$;
