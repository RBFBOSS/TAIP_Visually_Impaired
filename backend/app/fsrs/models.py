"""Data models and enums for the flashcard study module."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID


class RecallRating(Enum):
    HARD = "HARD"   # Student remembered, but struggled.
    GOOD = "GOOD"   # Student remembered correctly.
    EASY = "EASY"   # Student remembered immediately.


class SessionStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"


class FSRSCardState(Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class FeedbackLevel(Enum):
    TASK = "TASK"
    PROCESS = "PROCESS"
    SELF_REGULATION = "SELF_REGULATION"


@dataclass
class User:
    id: UUID
    role: str


@dataclass
class Flashcard:
    id: UUID
    question: str
    answer: str
    approval_status: str = "APPROVED"


@dataclass
class ReviewLog:
    id: UUID
    flashcard_id: UUID
    rating: RecallRating
    response_latency_ms: int
    reviewed_at: datetime


@dataclass
class ReviewSession:
    id: UUID
    user_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    review_logs: List[ReviewLog] = field(default_factory=list)

    def end_session(self):
        self.ended_at = datetime.now()
        self.status = SessionStatus.COMPLETED


@dataclass
class FSRSState:
    id: UUID
    user_id: UUID
    flashcard_id: UUID
    state: FSRSCardState = FSRSCardState.NEW
    stability: float = 0.0
    difficulty: float = 5.0
    due_at: Optional[datetime] = None
    last_review: Optional[datetime] = None
    repetitions: int = 0
    lapses: int = 0


@dataclass
class ProgressReport:
    total_reviews: int
    due_cards: int
    average_latency_ms: float
    generated_at: datetime


@dataclass
class LearningFeedback:
    level: FeedbackLevel
    message: str
