from uuid import UUID

from fastapi import Depends, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.pdf_upload.helpers.constants import ALLOWED_PDF_CONTENT_TYPES, MAX_PDF_SIZE_BYTES
from app.modules.pdf_upload.repositories.document_repository import DocumentRepository
from app.modules.pdf_upload.services.upload_service import DocumentUploadService

DEV_DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class CurrentUser:
    def __init__(self, id: UUID = DEV_DEFAULT_USER_ID, role: str = "admin") -> None:
        self.id = id
        self.role = role


def get_current_user(request: Request) -> CurrentUser:
    """Temporary no-auth dependency; replace with real session/JWT lookup later."""
    return CurrentUser()


def require_instructor_or_admin() -> CurrentUser:
    """Temporary no-auth role check; replace once roles exist."""
    return CurrentUser()


def get_storage_client(request: Request):
    """Retrieve the storage client initialized during app lifespan startup."""
    storage = getattr(request.app.state, "supabase_storage", None)
    if storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage client is not initialized",
        )
    return storage


def get_upload_service(
    request: Request,
    db: Session = Depends(get_db),
) -> DocumentUploadService:
    """Build DocumentUploadService per request with a fresh SQLAlchemy Session."""
    storage = get_storage_client(request)
    repository = DocumentRepository(db=db)
    return DocumentUploadService(
        db=db,
        storage_repo=storage,
        document_repo=repository,
    )


async def validate_pdf_upload(file: UploadFile) -> UploadFile:
    """Early HTTP-level check for filename, content type, and declared/streamed size."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pdf files are accepted",
        )

    if file.content_type and file.content_type.lower() not in ALLOWED_PDF_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {file.content_type}",
        )

    if file.size is not None and file.size > MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF exceeds maximum allowed size of {MAX_PDF_SIZE_BYTES} bytes",
        )

    return file