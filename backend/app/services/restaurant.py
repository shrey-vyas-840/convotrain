"""Restaurant service layer."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def create_restaurant(
    db: Session,
    payload: RestaurantCreate,
    user_id: UUID,
) -> Restaurant:
    """Create a restaurant owned by the authenticated user."""

    restaurant = Restaurant(
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        **payload.model_dump(),
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant


def get_owned_restaurant(
    db: Session,
    restaurant_id: UUID,
    user_id: UUID,
) -> Restaurant:
    """Return an active restaurant owned by the authenticated user."""

    restaurant = db.scalar(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == user_id,
            Restaurant.deleted_at.is_(None),
        )
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return restaurant


def list_owned_restaurants(
    db: Session,
    user_id: UUID,
) -> list[Restaurant]:
    """List active restaurants owned by the authenticated user."""

    return list(
        db.scalars(
            select(Restaurant)
            .where(
                Restaurant.owner_id == user_id,
                Restaurant.deleted_at.is_(None),
            )
            .order_by(Restaurant.created_at.desc())
        )
    )


def update_restaurant(
    db: Session,
    restaurant: Restaurant,
    payload: RestaurantUpdate,
    user_id: UUID,
) -> Restaurant:
    """Update an owned restaurant."""

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)

    restaurant.updated_by = user_id
    restaurant.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(restaurant)

    return restaurant


def delete_restaurant(
    db: Session,
    restaurant: Restaurant,
    user_id: UUID,
) -> None:
    """Soft-delete an owned restaurant."""

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    restaurant.deleted_at = now
    restaurant.updated_by = user_id
    restaurant.updated_at = now

    db.commit()
