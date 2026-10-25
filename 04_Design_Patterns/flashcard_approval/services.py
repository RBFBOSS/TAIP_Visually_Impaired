"""Approval service declarations"""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from .models import Flashcard
from .states import FlashcardState
from .commands import FlashcardCommand
if TYPE_CHECKING:
    from .references import GeneratedFlashcard
    from .repository import FlashcardRepository
    from .validation import CitationValidator

class FlashcardService:
    repository: FlashcardRepository
    citationValidator: CitationValidator

    def __init__(self, repository: FlashcardRepository, citationValidator: CitationValidator) -> None:
        pass

    def createDraft(self, data: GeneratedFlashcard) -> Flashcard:
        pass

    def getDrafts(self, deckId: UUID) -> list[Flashcard]:
        pass

    def approveCard(self, cardId: UUID) -> Flashcard:
        pass

    def rejectCard(self, cardId: UUID) -> Flashcard:
        pass

    def editCard(self, cardId: UUID, question: str, answer: str) -> Flashcard:
        pass

    def approveAll(self, deckId: UUID) -> int:
        pass
