"""Knowledge fact API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.extraction import ExtractionOutput
from app.schemas.knowledge_fact import (
    KnowledgeCandidatePersistResponse,
    KnowledgeFactCreate,
    KnowledgeFactResponse,
    KnowledgeReviewEdit,
    KnowledgeReviewItem,
)
from app.services.knowledge_fact import (
    approve_fact,
    create_fact,
    delete_fact,
    edit_pending_fact,
    get_fact,
    list_facts,
    list_review_candidates,
    persist_extraction_candidates,
    reject_fact,
)
from app.services.training import get_training_session


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
    """Create a pending knowledge fact for an owned restaurant."""
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
    "/review",
    response_model=list[KnowledgeReviewItem],
)
def get_knowledge_review(
    restaurant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[KnowledgeReviewItem]:
    """List pending candidates with current approved comparisons."""
    return [
        KnowledgeReviewItem(
            candidate=candidate,
            current_approved=current,
        )
        for candidate, current in list_review_candidates(
            db=db,
            restaurant_id=restaurant_id,
            owner_id=current_user.id,
        )
    ]


@router.post(
    "/from-sessions/{session_id}",
    response_model=KnowledgeCandidatePersistResponse,
)
def persist_session_extraction(
    restaurant_id: UUID,
    session_id: UUID,
    payload: ExtractionOutput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeCandidatePersistResponse:
    """
    Persist a validated extraction result for one completed session.

    This endpoint expects ExtractionOutput produced by the already-validated
    session extraction boundary.
    """
    from app.services.knowledge_fact import get_owned_restaurant

    get_owned_restaurant(db, restaurant_id, current_user.id)

    session = get_training_session(
        db,
        restaurant_id,
        session_id,
    )

    created, equivalent = persist_extraction_candidates(
        db=db,
        session=session,
        extraction_output=payload,
    )

    return KnowledgeCandidatePersistResponse(
        created=created,
        existing_equivalent=equivalent,
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
    payload: KnowledgeReviewEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeFactResponse:
    """Edit a pending knowledge candidate."""
    fact = get_fact(
        db=db,
        restaurant_id=restaurant_id,
        fact_id=fact_id,
        owner_id=current_user.id,
    )

    return edit_pending_fact(
        db=db,
        fact=fact,
        payload=payload,
    )


@router.post(
    "/{fact_id}/approve",
    response_model=KnowledgeFactResponse,
)
def approve_knowledge_fact(
    restaurant_id: UUID,
    fact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeFactResponse:
    """Approve one pending knowledge candidate."""
    fact = get_fact(
        db=db,
        restaurant_id=restaurant_id,
        fact_id=fact_id,
        owner_id=current_user.id,
    )

    return approve_fact(
        db=db,
        fact=fact,
    )


@router.post(
    "/{fact_id}/reject",
    response_model=KnowledgeFactResponse,
)
def reject_knowledge_fact(
    restaurant_id: UUID,
    fact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeFactResponse:
    """Reject one pending knowledge candidate."""
    fact = get_fact(
        db=db,
        restaurant_id=restaurant_id,
        fact_id=fact_id,
        owner_id=current_user.id,
    )

    return reject_fact(
        db=db,
        fact=fact,
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
