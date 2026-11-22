import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status

from app.modules.pdf_upload.api.dependencies import (
    CurrentUser,
    get_current_user,
    get_upload_service,
    validate_pdf_upload,
)
from app.modules.pdf_upload.api.schemas import DocumentUploadResponse
from app.modules.pdf_upload.helpers.exceptions import (
    FileTooLargeError,
    InvalidPdfError,
    StorageUploadError,
)
from app.modules.pdf_upload.services.upload_service import DocumentUploadService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf_upload", tags=["pdf_upload"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pdf_document(
    file: Annotated[UploadFile, Depends(validate_pdf_upload)],
    title: Annotated[str, Form(..., min_length=1, max_length=255)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[DocumentUploadService, Depends(get_upload_service)],
) -> DocumentUploadResponse:
    try:
        result = await service.upload_pdf(
            file=file,
            title=title,
            student_id=current_user.id,
        )
    except InvalidPdfError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)
        ) from exc
    except StorageUploadError as exc:
        logger.exception("Supabase Storage upload failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to store PDF in Supabase Storage",
        ) from exc

    return DocumentUploadResponse(
        id=result.document_id,
        student_id=result.student_id,
        title=result.title,
        original_filename=result.filename,
        storage_path=result.storage_path,
        size_bytes=result.size_bytes,
        status=result.status.value if hasattr(result.status, "value") else str(result.status),
        download_url=result.download_url,
        uploaded_at=result.uploaded_at,
    )