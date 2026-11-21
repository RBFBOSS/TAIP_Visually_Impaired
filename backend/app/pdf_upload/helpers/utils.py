from uuid import UUID


def build_document_storage_path(student_id: UUID, document_id: UUID) -> str:
    """Deterministic object key grouped by student and document ID."""
    return f"students/{student_id}/documents/{document_id}.pdf"