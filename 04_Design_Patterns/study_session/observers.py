"""Observer pattern declarations for study-review notifications."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .models import ReviewLog, ReviewSession

if TYPE_CHECKING:
    from .services import ProgressService


class SessionObserver(ABC):
    @abstractmethod
    def onReview(self, session: ReviewSession, review: ReviewLog) -> None:
        pass


class ProgressObserver(SessionObserver):
    progressService: ProgressService

    def __init__(self, progressService: ProgressService) -> None:
        pass

    def onReview(self, session: ReviewSession, review: ReviewLog) -> None:
        pass
