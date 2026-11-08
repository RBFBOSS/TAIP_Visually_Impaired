from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from ai.groq_client import GeneratedFlashcard, GeneratedStudyMaterial
from api.dependencies import get_document_service
from main import app
from repositories import InMemoryDocumentRepository
from services import DocumentService

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


@pytest.fixture
def repository():
    repository = InMemoryDocumentRepository()
    app.dependency_overrides[get_document_service] = lambda: DocumentService(
        repository=repository,
        pdf_reader=fake_read_pdf,
        study_material_generator=fake_generate_study_material,
    )
    yield repository
    app.dependency_overrides.clear()


@pytest.fixture
def client(repository):
    return TestClient(app)


def pdf_part(filename: str):
    return ("files", (filename, PDF_CONTENT, "application/pdf"))


def upload_and_process(client):
    upload = client.post("/documents", files=[pdf_part("lesson.pdf")])
    document_id = upload.json()[0]["id"]
    assert client.post(f"/documents/{document_id}/process").status_code == 200
    return document_id


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


def test_list_documents_and_filter_by_status(client):
    uploaded = client.post("/documents", files=[pdf_part("uploaded.pdf")])
    completed = client.post("/documents", files=[pdf_part("completed.pdf")])
    completed_id = completed.json()[0]["id"]
    assert client.post(f"/documents/{completed_id}/process").status_code == 200

    response = client.get("/documents")

    assert response.status_code == 200
    assert [item["filename"] for item in response.json()] == [
        "uploaded.pdf", "completed.pdf"
    ]
    assert client.get("/documents?status=UPLOADED").json() == uploaded.json()
    assert [item["filename"] for item in
            client.get("/documents?status=COMPLETED").json()] == ["completed.pdf"]
    assert client.get("/documents?status=INVALID").status_code == 422


def test_delete_document_and_unknown_id(client, repository):
    upload = client.post("/documents", files=[pdf_part("lesson.pdf")])
    document_id = upload.json()[0]["id"]

    deleted = client.delete(f"/documents/{document_id}")

    assert deleted.status_code == 204
    assert repository.find_by_id(UUID(document_id)) is None
    assert client.get(f"/documents/{document_id}").status_code == 404
    assert client.delete(f"/documents/{document_id}").status_code == 404


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
    assert "pages" not in body
    assert "summary" not in body
    assert "flashcards" not in body
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
        pdf_reader=lambda filename, content: [""],
        study_material_generator=fake_generate_study_material,
    )

    processed = client.post(f"/documents/{document_id}/process")

    assert processed.status_code == 422
    assert "No readable text" in processed.json()["detail"]
    stored = client.get(f"/documents/{document_id}")
    assert stored.status_code == 200
    assert stored.json()["status"] == "FAILED"
    assert stored.json()["pageCount"] is None
    assert stored.json()["preview"] is None


def test_generate_then_read_summary_flashcards_and_one_flashcard(client):
    document_id = upload_and_process(client)

    assert client.get(f"/documents/summary/{document_id}").status_code == 404
    assert client.get(f"/documents/flashcards/{document_id}").json() == []

    generated = client.post(
        f"/documents/{document_id}/generate?fromPage=1&toPage=2"
    )

    assert generated.status_code == 200
    body = generated.json()
    assert set(body) == {"documentId", "summary", "flashcards"}
    assert body["documentId"] == document_id
    assert body["summary"] == "A short summary."
    assert len(body["flashcards"]) == 1
    card = body["flashcards"][0]
    assert set(card) == {"id", "documentId", "question", "answer", "sourcePage"}
    assert card["documentId"] == document_id

    summary = client.get(f"/documents/summary/{document_id}")
    assert summary.status_code == 200
    assert summary.json() == {"documentId": document_id, "summary": "A short summary."}

    flashcards = client.get(f"/documents/flashcards/{document_id}")
    assert flashcards.status_code == 200
    assert flashcards.json() == [card]

    one_card = client.get(f"/documents/flashcard/{card['id']}")
    assert one_card.status_code == 200
    assert one_card.json() == card


def test_generate_and_read_endpoints_return_404_for_unknown_ids(client):
    document_id = uuid4()
    flashcard_id = uuid4()

    assert client.post(f"/documents/{document_id}/generate").status_code == 404
    assert client.get(f"/documents/summary/{document_id}").status_code == 404
    assert client.get(f"/documents/flashcards/{document_id}").status_code == 404
    assert client.get(f"/documents/flashcard/{flashcard_id}").status_code == 404


def test_generate_rejects_unprocessed_document_and_invalid_range(client):
    upload = client.post("/documents", files=[pdf_part("lesson.pdf")])
    document_id = upload.json()[0]["id"]

    unprocessed = client.post(f"/documents/{document_id}/generate")
    assert unprocessed.status_code == 422

    assert client.post(f"/documents/{document_id}/process").status_code == 200
    invalid_range = client.post(
        f"/documents/{document_id}/generate?fromPage=2&toPage=1"
    )
    assert invalid_range.status_code == 422


def test_generate_returns_502_when_ai_provider_fails(client, repository):
    document_id = upload_and_process(client)

    def failing_generator(text: str):
        raise RuntimeError("provider unavailable")

    app.dependency_overrides[get_document_service] = lambda: DocumentService(
        repository=repository,
        pdf_reader=fake_read_pdf,
        study_material_generator=failing_generator,
    )

    response = client.post(f"/documents/{document_id}/generate")

    assert response.status_code == 502
    assert "Could not generate" in response.json()["detail"]
