from uuid import uuid4

from app.models.review_session import (
    RecallRating,
    ReviewLog,
    ReviewSession,
    SessionStatus,
)


def test_new_session_is_active():
    session = ReviewSession(user_id=uuid4())

    assert session.status == SessionStatus.ACTIVE
    assert session.ended_at is None
    assert session.review_logs == []


def test_add_review_records_log():
    session = ReviewSession(user_id=uuid4())
    review = ReviewLog(
        flashcard_id=uuid4(),
        rating=RecallRating.GOOD,
        response_latency_ms=1200
    )

    session.add_review(review)

    assert session.review_logs == [review]


def test_end_session_marks_completed():
    session = ReviewSession(user_id=uuid4())

    session.end_session()

    assert session.status == SessionStatus.COMPLETED
    assert session.ended_at is not None
