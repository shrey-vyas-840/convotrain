"""Training session ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrainingSession(Base):
    """Guided owner text-training session."""

    __tablename__ = "training_sessions"

    __table_args__ = (
        Index("idx_training_sessions_restaurant", "restaurant_id"),
        Index(
            "idx_training_sessions_restaurant_state",
            "restaurant_id",
            "state",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'active'"),
    )
    current_question_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )