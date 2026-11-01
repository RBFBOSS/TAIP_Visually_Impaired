from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"


class RecallRating(str, Enum):
    AGAIN = "AGAIN"
    HARD = "HARD"
    GOOD = "GOOD"
    EASY = "EASY"


@dataclass
class ReviewLog:
    flashcard_id: UUID
    rating: RecallRating
    response_latency_ms: int

    id: UUID = field(default_factory=uuid4)

    reviewed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class ReviewSession:
    user_id: UUID

    id: UUID = field(default_factory=uuid4)
    status: SessionStatus = SessionStatus.ACTIVE

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    ended_at: datetime | None = None
    review_logs: list[ReviewLog] = field(default_factory=list)

    def add_review(self, review: ReviewLog) -> None:
        self.review_logs.append(review)

    def end_session(self) -> None:
        self.status = SessionStatus.COMPLETED
        self.ended_at = datetime.now(timezone.utc)
