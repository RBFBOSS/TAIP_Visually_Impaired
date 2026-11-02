from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class ProcessingStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class DocumentSection:
    heading: str
    content: str
    page_number: int
    chunk_index: int
    id: UUID = field(default_factory=uuid4)


@dataclass
class Document:
    filename: str
    id: UUID = field(default_factory=uuid4)
    status: ProcessingStatus = ProcessingStatus.UPLOADED
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sections: list[DocumentSection] = field(default_factory=list)

    def update_status(self, status: ProcessingStatus) -> None:
        self.status = status

    def add_section(self, section: DocumentSection) -> None:
        self.sections.append(section)

    def get_sections(self) -> list[DocumentSection]:
        return self.sections.copy()
