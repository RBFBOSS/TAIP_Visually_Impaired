"""Interface only: concrete repository is owned by the Deck/Citation teammate."""
from __future__ import annotations
from abc import ABC, abstractmethod
from uuid import UUID
from .models import Flashcard

class FlashcardRepository(ABC):
    @abstractmethod
    def save(self, card: Flashcard) -> Flashcard:
        pass

    @abstractmethod
    def findById(self, id: UUID) -> Flashcard:
        pass

    @abstractmethod
    def findDrafts(self, deckId: UUID) -> list[Flashcard]:
        pass

    @abstractmethod
    def saveAll(self, cards: list[Flashcard]) -> None:
        pass
