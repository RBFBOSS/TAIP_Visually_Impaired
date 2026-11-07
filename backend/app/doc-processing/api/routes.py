from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from api.dependencies import get_document_service
from api.schemas import (
    DocumentDetailResponse,
    DocumentResponse,
    FlashcardResponse,
    StudyMaterialResponse,
    SummaryResponse,
)
from domain import Document, Flashcard, InvalidDocumentError
from services import (
    AiGenerationError,
    DocumentNotFoundError,
    DocumentService,
    FlashcardNotFoundError,
    PageSelectionError,
    PdfExtractionError,
)

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


def _map_flashcard_to_response(flashcard: Flashcard) -> FlashcardResponse:
    return FlashcardResponse(
        id=flashcard.id,
        documentId=flashcard.documentId,
        question=flashcard.question,
        answer=flashcard.answer,
        sourcePage=flashcard.sourcePage,
    )


def _map_study_material_to_response(document: Document) -> StudyMaterialResponse:
    return StudyMaterialResponse(
        documentId=document.id,
        summary=document.summary or "",
        flashcards=[
            _map_flashcard_to_response(flashcard)
            for flashcard in document.flashcards
        ],
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


@router.post("/{document_id}/generate", response_model=StudyMaterialResponse)
def generate_study_material(
    document_id: UUID,
    fromPage: int = Query(default=1, ge=1),
    toPage: Optional[int] = Query(default=None, ge=1),
    service: DocumentService = Depends(get_document_service),
):
    try:
        document = service.generateStudyMaterial(document_id, fromPage, toPage)
        return _map_study_material_to_response(document)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PageSelectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )
    except AiGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )


@router.get("/summary/{document_id}", response_model=SummaryResponse)
def get_summary(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        document = service.loadDocument(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if document.summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary has been generated for document {document_id}.",
        )
    return SummaryResponse(documentId=document.id, summary=document.summary)


@router.get("/flashcards/{document_id}", response_model=List[FlashcardResponse])
def get_flashcards(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        document = service.loadDocument(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return [_map_flashcard_to_response(flashcard) for flashcard in document.flashcards]


@router.get("/flashcard/{flashcardId}", response_model=FlashcardResponse)
def get_flashcard(
    flashcardId: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        return _map_flashcard_to_response(service.loadFlashcard(flashcardId))
    except FlashcardNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
