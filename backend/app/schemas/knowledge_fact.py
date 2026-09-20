"""Knowledge fact request and response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeFactCreate(BaseModel):
    """Fields accepted when manually creating a knowledge fact."""

    category: str = Field(min_length=1, max_length=50)
    fact_key: str = Field(min_length=1, max_length=150)
    fact_value_json: dict
    source_text: str = Field(min_length=1)
    source_language: str = Field(min_length=1, max_length=10)
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class KnowledgeFactUpdate(BaseModel):
    """Fields editable on a pending knowledge candidate."""

    category: str | None = Field(default=None, min_length=1, max_length=50)
    fact_key: str | None = Field(default=None, min_length=1, max_length=150)
    fact_value_json: dict | None = None


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
    source_turn_id: UUID | None
    confidence_score: float | None
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class KnowledgeReviewItem(BaseModel):
    """Pending candidate with its current approved comparison."""

    candidate: KnowledgeFactResponse
    current_approved: KnowledgeFactResponse | None


class KnowledgeReviewEdit(BaseModel):
    """Owner edit applied to a pending candidate."""

    category: str | None = Field(default=None, min_length=1, max_length=50)
    fact_key: str | None = Field(default=None, min_length=1, max_length=150)
    fact_value_json: dict | None = None


class KnowledgeCandidatePersistResponse(BaseModel):
    """Result of persisting extraction candidates."""

    created: list[KnowledgeFactResponse]
    existing_equivalent: list[KnowledgeFactResponse]
