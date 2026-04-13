import pytest


@pytest.fixture
def sample_txt(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("你好，我是学生。我在学校学习。", encoding="utf-8")
    return path


@pytest.fixture
def sample_pdf(tmp_path):
    from fpdf import FPDF

    path = tmp_path / "sample.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="Hello World. This is a test document.")
    pdf.output(str(path))
    return path


@pytest.fixture
def sample_epub(tmp_path):
    from ebooklib import epub

    book = epub.EpubBook()
    book.set_identifier("test-id")
    book.set_title("Test Book")
    book.set_language("zh")

    chapter = epub.EpubHtml(title="Chapter 1", file_name="chap1.xhtml")
    chapter.content = (
        "<html><body><p>Hello World.</p>"
        "<p>This is a test document.</p></body></html>"
    )
    book.add_item(chapter)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]

    path = tmp_path / "sample.epub"
    epub.write_epub(str(path), book)
    return path
