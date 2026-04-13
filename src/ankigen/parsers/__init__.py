from pathlib import Path
from ankigen.parsers.base import Parser
from ankigen.parsers.txt import TxtParser
from ankigen.parsers.pdf import PdfParser
from ankigen.parsers.epub import EpubParser

PARSERS: dict[str, type[Parser]] = {
    ".txt": TxtParser,
    ".pdf": PdfParser,
    ".epub": EpubParser,
}


def get_parser(file_path: str) -> Parser:
    ext = Path(file_path).suffix.lower()
    if ext not in PARSERS:
        supported = ", ".join(sorted(PARSERS.keys()))
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported formats: {supported}"
        )
    return PARSERS[ext]()
