"""Create extraction jobs table."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9c2d7e4f1a6b"
down_revision: Union[str, Sequence[str], None] = "8b4b6f3d5e8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the extraction_jobs table."""
    op.create_table(
        "extraction_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "restaurant_id",
            postgresql.UUID(as_uuid=True),
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
            "extracted_json",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "validation_status",
            sa.String(length=20),
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
        "idx_extraction_jobs_restaurant",
        "extraction_jobs",
        ["restaurant_id"],
    )
    op.create_index(
        "idx_extraction_jobs_restaurant_status",
        "extraction_jobs",
        ["restaurant_id", "validation_status"],
    )


def downgrade() -> None:
    """Drop the extraction_jobs table."""
    op.drop_index(
        "idx_extraction_jobs_restaurant_status",
        table_name="extraction_jobs",
    )
    op.drop_index(
        "idx_extraction_jobs_restaurant",
        table_name="extraction_jobs",
    )
    op.drop_table("extraction_jobs")