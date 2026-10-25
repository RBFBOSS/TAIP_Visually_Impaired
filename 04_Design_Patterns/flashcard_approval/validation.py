"""Reference declarations for CitationValidator and Citation; coordinate with teammate."""
from __future__ import annotations
from uuid import UUID
from .models import Flashcard

class Citation:
    id: UUID
    sectionId: UUID
    pageNumber: int
    sourceExcerpt: str

    def getSourceReference(self) -> str:
        pass

class CitationValidator:
    def validateCitation(self, card: Flashcard) -> bool:
        pass

    def verifySource(self, citation: Citation) -> bool:
        pass
