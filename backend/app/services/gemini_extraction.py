"""Gemini-backed knowledge extraction adapter."""

from google import genai

from app.core.settings import get_settings
from app.schemas.extraction import ExtractionInput, ExtractionOutput
from app.services.extraction import KnowledgeExtractor


class GeminiKnowledgeExtractor(KnowledgeExtractor):
    """Knowledge extractor implementation backed by Gemini."""

    MODEL = "gemini-3.6-flash"

    SYSTEM_INSTRUCTION = """
You extract restaurant knowledge from an owner's message.

Your job is to identify only information that is actually supported by the
owner's message.

Rules:
- Never hallucinate facts.
- Never use outside knowledge.
- Never make unsupported inferences.
- Never turn uncertainty into certainty.
- Preserve conditions, restrictions, exceptions, and qualifiers.
- Preserve the owner's original meaning.
- Separate independent facts into separate fact objects when appropriate.
- Ignore greetings, filler, conversational pleasantries, and unrelated text.
- Do not extract questions asked by the owner as facts.
- Do not invent missing values.
- Additional restaurant information is allowed even when it does not match
  the current guided question.
- If the message contains no supported restaurant facts, return an empty
  facts list.
- source_text must be an exact supporting portion copied from the owner's
  original message.
- confidence is only a review signal. It is not proof that a fact is correct.
- uncertain must be true when the owner's wording expresses uncertainty,
  approximation, possibility, or a condition that prevents treating the fact
  as fully certain.
- fact_value must preserve useful structured detail rather than flattening
  everything into a vague string.

The output must contain only the requested structured extraction.
"""

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self._client = genai.Client(api_key=settings.gemini_api_key)

    def extract(self, request: ExtractionInput) -> ExtractionOutput:
        """Extract candidate knowledge facts from an owner message."""

        context = (
            f"Current guided question key: {request.current_question_key or 'none'}\n"
            f"Current guided question: {request.current_question_text or 'none'}"
        )

        prompt = f"""
Extract restaurant knowledge from the following owner's message.

{context}

Source language:
{request.source_language}

Owner message:
{request.source_text}
""".strip()

        interaction = self._client.interactions.create(
            model=self.MODEL,
            input=prompt,
            system_instruction=self.SYSTEM_INSTRUCTION,
            response_format=[
                {
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": ExtractionOutput.model_json_schema(),
                }
            ],
            store=False,
        )

        result = ExtractionOutput.model_validate_json(interaction.output_text)

        for fact in result.facts:
            if fact.source_text not in request.source_text:
                raise ValueError(
                    "Gemini returned source_text that is not an exact "
                    "substring of the owner message"
                )

        return result
