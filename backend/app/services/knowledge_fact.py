"""Knowledge fact service layer."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_fact import KnowledgeFact
from app.models.restaurant import Restaurant
from app.schemas.knowledge_fact import (
    KnowledgeFactCreate,
    KnowledgeFactUpdate,
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


def create_fact(
    db: Session,
    restaurant_id: UUID,
    owner_id: UUID,
    payload: KnowledgeFactCreate,
) -> KnowledgeFact:
    """Create a knowledge fact for an owned restaurant."""

    get_owned_restaurant(db, restaurant_id, owner_id)

    fact = KnowledgeFact(
        restaurant_id=restaurant_id,
        category=payload.category,
        fact_key=payload.fact_key,
        fact_value_json=payload.fact_value_json,
        source_text=payload.source_text,
        source_language=payload.source_language,
        confidence_score=payload.confidence_score,
        status=payload.status,
    )

    db.add(fact)
    db.commit()
    db.refresh(fact)

    return fact


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
            .order_by(KnowledgeFact.created_at.asc())
        )
    )


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


def update_fact(
    db: Session,
    fact: KnowledgeFact,
    payload: KnowledgeFactUpdate,
) -> KnowledgeFact:
    """Update a knowledge fact without changing its version."""

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(fact, field, value)

    fact.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(fact)

    return fact


def delete_fact(
    db: Session,
    fact: KnowledgeFact,
) -> None:
    """Soft-delete a knowledge fact."""

    fact.deleted_at = datetime.now(timezone.utc)
    fact.updated_at = datetime.now(timezone.utc)

    db.commit()
