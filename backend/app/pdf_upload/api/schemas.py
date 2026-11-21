from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    title: str
    original_filename: str
    storage_path: str
    size_bytes: int
    status: str
    download_url: str | None = None
    uploaded_at: datetime