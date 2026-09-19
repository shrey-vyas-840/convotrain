"""Knowledge fact API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.knowledge_fact import (
    KnowledgeFactCreate,
    KnowledgeFactResponse,
    KnowledgeFactUpdate,
)
from app.services.knowledge_fact import (
    create_fact,
    delete_fact,
    get_fact,
    list_facts,
    update_fact,
)

router = APIRouter(
    prefix="/api/v1/restaurants/{restaurant_id}/knowledge-facts",
    tags=["knowledge facts"],
)


@router.post(
    "",
    response_model=KnowledgeFactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_fact(
    restaurant_id: UUID,
    payload: KnowledgeFactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeFactResponse:
    """Create a knowledge fact for an owned restaurant."""

    return create_fact(
        db=db,
        restaurant_id=restaurant_id,
        owner_id=current_user.id,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[KnowledgeFactResponse],
)
def get_knowledge_facts(
    restaurant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[KnowledgeFactResponse]:
    """List non-deleted knowledge facts."""

    return list_facts(
        db=db,
        restaurant_id=restaurant_id,
        owner_id=current_user.id,
    )


@router.get(
    "/{fact_id}",
    response_model=KnowledgeFactResponse,
)
def get_one_knowledge_fact(
    restaurant_id: UUID,
    fact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeFactResponse:
    """Get one non-deleted knowledge fact."""

    return get_fact(
        db=db,
        restaurant_id=restaurant_id,
        fact_id=fact_id,
        owner_id=current_user.id,
    )


@router.patch(
    "/{fact_id}",
    response_model=KnowledgeFactResponse,
)
def update_one_knowledge_fact(
    restaurant_id: UUID,
    fact_id: UUID,
    payload: KnowledgeFactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeFactResponse:
    """Update one knowledge fact."""

    fact = get_fact(
        db=db,
        restaurant_id=restaurant_id,
        fact_id=fact_id,
        owner_id=current_user.id,
    )

    return update_fact(
        db=db,
        fact=fact,
        payload=payload,
    )


@router.delete(
    "/{fact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_one_knowledge_fact(
    restaurant_id: UUID,
    fact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete one knowledge fact."""

    fact = get_fact(
        db=db,
        restaurant_id=restaurant_id,
        fact_id=fact_id,
        owner_id=current_user.id,
    )

    delete_fact(
        db=db,
        fact=fact,
    )
