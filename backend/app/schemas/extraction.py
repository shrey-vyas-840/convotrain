"""Pydantic contracts for knowledge extraction."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ExtractionTurn(BaseModel):
    """A single turn from a guided knowledge source."""

    turn_id: str = Field(min_length=1)
    speaker_type: Literal["owner", "system"]
    text: str = Field(min_length=1)
    input_language: str | None = Field(default=None, max_length=10)


class KnowledgeSource(BaseModel):
    """Generic source of restaurant knowledge."""

    source_type: Literal["guided_transcript", "owner_input"]
    source_id: str | None = None
    source_text: str | None = None
    turns: list[ExtractionTurn] = Field(default_factory=list)
    source_language: str | None = Field(default=None, max_length=10)

    @model_validator(mode="after")
    def validate_source_shape(self) -> "KnowledgeSource":
        if self.source_type == "guided_transcript":
            if not self.turns:
                raise ValueError(
                    "guided_transcript requires at least one turn"
                )

            if self.source_text is not None:
                raise ValueError(
                    "guided_transcript must not use source_text"
                )

            if not any(
                turn.speaker_type == "owner"
                for turn in self.turns
            ):
                raise ValueError(
                    "guided_transcript requires at least one owner turn"
                )

        elif self.source_type == "owner_input":
            if not self.source_text or not self.source_text.strip():
                raise ValueError(
                    "owner_input requires non-empty source_text"
                )

            if self.turns:
                raise ValueError(
                    "owner_input must not contain turns"
                )

        return self


class ExtractionInput(BaseModel):
    """Input provided to the provider-independent extractor."""

    source: KnowledgeSource
    current_question_key: str | None = Field(
        default=None,
        max_length=100,
    )
    current_question_text: str | None = None

    @model_validator(mode="after")
    def validate_question_context(self) -> "ExtractionInput":
        if self.source.source_type == "owner_input":
            if (
                self.current_question_key is not None
                or self.current_question_text is not None
            ):
                raise ValueError(
                    "current question context is only valid for "
                    "guided_transcript"
                )

        return self


class ExtractedFact(BaseModel):
    """A single candidate fact returned by an extraction provider."""

    category: str = Field(min_length=1, max_length=50)
    fact_key: str = Field(min_length=1, max_length=150)
    fact_value: dict
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    uncertain: bool = False
    source_turn_id: str | None = None
    source_text: str = Field(min_length=1)


class ExtractionOutput(BaseModel):
    """Validated extraction result."""

    facts: list[ExtractedFact]
