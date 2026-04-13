import pdfplumber
from ankigen.parsers.base import Parser


class PdfParser(Parser):
    def parse(self, file_path: str) -> str:
        texts: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
        return "\n".join(texts)
