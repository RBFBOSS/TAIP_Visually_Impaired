"""Study, scheduling, and progress service declarations."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from flashcard_approval.models import Flashcard

from .models import (
    FSRSState,
    LearningFeedback,
    ProgressReport,
    RecallRating,
    ReviewLog,
    ReviewSession,
)
from .observers import SessionObserver
from .scheduling import FSRSScheduler


class FSRSService:
    scheduler: FSRSScheduler

    def __init__(self, scheduler: FSRSScheduler) -> None:
        pass

    def getDueCards(self, userId: UUID) -> list[Flashcard]:
        pass

    def scheduleReview(self, userId: UUID, cardId: UUID, rating: RecallRating) -> FSRSState:
        pass

    def getNextReview(self, cardId: UUID) -> datetime:
        pass


class StudyService:
    fsrsService: FSRSService
    observers: list[SessionObserver]

    def __init__(self, fsrsService: FSRSService) -> None:
        pass

    def startSession(self, userId: UUID) -> ReviewSession:
        pass

    def getNextCard(self, sessionId: UUID) -> Flashcard:
        pass

    def submitGrade(
        self, sessionId: UUID, cardId: UUID, rating: RecallRating, latencyMs: int
    ) -> ReviewLog:
        pass

    def stopSession(self, sessionId: UUID) -> None:
        pass

    def addObserver(self, observer: SessionObserver) -> None:
        pass

    def removeObserver(self, observer: SessionObserver) -> None:
        pass

    def notifyObservers(self, session: ReviewSession, review: ReviewLog) -> None:
        pass


class ProgressService:
    reviewLogs: list[ReviewLog]
    fsrsStates: list[FSRSState]

    def __init__(self, reviewLogs: list[ReviewLog], fsrsStates: list[FSRSState]) -> None:
        pass

    def getUserProgress(self, userId: UUID) -> ProgressReport:
        pass

    def calculateRecallMetrics(self, userId: UUID) -> dict[str, float]:
        pass

    def generateFeedback(self, userId: UUID) -> list[LearningFeedback]:
        pass
