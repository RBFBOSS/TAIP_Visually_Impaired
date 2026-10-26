"""Adapter pattern declarations for the external FSRS scheduler."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import FSRSState, RecallRating


class FSRSScheduler(ABC):
    @abstractmethod
    def calculateNextReview(self, state: FSRSState, rating: RecallRating) -> FSRSState:
        pass


class FSRSLibrary:
    """External API reference only; no scheduling library is implemented here."""

    def review(self, state: FSRSState, rating: RecallRating) -> FSRSState:
        pass


class FSRSAdapter(FSRSScheduler):
    library: FSRSLibrary

    def __init__(self, library: FSRSLibrary) -> None:
        pass

    def calculateNextReview(self, state: FSRSState, rating: RecallRating) -> FSRSState:
        pass
