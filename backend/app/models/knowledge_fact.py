"""Knowledge fact ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeFact(Base):
    """Structured restaurant knowledge fact."""

    __tablename__ = "knowledge_facts"

    __table_args__ = (
        Index(
            "idx_knowledge_facts_restaurant",
            "restaurant_id",
        ),
        Index(
            "idx_knowledge_facts_restaurant_status",
            "restaurant_id",
            "status",
        ),
        Index(
            "idx_knowledge_facts_restaurant_category",
            "restaurant_id",
            "category",
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

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    fact_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    fact_value_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    source_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
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

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
