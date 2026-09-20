"""Temporary Gemini extraction stress-test suite."""

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.extraction import ExtractionInput
from app.services.gemini_extraction import GeminiKnowledgeExtractor


TEST_CASES = [
    (
        "1. Multiple facts + exception + unrelated information",
        "We normally open at 11 AM and close at 11 PM, although on Fridays and Saturdays we stay open until midnight. We don't serve breakfast at the moment, but we're considering starting it during the winter. We have a small private dining room upstairs, and customers can order delivery through Swiggy or Zomato. Oh, and parking is available behind the building.",
        "opening_hours",
        "What are your opening hours?",
        False,
    ),
    (
        "2. Uncertainty",
        "I think we usually open around 10:30 or 11 in the morning, but I'm not completely sure because our manager sometimes opens earlier on weekends. We might also start serving breakfast next month if the kitchen staff agrees.",
        "opening_hours",
        "What are your opening hours?",
        False,
    ),
    (
        "3. Negation",
        "We don't offer home delivery ourselves. Customers can pick up their orders from the restaurant, and some customers arrange delivery through third-party platforms. We also don't currently provide catering.",
        "ordering_and_delivery",
        "How do customers order and receive food?",
        False,
    ),
    (
        "4. Conditional information",
        "Our regular menu is available every day, but the Sunday brunch menu is only available if we have enough staff that week. During private events, we sometimes offer a completely different menu depending on what the customer has booked.",
        "menu_and_specialties",
        "Tell me about your menu and specialties.",
        False,
    ),
    (
        "5. Correction",
        "We close at 10 PM every day - actually, sorry, that's Monday through Thursday. On Friday and Saturday we close at midnight, and on Sunday we close at 9 PM.",
        "opening_hours",
        "What are your opening hours?",
        False,
    ),
    (
        "6. Owner question + current fact",
        "Do you think we should start accepting reservations for the new private dining room? I'm not sure yet. We currently only accept walk-ins.",
        "reservations",
        "How do you handle reservations?",
        False,
    ),
    (
        "7. Unsupported inference",
        "We have twelve tables inside the restaurant and four tables outside. Most of our customers come in the evening, especially on weekends.",
        "additional_information",
        "Is there anything else about the restaurant that customers should know?",
        False,
    ),
    (
        "8. Conversational answer + historical example",
        "Honestly, it depends. Usually we're there by eleven, but if there's a private event we sometimes open earlier. Last Sunday we actually opened at nine because we had a family function. We don't have a fixed breakfast service though.",
        "opening_hours",
        "What are your opening hours?",
        False,
    ),
    (
        "9. Blind discovery - patio, pets, private bookings",
        "Last month we started letting customers bring their dogs onto the outdoor patio, but only after 6 PM because that's when the dinner service begins. We don't advertise it yet because we're still figuring out whether people actually like the idea. One family also asked if they could reserve the whole patio for a birthday, and we said yes as long as they give us at least three days' notice.",
        None,
        "What other things should customers know about visiting the restaurant?",
        True,
    ),
    (
        "10. Blind discovery - food preparation and seasonal offering",
        "My grandmother's recipe is the reason our lamb curry tastes different from most places. We make the spice paste here every morning, and we don't use any premade curry sauce. The naan is cooked fresh when ordered. During Diwali we also prepare a special vegetarian thali, but that's only available if we announce it ahead of time.",
        None,
        "Tell me anything you'd like customers to know about the food.",
        True,
    ),
    (
        "11. Blind discovery - workspace and Wi-Fi",
        "We've had a few people ask whether they can work from here during the afternoon. We're okay with it Monday through Thursday, but not during lunch because the tables get too busy. There's free Wi-Fi, although I wouldn't describe it as especially fast.",
        None,
        "What should customers know about using the restaurant?",
        True,
    ),
]


def main():
    output_file = BACKEND_ROOT / "scripts" / "extraction_stress_test_results.txt"
    extractor = GeminiKnowledgeExtractor()

    with output_file.open("w", encoding="utf-8") as output:
        output.write("GEMINI EXTRACTION STRESS TEST RESULTS\n")
        output.write("=" * 100 + "\n\n")

        for name, source_text, question_key, question_text, blind in TEST_CASES:
            output.write("=" * 100 + "\n")
            output.write(name + "\n")
            output.write("=" * 100 + "\n\n")

            output.write("INPUT:\n")
            output.write(source_text + "\n\n")

            try:
                result = extractor.extract(
                    ExtractionInput(
                        source_text=source_text,
                        source_language="en",
                        current_question_key=question_key,
                        current_question_text=question_text,
                    )
                )

                validated = result.__class__.model_validate(result.model_dump())

                output.write("EXTRACTED JSON:\n")
                output.write(
                    json.dumps(
                        validated.model_dump(),
                        indent=2,
                        ensure_ascii=False,
                    )
                )
                output.write("\n\n")

                output.write(f"NUMBER OF FACTS: {len(validated.facts)}\n")
                output.write("PYDANTIC VALIDATION PASSED: True\n")

                if not blind:
                    output.write("\nHUMAN REVIEW CHECKLIST:\n")
                    output.write("- Multiple independent facts captured? Inspect extracted JSON.\n")
                    output.write("- Uncertainty preserved? Inspect confidence, uncertain, and fact_value.\n")
                    output.write("- Negations preserved? Inspect fact_value and wording.\n")
                    output.write("- Conditions preserved? Inspect fact_value and qualifiers.\n")
                    output.write("- Corrections handled correctly? Compare final/current meaning with input.\n")
                    output.write("- Questions kept separate from factual statements? Inspect facts.\n")
                    output.write("- Historical information kept from becoming a permanent fact? Inspect temporal wording.\n")
                    output.write("- Future/planned information preserved as future/planned? Inspect fact_value.\n")
                    output.write("- Unsupported information invented? Compare every fact with the input.\n")
                    output.write("- Uncertainty/conditions incorrectly converted to certainty? Inspect carefully.\n")

            except Exception as exc:
                output.write("EXTRACTION ERROR:\n")
                output.write(f"{type(exc).__name__}: {exc}\n\n")
                output.write("NUMBER OF FACTS: unavailable\n")
                output.write("PYDANTIC VALIDATION PASSED: False\n")

            output.write("\n")

    print(f"COMPLETE: {len(TEST_CASES)} extraction cases executed.")
    print(f"RESULTS FILE: {output_file}")
    print("The extractor implementation and database were not modified.")
    print("No KnowledgeFact records were created.")


if __name__ == "__main__":
    main()
