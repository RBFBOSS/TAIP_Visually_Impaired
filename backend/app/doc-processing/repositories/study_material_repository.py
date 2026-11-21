from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from domain import Citation, Flashcard

from app.models.documents import DocumentProcessingSummary as SummaryORM
from app.models.learning import Citation as CitationORM
from app.models.learning import Flashcard as FlashcardORM


class StudyMaterialRepository:
    """Saves the generated study material (summary and flashcards) in PostgreSQL."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_study_material(
        self,
        document_id: UUID,
        summary: str,
        summary_citation: Citation,
        flashcards: List[Flashcard],
    ) -> None:
        """Replaces the study material stored for one document in a single transaction."""
        self.db.execute(
            delete(FlashcardORM).where(FlashcardORM.document_id == document_id)
        )
        self._save_summary(document_id, summary, summary_citation)
        self.db.add_all(
            [self._flashcard_to_orm(flashcard) for flashcard in flashcards]
        )
        self.db.commit()

    def find_summary(self, document_id: UUID) -> Optional[Tuple[str, Citation]]:
        """Returns the (summary, citation) saved for a document, or None."""
        summary_orm = self.db.get(SummaryORM, document_id)
        if summary_orm is None:
            return None
        return (
            summary_orm.content,
            Citation(
                id=summary_orm.citation_id,
                page_number=summary_orm.citation_page_number,
                source_excerpt=summary_orm.citation_source_excerpt,
            ),
        )

    def find_flashcards(self, document_id: UUID) -> List[Flashcard]:
        """Returns the flashcards saved for a document, with their citations."""
        stmt = (
            select(FlashcardORM)
            .where(FlashcardORM.document_id == document_id)
            .options(selectinload(FlashcardORM.citations))
        )
        orm_flashcards = self.db.scalars(stmt).all()
        return [self._flashcard_to_domain(fc) for fc in orm_flashcards]

    def delete_for_document(self, document_id: UUID) -> None:
        """Deletes the summary and flashcards saved for one document."""
        self.db.execute(
            delete(FlashcardORM).where(FlashcardORM.document_id == document_id)
        )
        self.db.execute(
            delete(SummaryORM).where(SummaryORM.document_id == document_id)
        )
        self.db.commit()

    def _save_summary(
        self,
        document_id: UUID,
        summary: str,
        summary_citation: Citation,
    ) -> None:
        # Update-or-insert: the row keeps its primary key, so re-generating a
        # document must not try to insert a second row for the same id.
        summary_orm = self.db.get(SummaryORM, document_id)
        if summary_orm is None:
            summary_orm = SummaryORM(document_id=document_id)
            self.db.add(summary_orm)
        summary_orm.content = summary
        summary_orm.citation_id = summary_citation.id
        summary_orm.citation_page_number = summary_citation.page_number
        summary_orm.citation_source_excerpt = summary_citation.source_excerpt

    def _flashcard_to_orm(self, flashcard: Flashcard) -> FlashcardORM:
        return FlashcardORM(
            id=flashcard.id,
            document_id=flashcard.documentId,
            question=flashcard.question,
            answer=flashcard.answer,
            citations=[
                CitationORM(
                    id=citation.id,
                    flashcard_id=flashcard.id,
                    page_number=citation.page_number,
                    source_excerpt=citation.source_excerpt,
                )
                for citation in flashcard.citations
            ],
        )

    def _flashcard_to_domain(self, orm_flashcard: FlashcardORM) -> Flashcard:
        return Flashcard(
            id=orm_flashcard.id,
            documentId=orm_flashcard.document_id,
            question=orm_flashcard.question,
            answer=orm_flashcard.answer,
            citations=[
                Citation(
                    id=citation.id,
                    page_number=citation.page_number,
                    source_excerpt=citation.source_excerpt,
                )
                for citation in orm_flashcard.citations
            ],
        )
