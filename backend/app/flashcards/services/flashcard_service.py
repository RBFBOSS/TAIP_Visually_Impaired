from typing import List, Optional
from uuid import UUID

from app.flashcards.domain import (
    Citation,
    Flashcard,
    GeneratedFlashcard,
)
from app.flashcards.repositories import FlashcardRepository
from app.flashcards.services import CitationValidator


class FlashcardNotFoundError(Exception):
    """Raised when a flashcard is not found in the persistence store."""
    pass


class UnauthorizedApprovalError(Exception):
    """Raised when an approval/moderation action is attempted by a non-teacher."""
    pass


class FlashcardService:
    """
    Core domain service handling flashcard lifecycle and approval workflow.
    Manages drafts, approvals, rejections, edits, and bulk actions.
    """

    def __init__(
        self,
        repository: FlashcardRepository,
        citation_validator: CitationValidator,
    ) -> None:
        self.repository = repository
        self.citation_validator = citation_validator

    def _verify_teacher_role(self, role: Optional[str]) -> None:
        """Enforces teacher-only moderation rules."""
        if role != "TEACHER":
            raise UnauthorizedApprovalError(
                "Only teachers are authorized to validate, approve, or edit flashcards."
            )

    def createDraft(
        self, data: GeneratedFlashcard, deck_id: Optional[UUID] = None
    ) -> Flashcard:
        """
        Creates a DRAFT flashcard from generated PDF data and binds its source citation.
        """
        citation = Citation(
            sectionId=data.sourceSectionId,
            pageNumber=data.sourcePage,
            sourceExcerpt=f"Source reference from page {data.sourcePage}",
        )

        card = Flashcard(
            deck_id=deck_id,
            question=data.question,
            answer=data.answer,
            citations=[citation],
        )

        self.citation_validator.validateCitation(card)

        return self.repository.save(card)

    def getDrafts(self, deckId: UUID) -> List[Flashcard]:
        """Retrieves all pending DRAFT flashcards for a specific deck."""
        return self.repository.find_drafts(deckId)

    def approveCard(self, cardId: UUID, user_role: str = "TEACHER") -> Flashcard:
        """Approves a single flashcard."""
        self._verify_teacher_role(user_role)

        card = self.repository.find_by_id(cardId)
        if not card:
            raise FlashcardNotFoundError(f"Flashcard with ID {cardId} was not found.")

        card.approve()
        return self.repository.save(card)

    def rejectCard(self, cardId: UUID, user_role: str = "TEACHER") -> Flashcard:
        """Rejects a single flashcard."""
        self._verify_teacher_role(user_role)

        card = self.repository.find_by_id(cardId)
        if not card:
            raise FlashcardNotFoundError(f"Flashcard with ID {cardId} was not found.")

        card.reject()
        return self.repository.save(card)

    def editCard(
        self, cardId: UUID, question: str, answer: str, user_role: str = "TEACHER"
    ) -> Flashcard:
        """Edits question and answer content before or during the approval stage."""
        self._verify_teacher_role(user_role)

        card = self.repository.find_by_id(cardId)
        if not card:
            raise FlashcardNotFoundError(f"Flashcard with ID {cardId} was not found.")

        card.edit(question=question, answer=answer)
        return self.repository.save(card)

    def approveAll(self, deckId: UUID, user_role: str = "TEACHER") -> int:
        """
        Bulk-approves all draft cards in a deck.
        Returns the total number of approved cards.
        """
        self._verify_teacher_role(user_role)

        drafts = self.repository.find_drafts(deckId)
        for card in drafts:
            card.approve()

        self.repository.save_all(drafts)
        return len(drafts)