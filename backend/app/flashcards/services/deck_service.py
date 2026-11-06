from typing import Dict, List, Optional
from uuid import UUID

from app.flashcards.domain import ApprovalStatus, Deck, Flashcard
from app.flashcards.repositories import FlashcardRepository


class DeckNotFoundError(Exception):
    """Raised when a requested deck is not found."""
    pass


class DeckService:
    """
    Domain service for managing Deck lifecycle and aggregating approved cards.
    """

    def __init__(
        self,
        flashcard_repository: FlashcardRepository,
        decks_storage: Optional[Dict[UUID, Deck]] = None,
    ) -> None:
        self.flashcard_repository = flashcard_repository
        self._decks: Dict[UUID, Deck] = (
            decks_storage if decks_storage is not None else {}
        )

    def createDeck(self, documentId: UUID, title: str = "Untitled Deck") -> Deck:
        """
        Creates and stores a new Deck linked to a processed document.
        """
        deck = Deck(documentId=documentId, title=title)
        self._decks[deck.id] = deck
        return deck

    def getDeck(self, deckId: UUID) -> Deck:
        """
        Retrieves a Deck entity by its identifier.
        """
        deck = self._decks.get(deckId)
        if not deck:
            raise DeckNotFoundError(f"Deck with ID {deckId} was not found.")
        return deck

    def getApprovedCards(self, deckId: UUID) -> List[Flashcard]:
        """
        Retrieves all cards belonging to the specified deck that have APPROVED status.
        Reads cards via repository/storage and filters by status.
        """
        # Ensure deck exists
        _ = self.getDeck(deckId)

        # Retrieve all cards associated with this deck from repository storage
        # If in-memory repo is used, filter approved cards
        if hasattr(self.flashcard_repository, "_storage"):
            return [
                card
                for card in self.flashcard_repository._storage.values()
                if card.deck_id == deckId and card.status == ApprovalStatus.APPROVED
            ]

        return []