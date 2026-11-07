from datetime import datetime, timezone
from enum import Enum
from typing import Optional
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


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    content: bytes = Field(repr=False)
    status: ProcessingStatus = ProcessingStatus.UPLOADED
    uploadedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pageCount: Optional[int] = None
    text: Optional[str] = Field(default=None, repr=False, exclude=True)

    def start_processing(self) -> None:
        self.status = ProcessingStatus.PROCESSING
        self.pageCount = None
        self.text = None

    def complete(self, pageCount: int, text: str) -> None:
        self.pageCount = pageCount
        self.text = text
        self.status = ProcessingStatus.COMPLETED

    def fail(self) -> None:
        self.status = ProcessingStatus.FAILED
        self.pageCount = None
        self.text = None

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
