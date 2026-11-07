from uuid import uuid4

import pytest

from domain import InvalidDocumentError, ProcessingStatus
from repositories import InMemoryDocumentRepository
from services import DocumentNotFoundError, DocumentService, PdfExtractionError

PDF_CONTENT = b"%PDF-1.7\n%test document\n"
PDF_TEXT = "BASIC MATHEMATICS\n\nThis is a paragraph from the PDF."


def fake_read_pdf(filename: str, content: bytes) -> tuple[int, str]:
    return 2, PDF_TEXT


def make_service(pdf_reader=fake_read_pdf) -> tuple[DocumentService, InMemoryDocumentRepository]:
    repository = InMemoryDocumentRepository()
    return DocumentService(repository=repository, pdf_reader=pdf_reader), repository


def upload_one(service: DocumentService):
    return service.uploadDocuments([("lesson.pdf", PDF_CONTENT)])[0]


def test_upload_documents_saves_every_pdf():
    service, repository = make_service()

    documents = service.uploadDocuments(
        [("first.pdf", PDF_CONTENT), ("second.pdf", PDF_CONTENT)]
    )

    assert [document.filename for document in documents] == ["first.pdf", "second.pdf"]
    for document in documents:
        assert document.status == ProcessingStatus.UPLOADED
        assert repository.find_by_id(document.id) is document


def test_upload_documents_rejects_whole_batch_when_one_file_is_invalid():
    service, repository = make_service()

    with pytest.raises(InvalidDocumentError, match="notes.txt"):
        service.uploadDocuments([("first.pdf", PDF_CONTENT), ("notes.txt", b"plain text")])

    assert repository._storage == {}


def test_load_document_rejects_unknown_id():
    service, _ = make_service()

    with pytest.raises(DocumentNotFoundError):
        service.loadDocument(uuid4())


def test_process_document_stores_page_count_and_full_text():
    service, repository = make_service()
    document = upload_one(service)

    processed = service.processDocument(document.id)

    assert processed.status == ProcessingStatus.COMPLETED
    assert processed.content == PDF_CONTENT
    assert processed.pageCount == 2
    assert processed.text == PDF_TEXT
    assert repository.find_by_id(document.id) is processed


def test_process_document_replaces_previous_text_on_repeat():
    responses = iter([(1, "old text"), (3, "new text")])
    service, _ = make_service(pdf_reader=lambda filename, content: next(responses))
    document = upload_one(service)

    service.processDocument(document.id)
    processed = service.processDocument(document.id)

    assert processed.pageCount == 3
    assert processed.text == "new text"


def test_process_document_marks_failed_when_reader_returns_no_text():
    service, repository = make_service(pdf_reader=lambda filename, content: (1, "  "))
    document = upload_one(service)

    with pytest.raises(PdfExtractionError, match="No readable text"):
        service.processDocument(document.id)

    stored = repository.find_by_id(document.id)
    assert stored.status == ProcessingStatus.FAILED
    assert stored.pageCount is None
    assert stored.text is None


def test_process_document_marks_failed_when_reader_raises():
    def failing_reader(filename, content):
        raise ValueError("broken PDF")

    service, repository = make_service(pdf_reader=failing_reader)
    document = upload_one(service)

    with pytest.raises(PdfExtractionError, match="Could not read"):
        service.processDocument(document.id)

    stored = repository.find_by_id(document.id)
    assert stored.status == ProcessingStatus.FAILED
    assert stored.pageCount is None
    assert stored.text is None
