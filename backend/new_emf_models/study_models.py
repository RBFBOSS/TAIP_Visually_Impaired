"""Python code generated from an Ecore metamodel."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

class RecallRating(str, Enum):
    AGAIN = "AGAIN"
    HARD = "HARD"
    GOOD = "GOOD"
    EASY = "EASY"

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"

class FSRSCardState(str, Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"

class FeedbackLevel(str, Enum):
    TASK = "TASK"
    PROCESS = "PROCESS"
    SELF_REGULATION = "SELF_REGULATION"

@dataclass
class FlashcardRef:
    id: str = field(default=None)  # type: ignore[assignment]
    question: str = field(default=None)  # type: ignore[assignment]
    answer: str = field(default=None)  # type: ignore[assignment]

@dataclass
class User:
    id: str = field(default=None)  # type: ignore[assignment]
    role: str | None = None
    sessions: list["ReviewSession"] = field(default_factory=list)
    fsrsStates: list["FSRSState"] = field(default_factory=list)

@dataclass
class ReviewSession:
    id: str = field(default=None)  # type: ignore[assignment]
    startedAt: datetime | None = None
    endedAt: datetime | None = None
    status: SessionStatus = field(default=None)  # type: ignore[assignment]
    user: "User" = field(default=None)  # type: ignore[assignment]
    logs: list["ReviewLog"] = field(default_factory=list)
    def endSession(self) -> None:
        raise NotImplementedError


@dataclass
class ReviewLog:
    id: str = field(default=None)  # type: ignore[assignment]
    rating: RecallRating = field(default=None)  # type: ignore[assignment]
    responseLatencyMs: int | None = None
    reviewedAt: datetime | None = None
    session: "ReviewSession" = field(default=None)  # type: ignore[assignment]
    flashcard: "FlashcardRef" = field(default=None)  # type: ignore[assignment]

@dataclass
class FSRSState:
    id: str = field(default=None)  # type: ignore[assignment]
    state: FSRSCardState = field(default=None)  # type: ignore[assignment]
    stability: float | None = None
    difficulty: float | None = None
    dueAt: datetime | None = None
    lastReview: datetime | None = None
    repetitions: int | None = None
    lapses: int | None = None
    user: "User" = field(default=None)  # type: ignore[assignment]
    flashcard: "FlashcardRef" = field(default=None)  # type: ignore[assignment]

@dataclass
class ProgressReport:
    totalReviews: int | None = None
    dueCards: int | None = None
    averageLatencyMs: float | None = None
    generatedAt: datetime | None = None
    user: "User" = field(default=None)  # type: ignore[assignment]
    feedbackItems: list["LearningFeedback"] = field(default_factory=list)

@dataclass
class LearningFeedback:
    level: FeedbackLevel = field(default=None)  # type: ignore[assignment]
    message: str = field(default=None)  # type: ignore[assignment]
