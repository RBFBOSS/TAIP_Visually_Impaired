from uuid import uuid4

import pytest

from ai.groq_client import GeneratedFlashcard, GeneratedStudyMaterial
from domain import InvalidDocumentError, ProcessingStatus
from repositories import InMemoryDocumentRepository
from services import (
    AiGenerationError,
    DocumentNotFoundError,
    DocumentService,
    FlashcardNotFoundError,
    PageSelectionError,
    PdfExtractionError,
)

PDF_CONTENT = b"%PDF-1.7\n%test document\n"
PDF_TEXT = "BASIC MATHEMATICS\n\nThis is a paragraph from the PDF."
PDF_PAGES = [PDF_TEXT, "Second page paragraph for Docling."]


def fake_read_pdf(filename: str, content: bytes) -> list[str]:
    return PDF_PAGES.copy()


def fake_generate_study_material(text: str) -> GeneratedStudyMaterial:
    return GeneratedStudyMaterial(
        summary="A short summary.",
        flashcards=[
            GeneratedFlashcard(
                question="What is the topic?",
                answer="Basic mathematics.",
                sourcePage=1,
            )
        ],
    )


def make_service(
    pdf_reader=fake_read_pdf,
    study_material_generator=fake_generate_study_material,
) -> tuple[DocumentService, InMemoryDocumentRepository]:
    repository = InMemoryDocumentRepository()
    return (
        DocumentService(
            repository=repository,
            pdf_reader=pdf_reader,
            study_material_generator=study_material_generator,
        ),
        repository,
    )


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


def test_process_document_stores_page_count_and_pages():
    service, repository = make_service()
    document = upload_one(service)

    processed = service.processDocument(document.id)

    assert processed.status == ProcessingStatus.COMPLETED
    assert processed.content == PDF_CONTENT
    assert processed.pageCount == 2
    assert processed.pages == PDF_PAGES
    assert processed.text == "\n\n".join(PDF_PAGES)
    assert repository.find_by_id(document.id) is processed


def test_process_document_replaces_previous_pages_on_repeat():
    responses = iter([["old text"], ["new text", "another page"]])
    service, _ = make_service(pdf_reader=lambda filename, content: next(responses))
    document = upload_one(service)

    service.processDocument(document.id)
    processed = service.processDocument(document.id)

    assert processed.pageCount == 2
    assert processed.pages == ["new text", "another page"]


def test_process_document_marks_failed_when_reader_returns_no_text():
    service, repository = make_service(pdf_reader=lambda filename, content: ["  "])
    document = upload_one(service)

    with pytest.raises(PdfExtractionError, match="No readable text"):
        service.processDocument(document.id)

    stored = repository.find_by_id(document.id)
    assert stored.status == ProcessingStatus.FAILED
    assert stored.pageCount is None
    assert stored.pages == []
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
    assert stored.pages == []
    assert stored.text is None


def test_generate_study_material_uses_default_ten_page_range_and_skips_empty_pages():
    pages = [f"Content for page {number}." for number in range(1, 13)]
    pages[2] = " "
    captured = {}

    def generator(text: str) -> GeneratedStudyMaterial:
        captured["text"] = text
        return fake_generate_study_material(text)

    service, repository = make_service(
        pdf_reader=lambda filename, content: pages,
        study_material_generator=generator,
    )
    document = upload_one(service)
    service.processDocument(document.id)

    result = service.generateStudyMaterial(document.id)

    assert "--- Page 1 ---\nContent for page 1." in captured["text"]
    assert "--- Page 3 ---" not in captured["text"]
    assert "--- Page 10 ---\nContent for page 10." in captured["text"]
    assert "--- Page 11 ---" not in captured["text"]
    assert result.summary == "A short summary."
    assert len(result.flashcards) == 1
    assert result.flashcards[0].documentId == document.id
    assert result.flashcards[0].sourcePage == 1
    assert repository.find_by_id(document.id) is result


def test_generate_study_material_uses_requested_page_range():
    captured = {}

    def generator(text: str) -> GeneratedStudyMaterial:
        captured["text"] = text
        return fake_generate_study_material(text)

    service, _ = make_service(study_material_generator=generator)
    document = upload_one(service)
    service.processDocument(document.id)

    service.generateStudyMaterial(document.id, fromPage=2, toPage=2)

    assert captured["text"].startswith("--- Page 2 ---")
    assert "Page 1" not in captured["text"]


def test_generate_study_material_rejects_unprocessed_document():
    service, _ = make_service()
    document = upload_one(service)

    with pytest.raises(PageSelectionError, match="Process it first"):
        service.generateStudyMaterial(document.id)


def test_generate_study_material_rejects_empty_or_invalid_page_selection():
    service, _ = make_service(
        pdf_reader=lambda filename, content: ["content", " ", " "]
    )
    document = upload_one(service)
    service.processDocument(document.id)

    with pytest.raises(PageSelectionError, match="No readable text"):
        service.generateStudyMaterial(document.id, fromPage=2, toPage=3)
    with pytest.raises(PageSelectionError, match="outside"):
        service.generateStudyMaterial(document.id, fromPage=1, toPage=4)
    with pytest.raises(PageSelectionError, match="greater than"):
        service.generateStudyMaterial(document.id, fromPage=2, toPage=1)


def test_generate_study_material_rejects_text_over_the_token_budget():
    service, _ = make_service(
        pdf_reader=lambda filename, content: ["x" * 15_001]
    )
    document = upload_one(service)
    service.processDocument(document.id)

    with pytest.raises(PageSelectionError, match="choose fewer pages"):
        service.generateStudyMaterial(document.id)


def test_generate_study_material_failure_keeps_previous_results():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)
    previous_summary = document.summary
    previous_flashcards = document.flashcards

    def failing_generator(text: str):
        raise RuntimeError("provider unavailable")

    service.study_material_generator = failing_generator
    with pytest.raises(AiGenerationError, match="Could not generate"):
        service.generateStudyMaterial(document.id)

    assert document.summary == previous_summary
    assert document.flashcards == previous_flashcards


def test_load_flashcard_finds_saved_card_and_rejects_unknown_id():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)
    flashcard = document.flashcards[0]

    assert service.loadFlashcard(flashcard.id) is flashcard
    with pytest.raises(FlashcardNotFoundError):
        service.loadFlashcard(uuid4())
