from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from domain import ProcessingStatus


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: ProcessingStatus
    uploadedAt: datetime


class DocumentDetailResponse(DocumentResponse):
    pageCount: Optional[int]
    preview: Optional[str]
