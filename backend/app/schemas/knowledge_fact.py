"""Knowledge fact request and response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class KnowledgeFactCreate(BaseModel):
    """Fields accepted when creating a knowledge fact."""

    category: str
    fact_key: str
    fact_value_json: dict
    source_text: str
    source_language: str
    confidence_score: float | None = None
    status: str = "pending"


class KnowledgeFactUpdate(BaseModel):
    """Fields that can be updated on a knowledge fact."""

    category: str | None = None
    fact_key: str | None = None
    fact_value_json: dict | None = None
    source_text: str | None = None
    source_language: str | None = None
    confidence_score: float | None = None
    status: str | None = None


class KnowledgeFactResponse(BaseModel):
    """Public knowledge fact representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    category: str
    fact_key: str
    fact_value_json: dict
    source_text: str
    source_language: str
    confidence_score: float | None
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
