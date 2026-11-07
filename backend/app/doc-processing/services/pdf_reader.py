from io import BytesIO
from threading import Lock

from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import NativePdfPipelineOptions
from docling.document_converter import DocumentConverter, NativePdfFormatOption

_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: NativePdfFormatOption(
            pipeline_options=NativePdfPipelineOptions()
        )
    }
)
_conversion_lock = Lock()


def read_pdf(filename: str, content: bytes) -> tuple[int, str]:
    """Read embedded PDF text without OCR or AI models."""
    with _conversion_lock:
        result = _converter.convert(
            DocumentStream(name=filename, stream=BytesIO(content))
        )
        try:
            return result.document.num_pages(), result.document.export_to_text()
        finally:
            result.input.release()
