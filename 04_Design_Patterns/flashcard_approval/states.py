"""State pattern: abstract state and concrete approval states."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .models import Flashcard

class FlashcardState(ABC):
    @abstractmethod
    def approve(self, card: Flashcard) -> None:
        pass

    @abstractmethod
    def reject(self, card: Flashcard) -> None:
        pass

class DraftState(FlashcardState):
    def approve(self, card: Flashcard) -> None:
        pass

    def reject(self, card: Flashcard) -> None:
        pass

class ApprovedState(FlashcardState):
    def approve(self, card: Flashcard) -> None:
        pass

    def reject(self, card: Flashcard) -> None:
        pass

class RejectedState(FlashcardState):
    def approve(self, card: Flashcard) -> None:
        pass

    def reject(self, card: Flashcard) -> None:
        pass
