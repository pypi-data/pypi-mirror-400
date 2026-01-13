"""Initial Mind v5 schema.

Revision ID: 20251228_000001
Revises: None
Create Date: 2025-12-28 00:00:01

Creates all core tables for Mind v5:
- Users and authentication
- Hierarchical memory system
- Decision tracking with outcomes
- Events log for event sourcing
- API keys for authentication
- Federated patterns for collective learning
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20251228_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create enum types
    op.execute("""
        CREATE TYPE temporal_level AS ENUM (
            'immediate', 'situational', 'seasonal', 'identity'
        )
    """)

    op.execute("""
        CREATE TYPE memory_content_type AS ENUM (
            'observation', 'preference', 'fact', 'procedure',
            'episode', 'skill', 'value', 'identity'
        )
    """)

    op.execute("""
        CREATE TYPE decision_status AS ENUM (
            'pending', 'in_progress', 'completed', 'failed', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE outcome_quality AS ENUM (
            'positive', 'negative', 'neutral', 'mixed'
        )
    """)

    op.execute("""
        CREATE TYPE pattern_type AS ENUM (
            'decision_strategy', 'context_pattern', 'outcome_correlation',
            'temporal_pattern', 'preference_cluster'
        )
    """)

    # Users table
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # Memories table - core hierarchical memory storage
    op.create_table(
        "memories",
        sa.Column("memory_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_type", sa.Enum("observation", "preference", "fact", "procedure",
                                          "episode", "skill", "value", "identity",
                                          name="memory_content_type", create_type=False)),
        sa.Column("temporal_level", sa.Enum("immediate", "situational", "seasonal", "identity",
                                            name="temporal_level", create_type=False)),
        sa.Column("base_salience", sa.Float, server_default="0.5"),
        sa.Column("outcome_adjustment", sa.Float, server_default="0.0"),
        sa.Column("access_count", sa.Integer, server_default="0"),
        sa.Column("valid_from", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("embedding", postgresql.ARRAY(sa.Float), nullable=True),
    )

    # Memory embeddings table (separate for efficiency)
    op.create_table(
        "memory_embeddings",
        sa.Column("memory_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("memories.memory_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("embedding", sa.LargeBinary, nullable=False),  # vector as bytes
        sa.Column("model", sa.String(100), server_default="'text-embedding-3-small'"),
        sa.Column("dimensions", sa.Integer, server_default="1536"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # Decisions table - tracks decision points
    op.create_table(
        "decisions",
        sa.Column("trace_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("context_used", postgresql.JSONB, server_default="[]"),
        sa.Column("decision_made", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("status", sa.Enum("pending", "in_progress", "completed", "failed", "cancelled",
                                    name="decision_status", create_type=False),
                  server_default="'pending'"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # Outcomes table - tracks decision outcomes
    op.create_table(
        "outcomes",
        sa.Column("outcome_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("decisions.trace_id", ondelete="CASCADE"), nullable=False),
        sa.Column("quality", sa.Enum("positive", "negative", "neutral", "mixed",
                                     name="outcome_quality", create_type=False)),
        sa.Column("quality_score", sa.Float, nullable=True),  # -1.0 to 1.0
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # Decision-Memory links for outcome attribution
    op.create_table(
        "decision_memory_links",
        sa.Column("link_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("decisions.trace_id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("memories.memory_id", ondelete="CASCADE"), nullable=False),
        sa.Column("relevance_score", sa.Float, server_default="0.0"),
        sa.Column("contribution_weight", sa.Float, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # Events table - event sourcing backbone
    op.create_table(
        "events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("aggregate_type", sa.String(100), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("data", postgresql.JSONB, nullable=False),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("published", sa.Boolean, server_default="false"),
    )

    # API Keys table
    op.create_table(
        "api_keys",
        sa.Column("key_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("scopes", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("rate_limit", sa.Integer, server_default="1000"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Federated patterns table
    op.create_table(
        "federated_patterns",
        sa.Column("pattern_id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("pattern_type", sa.Enum("decision_strategy", "context_pattern",
                                          "outcome_correlation", "temporal_pattern",
                                          "preference_cluster",
                                          name="pattern_type", create_type=False)),
        sa.Column("trigger", sa.String(500), nullable=False),
        sa.Column("strategy", sa.String(500), nullable=False),
        sa.Column("success_rate", sa.Float, server_default="0.0"),
        sa.Column("sample_count", sa.Integer, server_default="0"),
        sa.Column("user_count", sa.Integer, server_default="0"),
        sa.Column("epsilon", sa.Float, server_default="0.1"),
        sa.Column("sanitized", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
    )

    # Create indexes for performance

    # Memory indexes
    op.create_index("ix_memories_user_id", "memories", ["user_id"])
    op.create_index("ix_memories_temporal_level", "memories", ["temporal_level"])
    op.create_index("ix_memories_valid_from", "memories", ["valid_from"])
    op.create_index("ix_memories_salience", "memories",
                    [sa.text("(base_salience + outcome_adjustment) DESC")])
    op.create_index("ix_memories_content_trgm", "memories", ["content"],
                    postgresql_using="gin",
                    postgresql_ops={"content": "gin_trgm_ops"})

    # Decision indexes
    op.create_index("ix_decisions_user_id", "decisions", ["user_id"])
    op.create_index("ix_decisions_created_at", "decisions", ["created_at"])
    op.create_index("ix_decisions_status", "decisions", ["status"])

    # Outcome indexes
    op.create_index("ix_outcomes_trace_id", "outcomes", ["trace_id"])
    op.create_index("ix_outcomes_quality", "outcomes", ["quality"])

    # Event indexes
    op.create_index("ix_events_aggregate", "events", ["aggregate_type", "aggregate_id"])
    op.create_index("ix_events_type", "events", ["event_type"])
    op.create_index("ix_events_occurred_at", "events", ["occurred_at"])
    op.create_index("ix_events_unpublished", "events", ["published"],
                    postgresql_where=sa.text("published = false"))

    # API key indexes
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_hash", "api_keys", ["key_hash"])

    # Pattern indexes
    op.create_index("ix_federated_patterns_type", "federated_patterns", ["pattern_type"])
    op.create_index("ix_federated_patterns_success", "federated_patterns",
                    ["success_rate"],
                    postgresql_where=sa.text("sample_count >= 100"))


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table("federated_patterns")
    op.drop_table("api_keys")
    op.drop_table("events")
    op.drop_table("decision_memory_links")
    op.drop_table("outcomes")
    op.drop_table("decisions")
    op.drop_table("memory_embeddings")
    op.drop_table("memories")
    op.drop_table("users")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS pattern_type")
    op.execute("DROP TYPE IF EXISTS outcome_quality")
    op.execute("DROP TYPE IF EXISTS decision_status")
    op.execute("DROP TYPE IF EXISTS memory_content_type")
    op.execute("DROP TYPE IF EXISTS temporal_level")
