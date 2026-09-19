"""Restaurant API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
)
from app.services.restaurant import (
    create_restaurant,
    delete_restaurant,
    get_owned_restaurant,
    list_owned_restaurants,
    update_restaurant,
)

router = APIRouter(
    prefix="/api/v1/restaurants",
    tags=["restaurants"],
)


@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: RestaurantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RestaurantResponse:
    """Create a restaurant for the authenticated user."""

    return create_restaurant(
        db=db,
        payload=payload,
        user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[RestaurantResponse],
)
def list_restaurants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RestaurantResponse]:
    """List restaurants owned by the authenticated user."""

    return list_owned_restaurants(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def get_restaurant(
    restaurant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RestaurantResponse:
    """Get one restaurant owned by the authenticated user."""

    return get_owned_restaurant(
        db=db,
        restaurant_id=restaurant_id,
        user_id=current_user.id,
    )


@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def update(
    restaurant_id: UUID,
    payload: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RestaurantResponse:
    """Update an owned restaurant."""

    restaurant = get_owned_restaurant(
        db=db,
        restaurant_id=restaurant_id,
        user_id=current_user.id,
    )

    return update_restaurant(
        db=db,
        restaurant=restaurant,
        payload=payload,
        user_id=current_user.id,
    )


@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    restaurant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete an owned restaurant."""

    restaurant = get_owned_restaurant(
        db=db,
        restaurant_id=restaurant_id,
        user_id=current_user.id,
    )

    delete_restaurant(
        db=db,
        restaurant=restaurant,
        user_id=current_user.id,
    )