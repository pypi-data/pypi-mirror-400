"""Create federated_patterns table for SanitizedPattern model.

Revision ID: 20250104_000001
Revises: 20251228_000001
Create Date: 2025-01-04 00:00:01

Creates the federated_patterns table for storing federated patterns
with the SanitizedPattern model schema:
- pattern_id: UUID primary key
- pattern_type: varchar for flexibility
- trigger_category: category of triggering context
- response_strategy: recommended strategy
- outcome_improvement: outcome improvement metric
- confidence: pattern confidence score
- source_count: number of source samples
- user_count: number of contributing users
- epsilon: differential privacy parameter
- created_at: creation timestamp
- expires_at: optional expiry timestamp
- is_active: whether pattern is active
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20250104_000001"
down_revision: Union[str, None] = "20251228_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create federated_patterns table
    op.create_table(
        "federated_patterns",
        sa.Column(
            "pattern_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("pattern_type", sa.String(50), nullable=False),
        sa.Column("trigger_category", sa.String(100), nullable=False, index=True),
        sa.Column("response_strategy", sa.Text, nullable=False),
        sa.Column("outcome_improvement", sa.Float, server_default="0.0"),
        sa.Column("confidence", sa.Float, server_default="0.5"),
        sa.Column("source_count", sa.Integer, server_default="0"),
        sa.Column("user_count", sa.Integer, server_default="0"),
        sa.Column("epsilon", sa.Float, server_default="0.1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", index=True),
    )

    # Create indexes for efficient queries
    op.create_index(
        "idx_patterns_trigger_type",
        "federated_patterns",
        ["trigger_category", "pattern_type"],
    )
    op.create_index(
        "idx_patterns_active_confidence",
        "federated_patterns",
        ["is_active", "confidence"],
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_patterns_active_confidence", table_name="federated_patterns")
    op.drop_index("idx_patterns_trigger_type", table_name="federated_patterns")

    # Drop table
    op.drop_table("federated_patterns")
