"""Command pattern: each approval action is represented by an object."""
from __future__ import annotations
from abc import ABC, abstractmethod
from .models import Flashcard

class FlashcardCommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

class ApproveFlashcardCommand(FlashcardCommand):
    card: Flashcard

    def __init__(self, card: Flashcard) -> None:
        pass

    def execute(self) -> None:
        pass

class RejectFlashcardCommand(FlashcardCommand):
    card: Flashcard

    def __init__(self, card: Flashcard) -> None:
        pass

    def execute(self) -> None:
        pass

class EditFlashcardCommand(FlashcardCommand):
    card: Flashcard
    question: str
    answer: str

    def __init__(self, card: Flashcard, question: str, answer: str) -> None:
        pass

    def execute(self) -> None:
        pass
