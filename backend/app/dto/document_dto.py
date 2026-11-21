from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DocumentUploadResultDTO:
    document_id: UUID
    student_id: UUID
    title: str
    filename: str
    storage_path: str
    size_bytes: int
    sha256: str | None
    status: str
    uploaded_at: datetime
    download_url: str | None = None