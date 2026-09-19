"""create training sessions and conversations

Revision ID: 8b4b6f3d5e8c
Revises: 7f1c9a2d4e61
Create Date: 2026-09-19 23:00:49.212649

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "8b4b6f3d5e8c"
down_revision = "7f1c9a2d4e61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "training_sessions",
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
            "state",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column(
            "current_question_key",
            sa.String(length=100),
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
        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_training_sessions_restaurant",
        "training_sessions",
        ["restaurant_id"],
    )
    op.create_index(
        "idx_training_sessions_restaurant_state",
        "training_sessions",
        ["restaurant_id", "state"],
    )

    op.create_table(
        "conversations",
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
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "speaker_type",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "input_language",
            sa.String(length=10),
            nullable=True,
        ),
        sa.Column(
            "input_text",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "output_text",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurants.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["training_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_conversations_restaurant",
        "conversations",
        ["restaurant_id"],
    )
    op.create_index(
        "idx_conversations_session",
        "conversations",
        ["session_id"],
    )
    op.create_index(
        "idx_conversations_restaurant_session",
        "conversations",
        ["restaurant_id", "session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_conversations_restaurant_session",
        table_name="conversations",
    )
    op.drop_index(
        "idx_conversations_session",
        table_name="conversations",
    )
    op.drop_index(
        "idx_conversations_restaurant",
        table_name="conversations",
    )
    op.drop_table("conversations")

    op.drop_index(
        "idx_training_sessions_restaurant_state",
        table_name="training_sessions",
    )
    op.drop_index(
        "idx_training_sessions_restaurant",
        table_name="training_sessions",
    )
    op.drop_table("training_sessions")
