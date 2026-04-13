import json
from pathlib import Path
from ankigen.languages.base import ProficiencyFilter

DATA_DIR = Path(__file__).parent / "data"


class MandarinProficiency(ProficiencyFilter):
    def __init__(self, hsk_path: Path | None = None):
        self._path = hsk_path or DATA_DIR / "hsk.json"
        self._levels: dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        with open(self._path, encoding="utf-8") as f:
            self._levels = json.load(f)

    def get_level(self, word: str) -> int | None:
        return self._levels.get(word)

    def filter(
        self,
        words: list[tuple[str, int]],
        min_level: int,
        max_level: int,
        include_ungraded: bool,
    ) -> list[tuple[str, int]]:
        result: list[tuple[str, int]] = []
        for word, count in words:
            level = self.get_level(word)
            if level is None:
                if include_ungraded:
                    result.append((word, count))
            elif min_level <= level <= max_level:
                result.append((word, count))
        return result
