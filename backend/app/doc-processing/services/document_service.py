from typing import Callable, List, Tuple
from uuid import UUID

from domain import Document
from repositories import DocumentRepository
from services.pdf_reader import read_pdf


class DocumentNotFoundError(Exception):
    """Raised when a requested document is not found."""
    pass


class PdfExtractionError(Exception):
    """Raised when no text can be loaded from a PDF."""
    pass


class DocumentService:
    """Application service for uploading and processing documents."""

    def __init__(
        self,
        repository: DocumentRepository,
        pdf_reader: Callable[[str, bytes], Tuple[int, str]] = read_pdf,
    ) -> None:
        self.repository = repository
        self.pdf_reader = pdf_reader

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
            page_count, text = self.pdf_reader(document.filename, document.content)
            text = text.strip()
            if not text:
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

        document.complete(page_count, text)
        self.repository.save(document)
        return document
