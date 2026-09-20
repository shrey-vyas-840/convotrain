"""Guided owner text-training service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.training_session import TrainingSession
from app.services.restaurant import get_owned_restaurant


QUESTION_CATALOG: tuple[tuple[str, str], ...] = (
    (
        "restaurant_identity",
        "Tell me the name of your restaurant and briefly describe what it is.",
    ),
    (
        "location",
        "Where is your restaurant located?",
    ),
    (
        "opening_hours",
        "What are your regular opening hours?",
    ),
    (
        "menu_and_specialties",
        "What food, drinks, specialties, or signature items should customers know about?",
    ),
    (
        "ordering_and_delivery",
        "How can customers order from you, including delivery, takeaway, or online ordering?",
    ),
    (
        "reservations",
        "Do you accept reservations? If so, how do they work?",
    ),
    (
        "additional_information",
        "Is there anything else about your restaurant that you want customers to know?",
    ),
)


def get_question_text(question_key: str) -> str:
    """Return the deterministic question text for a question key."""
    for key, question in QUESTION_CATALOG:
        if key == question_key:
            return question

    raise ValueError(f"Unknown training question key: {question_key}")


def get_next_question_key(question_key: str) -> str | None:
    """Return the deterministic next question key."""
    for index, (key, _) in enumerate(QUESTION_CATALOG):
        if key == question_key:
            if index + 1 < len(QUESTION_CATALOG):
                return QUESTION_CATALOG[index + 1][0]
            return None

    raise ValueError(f"Unknown training question key: {question_key}")


def get_training_session(
    db: Session,
    restaurant_id: UUID,
    session_id: UUID,
) -> TrainingSession:
    """Return a tenant-scoped training session."""
    session = db.scalar(
        select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.restaurant_id == restaurant_id,
        )
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        )

    return session


def create_training_session(
    db: Session,
    restaurant_id: UUID,
) -> TrainingSession:
    """Create a new deterministic guided training session."""
    session = TrainingSession(
        restaurant_id=restaurant_id,
        state="active",
        current_question_key=QUESTION_CATALOG[0][0],
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def complete_training_session(
    db: Session,
    session: TrainingSession,
) -> TrainingSession:
    """Explicitly complete an active guided training session."""
    if session.state == "completed":
        return session

    if session.state != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session cannot be completed from its current state",
        )

    session.state = "completed"
    session.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(session)

    return session


def add_owner_message(
    db: Session,
    session: TrainingSession,
    input_text: str,
    input_language: str | None,
) -> Conversation:
    """Persist the complete owner message and advance the guided flow."""
    if session.state != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is not active",
        )

    next_question_key = get_next_question_key(session.current_question_key)

    if next_question_key is None:
        output_text = (
            "Thank you. The guided training session is ready to be completed."
        )
    else:
        output_text = get_question_text(next_question_key)
        session.current_question_key = next_question_key

    session.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    conversation = Conversation(
        restaurant_id=session.restaurant_id,
        session_id=session.id,
        speaker_type="owner",
        input_language=input_language,
        input_text=input_text,
        output_text=output_text,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation
