from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from api.dependencies import get_document_service
from api.schemas import DocumentDetailResponse, DocumentResponse
from domain import Document, InvalidDocumentError
from services import DocumentNotFoundError, DocumentService, PdfExtractionError

router = APIRouter(prefix="/documents", tags=["Document Processing"])


def _map_document_to_response(document: Document) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        uploadedAt=document.uploadedAt,
    )


def _map_document_to_detail_response(document: Document) -> DocumentDetailResponse:
    return DocumentDetailResponse(
        **_map_document_to_response(document).model_dump(),
        pageCount=document.pageCount,
        preview=document.text[:30] if document.text is not None else None,
    )


@router.post("", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: List[UploadFile] = File(..., description="One or more PDF files"),
    service: DocumentService = Depends(get_document_service),
):
    uploads = [(file.filename or "", await file.read()) for file in files]
    try:
        documents = service.uploadDocuments(uploads)
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return [_map_document_to_response(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        return _map_document_to_detail_response(service.loadDocument(document_id))
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{document_id}/process", response_model=DocumentDetailResponse)
def process_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        return _map_document_to_detail_response(service.processDocument(document_id))
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PdfExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )
