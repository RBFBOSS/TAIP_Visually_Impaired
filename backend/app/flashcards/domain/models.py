from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DocumentSection(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    heading: str
    pageNumber: int


class Citation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sectionId: UUID
    pageNumber: int
    sourceExcerpt: str

    def get_source_reference(self) -> str:
        return f"Pagina {self.pageNumber}: \"{self.sourceExcerpt}\""


class GeneratedFlashcard(BaseModel):
    question: str
    answer: str
    sourcePage: int
    sourceSectionId: UUID


class Flashcard(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    deck_id: Optional[UUID] = None
    question: str
    answer: str
    status: ApprovalStatus = ApprovalStatus.DRAFT
    citations: List[Citation] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def approve(self) -> None:
        self.status = ApprovalStatus.APPROVED
        self.updatedAt = datetime.utcnow()

    def reject(self) -> None:
        self.status = ApprovalStatus.REJECTED
        self.updatedAt = datetime.utcnow()

    def edit(self, question: str, answer: str) -> None:
        self.question = question
        self.answer = answer
        self.updatedAt = datetime.utcnow()


class Deck(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    documentId: UUID
    title: str
    cards: List[Flashcard] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    def get_approved_cards(self) -> List[Flashcard]:
        return [card for card in self.cards if card.status == ApprovalStatus.APPROVED]