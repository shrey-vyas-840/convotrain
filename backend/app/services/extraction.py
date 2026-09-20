"""Provider-independent knowledge extraction interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.training_session import TrainingSession
from app.schemas.extraction import (
    ExtractedFact,
    ExtractionInput,
    ExtractionOutput,
    ExtractionTurn,
    KnowledgeSource,
)


class KnowledgeExtractor(ABC):
    """Application-level contract for knowledge extraction providers."""

    @abstractmethod
    def extract(self, request: ExtractionInput) -> ExtractionOutput:
        """Extract candidate knowledge facts from a generic knowledge source."""
        raise NotImplementedError


def _build_guided_source(
    db: Session,
    session: TrainingSession,
) -> KnowledgeSource:
    """Build an immutable extraction source from one completed session only."""
    conversations = list(
        db.scalars(
            select(Conversation)
            .where(
                Conversation.restaurant_id == session.restaurant_id,
                Conversation.session_id == session.id,
            )
            .order_by(
                Conversation.created_at.asc(),
                Conversation.id.asc(),
            )
        )
    )

    if not conversations:
        raise ValueError("Completed training session has no conversation turns")

    turns: list[ExtractionTurn] = []
    owner_languages: list[str] = []

    for conversation in conversations:
        if conversation.speaker_type != "owner":
            raise ValueError(
                "Unsupported conversation speaker type in guided transcript"
            )

        if not conversation.input_text:
            raise ValueError(
                f"Owner conversation {conversation.id} has no input text"
            )

        turns.append(
            ExtractionTurn(
                turn_id=str(conversation.id),
                speaker_type="owner",
                text=conversation.input_text,
                input_language=conversation.input_language,
            )
        )

        if conversation.input_language:
            owner_languages.append(conversation.input_language)

        if conversation.output_text:
            turns.append(
                ExtractionTurn(
                    turn_id=f"{conversation.id}:system",
                    speaker_type="system",
                    text=conversation.output_text,
                )
            )

    source_language = (
        owner_languages[0]
        if owner_languages and all(
            language == owner_languages[0]
            for language in owner_languages
        )
        else None
    )

    return KnowledgeSource(
        source_type="guided_transcript",
        source_id=str(session.id),
        turns=turns,
        source_language=source_language,
    )


def _validate_extraction_provenance(
    output: ExtractionOutput,
    owner_source_text_by_id: dict[str, str],
) -> ExtractionOutput:
    """Reject extracted facts whose provenance is not grounded in owner text."""
    for fact in output.facts:
        _validate_fact_provenance(fact, owner_source_text_by_id)

    return output


def _validate_fact_provenance(
    fact: ExtractedFact,
    owner_source_text_by_id: dict[str, str],
) -> None:
    """Validate one extracted fact against the session's owner transcript."""
    if fact.source_turn_id is None:
        raise ValueError(
            "Guided transcript fact is missing source_turn_id"
        )

    source_text = owner_source_text_by_id.get(fact.source_turn_id)

    if source_text is None:
        raise ValueError(
            f"Fact source_turn_id does not reference an owner turn in this session: "
            f"{fact.source_turn_id}"
        )

    if fact.source_text not in source_text:
        raise ValueError(
            "Fact source_text is not an exact substring of the referenced "
            "owner turn"
        )


def extract_completed_training_session(
    db: Session,
    session: TrainingSession,
    extractor: KnowledgeExtractor,
) -> ExtractionOutput:
    """
    Extract knowledge from exactly one completed training session.

    The extractor receives only this session's transcript. Existing knowledge
    from other sessions is intentionally not supplied.
    """
    if session.state != "completed":
        raise ValueError(
            "Knowledge extraction requires a completed training session"
        )

    conversations = list(
        db.scalars(
            select(Conversation)
            .where(
                Conversation.restaurant_id == session.restaurant_id,
                Conversation.session_id == session.id,
            )
            .order_by(
                Conversation.created_at.asc(),
                Conversation.id.asc(),
            )
        )
    )

    owner_source_text_by_id: dict[str, str] = {}

    for conversation in conversations:
        if conversation.speaker_type != "owner":
            raise ValueError(
                "Unsupported conversation speaker type in guided transcript"
            )

        if not conversation.input_text:
            raise ValueError(
                f"Owner conversation {conversation.id} has no input text"
            )

        owner_source_text_by_id[str(conversation.id)] = conversation.input_text

    source = _build_guided_source(db, session)

    request = ExtractionInput(
        source=source,
    )

    output = extractor.extract(request)

    return _validate_extraction_provenance(
        output,
        owner_source_text_by_id,
    )
