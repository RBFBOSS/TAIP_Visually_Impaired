class MaterialDomainError(Exception):
    """Base exception for domain-level material errors."""


class InvalidPdfError(MaterialDomainError):
    """Raised when uploaded content is not a valid PDF."""


class FileTooLargeError(MaterialDomainError):
    """Raised when a PDF exceeds the allowed size limit."""


class StorageUploadError(MaterialDomainError):
    """Raised when storing, reading, or deleting a file in object storage fails."""


class MetadataPersistenceError(MaterialDomainError):
    """Raised when saving or updating material metadata fails."""


class MaterialNotFoundError(MaterialDomainError):
    """Raised when a requested material record does not exist."""
