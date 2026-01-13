-- Mind v5 Database Initialization
-- This script runs on first PostgreSQL startup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create memories table
CREATE TABLE IF NOT EXISTS memories (
    memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL DEFAULT 'observation',
    temporal_level INTEGER NOT NULL DEFAULT 1,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    base_salience FLOAT NOT NULL DEFAULT 0.5,
    outcome_adjustment FLOAT NOT NULL DEFAULT 0.0,
    embedding vector(1536),
    retrieval_count INTEGER NOT NULL DEFAULT 0,
    decision_count INTEGER NOT NULL DEFAULT 0,
    positive_outcomes INTEGER NOT NULL DEFAULT 0,
    negative_outcomes INTEGER NOT NULL DEFAULT 0,
    promoted_from_level INTEGER,
    promotion_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create decisions table
CREATE TABLE IF NOT EXISTS decisions (
    trace_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    query TEXT NOT NULL,
    context JSONB,
    decision_made TEXT,
    confidence FLOAT,
    memory_ids UUID[],
    outcome_observed BOOLEAN NOT NULL DEFAULT FALSE,
    outcome_value FLOAT,
    outcome_feedback TEXT,
    outcome_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    key_hash VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT '{}',
    expires_at TIMESTAMPTZ,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_temporal_level ON memories(temporal_level);
CREATE INDEX IF NOT EXISTS idx_memories_valid_from ON memories(valid_from);
CREATE INDEX IF NOT EXISTS idx_memories_salience ON memories((base_salience + outcome_adjustment) DESC);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at DESC);

-- Vector similarity index (IVFFlat for performance)
CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_memories_content_fts ON memories
    USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS idx_decisions_user_id ON decisions(user_id);
CREATE INDEX IF NOT EXISTS idx_decisions_created_at ON decisions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_outcome ON decisions(outcome_observed);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
DROP TRIGGER IF EXISTS memories_updated_at ON memories;
CREATE TRIGGER memories_updated_at
    BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS decisions_updated_at ON decisions;
CREATE TRIGGER decisions_updated_at
    BEFORE UPDATE ON decisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mind;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mind;
