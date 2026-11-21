MAX_PDF_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
ALLOWED_PDF_CONTENT_TYPES: frozenset[str] = frozenset({"application/pdf"})
PDF_MAGIC_HEADER: bytes = b"%PDF-"