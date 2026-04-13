from ankigen.parsers import get_parser
from ankigen.parsers.txt import TxtParser
from ankigen.parsers.pdf import PdfParser
from ankigen.parsers.epub import EpubParser
import pytest


def test_txt_parser(sample_txt):
    parser = TxtParser()
    text = parser.parse(str(sample_txt))
    assert "你好" in text
    assert "学生" in text


def test_pdf_parser(sample_pdf):
    parser = PdfParser()
    text = parser.parse(str(sample_pdf))
    assert "Hello World" in text


def test_epub_parser(sample_epub):
    parser = EpubParser()
    text = parser.parse(str(sample_epub))
    assert "Hello World" in text
    assert "<p>" not in text


def test_get_parser_txt(sample_txt):
    parser = get_parser(str(sample_txt))
    assert isinstance(parser, TxtParser)


def test_get_parser_pdf(sample_pdf):
    parser = get_parser(str(sample_pdf))
    assert isinstance(parser, PdfParser)


def test_get_parser_epub(sample_epub):
    parser = get_parser(str(sample_epub))
    assert isinstance(parser, EpubParser)


def test_get_parser_unsupported():
    with pytest.raises(ValueError, match="Unsupported file type"):
        get_parser("file.docx")
