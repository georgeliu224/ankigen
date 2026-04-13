import re
from pathlib import Path

from ankigen.languages.base import DictEntry, DictionaryLookup
from ankigen.languages.mandarin.pinyin import numbered_to_marked

_CEDICT_LINE = re.compile(r"^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/(.+)/$")

DATA_DIR = Path(__file__).parent / "data"


def _parse_line(line: str) -> tuple[str, str, str, list[str]] | None:
    """Parse a CC-CEDICT line into (traditional, simplified, pinyin, definitions)."""
    m = _CEDICT_LINE.match(line.strip())
    if not m:
        return None
    traditional, simplified, pinyin_numbered, defs_raw = m.groups()
    definitions = [d for d in defs_raw.split("/") if d]
    return traditional, simplified, pinyin_numbered, definitions


class MandarinDictionary(DictionaryLookup):
    def __init__(self, dict_path: Path | None = None):
        self._path = dict_path or DATA_DIR / "cedict_ts.u8"
        self._entries: dict[str, DictEntry] = {}
        self._compound_index: dict[str, list[str]] = {}
        self._load()

    def _load(self) -> None:
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parsed = _parse_line(line)
                if not parsed:
                    continue
                _traditional, simplified, pinyin_numbered, definitions = parsed
                pinyin_marked = numbered_to_marked(pinyin_numbered)
                entry = DictEntry(
                    word=simplified,
                    pronunciation=pinyin_marked,
                    definitions=definitions,
                    level=None,
                )
                self._entries[simplified] = entry

                for char in set(simplified):
                    if char not in self._compound_index:
                        self._compound_index[char] = []
                    self._compound_index[char].append(simplified)

    def lookup(self, word: str) -> DictEntry | None:
        return self._entries.get(word)

    def find_compounds(
        self, word: str, limit: int = 5, text_words: set[str] | None = None
    ) -> list[DictEntry]:
        candidates: set[str] = set()
        for char in word:
            for compound_word in self._compound_index.get(char, []):
                if compound_word != word and word in compound_word:
                    candidates.add(compound_word)

        def sort_key(w: str) -> tuple[int, int]:
            in_text = 0 if (text_words and w in text_words) else 1
            return (in_text, len(w))

        sorted_words = sorted(candidates, key=sort_key)
        return [self._entries[w] for w in sorted_words[:limit] if w in self._entries]
