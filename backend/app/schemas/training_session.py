"""Training session schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TrainingSessionResponse(BaseModel):
    """Training session response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    state: str
    current_question_key: str
    current_question: str
    created_at: datetime
    updated_at: datetime