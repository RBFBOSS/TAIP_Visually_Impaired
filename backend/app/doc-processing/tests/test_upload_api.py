from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_document_service
from main import app
from repositories import InMemoryDocumentRepository
from services import DocumentService

PDF_CONTENT = b"%PDF-1.7\n%test document\n"
PDF_TEXT = "BASIC MATHEMATICS\n\nThis is a paragraph from the PDF."


def fake_read_pdf(filename: str, content: bytes) -> tuple[int, str]:
    return 2, PDF_TEXT


@pytest.fixture
def repository():
    repository = InMemoryDocumentRepository()
    app.dependency_overrides[get_document_service] = lambda: DocumentService(
        repository=repository,
        pdf_reader=fake_read_pdf,
    )
    yield repository
    app.dependency_overrides.clear()


@pytest.fixture
def client(repository):
    return TestClient(app)


def pdf_part(filename: str):
    return ("files", (filename, PDF_CONTENT, "application/pdf"))


def test_upload_multiple_pdfs_returns_created_documents(client, repository):
    response = client.post("/documents", files=[pdf_part("first.pdf"), pdf_part("second.pdf")])

    assert response.status_code == 201
    body = response.json()
    assert [item["filename"] for item in body] == ["first.pdf", "second.pdf"]
    for item in body:
        assert set(item) == {"id", "filename", "status", "uploadedAt"}
        assert item["status"] == "UPLOADED"
        assert repository.find_by_id(UUID(item["id"])) is not None


def test_upload_with_a_non_pdf_file_is_rejected_and_nothing_is_saved(client, repository):
    response = client.post(
        "/documents",
        files=[pdf_part("first.pdf"), ("files", ("notes.txt", b"plain text", "text/plain"))],
    )

    assert response.status_code == 400
    assert "notes.txt" in response.json()["detail"]
    assert repository._storage == {}


def test_upload_without_files_is_rejected(client):
    response = client.post("/documents")

    assert response.status_code == 422


def test_process_and_get_document_return_page_count_and_preview(client):
    upload = client.post("/documents", files=[pdf_part("lesson.pdf")])
    document_id = upload.json()[0]["id"]

    unprocessed = client.get(f"/documents/{document_id}")

    assert unprocessed.status_code == 200
    assert set(unprocessed.json()) == {
        "id", "filename", "status", "uploadedAt", "pageCount", "preview"
    }
    assert unprocessed.json()["status"] == "UPLOADED"
    assert unprocessed.json()["pageCount"] is None
    assert unprocessed.json()["preview"] is None

    processed = client.post(f"/documents/{document_id}/process")

    assert processed.status_code == 200
    body = processed.json()
    assert body["status"] == "COMPLETED"
    assert body["pageCount"] == 2
    assert body["preview"] == PDF_TEXT[:30]
    assert len(body["preview"]) == 30
    assert "text" not in body
    assert "sections" not in body
    assert client.get(f"/documents/{document_id}").json() == body


def test_get_and_process_unknown_document_return_not_found(client):
    document_id = uuid4()

    assert client.get(f"/documents/{document_id}").status_code == 404
    assert client.post(f"/documents/{document_id}/process").status_code == 404


def test_failed_processing_returns_422_and_persists_failed_status(client, repository):
    upload = client.post("/documents", files=[pdf_part("lesson.pdf")])
    document_id = upload.json()[0]["id"]
    app.dependency_overrides[get_document_service] = lambda: DocumentService(
        repository=repository,
        pdf_reader=lambda filename, content: (1, ""),
    )

    processed = client.post(f"/documents/{document_id}/process")

    assert processed.status_code == 422
    assert "No readable text" in processed.json()["detail"]
    stored = client.get(f"/documents/{document_id}")
    assert stored.status_code == 200
    assert stored.json()["status"] == "FAILED"
    assert stored.json()["pageCount"] is None
    assert stored.json()["preview"] is None
