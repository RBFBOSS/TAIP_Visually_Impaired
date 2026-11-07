from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from domain import ProcessingStatus


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: ProcessingStatus
    uploadedAt: datetime


class DocumentDetailResponse(DocumentResponse):
    pageCount: Optional[int]
    preview: Optional[str]


class FlashcardResponse(BaseModel):
    id: UUID
    documentId: UUID
    question: str
    answer: str
    sourcePage: int


class StudyMaterialResponse(BaseModel):
    documentId: UUID
    summary: str
    flashcards: List[FlashcardResponse]


class SummaryResponse(BaseModel):
    documentId: UUID
    summary: str
