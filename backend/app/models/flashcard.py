from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class ApprovalStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class Flashcard:
    question: str
    answer: str

    id: UUID = field(default_factory=uuid4)
    status: ApprovalStatus = ApprovalStatus.DRAFT

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def _update_status(self, new_status: ApprovalStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def approve(self) -> None:
        self._update_status(ApprovalStatus.APPROVED)

    def reject(self) -> None:
        self._update_status(ApprovalStatus.REJECTED)

    def edit(self, question: str, answer: str) -> None:
        self.question = question
        self.answer = answer
        self.updated_at = datetime.now(timezone.utc)

