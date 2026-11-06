from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.flashcards.domain.models import ApprovalStatus


class CitationResponse(BaseModel):
    id: UUID
    sectionId: UUID
    pageNumber: int
    sourceExcerpt: str
    referenceText: str


class FlashcardResponse(BaseModel):
    id: UUID
    deck_id: Optional[UUID]
    question: str
    answer: str
    status: ApprovalStatus
    citations: List[CitationResponse]
    createdAt: datetime
    updatedAt: datetime


class FlashcardEditRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Updated question text")
    answer: str = Field(..., min_length=1, description="Updated answer text")


class CreateDraftRequest(BaseModel):
    deck_id: Optional[UUID] = None
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    sourcePage: int = Field(..., gt=0)
    sourceSectionId: UUID


class BulkApprovalResponse(BaseModel):
    deckId: UUID
    approvedCount: int