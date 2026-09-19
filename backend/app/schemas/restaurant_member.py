"""Restaurant membership request and response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


MemberRole = Literal["owner", "manager", "staff"]
MemberStatus = Literal["active", "invited", "suspended", "removed"]


class RestaurantMemberCreate(BaseModel):
    """Fields accepted when adding a restaurant member."""

    user_id: UUID
    role: MemberRole = "staff"
    status: MemberStatus = "active"


class RestaurantMemberUpdate(BaseModel):
    """Fields that can be updated on a restaurant member."""

    role: MemberRole | None = None
    status: MemberStatus | None = None


class RestaurantMemberResponse(BaseModel):
    """Public restaurant membership representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    user_id: UUID
    role: MemberRole
    status: MemberStatus
    created_at: datetime
    updated_at: datetime
    joined_at: datetime
    invited_by: UUID | None
