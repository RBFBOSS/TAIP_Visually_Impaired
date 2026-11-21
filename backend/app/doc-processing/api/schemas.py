from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import ConfigDict

from pydantic import BaseModel

from domain import ProcessingStatus

class Citation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    page_number: int
    source_excerpt: str

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
    citation: Citation


class StudyMaterialResponse(BaseModel):
    documentId: UUID
    summary: str
    summary_citation: Citation
    flashcards: List[FlashcardResponse]


class SummaryResponse(BaseModel):
    documentId: UUID
    summary: str
    summary_citation: Citation
