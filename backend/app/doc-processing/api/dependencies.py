from ai.groq_client import generate_study_material
from repositories import InMemoryDocumentRepository
from services import DocumentService
from services.pdf_reader import read_pdf

_shared_document_repository = InMemoryDocumentRepository()

_shared_document_service = DocumentService(
    repository=_shared_document_repository,
    pdf_reader=read_pdf,
    study_material_generator=generate_study_material,
)


def get_document_service() -> DocumentService:
    return _shared_document_service
