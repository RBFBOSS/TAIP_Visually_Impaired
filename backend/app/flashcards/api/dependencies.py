from typing import Dict
from uuid import UUID
from fastapi import Header, HTTPException, status

from app.flashcards.domain import Deck
from app.flashcards.repositories import InMemoryFlashcardRepository
from app.flashcards.services import CitationValidator
from app.flashcards.services import DeckService
from app.flashcards.services import FlashcardService

_shared_flashcard_repository = InMemoryFlashcardRepository()
_shared_decks_storage: Dict[UUID, Deck] = {}
_shared_citation_validator = CitationValidator()

_shared_flashcard_service = FlashcardService(
    repository=_shared_flashcard_repository,
    citation_validator=_shared_citation_validator,
)
_shared_deck_service = DeckService(
    flashcard_repository=_shared_flashcard_repository,
    decks_storage=_shared_decks_storage,
)


def get_flashcard_service() -> FlashcardService:
    return _shared_flashcard_service


def get_deck_service() -> DeckService:
    return _shared_deck_service


def get_current_user_role(
    x_user_role: str = Header(default="TEACHER", alias="X-User-Role")
) -> str:
    """
    Simulates role extraction from request headers.
    In production, this would decode a JWT auth token.
    """
    if not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User role header is missing",
        )
    return x_user_role