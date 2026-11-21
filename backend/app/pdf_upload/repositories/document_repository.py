import uuid
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.documents import Document
from app.pdf_upload.helpers.exceptions import MetadataPersistenceError


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        try:
            return self._db.get(Document, document_id)
        except SQLAlchemyError as exc:
            raise MetadataPersistenceError(
                f"Failed to fetch document '{document_id}'"
            ) from exc

    def list_by_student(self, student_id: uuid.UUID) -> list[Document]:
        try:
            stmt = (
                select(Document)
                .where(Document.student_id == student_id)
                .order_by(Document.uploaded_at.desc())
            )
            return list(self._db.scalars(stmt).all())
        except SQLAlchemyError as exc:
            raise MetadataPersistenceError(
                f"Failed to list documents for student '{student_id}'"
            ) from exc

    def create(self, document: Document) -> Document:
        try:
            self._db.add(document)
            self._db.flush()
            return document
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise MetadataPersistenceError(
                f"Failed to persist document '{document.filename}'"
            ) from exc

    def delete(self, document: Document) -> None:
        try:
            self._db.delete(document)
            self._db.flush()
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise MetadataPersistenceError(
                f"Failed to delete document '{document.id}'"
            ) from exc

    def commit(self) -> None:
        try:
            self._db.commit()
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise MetadataPersistenceError("Failed to commit database transaction") from exc