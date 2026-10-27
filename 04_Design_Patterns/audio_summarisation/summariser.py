from .summarisation_strategy import SummarisationStrategy


class Summariser:
    strategy: SummarisationStrategy

    def __init__(self, strategy: SummarisationStrategy) -> None:
        self.strategy = strategy

    def summarise_text(self, text: str) -> str:
        return self.strategy.summarise(text)
