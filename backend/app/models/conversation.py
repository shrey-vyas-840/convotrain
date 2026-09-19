"""Conversation ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Conversation(Base):
    """Stored owner-training conversation turn."""

    __tablename__ = "conversations"

    __table_args__ = (
        Index("idx_conversations_restaurant", "restaurant_id"),
        Index("idx_conversations_session", "session_id"),
        Index(
            "idx_conversations_restaurant_session",
            "restaurant_id",
            "session_id",
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
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    speaker_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    input_language: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    input_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    output_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )