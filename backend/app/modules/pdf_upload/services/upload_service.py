from datetime import datetime, timezone
import hashlib
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.dto.document_dto import DocumentUploadResultDTO
from app.models.documents import Document
from app.models.enums import ProcessingStatus
from app.modules.pdf_upload.helpers.constants import (
    MAX_PDF_SIZE_BYTES,
    PDF_MAGIC_HEADER,
)
from app.modules.pdf_upload.helpers.exceptions import (
    FileTooLargeError,
    InvalidPdfError,
    StorageUploadError,
)
from app.modules.pdf_upload.repositories.document_repository import DocumentRepository
from app.modules.pdf_upload.repositories.supabase_storage import ObjectStorageRepository

_CHUNK_SIZE_BYTES = 64 * 1024


class DocumentUploadService:
    def __init__(
        self,
        *,
        db: Session,
        storage_repo: ObjectStorageRepository,
        document_repo: DocumentRepository,
        max_size_bytes: int = MAX_PDF_SIZE_BYTES,
    ) -> None:
        self._db = db
        self._storage = storage_repo
        self._documents = document_repo
        self._max_size_bytes = max_size_bytes

    async def upload_pdf(
        self,
        *,
        file: UploadFile,
        title: str,
        student_id: UUID,
        managed_by_validator_id: UUID | None = None,
    ) -> DocumentUploadResultDTO:
        data, sha256, safe_filename = await self._read_and_validate_pdf(file)
        doc_id = uuid4()
        storage_path = f"students/{student_id}/documents/{doc_id}/{safe_filename}"

        # 1. Încărcare fișier în Supabase Storage
        await self._storage.upload_pdf(
            storage_path=storage_path,
            content=data,
            content_type="application/pdf",
        )

        now = datetime.now(timezone.utc)
        document = Document(
            id=doc_id,
            student_id=student_id,
            managed_by_validator_id=managed_by_validator_id,
            title=title.strip() or safe_filename,
            filename=safe_filename,
            storage_path=storage_path,
            content_type="application/pdf",
            size_bytes=len(data),
            sha256=sha256,
            status=ProcessingStatus.UPLOADED,
            uploaded_at=now,
        )

        # 2. Persistență în BD (cu rollback pe Storage dacă eșuează)
        try:
            saved = self._documents.create(document)
            self._documents.commit()
        except Exception:
            try:
                await self._storage.delete_pdf(storage_path=storage_path)
            except StorageUploadError:
                pass
            raise

        # 3. Generare signed URL (opțional, nu blochează upload-ul dacă pică)
        try:
            download_url = await self._storage.create_signed_download_url(
                storage_path=saved.storage_path,
                expires_in_seconds=3600,
            )
        except StorageUploadError:
            download_url = None

        return DocumentUploadResultDTO(
            document_id=saved.id,
            student_id=saved.student_id,
            title=saved.title,
            filename=saved.filename,
            storage_path=saved.storage_path,
            size_bytes=saved.size_bytes,
            sha256=saved.sha256,
            status=saved.status.value,
            uploaded_at=saved.uploaded_at,
            download_url=download_url,
        )

    async def _read_and_validate_pdf(self, file: UploadFile) -> tuple[bytes, str, str]:
        hasher = hashlib.sha256()
        chunks: list[bytes] = []
        total_bytes = 0

        try:
            while True:
                chunk = await file.read(_CHUNK_SIZE_BYTES)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > self._max_size_bytes:
                    raise FileTooLargeError(
                        f"PDF exceeds maximum size of {self._max_size_bytes} bytes"
                    )
                hasher.update(chunk)
                chunks.append(chunk)
        finally:
            await file.close()

        data = b"".join(chunks)
        if not data or not data.startswith(PDF_MAGIC_HEADER):
            raise InvalidPdfError("Uploaded file does not have a valid %PDF- header")

        safe_filename = (file.filename or "document.pdf").split("/")[-1].split("\\")[-1]
        return data, hasher.hexdigest(), safe_filename