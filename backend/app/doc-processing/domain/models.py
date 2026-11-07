from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

PDF_SIGNATURE = b"%PDF-"


class InvalidDocumentError(Exception):
    """Raised when an uploaded file is not a valid PDF document."""
    pass


class ProcessingStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Flashcard(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    documentId: UUID
    question: str
    answer: str
    sourcePage: int


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    content: bytes = Field(repr=False)
    status: ProcessingStatus = ProcessingStatus.UPLOADED
    uploadedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pageCount: Optional[int] = None
    pages: List[str] = Field(default_factory=list, repr=False, exclude=True)
    summary: Optional[str] = None
    flashcards: List[Flashcard] = Field(default_factory=list)

    @property
    def text(self) -> Optional[str]:
        """Reconstruct the full text for the existing preview response."""
        non_empty_pages = [page for page in self.pages if page.strip()]
        return "\n\n".join(non_empty_pages) if non_empty_pages else None

    def start_processing(self) -> None:
        self.status = ProcessingStatus.PROCESSING
        self.pageCount = None
        self.pages = []
        self.summary = None
        self.flashcards = []

    def complete(self, pages: List[str]) -> None:
        self.pageCount = len(pages)
        self.pages = pages
        self.status = ProcessingStatus.COMPLETED

    def fail(self) -> None:
        self.status = ProcessingStatus.FAILED
        self.pageCount = None
        self.pages = []
        self.summary = None
        self.flashcards = []

    @classmethod
    def from_upload(cls, filename: str, content: bytes) -> "Document":
        """
        Creates an UPLOADED document from a file sent by a client.
        Raises InvalidDocumentError if the file is not a PDF.
        """
        if not filename.lower().endswith(".pdf"):
            raise InvalidDocumentError(f"'{filename}' is not a PDF file.")

        # PDF readers accept the header anywhere in the first 1024 bytes.
        if PDF_SIGNATURE not in content[:1024]:
            raise InvalidDocumentError(f"'{filename}' is not a valid PDF document.")

        return cls(filename=filename, content=content)
