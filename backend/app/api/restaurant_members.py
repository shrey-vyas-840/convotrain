"""Restaurant membership API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.restaurant_member import (
    RestaurantMemberCreate,
    RestaurantMemberResponse,
    RestaurantMemberUpdate,
)
from app.services.restaurant_member import (
    add_member,
    get_member,
    list_members,
    remove_member,
    update_member,
)

router = APIRouter(
    prefix="/api/v1/restaurants/{restaurant_id}/members",
    tags=["restaurant members"],
)


@router.post(
    "",
    response_model=RestaurantMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_member(
    restaurant_id: UUID,
    payload: RestaurantMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RestaurantMemberResponse:
    """Add a member to an owned restaurant."""

    return add_member(
        db=db,
        restaurant_id=restaurant_id,
        owner_id=current_user.id,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[RestaurantMemberResponse],
)
def get_members(
    restaurant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RestaurantMemberResponse]:
    """List members of an owned restaurant."""

    return list_members(
        db=db,
        restaurant_id=restaurant_id,
        owner_id=current_user.id,
    )


@router.get(
    "/{member_id}",
    response_model=RestaurantMemberResponse,
)
def get_one_member(
    restaurant_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RestaurantMemberResponse:
    """Get one member from an owned restaurant."""

    return get_member(
        db=db,
        restaurant_id=restaurant_id,
        member_id=member_id,
        owner_id=current_user.id,
    )


@router.patch(
    "/{member_id}",
    response_model=RestaurantMemberResponse,
)
def update_one_member(
    restaurant_id: UUID,
    member_id: UUID,
    payload: RestaurantMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RestaurantMemberResponse:
    """Update a member's role or status."""

    member = get_member(
        db=db,
        restaurant_id=restaurant_id,
        member_id=member_id,
        owner_id=current_user.id,
    )

    return update_member(
        db=db,
        member=member,
        payload=payload,
    )


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    restaurant_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Mark a restaurant member as removed."""

    member = get_member(
        db=db,
        restaurant_id=restaurant_id,
        member_id=member_id,
        owner_id=current_user.id,
    )

    remove_member(
        db=db,
        member=member,
    )
