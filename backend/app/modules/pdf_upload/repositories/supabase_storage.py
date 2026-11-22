import asyncio
from typing import Protocol

from supabase import Client

from app.modules.pdf_upload.helpers.exceptions import StorageUploadError


class ObjectStorageRepository(Protocol):
    """Port for storing, signing, and deleting PDF objects."""

    async def upload_pdf(
        self,
        *,
        storage_path: str,
        content: bytes,
        content_type: str = "application/pdf",
    ) -> str: ...

    async def create_signed_download_url(
        self,
        *,
        storage_path: str,
        expires_in_seconds: int = 3600,
    ) -> str: ...

    async def delete_pdf(self, *, storage_path: str) -> None: ...


class SupabasePdfStorageRepository:
    """Supabase Storage implementation using a configured bucket."""

    def __init__(self, client: Client, bucket_name: str = "course-materials") -> None:
        self._client = client
        self._bucket_name = bucket_name

    def _bucket(self):
        return self._client.storage.from_(self._bucket_name)

    async def upload_pdf(
        self,
        *,
        storage_path: str,
        content: bytes,
        content_type: str = "application/pdf",
    ) -> str:
        try:
            await asyncio.to_thread(
                self._bucket().upload,
                storage_path,
                content,
                {"content-type": content_type, "upsert": "false"},
            )
            return storage_path
        except Exception as exc:
            raise StorageUploadError(
                f"Failed to upload PDF to '{self._bucket_name}/{storage_path}': {exc}"
            ) from exc

    async def create_signed_download_url(
        self,
        *,
        storage_path: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        try:
            result = await asyncio.to_thread(
                self._bucket().create_signed_url,
                storage_path,
                expires_in_seconds,
            )
        except Exception as exc:
            raise StorageUploadError(
                f"Failed to generate signed URL for '{storage_path}': {exc}"
            ) from exc

        signed_url = self._extract_signed_url(result)
        if not signed_url:
            raise StorageUploadError(
                f"Supabase returned an empty signed URL for '{storage_path}'"
            )
        return signed_url

    async def delete_pdf(self, *, storage_path: str) -> None:
        try:
            await asyncio.to_thread(self._bucket().remove, [storage_path])
        except Exception as exc:
            raise StorageUploadError(
                f"Failed to delete PDF '{storage_path}' from bucket '{self._bucket_name}': {exc}"
            ) from exc

    @staticmethod
    def _extract_signed_url(result: object) -> str | None:
        if isinstance(result, dict):
            return result.get("signedURL") or result.get("signed_url")
        return getattr(result, "signedURL", None) or getattr(result, "signed_url", None)