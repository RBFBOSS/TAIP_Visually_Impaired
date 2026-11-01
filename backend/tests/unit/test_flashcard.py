from app.models.flashcard import Flashcard, ApprovalStatus


def test_approve_flashcard():
    flashcard = Flashcard(
        question="What is TDD?",
        answer="Test Driven Development."
    )

    assert flashcard.status == ApprovalStatus.DRAFT

    flashcard.approve()

    assert flashcard.status == ApprovalStatus.APPROVED


def test_reject_flashcard():
    flashcard = Flashcard(
        question="What is TDD?",
        answer="Test Driven Development."
    )

    assert flashcard.status == ApprovalStatus.DRAFT

    flashcard.reject()

    assert flashcard.status == ApprovalStatus.REJECTED



def test_edit_flashcard():
    card = Flashcard(
        question="Old question",
        answer="Old answer"
    )

    card.edit(
        question="New question",
        answer="New answer"
    )

    assert card.question == "New question"
    assert card.answer == "New answer"
