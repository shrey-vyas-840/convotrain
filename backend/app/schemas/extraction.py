"""Pydantic contracts for knowledge extraction."""

from pydantic import BaseModel, Field


class ExtractionInput(BaseModel):
    """Input provided to an extraction provider."""

    source_text: str = Field(min_length=1)
    source_language: str = Field(min_length=1, max_length=10)
    current_question_key: str | None = Field(default=None, max_length=100)
    current_question_text: str | None = None


class ExtractedFact(BaseModel):
    """A single candidate fact returned by an extraction provider."""

    category: str = Field(min_length=1, max_length=50)
    fact_key: str = Field(min_length=1, max_length=150)
    fact_value: dict
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    uncertain: bool = False
    source_text: str = Field(min_length=1)


class ExtractionOutput(BaseModel):
    """Validated extraction result."""

    facts: list[ExtractedFact]