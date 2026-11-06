from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.flashcards.domain import Flashcard


class FlashcardRepository(ABC):
    """Abstract contract for Flashcard entities persistance."""

    @abstractmethod
    def save(self, card: Flashcard) -> Flashcard:
        """Saves or updates a flashcard's state."""
        pass

    @abstractmethod
    def find_by_id(self, card_id: UUID) -> Optional[Flashcard]:
        """Finds a card by ID. Returns None otherwise."""
        pass

    @abstractmethod
    def find_drafts(self, deck_id: UUID) -> List[Flashcard]:
        """Returns all DRAFT cards associated to a deck."""
        pass

    @abstractmethod
    def save_all(self, cards: List[Flashcard]) -> None:
        """Saves a collection of flashcards."""
        pass