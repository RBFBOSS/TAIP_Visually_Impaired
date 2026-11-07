import pytest

from domain import Document, InvalidDocumentError, ProcessingStatus

PDF_CONTENT = b"%PDF-1.7\n%test document\n"


def test_from_upload_creates_uploaded_document():
    document = Document.from_upload("lesson.pdf", PDF_CONTENT)

    assert document.filename == "lesson.pdf"
    assert document.content == PDF_CONTENT
    assert document.status == ProcessingStatus.UPLOADED
    assert document.pageCount is None
    assert document.text is None


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


def test_processing_lifecycle_stores_text_and_clears_it_on_restart_or_failure():
    document = Document.from_upload("lesson.pdf", PDF_CONTENT)
    document.complete(2, "first text")

    assert document.status == ProcessingStatus.COMPLETED
    assert document.pageCount == 2
    assert document.text == "first text"

    document.start_processing()

    assert document.status == ProcessingStatus.PROCESSING
    assert document.pageCount is None
    assert document.text is None

    document.complete(3, "new text")
    document.fail()

    assert document.status == ProcessingStatus.FAILED
    assert document.pageCount is None
    assert document.text is None
