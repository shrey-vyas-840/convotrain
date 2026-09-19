"""Restaurant request and response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RestaurantCreate(BaseModel):
    """Fields accepted when creating a restaurant."""

    name: str = Field(min_length=1, max_length=200)
    cuisine_type: str | None = Field(default=None, max_length=100)
    timezone: str = Field(default="UTC", max_length=100)
    location: str | None = None
    phone_number: str | None = Field(default=None, max_length=20)
    supported_languages: list[str] = Field(
        default_factory=lambda: ["en"],
        min_length=1,
    )


class RestaurantUpdate(BaseModel):
    """Fields that can be updated on a restaurant."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    cuisine_type: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)
    location: str | None = None
    phone_number: str | None = Field(default=None, max_length=20)
    supported_languages: list[str] | None = Field(
        default=None,
        min_length=1,
    )


class RestaurantResponse(BaseModel):
    """Public restaurant representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    cuisine_type: str | None
    timezone: str
    location: str | None
    phone_number: str | None
    lifecycle_status: str
    created_at: datetime
    updated_at: datetime
    supported_languages: list[str]
