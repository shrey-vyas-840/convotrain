"""add knowledge fact conversation provenance

Revision ID: c4e8a1b7d932
Revises: 9c2d7e4f1a6b
Create Date: 2026-09-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c4e8a1b7d932"
down_revision: Union[str, None] = "9c2d7e4f1a6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_facts",
        sa.Column(
            "source_turn_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_knowledge_facts_source_turn",
        "knowledge_facts",
        "conversations",
        ["source_turn_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "idx_knowledge_facts_source_turn",
        "knowledge_facts",
        ["source_turn_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_knowledge_facts_source_turn",
        table_name="knowledge_facts",
    )

    op.drop_constraint(
        "fk_knowledge_facts_source_turn",
        "knowledge_facts",
        type_="foreignkey",
    )

    op.drop_column(
        "knowledge_facts",
        "source_turn_id",
    )
