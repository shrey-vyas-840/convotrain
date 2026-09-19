"""Conversation schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Owner message payload."""

    input_text: str = Field(min_length=1)
    input_language: str | None = None


class ConversationResponse(BaseModel):
    """Conversation response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    session_id: UUID
    speaker_type: str
    input_language: str | None
    input_text: str | None
    output_text: str | None
    created_at: datetime