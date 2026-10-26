"""Factory Method pattern for creating PDF text extractors."""

from abc import ABC, abstractmethod

from .extraction import (
    TextExtractionStrategy,
    PyMuPDFExtraction,
    OCRExtraction,
)


class ExtractionFactory(ABC):

    @abstractmethod
    def createExtractor(self) -> TextExtractionStrategy:
        pass


class TextPDFExtractionFactory(ExtractionFactory):

    def createExtractor(self) -> PyMuPDFExtraction:
        pass


class ScannedPDFExtractionFactory(ExtractionFactory):

    def createExtractor(self) -> OCRExtraction:
        pass