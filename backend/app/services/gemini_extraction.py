"""Gemini-backed knowledge extraction adapter."""

from google import genai

from app.core.settings import get_settings
from app.schemas.extraction import ExtractionInput, ExtractionOutput
from app.services.extraction import KnowledgeExtractor


class GeminiKnowledgeExtractor(KnowledgeExtractor):
    """Knowledge extractor implementation backed by Gemini."""

    MODEL = "gemini-3.6-flash"

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self._client = genai.Client(api_key=settings.gemini_api_key)

    def extract(self, request: ExtractionInput) -> ExtractionOutput:
        """Extract candidate knowledge facts from a generic knowledge source."""
        prompt = self._build_prompt(request)

        interaction = self._client.interactions.create(
            model=self.MODEL,
            input=prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction_output",
                    "schema": ExtractionOutput.model_json_schema(),
                },
            },
        )

        return ExtractionOutput.model_validate_json(
            interaction.output_text
        )

    @staticmethod
    def _build_prompt(request: ExtractionInput) -> str:
        source = request.source

        instructions = """You extract restaurant knowledge from owner-provided
content.

Return JSON matching the required ExtractionOutput schema.

Core rules:
- Extract only restaurant information actually supported by owner-provided content.
- Do not hallucinate facts.
- Do not use outside knowledge.
- Do not make unsupported inferences.
- Do not silently convert uncertainty into certainty.
- Preserve conditions, exceptions, corrections, historical meaning, and future/planned meaning.
- Preserve the owner's original meaning.
- Separate independent facts when appropriate.
- Zero facts is valid.
- Do not treat questions, suggestions, opinions, or filler as restaurant facts unless
  the owner also explicitly provides a supported factual statement.
- source_text must be the exact supporting portion of the owner's original wording.
"""

        if source.source_type == "guided_transcript":
            prompt_parts = [
                instructions,
                "",
                "KNOWLEDGE SOURCE TYPE: guided_transcript",
                "",
                "The transcript contains system-generated guided questions and "
                "owner responses.",
                "System turns are context only and must NEVER be treated as "
                "factual sources.",
                "Only OWNER turns may support extracted facts.",
                "For every fact supported by a guided owner response, return "
                "the relevant owner's turn_id in source_turn_id.",
                "Do not use a system turn's turn_id as source_turn_id.",
                "",
                "GUIDED TRANSCRIPT:",
                "",
            ]

            for turn in source.turns:
                language = (
                    f" | language={turn.input_language}"
                    if turn.input_language
                    else ""
                )
                prompt_parts.append(
                    f"[TURN {turn.turn_id} | {turn.speaker_type.upper()}{language}]"
                )
                prompt_parts.append(turn.text)
                prompt_parts.append("")

            if request.current_question_key is not None:
                prompt_parts.extend(
                    [
                        "CURRENT GUIDED QUESTION CONTEXT:",
                        f"question_key: {request.current_question_key}",
                    ]
                )

            if request.current_question_text is not None:
                prompt_parts.append(
                    f"question_text: {request.current_question_text}"
                )

            return "\n".join(prompt_parts)

        prompt_parts = [
            instructions,
            "",
            "KNOWLEDGE SOURCE TYPE: owner_input",
            "",
            "This is arbitrary owner-provided restaurant information.",
            "There is no required guided question.",
            "Discover restaurant-relevant information without relying on a "
            "predefined list of fact types.",
            "Do not invent a source_turn_id. For this source type, "
            "source_turn_id must be null.",
            "",
            "OWNER INPUT:",
            source.source_text or "",
        ]

        return "\n".join(prompt_parts)
