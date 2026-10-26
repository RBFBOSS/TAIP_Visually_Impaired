"""Strategy pattern for PDF text extraction."""

from abc import ABC, abstractmethod


class TextExtractionStrategy(ABC):

    @abstractmethod
    def extractText(self, filePath: str) -> str:
        pass


class PyMuPDFExtraction(TextExtractionStrategy):

    def extractText(self, filePath: str) -> str:
        pass


class OCRExtraction(TextExtractionStrategy):

    def extractText(self, filePath: str) -> str:
        pass


class PDFProcessor:

    strategy: TextExtractionStrategy

    def __init__(self, strategy: TextExtractionStrategy) -> None:
        pass

    def processPDF(self, filePath: str) -> str:
        pass