from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.aspects.security import AccessDeniedError
from app.flashcards.api.dependencies import (
    get_current_user_role,
    get_deck_service,
    get_flashcard_service,
)
from app.flashcards.api.schemas import (
    BulkApprovalResponse,
    CitationResponse,
    CreateDraftRequest,
    FlashcardEditRequest,
    FlashcardResponse,
)
from app.flashcards.domain.models import Flashcard, GeneratedFlashcard
from app.flashcards.services.citation_validator import InvalidCitationError
from app.flashcards.services.deck_service import DeckNotFoundError, DeckService
from app.flashcards.services.flashcard_service import (
    FlashcardNotFoundError,
    FlashcardService,
    UnauthorizedApprovalError,
)

router = APIRouter(prefix="/flashcards", tags=["Flashcards Approval & Management"])


def _map_flashcard_to_response(card: Flashcard) -> FlashcardResponse:
    return FlashcardResponse(
        id=card.id,
        deck_id=card.deck_id,
        question=card.question,
        answer=card.answer,
        status=card.status,
        citations=[
            CitationResponse(
                id=c.id,
                sectionId=c.sectionId,
                pageNumber=c.pageNumber,
                sourceExcerpt=c.sourceExcerpt,
                referenceText=c.get_source_reference(),
            )
            for c in card.citations
        ],
        createdAt=card.createdAt,
        updatedAt=card.updatedAt,
    )


@router.post("/drafts", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
def create_draft(
    request: CreateDraftRequest,
    service: FlashcardService = Depends(get_flashcard_service),
):
    try:
        generated_data = GeneratedFlashcard(
            question=request.question,
            answer=request.answer,
            sourcePage=request.sourcePage,
            sourceSectionId=request.sourceSectionId,
        )
        created_card = service.createDraft(data=generated_data, deck_id=request.deck_id)
        return _map_flashcard_to_response(created_card)
    except InvalidCitationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/decks/{deck_id}/drafts", response_model=List[FlashcardResponse])
def get_deck_drafts(
    deck_id: UUID,
    service: FlashcardService = Depends(get_flashcard_service),
):
    cards = service.getDrafts(deckId=deck_id)
    return [_map_flashcard_to_response(card) for card in cards]


@router.post("/{card_id}/approve", response_model=FlashcardResponse)
def approve_flashcard(
    card_id: UUID,
    user_role: str = Depends(get_current_user_role),
    service: FlashcardService = Depends(get_flashcard_service),
):
    try:
        card = service.approveCard(cardId=card_id, user_role=user_role)
        return _map_flashcard_to_response(card)
    except (UnauthorizedApprovalError, AccessDeniedError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except FlashcardNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{card_id}/reject", response_model=FlashcardResponse)
def reject_flashcard(
    card_id: UUID,
    user_role: str = Depends(get_current_user_role),
    service: FlashcardService = Depends(get_flashcard_service),
):
    try:
        card = service.rejectCard(cardId=card_id, user_role=user_role)
        return _map_flashcard_to_response(card)
    except (UnauthorizedApprovalError, AccessDeniedError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except FlashcardNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/{card_id}", response_model=FlashcardResponse)
def edit_flashcard(
    card_id: UUID,
    request: FlashcardEditRequest,
    user_role: str = Depends(get_current_user_role),
    service: FlashcardService = Depends(get_flashcard_service),
):
    try:
        card = service.editCard(
            cardId=card_id,
            question=request.question,
            answer=request.answer,
            user_role=user_role,
        )
        return _map_flashcard_to_response(card)
    except (UnauthorizedApprovalError, AccessDeniedError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except FlashcardNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/decks/{deck_id}/approve-all", response_model=BulkApprovalResponse)
def approve_all_deck_flashcards(
    deck_id: UUID,
    user_role: str = Depends(get_current_user_role),
    service: FlashcardService = Depends(get_flashcard_service),
):
    try:
        count = service.approveAll(deckId=deck_id, user_role=user_role)
        return BulkApprovalResponse(deckId=deck_id, approvedCount=count)
    except (UnauthorizedApprovalError, AccessDeniedError) as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.get("/decks/{deck_id}/approved", response_model=List[FlashcardResponse])
def get_approved_deck_cards(
    deck_id: UUID,
    deck_service: DeckService = Depends(get_deck_service),
):
    try:
        cards = deck_service.getApprovedCards(deckId=deck_id)
        return [_map_flashcard_to_response(card) for card in cards]
    except DeckNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))