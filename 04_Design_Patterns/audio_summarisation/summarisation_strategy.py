from abc import ABC, abstractmethod


class SummarisationStrategy(ABC):
    @abstractmethod
    def summarise(self, text: str) -> str:
        pass


class SimpleSummarisation(SummarisationStrategy):
    def summarise(self, text: str) -> str:
        pass


class AIBasedSummarisation(SummarisationStrategy):
    def summarise(self, text: str) -> str:
        pass
