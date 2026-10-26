"""Study-session, scheduling, and progress model declarations."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID


class SessionStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"


class RecallRating(Enum):
    AGAIN = "AGAIN"
    HARD = "HARD"
    GOOD = "GOOD"
    EASY = "EASY"


class FSRSCardState(Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class FeedbackLevel(Enum):
    TASK = "TASK"
    PROCESS = "PROCESS"
    SELF_REGULATION = "SELF_REGULATION"


class ReviewSession:
    id: UUID
    userId: UUID
    startedAt: datetime
    endedAt: datetime | None
    status: SessionStatus
    reviewLogs: list[ReviewLog]

    def endSession(self) -> None:
        pass


class ReviewLog:
    id: UUID
    flashcardId: UUID
    rating: RecallRating
    responseLatencyMs: int
    reviewedAt: datetime


class FSRSState:
    id: UUID
    userId: UUID
    flashcardId: UUID
    state: FSRSCardState
    stability: float
    difficulty: float
    dueAt: datetime
    lastReview: datetime | None
    repetitions: int
    lapses: int


class ProgressReport:
    totalReviews: int
    dueCards: int
    averageLatencyMs: float
    generatedAt: datetime
    feedback: list[LearningFeedback]


class LearningFeedback:
    level: FeedbackLevel
    message: str
