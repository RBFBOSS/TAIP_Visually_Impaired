from typing import Dict, List, Optional, Tuple
from uuid import UUID

from domain import Citation, Flashcard


class FakeStudyMaterialRepository:
    """In-memory stand-in for StudyMaterialRepository, used by the tests."""

    def __init__(self) -> None:
        self.flashcards_by_document: Dict[UUID, List[Flashcard]] = {}
        self.summaries_by_document: Dict[UUID, Tuple[str, Citation]] = {}

    def save_study_material(
        self,
        document_id: UUID,
        summary: str,
        summary_citation: Citation,
        flashcards: List[Flashcard],
    ) -> None:
        self.summaries_by_document[document_id] = (summary, summary_citation)
        self.flashcards_by_document[document_id] = list(flashcards)

    def find_summary(self, document_id: UUID) -> Optional[Tuple[str, Citation]]:
        return self.summaries_by_document.get(document_id)

    def find_flashcards(self, document_id: UUID) -> List[Flashcard]:
        return list(self.flashcards_by_document.get(document_id, []))

    def delete_for_document(self, document_id: UUID) -> None:
        self.flashcards_by_document.pop(document_id, None)
        self.summaries_by_document.pop(document_id, None)
