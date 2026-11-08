from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain import Document


class DocumentRepository(ABC):
    """Abstract contract for Document entities persistence."""

    @abstractmethod
    def save(self, document: Document) -> None:
        """Saves a document."""
        pass

    @abstractmethod
    def save_all(self, documents: List[Document]) -> None:
        """Saves a collection of documents."""
        pass

    @abstractmethod
    def find_by_id(self, document_id: UUID) -> Optional[Document]:
        """Finds a document by ID. Returns None otherwise."""
        pass

    @abstractmethod
    def find_all(self) -> List[Document]:
        """Finds all stored documents."""
        pass

    @abstractmethod
    def delete(self, document_id: UUID) -> bool:
        """Deletes a document by ID. Returns False when it does not exist."""
        pass
