from pathlib import Path

from services.pdf_reader import read_pdf


FIXTURE = Path(__file__).parent / "fixtures" / "sample.pdf"


def test_native_docling_reader_extracts_embedded_text_without_ocr():
    page_count, text = read_pdf(FIXTURE.name, FIXTURE.read_bytes())

    assert page_count == 2
    assert "First page paragraph for Docling." in text
    assert "Second page paragraph for Docling." in text
