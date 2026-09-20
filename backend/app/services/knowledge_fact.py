"""Knowledge fact persistence and owner-review service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.knowledge_fact import KnowledgeFact
from app.models.restaurant import Restaurant
from app.models.training_session import TrainingSession
from app.schemas.extraction import ExtractionOutput, ExtractedFact
from app.schemas.knowledge_fact import (
    KnowledgeFactCreate,
    KnowledgeReviewEdit,
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


def _logical_key_filter(
    restaurant_id: UUID,
    category: str,
    fact_key: str,
):
    return (
        KnowledgeFact.restaurant_id == restaurant_id,
        KnowledgeFact.category == category,
        KnowledgeFact.fact_key == fact_key,
        KnowledgeFact.deleted_at.is_(None),
    )


def get_current_approved_fact(
    db: Session,
    restaurant_id: UUID,
    category: str,
    fact_key: str,
) -> KnowledgeFact | None:
    """Return only the highest-version approved fact for a logical key."""
    return db.scalar(
        select(KnowledgeFact)
        .where(
            *_logical_key_filter(
                restaurant_id,
                category,
                fact_key,
            ),
            KnowledgeFact.status == "approved",
        )
        .order_by(KnowledgeFact.version.desc(), KnowledgeFact.created_at.desc())
        .limit(1)
    )


def _next_version(
    db: Session,
    restaurant_id: UUID,
    category: str,
    fact_key: str,
) -> int:
    """Return the next version number in the approved-value history.

    Pending and rejected candidates do not consume version numbers.
    """
    latest = db.scalar(
        select(KnowledgeFact)
        .where(
            KnowledgeFact.restaurant_id == restaurant_id,
            KnowledgeFact.category == category,
            KnowledgeFact.fact_key == fact_key,
            KnowledgeFact.status == "approved",
            KnowledgeFact.deleted_at.is_(None),
        )
        .order_by(KnowledgeFact.version.desc())
        .limit(1)
    )

    return 1 if latest is None else latest.version + 1


def _validate_session_provenance(
    db: Session,
    session: TrainingSession,
    extracted_fact: ExtractedFact,
) -> Conversation | None:
    """Validate that guided provenance belongs to this completed session."""
    if extracted_fact.source_turn_id is None:
        return None

    try:
        conversation_id = UUID(extracted_fact.source_turn_id)
    except ValueError as exc:
        raise ValueError("Invalid source_turn_id") from exc

    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.restaurant_id == session.restaurant_id,
            Conversation.session_id == session.id,
            Conversation.speaker_type == "owner",
        )
    )

    if conversation is None:
        raise ValueError(
            "Extracted fact provenance does not belong to the originating "
            "owner conversation in this session"
        )

    if not conversation.input_text or extracted_fact.source_text not in conversation.input_text:
        raise ValueError(
            "Extracted fact source_text is not grounded in the originating "
            "owner conversation"
        )

    return conversation


def persist_extraction_candidates(
    db: Session,
    session: TrainingSession,
    extraction_output: ExtractionOutput,
) -> tuple[list[KnowledgeFact], list[KnowledgeFact]]:
    """
    Persist validated extraction candidates for one completed session.

    Returns:
        (created_candidates, equivalent_existing_facts)
    """
    if session.state != "completed":
        raise ValueError(
            "KnowledgeFact persistence requires a completed training session"
        )

    created: list[KnowledgeFact] = []
    equivalent_existing: list[KnowledgeFact] = []

    for extracted_fact in extraction_output.facts:
        conversation = _validate_session_provenance(
            db,
            session,
            extracted_fact,
        )

        source_language = (
            conversation.input_language
            if conversation is not None and conversation.input_language
            else "unknown"
        )

        current = get_current_approved_fact(
            db,
            session.restaurant_id,
            extracted_fact.category,
            extracted_fact.fact_key,
        )

        if (
            current is not None
            and current.fact_value_json == extracted_fact.fact_value
        ):
            # Preserve the new session's evidence without creating a
            # competing approved/current value.
            duplicate_candidate = db.scalar(
                select(KnowledgeFact).where(
                    *_logical_key_filter(
                        session.restaurant_id,
                        extracted_fact.category,
                        extracted_fact.fact_key,
                    ),
                    KnowledgeFact.status == "pending",
                    KnowledgeFact.source_turn_id
                    == (
                        conversation.id
                        if conversation is not None
                        else None
                    ),
                )
            )

            if duplicate_candidate is None:
                duplicate_candidate = KnowledgeFact(
                    restaurant_id=session.restaurant_id,
                    category=extracted_fact.category,
                    fact_key=extracted_fact.fact_key,
                    fact_value_json=extracted_fact.fact_value,
                    source_text=extracted_fact.source_text,
                    source_language=source_language,
                    source_turn_id=(
                        conversation.id
                        if conversation is not None
                        else None
                    ),
                    confidence_score=extracted_fact.confidence,
                    status="pending",
                    version=_next_version(
                        db,
                        session.restaurant_id,
                        extracted_fact.category,
                        extracted_fact.fact_key,
                    ),
                )
                db.add(duplicate_candidate)
                db.flush()

            equivalent_existing.append(current)
            continue

        candidate = KnowledgeFact(
            restaurant_id=session.restaurant_id,
            category=extracted_fact.category,
            fact_key=extracted_fact.fact_key,
            fact_value_json=extracted_fact.fact_value,
            source_text=extracted_fact.source_text,
            source_language=source_language,
            source_turn_id=(
                conversation.id
                if conversation is not None
                else None
            ),
            confidence_score=extracted_fact.confidence,
            status="pending",
            version=_next_version(
                db,
                session.restaurant_id,
                extracted_fact.category,
                extracted_fact.fact_key,
            ),
        )

        db.add(candidate)
        db.flush()
        created.append(candidate)

    db.commit()

    for fact in [*created]:
        db.refresh(fact)

    for fact in equivalent_existing:
        db.refresh(fact)

    return created, equivalent_existing


def list_facts(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
) -> list[KnowledgeFact]:
    """List non-deleted knowledge facts for an owned restaurant."""
    get_owned_restaurant(db, restaurant_id, owner_id)

    return list(
        db.scalars(
            select(KnowledgeFact)
            .where(
                KnowledgeFact.restaurant_id == restaurant_id,
                KnowledgeFact.deleted_at.is_(None),
            )
            .order_by(
                KnowledgeFact.category.asc(),
                KnowledgeFact.fact_key.asc(),
                KnowledgeFact.version.desc(),
            )
        )
    )


def list_review_candidates(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
) -> list[tuple[KnowledgeFact, KnowledgeFact | None]]:
    """List pending candidates with their current approved comparison."""
    get_owned_restaurant(db, restaurant_id, owner_id)

    candidates = list(
        db.scalars(
            select(KnowledgeFact)
            .where(
                KnowledgeFact.restaurant_id == restaurant_id,
                KnowledgeFact.status == "pending",
                KnowledgeFact.deleted_at.is_(None),
            )
            .order_by(KnowledgeFact.created_at.asc())
        )
    )

    return [
        (
            candidate,
            get_current_approved_fact(
                db,
                restaurant_id,
                candidate.category,
                candidate.fact_key,
            ),
        )
        for candidate in candidates
    ]


def get_fact(
    db: Session,
    restaurant_id: UUID,
    fact_id: UUID,
    owner_id: UUID,
) -> KnowledgeFact:
    """Return one non-deleted knowledge fact."""
    get_owned_restaurant(db, restaurant_id, owner_id)

    fact = db.scalar(
        select(KnowledgeFact).where(
            KnowledgeFact.id == fact_id,
            KnowledgeFact.restaurant_id == restaurant_id,
            KnowledgeFact.deleted_at.is_(None),
        )
    )

    if fact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge fact not found",
        )

    return fact


def edit_pending_fact(
    db: Session,
    fact: KnowledgeFact,
    payload: KnowledgeReviewEdit,
) -> KnowledgeFact:
    """Edit only the knowledge content of a pending candidate."""
    if fact.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending knowledge candidates can be edited",
        )

    values = payload.model_dump(exclude_unset=True)

    for field, value in values.items():
        setattr(fact, field, value)

    fact.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(fact)

    return fact


def approve_fact(
    db: Session,
    fact: KnowledgeFact,
) -> KnowledgeFact:
    """Approve a pending candidate without rewriting historical facts."""
    if fact.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending knowledge candidates can be approved",
        )

    current = get_current_approved_fact(
        db,
        fact.restaurant_id,
        fact.category,
        fact.fact_key,
    )

    if (
        current is not None
        and current.id != fact.id
        and current.fact_value_json == fact.fact_value_json
    ):
        # The knowledge value is already represented by the current
        # approved fact. Preserve this pending candidate and its
        # provenance, but do not create another approved record.
        return fact

    # Recalculate from approved history at approval time. This prevents
    # pending candidates from consuming approved-version numbers and
    # also handles another candidate having been approved meanwhile.
    next_version = _next_version(
        db,
        fact.restaurant_id,
        fact.category,
        fact.fact_key,
    )

    fact.version = next_version
    fact.status = "approved"
    fact.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(fact)

    return fact


def create_fact(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
    payload: KnowledgeFactCreate,
) -> KnowledgeFact:
    """
    Retain the existing manual-create API.

    Manual creation remains pending and does not bypass owner review.
    """
    get_owned_restaurant(db, restaurant_id, owner_id)

    fact = KnowledgeFact(
        restaurant_id=restaurant_id,
        category=payload.category,
        fact_key=payload.fact_key,
        fact_value_json=payload.fact_value_json,
        source_text=payload.source_text,
        source_language=payload.source_language,
        confidence_score=payload.confidence_score,
        status="pending",
        version=_next_version(
            db,
            restaurant_id,
            payload.category,
            payload.fact_key,
        ),
    )

    db.add(fact)
    db.commit()
    db.refresh(fact)

    return fact

def reject_fact(
    db: Session,
    fact: KnowledgeFact,
) -> KnowledgeFact:
    """Reject a pending candidate while retaining it for audit."""
    if fact.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending knowledge candidates can be rejected",
        )

    fact.status = "rejected"
    fact.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(fact)

    return fact


def delete_fact(
    db: Session,
    fact: KnowledgeFact,
) -> None:
    """Soft-delete one knowledge fact."""
    fact.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    fact.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
