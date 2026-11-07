from typing import Dict, List, Optional
from uuid import UUID

from domain import Document
from repositories.document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """
    In-memory implementation of the document repository.
    Stored documents are lost when the service restarts.
    """

    def __init__(self) -> None:
        self._storage: Dict[UUID, Document] = {}

    def save(self, document: Document) -> None:
        self._storage[document.id] = document

    def save_all(self, documents: List[Document]) -> None:
        for document in documents:
            self.save(document)

    def find_by_id(self, document_id: UUID) -> Optional[Document]:
        return self._storage.get(document_id)
