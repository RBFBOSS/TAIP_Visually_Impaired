import logging
from typing import Callable, List, Optional, Tuple
from uuid import UUID

from ai.groq_client import GeneratedStudyMaterial, generate_study_material
from domain import Document, Flashcard
from repositories import DocumentRepository
from services.pdf_reader import read_pdf

logger = logging.getLogger(__name__)

MAX_SOURCE_CHARS = 15_000
DEFAULT_PAGE_SPAN = 9


class DocumentNotFoundError(Exception):
    """Raised when a requested document is not found."""
    pass


class PdfExtractionError(Exception):
    """Raised when no text can be loaded from a PDF."""
    pass


class PageSelectionError(Exception):
    """Raised when the requested pages cannot be sent for generation."""
    pass


class AiGenerationError(Exception):
    """Raised when the AI provider cannot generate valid study material."""
    pass


class FlashcardNotFoundError(Exception):
    """Raised when a requested flashcard is not found."""
    pass


class DocumentService:
    """Application service for uploading and processing documents."""

    def __init__(
        self,
        repository: DocumentRepository,
        pdf_reader: Callable[[str, bytes], List[str]] = read_pdf,
        study_material_generator: Callable[[str], GeneratedStudyMaterial] = generate_study_material,
    ) -> None:
        self.repository = repository
        self.pdf_reader = pdf_reader
        self.study_material_generator = study_material_generator

    def uploadDocuments(self, files: List[Tuple[str, bytes]]) -> List[Document]:
        """
        Creates an UPLOADED Document for each (filename, content) pair and stores them.
        Every file is validated before any is saved, so one invalid file rejects the whole batch.
        """
        documents = [Document.from_upload(filename, content) for filename, content in files]
        self.repository.save_all(documents)
        return documents

    def loadDocument(self, id: UUID) -> Document:
        document = self.repository.find_by_id(id)
        if document is None:
            raise DocumentNotFoundError(f"Document with ID {id} was not found.")
        return document

    def processDocument(self, id: UUID) -> Document:
        document = self.loadDocument(id)
        document.start_processing()
        self.repository.save(document)

        try:
            pages = [page.strip() for page in self.pdf_reader(document.filename, document.content)]
            if not any(pages):
                raise PdfExtractionError(
                    f"No readable text found in '{document.filename}'."
                )
        except Exception as exc:
            document.fail()
            self.repository.save(document)
            if isinstance(exc, PdfExtractionError):
                raise
            raise PdfExtractionError(
                f"Could not read '{document.filename}' as a PDF."
            ) from exc

        document.complete(pages)
        self.repository.save(document)
        return document

    def generateStudyMaterial(
        self,
        id: UUID,
        fromPage: int = 1,
        toPage: Optional[int] = None,
    ) -> Document:
        document = self.loadDocument(id)
        source_text = self._select_source_text(document, fromPage, toPage)

        try:
            generated = self.study_material_generator(source_text)
            flashcards = [
                Flashcard(
                    documentId=document.id,
                    question=card.question,
                    answer=card.answer,
                    sourcePage=card.sourcePage,
                )
                for card in generated.flashcards
            ]
        except Exception as exc:
            logger.exception("AI study-material generation failed for document %s", id)
            raise AiGenerationError(
                f"Could not generate study material for '{document.filename}'."
            ) from exc

        document.summary = generated.summary
        document.flashcards = flashcards
        self.repository.save(document)
        return document

    def loadFlashcard(self, flashcardId: UUID) -> Flashcard:
        for document in self.repository.find_all():
            for flashcard in document.flashcards:
                if flashcard.id == flashcardId:
                    return flashcard
        raise FlashcardNotFoundError(f"Flashcard with ID {flashcardId} was not found.")

    def _select_source_text(
        self,
        document: Document,
        fromPage: int,
        toPage: Optional[int],
    ) -> str:
        if not document.pages:
            raise PageSelectionError(
                f"Document '{document.filename}' has no extracted text. Process it first."
            )

        page_count = len(document.pages)
        if fromPage < 1:
            raise PageSelectionError("fromPage must be at least 1.")
        if toPage is None:
            toPage = min(fromPage + DEFAULT_PAGE_SPAN, page_count)
        if toPage < fromPage:
            raise PageSelectionError("toPage must be greater than or equal to fromPage.")
        if fromPage > page_count or toPage > page_count:
            raise PageSelectionError(
                f"Page range {fromPage}-{toPage} is outside the document's {page_count} pages."
            )

        selected = [
            f"--- Page {page_number} ---\n{document.pages[page_number - 1]}"
            for page_number in range(fromPage, toPage + 1)
            if document.pages[page_number - 1].strip()
        ]
        if not selected:
            raise PageSelectionError(
                f"No readable text found in pages {fromPage}-{toPage}."
            )

        source_text = "\n\n".join(selected)
        if len(source_text) > MAX_SOURCE_CHARS:
            raise PageSelectionError(
                f"Selected pages contain {len(source_text)} characters; "
                f"choose fewer pages (maximum {MAX_SOURCE_CHARS} characters)."
            )
        return source_text
