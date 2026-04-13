import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from ankigen.parsers.base import Parser


class EpubParser(Parser):
    def parse(self, file_path: str) -> str:
        book = epub.read_epub(file_path)
        texts: list[str] = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "lxml")
            text = soup.get_text(separator="\n")
            if text.strip():
                texts.append(text)
        return "\n".join(texts)
