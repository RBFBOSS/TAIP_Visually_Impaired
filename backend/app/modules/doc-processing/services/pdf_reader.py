from io import BytesIO
from threading import Lock
from typing import List

from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import NativePdfPipelineOptions
from docling.document_converter import DocumentConverter, NativePdfFormatOption
from docling_core.types.doc import TextItem

_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: NativePdfFormatOption(
            pipeline_options=NativePdfPipelineOptions()
        )
    }
)
_conversion_lock = Lock()


def read_pdf(filename: str, content: bytes) -> List[str]:
    """Read embedded PDF text without OCR or AI models, grouped by page."""
    with _conversion_lock:
        result = _converter.convert(
            DocumentStream(name=filename, stream=BytesIO(content))
        )
        try:
            document = result.document
            pages = [[] for _ in range(document.num_pages())]
            # One pass keeps page extraction fast on large PDFs.
            for item, _ in document.iterate_items():
                if isinstance(item, TextItem) and item.prov:
                    page_no = item.prov[0].page_no
                    if 1 <= page_no <= len(pages):
                        pages[page_no - 1].append(item.text)
            return ["\n".join(page).strip() for page in pages]
        finally:
            result.input.release()
