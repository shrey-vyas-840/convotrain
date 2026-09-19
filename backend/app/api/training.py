"""Guided owner text-training API."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)
from app.schemas.training_session import TrainingSessionResponse
from app.services.training import (
    add_owner_message,
    create_training_session,
    get_owned_restaurant,
    get_question_text,
    get_training_session,
)


router = APIRouter(
    prefix="/api/v1/restaurants/{restaurant_id}/training",
    tags=["training"],
)


def session_response(session) -> TrainingSessionResponse:
    """Build a training session response."""
    return TrainingSessionResponse(
        id=session.id,
        restaurant_id=session.restaurant_id,
        state=session.state,
        current_question_key=session.current_question_key,
        current_question=get_question_text(session.current_question_key),
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.post(
    "/sessions",
    response_model=TrainingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_training_session(
    restaurant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingSessionResponse:
    """Start a guided owner text-training session."""
    get_owned_restaurant(db, restaurant_id, current_user.id)

    session = create_training_session(db, restaurant_id)

    return session_response(session)


@router.get(
    "/sessions/{session_id}",
    response_model=TrainingSessionResponse,
)
def get_training_session_endpoint(
    restaurant_id: UUID,
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingSessionResponse:
    """Get the current state of a training session."""
    get_owned_restaurant(db, restaurant_id, current_user.id)

    session = get_training_session(
        db,
        restaurant_id,
        session_id,
    )

    return session_response(session)


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_owner_message(
    restaurant_id: UUID,
    session_id: UUID,
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Store a complete owner message and advance the guided interview."""
    get_owned_restaurant(db, restaurant_id, current_user.id)

    session = get_training_session(
        db,
        restaurant_id,
        session_id,
    )

    return add_owner_message(
        db,
        session,
        payload.input_text,
        payload.input_language,
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[ConversationResponse],
)
def get_training_history(
    restaurant_id: UUID,
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationResponse]:
    """Return chronological conversation history for a training session."""
    get_owned_restaurant(db, restaurant_id, current_user.id)

    get_training_session(
        db,
        restaurant_id,
        session_id,
    )

    return list(
        db.scalars(
            select(Conversation)
            .where(
                Conversation.restaurant_id == restaurant_id,
                Conversation.session_id == session_id,
            )
            .order_by(
                Conversation.created_at.asc(),
                Conversation.id.asc(),
            )
        )
    )