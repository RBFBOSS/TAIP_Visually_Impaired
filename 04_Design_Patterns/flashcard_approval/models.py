"""Shared flashcard entity and approval status (owned by one module in the team)."""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from uuid import UUID

class ApprovalStatus(Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Flashcard:
    id: UUID
    question: str
    answer: str
    status: ApprovalStatus
    createdAt: datetime
    updatedAt: datetime
    state: FlashcardState

    def approve(self) -> None:
        pass

    def reject(self) -> None:
        pass

    def edit(self, question: str, answer: str) -> None:
        pass

from .states import FlashcardState
