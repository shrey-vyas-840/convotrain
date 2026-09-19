"""Restaurant membership service layer."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.restaurant_member import RestaurantMember
from app.models.user import User
from app.schemas.restaurant_member import (
    RestaurantMemberCreate,
    RestaurantMemberUpdate,
)


def get_owned_restaurant(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
) -> Restaurant:
    """Return a restaurant owned by the authenticated user."""

    restaurant = db.scalar(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == owner_id,
            Restaurant.deleted_at.is_(None),
        )
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return restaurant


def add_member(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
    payload: RestaurantMemberCreate,
) -> RestaurantMember:
    """Add a user to an owned restaurant."""

    get_owned_restaurant(db, restaurant_id, owner_id)

    user = db.scalar(
        select(User).where(User.id == payload.user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_member = db.scalar(
        select(RestaurantMember).where(
            RestaurantMember.restaurant_id == restaurant_id,
            RestaurantMember.user_id == payload.user_id,
        )
    )

    if existing_member is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this restaurant",
        )

    member = RestaurantMember(
        restaurant_id=restaurant_id,
        user_id=payload.user_id,
        role=payload.role,
        status=payload.status,
        invited_by=owner_id,
    )

    db.add(member)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this restaurant",
        ) from exc

    db.refresh(member)

    return member


def list_members(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
) -> list[RestaurantMember]:
    """List members of an owned restaurant."""

    get_owned_restaurant(db, restaurant_id, owner_id)

    return list(
        db.scalars(
            select(RestaurantMember)
            .where(RestaurantMember.restaurant_id == restaurant_id)
            .order_by(RestaurantMember.created_at.asc())
        )
    )


def get_member(
    db: Session,
    restaurant_id: UUID,
    member_id: UUID,
    owner_id: UUID,
) -> RestaurantMember:
    """Return one member from an owned restaurant."""

    get_owned_restaurant(db, restaurant_id, owner_id)

    member = db.scalar(
        select(RestaurantMember).where(
            RestaurantMember.id == member_id,
            RestaurantMember.restaurant_id == restaurant_id,
        )
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant member not found",
        )

    return member


def update_member(
    db: Session,
    member: RestaurantMember,
    payload: RestaurantMemberUpdate,
) -> RestaurantMember:
    """Update a member's role or status."""

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)

    member.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(member)

    return member


def remove_member(
    db: Session,
    member: RestaurantMember,
) -> None:
    """Mark a restaurant member as removed."""

    member.status = "removed"
    member.updated_at = datetime.now(timezone.utc)

    db.commit()
