from typing import Dict, List, Optional
from uuid import UUID

from app.flashcards.domain import ApprovalStatus, Flashcard
from app.flashcards.repositories import FlashcardRepository


class InMemoryFlashcardRepository(FlashcardRepository):
    """
    In-memory implementation of flashcard repository.
    For fast develompent and testing before database integration.
    """

    def __init__(self) -> None:
        self._storage: Dict[UUID, Flashcard] = {}

    def save(self, card: Flashcard) -> Flashcard:
        self._storage[card.id] = card
        return card

    def find_by_id(self, card_id: UUID) -> Optional[Flashcard]:
        return self._storage.get(card_id)

    def find_drafts(self, deck_id: UUID) -> List[Flashcard]:
        return [
            card
            for card in self._storage.values()
            if card.deck_id == deck_id and card.status == ApprovalStatus.DRAFT
        ]

    def save_all(self, cards: List[Flashcard]) -> None:
        for card in cards:
            self._storage[card.id] = card