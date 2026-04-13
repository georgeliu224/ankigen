from pathlib import Path
from ankigen.parsers.base import Parser


class TxtParser(Parser):
    def parse(self, file_path: str) -> str:
        return Path(file_path).read_text(encoding="utf-8")
