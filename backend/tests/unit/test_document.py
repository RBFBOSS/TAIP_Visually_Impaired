from app.models.document import Document, DocumentSection, ProcessingStatus


def make_section(index: int = 0) -> DocumentSection:
    return DocumentSection(
        heading="Introduction",
        content="Accessible learning content",
        page_number=1,
        chunk_index=index,
    )


def test_update_status_to_processing():
    document = Document(filename="lesson.pdf")
    document.update_status(ProcessingStatus.PROCESSING)
    assert document.status == ProcessingStatus.PROCESSING


def test_update_status_to_completed():
    document = Document(filename="lesson.pdf")
    document.update_status(ProcessingStatus.COMPLETED)
    assert document.status == ProcessingStatus.COMPLETED


def test_add_section_stores_section_on_document():
    document = Document(filename="lesson.pdf")
    section = make_section()
    document.add_section(section)
    assert document.sections == [section]


def test_get_sections_returns_added_sections():
    document = Document(filename="lesson.pdf")
    first = make_section(0)
    second = make_section(1)
    document.add_section(first)
    document.add_section(second)
    assert document.get_sections() == [first, second]


def test_get_sections_returns_empty_list_for_new_document():
    document = Document(filename="lesson.pdf")
    assert document.get_sections() == []
