from fastapi import Depends
from sqlalchemy.orm import Session

from ai.groq_client import generate_study_material
from app.database.session import get_db
from repositories import InMemoryDocumentRepository, StudyMaterialRepository
from services import DocumentService
from services.pdf_reader import read_pdf

_shared_document_repository = InMemoryDocumentRepository()


def get_study_material_repository(db: Session = Depends(get_db)) -> StudyMaterialRepository:
    """One database session per request."""
    return StudyMaterialRepository(db)


def get_document_service(
    study_material_repository: StudyMaterialRepository = Depends(get_study_material_repository),
) -> DocumentService:
    return DocumentService(
        repository=_shared_document_repository,
        studyMaterialRepository=study_material_repository,
        pdf_reader=read_pdf,
        study_material_generator=generate_study_material,
    )
