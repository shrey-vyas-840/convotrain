"""create knowledge_facts table

Revision ID: 7f1c9a2d4e61
Revises: b73c5810e344
Create Date: 2026-09-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7f1c9a2d4e61"
down_revision: Union[str, None] = "b73c5810e344"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the knowledge_facts table."""
    op.create_table(
        "knowledge_facts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "restaurant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "fact_key",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "fact_value_json",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "source_text",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "source_language",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurants.id"],
            name="fk_knowledge_facts_restaurant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_knowledge_facts_restaurant",
        "knowledge_facts",
        ["restaurant_id"],
    )

    op.create_index(
        "idx_knowledge_facts_restaurant_status",
        "knowledge_facts",
        ["restaurant_id", "status"],
    )

    op.create_index(
        "idx_knowledge_facts_restaurant_category",
        "knowledge_facts",
        ["restaurant_id", "category"],
    )


def downgrade() -> None:
    """Remove the knowledge_facts table."""
    op.drop_index(
        "idx_knowledge_facts_restaurant_category",
        table_name="knowledge_facts",
    )
    op.drop_index(
        "idx_knowledge_facts_restaurant_status",
        table_name="knowledge_facts",
    )
    op.drop_index(
        "idx_knowledge_facts_restaurant",
        table_name="knowledge_facts",
    )
    op.drop_table("knowledge_facts")
