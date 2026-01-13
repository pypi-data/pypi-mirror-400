"""Standard tier database schema initialization.

This module initializes the PostgreSQL schema for Standard tier.
The schema matches what the Standard tier adapters expect:
- PostgresMemoryStorage
- PostgresDecisionStorage

This is separate from Alembic migrations which are for Enterprise tier.
Standard tier uses this simpler schema that runs with asyncpg directly.
"""

import asyncpg
import structlog

logger = structlog.get_logger()


STANDARD_SCHEMA_VERSION = "1.0.0"


async def init_standard_schema(pool: asyncpg.Pool) -> None:
    """Initialize the Standard tier database schema.

    Creates all tables required by the Standard tier adapters.
    Safe to call multiple times - uses CREATE IF NOT EXISTS.

    Args:
        pool: asyncpg connection pool
    """
    log = logger.bind(schema_version=STANDARD_SCHEMA_VERSION)
    log.info("initializing_standard_schema")

    async with pool.acquire() as conn:
        # Create extensions
        await _create_extensions(conn)

        # Create tables
        await _create_memories_table(conn)
        await _create_decision_traces_table(conn)
        await _create_salience_updates_table(conn)
        await _create_events_table(conn)
        await _create_causal_edges_table(conn)
        await _create_vector_embeddings_table(conn)

        # Create indexes
        await _create_indexes(conn)

    log.info("standard_schema_initialized")


async def _create_extensions(conn: asyncpg.Connection) -> None:
    """Create required PostgreSQL extensions."""
    extensions = [
        ("uuid-ossp", True),   # UUID generation
        ("vector", False),      # pgvector for embeddings (optional)
        ("pg_trgm", False),     # Trigram for text search (optional)
    ]

    for ext, required in extensions:
        try:
            await conn.execute(f'CREATE EXTENSION IF NOT EXISTS "{ext}"')
            logger.debug("extension_created", extension=ext)
        except asyncpg.PostgresError as e:
            if required:
                raise RuntimeError(f"Required extension {ext} not available: {e}")
            logger.debug("extension_not_available", extension=ext)


async def _create_memories_table(conn: asyncpg.Connection) -> None:
    """Create the memories table for Standard tier."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            -- Primary key
            memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Ownership
            user_id UUID NOT NULL,

            -- Content
            content TEXT NOT NULL,
            content_type VARCHAR(50) DEFAULT 'observation',

            -- Temporal hierarchy
            temporal_level VARCHAR(20) DEFAULT 'immediate',
            valid_from TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            valid_until TIMESTAMPTZ,

            -- Salience tracking (outcome-based adjustment)
            base_salience FLOAT DEFAULT 0.5,
            outcome_adjustment FLOAT DEFAULT 0.0,

            -- Decision tracking (for self-improvement)
            retrieval_count INTEGER DEFAULT 0,
            decision_count INTEGER DEFAULT 0,
            positive_outcomes INTEGER DEFAULT 0,
            negative_outcomes INTEGER DEFAULT 0,

            -- Promotion tracking
            promoted_from_level VARCHAR(20),
            promotion_timestamp TIMESTAMPTZ,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.debug("table_created", table="memories")


async def _create_decision_traces_table(conn: asyncpg.Connection) -> None:
    """Create the decision_traces table for Standard tier."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS decision_traces (
            -- Primary key
            trace_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Context
            user_id UUID NOT NULL,
            session_id UUID,

            -- Memory usage
            memory_ids TEXT[] DEFAULT '{}',
            memory_scores JSONB DEFAULT '{}',

            -- Decision details
            decision_type VARCHAR(100),
            decision_summary TEXT,
            confidence FLOAT,
            alternatives_count INTEGER DEFAULT 0,

            -- Outcome tracking (inline for simpler queries)
            outcome_observed BOOLEAN DEFAULT FALSE,
            outcome_quality FLOAT,
            outcome_timestamp TIMESTAMPTZ,
            outcome_signal VARCHAR(100),

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.debug("table_created", table="decision_traces")


async def _create_salience_updates_table(conn: asyncpg.Connection) -> None:
    """Create the salience_updates table for tracking adjustments."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS salience_updates (
            -- Primary key
            update_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- References
            memory_id UUID NOT NULL,
            trace_id UUID,

            -- Update details
            delta FLOAT NOT NULL,
            reason VARCHAR(255),

            -- Timestamp
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.debug("table_created", table="salience_updates")


async def _create_events_table(conn: asyncpg.Connection) -> None:
    """Create the events table for Standard tier event processing.

    This schema matches what PostgresEventPublisher/Consumer expect:
    - Events are stored with payload and status for processing
    - NOTIFY/LISTEN is used for real-time notification
    """
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            -- Primary key
            event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Event metadata
            event_type VARCHAR(100) NOT NULL,
            user_id UUID,

            -- Event data
            payload JSONB NOT NULL,

            -- Processing state
            status VARCHAR(20) DEFAULT 'pending',
            processed_at TIMESTAMPTZ,
            retry_count INTEGER DEFAULT 0,
            last_error TEXT,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.debug("table_created", table="events")


async def _create_causal_edges_table(conn: asyncpg.Connection) -> None:
    """Create the causal_edges table for causal graph."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS causal_edges (
            -- Primary key
            edge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Ownership
            user_id UUID NOT NULL,

            -- Edge definition
            cause_id UUID NOT NULL,
            effect_id UUID NOT NULL,
            cause_type VARCHAR(50) NOT NULL,
            effect_type VARCHAR(50) NOT NULL,

            -- Causal properties
            strength FLOAT DEFAULT 0.5,
            confidence FLOAT DEFAULT 0.5,
            evidence_count INTEGER DEFAULT 1,
            last_observed TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

            -- Timestamps
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

            -- Prevent duplicate edges
            UNIQUE (user_id, cause_id, effect_id)
        )
    """)
    logger.debug("table_created", table="causal_edges")


async def _create_vector_embeddings_table(conn: asyncpg.Connection) -> None:
    """Create the vector_embeddings table for pgvector search."""
    # Check if vector extension is available
    try:
        result = await conn.fetchval(
            "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
        )
        has_vector = result is not None
    except Exception:
        has_vector = False

    if has_vector:
        # Use native vector type
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vector_embeddings (
                -- Primary key
                memory_id UUID PRIMARY KEY,

                -- Vector data
                embedding vector(1536),

                -- Model info
                model VARCHAR(100) DEFAULT 'text-embedding-3-small',
                dimensions INTEGER DEFAULT 1536,

                -- Timestamp
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        # Fallback to float array (without vector similarity search)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vector_embeddings (
                -- Primary key
                memory_id UUID PRIMARY KEY,

                -- Vector data (as float array)
                embedding FLOAT[] NOT NULL,

                -- Model info
                model VARCHAR(100) DEFAULT 'text-embedding-3-small',
                dimensions INTEGER DEFAULT 1536,

                -- Timestamp
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        """)

    logger.debug("table_created", table="vector_embeddings", has_vector=has_vector)


async def _create_indexes(conn: asyncpg.Connection) -> None:
    """Create indexes for efficient queries."""
    indexes = [
        # Memories indexes
        ("ix_memories_user_id", "memories", "user_id"),
        ("ix_memories_temporal_level", "memories", "temporal_level"),
        ("ix_memories_valid_from", "memories", "valid_from"),

        # Decision traces indexes
        ("ix_decision_traces_user_id", "decision_traces", "user_id"),
        ("ix_decision_traces_created_at", "decision_traces", "created_at"),
        ("ix_decision_traces_outcome", "decision_traces", "outcome_observed"),

        # Salience updates indexes
        ("ix_salience_updates_memory_id", "salience_updates", "memory_id"),

        # Events indexes
        ("ix_events_type", "events", "event_type"),
        ("ix_events_status", "events", "status"),
        ("ix_events_created_at", "events", "created_at"),

        # Causal edges indexes
        ("ix_causal_edges_user_id", "causal_edges", "user_id"),
        ("ix_causal_edges_cause", "causal_edges", "cause_id"),
        ("ix_causal_edges_effect", "causal_edges", "effect_id"),
    ]

    for idx_name, table, columns in indexes:
        try:
            await conn.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})"
            )
        except asyncpg.PostgresError:
            # Index might already exist with different definition
            pass

    # Create special salience index (computed column)
    try:
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS ix_memories_salience
            ON memories ((base_salience + outcome_adjustment) DESC)
        """)
    except asyncpg.PostgresError:
        pass

    # Create vector index if available
    try:
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS ix_vector_embeddings_ivfflat
            ON vector_embeddings
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
    except asyncpg.PostgresError:
        # Vector extension might not be available
        pass

    logger.debug("indexes_created")


async def check_schema_health(pool: asyncpg.Pool) -> dict:
    """Check that the Standard tier schema is properly initialized.

    Returns:
        Dictionary with schema health information
    """
    async with pool.acquire() as conn:
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        table_names = [r["table_name"] for r in tables]

        required_tables = [
            "memories",
            "decision_traces",
            "salience_updates",
            "events",
            "causal_edges",
            "vector_embeddings",
        ]

        missing = [t for t in required_tables if t not in table_names]

        return {
            "healthy": len(missing) == 0,
            "tables_found": table_names,
            "tables_missing": missing,
            "schema_version": STANDARD_SCHEMA_VERSION,
        }
