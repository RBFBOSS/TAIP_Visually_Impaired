from repositories import InMemoryDocumentRepository
from services import DocumentService
from services.pdf_reader import read_pdf

_shared_document_repository = InMemoryDocumentRepository()

_shared_document_service = DocumentService(
    repository=_shared_document_repository,
    pdf_reader=read_pdf,
)


def get_document_service() -> DocumentService:
    return _shared_document_service
