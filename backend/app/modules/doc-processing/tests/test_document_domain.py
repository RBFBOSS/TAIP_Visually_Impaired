import pytest

from domain import Document, InvalidDocumentError, ProcessingStatus

PDF_CONTENT = b"%PDF-1.7\n%test document\n"


def test_from_upload_creates_uploaded_document():
    document = Document.from_upload("lesson.pdf", PDF_CONTENT)

    assert document.filename == "lesson.pdf"
    assert document.content == PDF_CONTENT
    assert document.status == ProcessingStatus.UPLOADED
    assert document.pageCount is None
    assert document.pages == []
    assert document.text is None
    assert document.summary is None
    assert document.flashcards == []


def test_from_upload_accepts_uppercase_extension():
    document = Document.from_upload("LESSON.PDF", PDF_CONTENT)

    assert document.status == ProcessingStatus.UPLOADED


def test_from_upload_gives_each_document_its_own_id():
    first = Document.from_upload("lesson.pdf", PDF_CONTENT)
    second = Document.from_upload("lesson.pdf", PDF_CONTENT)

    assert first.id != second.id


def test_from_upload_rejects_non_pdf_extension():
    with pytest.raises(InvalidDocumentError, match="notes.txt"):
        Document.from_upload("notes.txt", PDF_CONTENT)


def test_from_upload_rejects_content_without_pdf_header():
    with pytest.raises(InvalidDocumentError, match="image.pdf"):
        Document.from_upload("image.pdf", b"\x89PNG\r\n\x1a\n")


def test_from_upload_rejects_empty_file():
    with pytest.raises(InvalidDocumentError, match="empty.pdf"):
        Document.from_upload("empty.pdf", b"")


def test_processing_lifecycle_stores_pages_and_clears_generated_material_on_restart_or_failure():
    document = Document.from_upload("lesson.pdf", PDF_CONTENT)
    document.complete(["first text"])

    assert document.status == ProcessingStatus.COMPLETED
    assert document.pageCount == 1
    assert document.pages == ["first text"]
    assert document.text == "first text"

    document.summary = "old summary"
    document.start_processing()

    assert document.status == ProcessingStatus.PROCESSING
    assert document.pageCount is None
    assert document.pages == []
    assert document.text is None
    assert document.summary is None
    assert document.flashcards == []

    document.complete(["new text", "third page"])
    document.fail()

    assert document.status == ProcessingStatus.FAILED
    assert document.pageCount is None
    assert document.pages == []
    assert document.text is None


def test_text_reconstruction_ignores_empty_pages():
    document = Document.from_upload("lesson.pdf", PDF_CONTENT)
    document.complete(["BASIC MATHEMATICS", "", "SERGE LANG"])

    assert document.text == "BASIC MATHEMATICS\n\nSERGE LANG"
