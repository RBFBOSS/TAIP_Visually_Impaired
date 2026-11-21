from uuid import uuid4

import pytest

from ai.groq_client import Citation, GeneratedFlashcard, GeneratedStudyMaterial
from domain import InvalidDocumentError, ProcessingStatus
from fakes import FakeStudyMaterialRepository
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
        summary_citation=Citation(page_number=1, source_excerpt="BASIC MATHEMATICS"),
        flashcards=[
            GeneratedFlashcard(
                question="What is the topic?",
                answer="Basic mathematics.",
                citations=[Citation(page_number=1, source_excerpt="BASIC MATHEMATICS")],
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
            studyMaterialRepository=FakeStudyMaterialRepository(),
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


def test_list_documents_returns_all_documents_and_can_filter_by_status():
    service, _ = make_service()
    uploaded = upload_one(service)
    completed = service.uploadDocuments([("complete.pdf", PDF_CONTENT)])[0]
    service.processDocument(completed.id)

    assert service.listDocuments() == [uploaded, completed]
    assert service.listDocuments(status=ProcessingStatus.UPLOADED) == [uploaded]
    assert service.listDocuments(status=ProcessingStatus.COMPLETED) == [completed]
    assert service.listDocuments(status=ProcessingStatus.FAILED) == []


def test_delete_document_removes_it_and_unknown_id_is_not_found():
    service, repository = make_service()
    document = upload_one(service)

    service.deleteDocument(document.id)

    assert repository.find_by_id(document.id) is None
    with pytest.raises(DocumentNotFoundError):
        service.deleteDocument(document.id)


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
    assert result.flashcards[0].citations[0].page_number == 1
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
    assert len(service.studyMaterialRepository.find_flashcards(document.id)) == 1
    saved_summary = service.studyMaterialRepository.find_summary(document.id)
    assert saved_summary is not None
    assert saved_summary[0] == previous_summary


def test_load_flashcard_finds_saved_card_and_rejects_unknown_id():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)
    flashcard = document.flashcards[0]

    assert service.loadFlashcard(flashcard.id) is flashcard
    with pytest.raises(FlashcardNotFoundError):
        service.loadFlashcard(uuid4())


def test_generate_study_material_saves_the_generated_study_material_in_the_repository():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)

    service.generateStudyMaterial(document.id)

    saved_summary = service.studyMaterialRepository.find_summary(document.id)
    assert saved_summary[0] == "A short summary."
    assert saved_summary[1].page_number == 1
    assert saved_summary[1].source_excerpt == "BASIC MATHEMATICS"

    saved_flashcards = service.studyMaterialRepository.find_flashcards(document.id)
    assert [flashcard.id for flashcard in saved_flashcards] == [
        flashcard.id for flashcard in document.flashcards
    ]
    assert saved_flashcards[0].documentId == document.id
    assert saved_flashcards[0].citations[0].page_number == 1


def test_generate_study_material_replaces_the_previous_study_material():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)

    service.generateStudyMaterial(document.id)
    first_cards = service.studyMaterialRepository.find_flashcards(document.id)
    first_summary = service.studyMaterialRepository.find_summary(document.id)
    service.generateStudyMaterial(document.id)
    second_cards = service.studyMaterialRepository.find_flashcards(document.id)
    second_summary = service.studyMaterialRepository.find_summary(document.id)

    assert len(second_cards) == 1
    assert second_cards[0].id != first_cards[0].id
    assert second_summary[1].id != first_summary[1].id


def test_process_document_clears_the_saved_study_material():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)
    assert service.studyMaterialRepository.find_flashcards(document.id)
    assert service.studyMaterialRepository.find_summary(document.id) is not None

    service.processDocument(document.id)

    assert service.studyMaterialRepository.find_flashcards(document.id) == []
    assert service.studyMaterialRepository.find_summary(document.id) is None


def test_delete_document_clears_the_saved_study_material():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)

    service.deleteDocument(document.id)

    assert service.studyMaterialRepository.find_flashcards(document.id) == []
    assert service.studyMaterialRepository.find_summary(document.id) is None


def test_load_flashcards_reads_the_saved_flashcards_of_any_document():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)

    assert [f.id for f in service.loadFlashcards(document.id)] == [
        f.id for f in document.flashcards
    ]
    assert service.loadFlashcards(uuid4()) == []


def test_load_summary_reads_the_saved_summary_of_any_document():
    service, _ = make_service()
    document = upload_one(service)
    service.processDocument(document.id)
    service.generateStudyMaterial(document.id)

    summary = service.loadSummary(document.id)
    assert summary[0] == "A short summary."
    assert summary[1].page_number == 1
    assert service.loadSummary(uuid4()) is None
