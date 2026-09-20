from uuid import UUID

from sqlalchemy import select

from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.knowledge_fact import KnowledgeFact
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.extraction import ExtractedFact, ExtractionOutput
from app.schemas.knowledge_fact import KnowledgeReviewEdit
from app.services.knowledge_fact import (
    approve_fact,
    edit_pending_fact,
    get_current_approved_fact,
    persist_extraction_candidates,
    reject_fact,
)
from app.services.restaurant import get_owned_restaurant
from app.services.training import (
    complete_training_session,
    create_training_session,
)


db = next(get_db())

real_commit = db.commit
db.commit = db.flush

try:
    restaurant = db.scalar(
        select(Restaurant).where(
            Restaurant.id == UUID("76e587d9-8965-4878-bd2e-a58becbceb37")
        )
    )

    owner = db.scalar(
        select(User).where(
            User.id == UUID("3d6d929b-23e1-4912-ba81-eed4e503bd9f")
        )
    )

    assert restaurant is not None
    assert owner is not None

    get_owned_restaurant(db, restaurant.id, owner.id)
    print("PASS: tenant ownership verified")

    # ------------------------------------------------------------
    # Session 1 -> initial approved fact
    # ------------------------------------------------------------
    session_1 = create_training_session(db, restaurant.id)

    conversation_1 = Conversation(
        restaurant_id=restaurant.id,
        session_id=session_1.id,
        speaker_type="owner",
        input_language="en",
        input_text="We are open from 11 AM to 11 PM.",
        output_text="What are your regular opening hours?",
    )
    db.add(conversation_1)
    db.flush()

    session_1 = complete_training_session(db, session_1)

    output_1 = ExtractionOutput(
        facts=[
            ExtractedFact(
                category="opening_hours",
                fact_key="regular_hours",
                fact_value={"open": "11:00", "close": "23:00"},
                confidence=1.0,
                source_turn_id=str(conversation_1.id),
                source_text="11 AM to 11 PM",
            )
        ]
    )

    created_1, equivalent_1 = persist_extraction_candidates(
        db,
        session_1,
        output_1,
    )

    assert len(created_1) == 1
    assert not equivalent_1

    fact_1 = created_1[0]

    assert fact_1.status == "pending"
    assert fact_1.version == 1
    assert fact_1.source_turn_id == conversation_1.id

    approve_fact(db, fact_1)

    assert fact_1.status == "approved"
    assert fact_1.version == 1

    current = get_current_approved_fact(
        db,
        restaurant.id,
        "opening_hours",
        "regular_hours",
    )

    assert current.id == fact_1.id
    assert current.version == 1

    print("PASS: Session 1 candidate persisted and approved as v1")

    # ------------------------------------------------------------
    # Session 2 -> SAME value, NEW provenance
    # ------------------------------------------------------------
    session_2 = create_training_session(db, restaurant.id)

    conversation_2 = Conversation(
        restaurant_id=restaurant.id,
        session_id=session_2.id,
        speaker_type="owner",
        input_language="en",
        input_text="We are open from 11 AM to 11 PM.",
        output_text=(
            "Thank you. The guided training session is ready to be completed."
        ),
    )
    db.add(conversation_2)
    db.flush()

    session_2 = complete_training_session(db, session_2)

    output_2 = ExtractionOutput(
        facts=[
            ExtractedFact(
                category="opening_hours",
                fact_key="regular_hours",
                fact_value={"open": "11:00", "close": "23:00"},
                confidence=0.95,
                source_turn_id=str(conversation_2.id),
                source_text="11 AM to 11 PM",
            )
        ]
    )

    created_2, equivalent_2 = persist_extraction_candidates(
        db,
        session_2,
        output_2,
    )

    assert len(created_2) == 0
    assert len(equivalent_2) == 1
    assert equivalent_2[0].id == fact_1.id

    duplicate_candidate = db.scalar(
        select(KnowledgeFact).where(
            KnowledgeFact.restaurant_id == restaurant.id,
            KnowledgeFact.source_turn_id == conversation_2.id,
        )
    )

    assert duplicate_candidate is not None
    assert duplicate_candidate.status == "pending"
    assert duplicate_candidate.source_turn_id == conversation_2.id
    assert duplicate_candidate.id != fact_1.id

    # The pending evidence row must NOT consume an approved version.
    assert duplicate_candidate.version == 2

    current = get_current_approved_fact(
        db,
        restaurant.id,
        "opening_hours",
        "regular_hours",
    )

    assert current.id == fact_1.id
    assert current.version == 1

    print(
        "PASS: same-value later session preserved new provenance "
        "without changing current v1"
    )

    # ------------------------------------------------------------
    # Same-value approval request
    # ------------------------------------------------------------
    approve_fact(db, duplicate_candidate)

    assert duplicate_candidate.status == "pending"
    assert duplicate_candidate.source_turn_id == conversation_2.id
    assert duplicate_candidate.version == 2

    current = get_current_approved_fact(
        db,
        restaurant.id,
        "opening_hours",
        "regular_hours",
    )

    assert current.id == fact_1.id
    assert current.status == "approved"
    assert current.version == 1

    print(
        "PASS: same-value approval request retained pending evidence "
        "and did not create another approved record"
    )

    # ------------------------------------------------------------
    # Session 3 -> CONFLICTING value
    # ------------------------------------------------------------
    session_3 = create_training_session(db, restaurant.id)

    conversation_3 = Conversation(
        restaurant_id=restaurant.id,
        session_id=session_3.id,
        speaker_type="owner",
        input_language="en",
        input_text="Our new hours are 10 AM to 10 PM.",
        output_text=(
            "Thank you. The guided training session is ready to be completed."
        ),
    )
    db.add(conversation_3)
    db.flush()

    session_3 = complete_training_session(db, session_3)

    output_3 = ExtractionOutput(
        facts=[
            ExtractedFact(
                category="opening_hours",
                fact_key="regular_hours",
                fact_value={"open": "10:00", "close": "22:00"},
                confidence=0.9,
                source_turn_id=str(conversation_3.id),
                source_text="10 AM to 10 PM",
            )
        ]
    )

    created_3, equivalent_3 = persist_extraction_candidates(
        db,
        session_3,
        output_3,
    )

    assert len(equivalent_3) == 0
    assert len(created_3) == 1

    fact_3 = created_3[0]

    assert fact_3.version == 2
    assert fact_3.status == "pending"
    assert fact_3.source_turn_id == conversation_3.id

    current = get_current_approved_fact(
        db,
        restaurant.id,
        "opening_hours",
        "regular_hours",
    )

    assert current.id == fact_1.id
    assert current.version == 1
    assert current.status == "approved"

    print(
        "PASS: conflicting value became v2 pending "
        "while v1 remained current"
    )

    # ------------------------------------------------------------
    # Edit pending v2 candidate
    # ------------------------------------------------------------
    edit_pending_fact(
        db,
        fact_3,
        KnowledgeReviewEdit(
            fact_value_json={
                "open": "10:30",
                "close": "22:00",
            }
        ),
    )

    assert fact_3.status == "pending"
    assert fact_3.version == 2
    assert fact_3.source_turn_id == conversation_3.id
    assert fact_3.source_text == "10 AM to 10 PM"

    print("PASS: pending v2 candidate edited without changing provenance")

    # ------------------------------------------------------------
    # Approve v2
    # ------------------------------------------------------------
    approve_fact(db, fact_3)

    assert fact_3.status == "approved"
    assert fact_3.version == 2

    current = get_current_approved_fact(
        db,
        restaurant.id,
        "opening_hours",
        "regular_hours",
    )

    assert current.id == fact_3.id
    assert current.version == 2
    assert current.status == "approved"

    historical = db.scalar(
        select(KnowledgeFact).where(
            KnowledgeFact.id == fact_1.id
        )
    )

    assert historical.status == "approved"
    assert historical.version == 1
    assert historical.id != current.id

    print(
        "PASS: v2 approved value is current "
        "and v1 remains historical approved"
    )

    # ------------------------------------------------------------
    # Session 4 -> rejection
    # ------------------------------------------------------------
    session_4 = create_training_session(db, restaurant.id)

    conversation_4 = Conversation(
        restaurant_id=restaurant.id,
        session_id=session_4.id,
        speaker_type="owner",
        input_language="en",
        input_text="We are open 9 AM to 9 PM on holidays.",
        output_text="Thank you.",
    )
    db.add(conversation_4)
    db.flush()

    session_4 = complete_training_session(db, session_4)

    output_4 = ExtractionOutput(
        facts=[
            ExtractedFact(
                category="holiday_hours",
                fact_key="holiday_hours",
                fact_value={"open": "09:00", "close": "21:00"},
                confidence=0.8,
                source_turn_id=str(conversation_4.id),
                source_text="9 AM to 9 PM on holidays",
            )
        ]
    )

    created_4, equivalent_4 = persist_extraction_candidates(
        db,
        session_4,
        output_4,
    )

    assert len(equivalent_4) == 0
    assert len(created_4) == 1

    fact_4 = created_4[0]

    assert fact_4.version == 1
    assert fact_4.status == "pending"

    reject_fact(db, fact_4)

    assert fact_4.status == "rejected"
    assert fact_4.version == 1

    print("PASS: rejection retained candidate as rejected")

    # ------------------------------------------------------------
    # Conversation preservation
    # ------------------------------------------------------------
    for conversation_id, expected_text in [
        (conversation_1.id, "We are open from 11 AM to 11 PM."),
        (conversation_2.id, "We are open from 11 AM to 11 PM."),
        (conversation_3.id, "Our new hours are 10 AM to 10 PM."),
        (conversation_4.id, "We are open 9 AM to 9 PM on holidays."),
    ]:
        conversation = db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )

        assert conversation is not None
        assert conversation.input_text == expected_text

    print("PASS: Conversation rows unchanged")

    # ------------------------------------------------------------
    # Tenant isolation
    # ------------------------------------------------------------
    fake_restaurant_id = UUID("11111111-1111-1111-1111-111111111111")

    try:
        get_owned_restaurant(
            db,
            fake_restaurant_id,
            owner.id,
        )
    except Exception:
        print("PASS: tenant isolation rejects unrelated restaurant")
    else:
        raise AssertionError(
            "Tenant isolation failed: unrelated restaurant was accessible"
        )

    try:
        get_current_approved_fact(
            db,
            fake_restaurant_id,
            "opening_hours",
            "regular_hours",
        )
    except Exception:
        pass

    # ------------------------------------------------------------
    # Final assertions
    # ------------------------------------------------------------
    all_opening_hours = list(
        db.scalars(
            select(KnowledgeFact)
            .where(
                KnowledgeFact.restaurant_id == restaurant.id,
                KnowledgeFact.category == "opening_hours",
                KnowledgeFact.fact_key == "regular_hours",
            )
            .order_by(KnowledgeFact.version.asc(), KnowledgeFact.created_at.asc())
        )
    )

    assert len(all_opening_hours) == 3

    assert all_opening_hours[0].version == 1
    assert all_opening_hours[0].status == "approved"

    assert all_opening_hours[1].version == 2
    assert all_opening_hours[1].status == "pending"

    assert all_opening_hours[2].version == 2
    assert all_opening_hours[2].status == "approved"

    print("")
    print("==============================================")
    print("CORRECTED KNOWLEDGE FACT TEST: ALL PASSED")
    print("==============================================")
    print("v1 approved/current: YES")
    print("Same-value evidence retained: YES")
    print("Same-value evidence consumed no approved version: YES")
    print("Same-value approval retained pending evidence: YES")
    print("Conflicting candidate became v2: YES")
    print("v2 approval made v2 current: YES")
    print("v1 retained as historical approved: YES")
    print("Rejected candidate retained: YES")
    print("Conversation rows modified: NO")
    print("Tenant isolation: YES")
    print("Gemini called: NO")

finally:
    db.rollback()
    db.commit = real_commit
    db.close()
