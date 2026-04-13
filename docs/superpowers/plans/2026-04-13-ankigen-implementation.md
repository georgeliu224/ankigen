# ankigen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that extracts vocabulary from Chinese-language books and generates Anki-compatible flashcard decks.

**Architecture:** Modular pipeline with 6 stages (parse → tokenize → frequency → filter → dictionary → export). Language-specific components (tokenizer, proficiency filter, dictionary) are pluggable behind abstract interfaces. Mandarin is the first and only language module.

**Tech Stack:** Python 3.11+, jieba (segmentation), ebooklib + BeautifulSoup (EPUB), pdfplumber (PDF), CC-CEDICT (dictionary), pytest (testing)

**Spec:** `docs/superpowers/specs/2026-04-13-ankigen-design.md`

---

## File Map

| File | Responsibility |
|---|---|
| `pyproject.toml` | Package config, dependencies, entry point |
| `src/ankigen/__init__.py` | Package marker |
| `src/ankigen/cli.py` | CLI argument parsing, wiring |
| `src/ankigen/pipeline.py` | Orchestrates the 6 pipeline stages |
| `src/ankigen/parsers/__init__.py` | Parser dispatch (`get_parser`) |
| `src/ankigen/parsers/base.py` | Abstract `Parser` class |
| `src/ankigen/parsers/txt.py` | TXT parser |
| `src/ankigen/parsers/pdf.py` | PDF parser |
| `src/ankigen/parsers/epub.py` | EPUB parser |
| `src/ankigen/languages/__init__.py` | Language registry (`get_language`) |
| `src/ankigen/languages/base.py` | ABCs: `Tokenizer`, `ProficiencyFilter`, `DictionaryLookup`; dataclasses: `DictEntry`, `FlashcardEntry` |
| `src/ankigen/languages/mandarin/__init__.py` | Package marker |
| `src/ankigen/languages/mandarin/tokenizer.py` | jieba-based word segmentation |
| `src/ankigen/languages/mandarin/proficiency.py` | HSK level filtering |
| `src/ankigen/languages/mandarin/dictionary.py` | CC-CEDICT loader, lookup, compound index |
| `src/ankigen/languages/mandarin/pinyin.py` | Numbered pinyin → tone-marked conversion |
| `src/ankigen/languages/mandarin/data/` | Bundled CC-CEDICT + HSK data (downloaded via `update-dict`) |
| `src/ankigen/exporters/__init__.py` | Package marker |
| `src/ankigen/exporters/tsv.py` | Tab-separated Anki-importable output |
| `tests/conftest.py` | Shared fixtures |
| `tests/fixtures/cedict_sample.u8` | Small CC-CEDICT excerpt for tests |
| `tests/fixtures/hsk_sample.json` | Small HSK word list for tests |
| `tests/test_parsers.py` | Parser tests |
| `tests/test_pinyin.py` | Pinyin conversion tests |
| `tests/test_dictionary.py` | CC-CEDICT parsing + lookup tests |
| `tests/test_proficiency.py` | HSK filter tests |
| `tests/test_tokenizer.py` | Mandarin tokenizer tests |
| `tests/test_exporter.py` | TSV export tests |
| `tests/test_pipeline.py` | Pipeline orchestration tests |
| `tests/test_cli.py` | CLI integration tests |

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/ankigen/__init__.py`
- Create: `src/ankigen/parsers/__init__.py`
- Create: `src/ankigen/languages/__init__.py`
- Create: `src/ankigen/languages/mandarin/__init__.py`
- Create: `src/ankigen/languages/mandarin/data/.gitkeep`
- Create: `src/ankigen/exporters/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/fixtures/`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ankigen"
version = "0.1.0"
description = "Extract vocabulary from foreign-language texts and generate Anki flashcard decks"
requires-python = ">=3.11"
dependencies = [
    "jieba>=0.42",
    "ebooklib>=0.18",
    "beautifulsoup4>=4.12",
    "pdfplumber>=0.10",
    "lxml>=5.0",
]

[project.scripts]
ankigen = "ankigen.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "fpdf2>=2.7",
]

[tool.hatch.build.targets.wheel]
packages = ["src/ankigen"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create directory structure**

Create all `__init__.py` files (empty) and the `tests/fixtures/` directory:

```
src/ankigen/__init__.py
src/ankigen/parsers/__init__.py
src/ankigen/languages/__init__.py
src/ankigen/languages/mandarin/__init__.py
src/ankigen/languages/mandarin/data/.gitkeep
src/ankigen/exporters/__init__.py
tests/__init__.py
tests/fixtures/.gitkeep
```

All `__init__.py` files are empty.

- [ ] **Step 3: Install the package in dev mode**

Run: `cd /Users/georgeliu/src/ankigen && uv venv && uv pip install -e ".[dev]"`

If `uv` is not installed: `pip install -e ".[dev]"`

- [ ] **Step 4: Verify pytest runs**

Run: `cd /Users/georgeliu/src/ankigen && uv run pytest -v`
Expected: `no tests ran` with exit code 5 (no tests collected — that's fine)

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: scaffold ankigen project with pyproject.toml and directory structure"
```

---

### Task 2: Base Interfaces and Data Types

**Files:**
- Create: `src/ankigen/languages/base.py`
- Create: `src/ankigen/parsers/base.py`
- Test: `tests/test_base.py`

- [ ] **Step 1: Write the test**

```python
# tests/test_base.py
from ankigen.languages.base import DictEntry, FlashcardEntry


def test_dict_entry_fields():
    entry = DictEntry(
        word="学习",
        pronunciation="xué xí",
        definitions=["to learn", "to study"],
        level=1,
    )
    assert entry.word == "学习"
    assert entry.pronunciation == "xué xí"
    assert entry.definitions == ["to learn", "to study"]
    assert entry.level == 1


def test_dict_entry_ungraded():
    entry = DictEntry(word="foo", pronunciation="", definitions=[], level=None)
    assert entry.level is None


def test_flashcard_entry_fields():
    entry = FlashcardEntry(
        word="学习",
        pinyin="xué xí",
        definition="to learn; to study",
        hsk_level="1",
        frequency=47,
        compounds="学生 (xué shēng) student",
    )
    assert entry.word == "学习"
    assert entry.hsk_level == "1"
    assert entry.frequency == 47
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_base.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ankigen.languages.base'`

- [ ] **Step 3: Implement languages/base.py**

```python
# src/ankigen/languages/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DictEntry:
    word: str
    pronunciation: str
    definitions: list[str]
    level: int | None


@dataclass
class FlashcardEntry:
    word: str
    pinyin: str
    definition: str
    hsk_level: str
    frequency: int
    compounds: str


class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, text: str) -> list[str]: ...


class ProficiencyFilter(ABC):
    @abstractmethod
    def get_level(self, word: str) -> int | None: ...

    @abstractmethod
    def filter(
        self,
        words: list[tuple[str, int]],
        min_level: int,
        max_level: int,
        include_ungraded: bool,
    ) -> list[tuple[str, int]]: ...


class DictionaryLookup(ABC):
    @abstractmethod
    def lookup(self, word: str) -> DictEntry | None: ...

    @abstractmethod
    def find_compounds(
        self, word: str, limit: int = 5, text_words: set[str] | None = None
    ) -> list[DictEntry]: ...
```

- [ ] **Step 4: Implement parsers/base.py**

```python
# src/ankigen/parsers/base.py
from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str: ...
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_base.py -v`
Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add src/ankigen/languages/base.py src/ankigen/parsers/base.py tests/test_base.py
git commit -m "feat: add base interfaces and data types (DictEntry, FlashcardEntry, ABCs)"
```

---

### Task 3: File Parsers (TXT, PDF, EPUB)

**Files:**
- Create: `src/ankigen/parsers/txt.py`
- Create: `src/ankigen/parsers/pdf.py`
- Create: `src/ankigen/parsers/epub.py`
- Modify: `src/ankigen/parsers/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_parsers.py`

- [ ] **Step 1: Create test fixtures in conftest.py**

```python
# tests/conftest.py
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
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_parsers.py
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
    # HTML tags should be stripped
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_parsers.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement TXT parser**

```python
# src/ankigen/parsers/txt.py
from pathlib import Path

from ankigen.parsers.base import Parser


class TxtParser(Parser):
    def parse(self, file_path: str) -> str:
        return Path(file_path).read_text(encoding="utf-8")
```

- [ ] **Step 5: Implement PDF parser**

```python
# src/ankigen/parsers/pdf.py
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
```

- [ ] **Step 6: Implement EPUB parser**

```python
# src/ankigen/parsers/epub.py
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
```

- [ ] **Step 7: Implement parser dispatch in parsers/__init__.py**

```python
# src/ankigen/parsers/__init__.py
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
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `uv run pytest tests/test_parsers.py -v`
Expected: 7 passed

- [ ] **Step 9: Commit**

```bash
git add src/ankigen/parsers/ tests/conftest.py tests/test_parsers.py
git commit -m "feat: add file parsers for TXT, PDF, and EPUB with dispatch"
```

---

### Task 4: Pinyin Number-to-Tone Conversion

**Files:**
- Create: `src/ankigen/languages/mandarin/pinyin.py`
- Create: `tests/test_pinyin.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pinyin.py
from ankigen.languages.mandarin.pinyin import numbered_to_marked


def test_single_syllable_tone1():
    assert numbered_to_marked("ma1") == "mā"


def test_single_syllable_tone2():
    assert numbered_to_marked("ma2") == "má"


def test_single_syllable_tone3():
    assert numbered_to_marked("ma3") == "mǎ"


def test_single_syllable_tone4():
    assert numbered_to_marked("ma4") == "mà"


def test_neutral_tone():
    assert numbered_to_marked("ma5") == "ma"


def test_multi_syllable():
    assert numbered_to_marked("xue2 xi2") == "xué xí"


def test_tone_on_a():
    assert numbered_to_marked("bai2") == "bái"


def test_tone_on_e():
    assert numbered_to_marked("mei2") == "méi"


def test_tone_on_ou():
    assert numbered_to_marked("gou3") == "gǒu"


def test_tone_on_last_vowel():
    assert numbered_to_marked("liu2") == "liú"


def test_u_colon_becomes_u_umlaut():
    assert numbered_to_marked("lv4") == "lǜ"
    assert numbered_to_marked("lu:4") == "lǜ"


def test_full_pinyin_phrase():
    assert numbered_to_marked("ni3 hao3") == "nǐ hǎo"


def test_no_tone_number():
    assert numbered_to_marked("a") == "a"


def test_empty_string():
    assert numbered_to_marked("") == ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_pinyin.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement pinyin conversion**

```python
# src/ankigen/languages/mandarin/pinyin.py

TONE_MARKS: dict[str, tuple[str, str, str, str]] = {
    "a": ("ā", "á", "ǎ", "à"),
    "e": ("ē", "é", "ě", "è"),
    "i": ("ī", "í", "ǐ", "ì"),
    "o": ("ō", "ó", "ǒ", "ò"),
    "u": ("ū", "ú", "ǔ", "ù"),
    "ü": ("ǖ", "ǘ", "ǚ", "ǜ"),
}


def _convert_syllable(syllable: str) -> str:
    # Normalize ü representations
    syllable = syllable.replace("u:", "ü").replace("v", "ü")

    if not syllable or not syllable[-1].isdigit():
        return syllable

    tone = int(syllable[-1])
    base = syllable[:-1]

    if tone == 5 or tone == 0:
        return base

    # Rule 1: 'a' or 'e' always gets the tone mark
    for i, ch in enumerate(base):
        if ch in ("a", "e"):
            return base[:i] + TONE_MARKS[ch][tone - 1] + base[i + 1 :]

    # Rule 2: 'ou' → tone mark on 'o'
    if "ou" in base:
        i = base.index("o")
        return base[:i] + TONE_MARKS["o"][tone - 1] + base[i + 1 :]

    # Rule 3: tone mark on the last vowel
    for i in range(len(base) - 1, -1, -1):
        if base[i] in TONE_MARKS:
            return base[:i] + TONE_MARKS[base[i]][tone - 1] + base[i + 1 :]

    return base


def numbered_to_marked(pinyin: str) -> str:
    """Convert numbered pinyin to tone-marked pinyin.

    Example: 'xue2 xi2' → 'xué xí'
    """
    if not pinyin:
        return ""
    syllables = pinyin.split()
    return " ".join(_convert_syllable(s) for s in syllables)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_pinyin.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add src/ankigen/languages/mandarin/pinyin.py tests/test_pinyin.py
git commit -m "feat: add pinyin number-to-tone mark conversion"
```

---

### Task 5: CC-CEDICT Parser and Dictionary Lookup

**Files:**
- Create: `tests/fixtures/cedict_sample.u8`
- Create: `src/ankigen/languages/mandarin/dictionary.py`
- Create: `tests/test_dictionary.py`

- [ ] **Step 1: Create the CC-CEDICT test fixture**

```
# tests/fixtures/cedict_sample.u8
# CC-CEDICT test fixture
# Lines starting with # are comments
學習 学习 [xue2 xi2] /to learn/to study/
學生 学生 [xue2 sheng5] /student/pupil/
學校 学校 [xue2 xiao4] /school/
學問 学问 [xue2 wen4] /learning/knowledge/
吃 吃 [chi1] /to eat/to consume/
吃飯 吃饭 [chi1 fan4] /to eat a meal/to have a meal/
吃驚 吃惊 [chi1 jing1] /to be startled/to be shocked/
暗示 暗示 [an4 shi4] /to hint/to suggest/hint/suggestion/
暗 暗 [an4] /dark/gloomy/secret/
暗中 暗中 [an4 zhong1] /in secret/secretly/
你好 你好 [ni3 hao3] /hello/hi/
電腦 电脑 [dian4 nao3] /computer/
好 好 [hao3] /good/well/proper/
的 的 [de5] /of/(possessive particle)/
了 了 [le5] /(modal particle)/
是 是 [shi4] /is/are/am/yes/
飯 饭 [fan4] /food/meal/cooked rice/
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_dictionary.py
from pathlib import Path

import pytest

from ankigen.languages.mandarin.dictionary import MandarinDictionary

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"


@pytest.fixture
def dictionary():
    return MandarinDictionary(dict_path=FIXTURE_PATH)


def test_lookup_existing_word(dictionary):
    entry = dictionary.lookup("学习")
    assert entry is not None
    assert entry.word == "学习"
    assert "xué xí" == entry.pronunciation
    assert "to learn" in entry.definitions
    assert "to study" in entry.definitions


def test_lookup_single_char(dictionary):
    entry = dictionary.lookup("吃")
    assert entry is not None
    assert entry.definitions == ["to eat", "to consume"]


def test_lookup_missing_word(dictionary):
    entry = dictionary.lookup("不存在的词")
    assert entry is None


def test_pinyin_is_tone_marked(dictionary):
    entry = dictionary.lookup("你好")
    assert entry is not None
    assert entry.pronunciation == "nǐ hǎo"


def test_find_compounds(dictionary):
    compounds = dictionary.find_compounds("学", limit=5)
    compound_words = [c.word for c in compounds]
    assert "学习" in compound_words
    assert "学生" in compound_words
    assert "学校" in compound_words


def test_find_compounds_respects_limit(dictionary):
    compounds = dictionary.find_compounds("学", limit=2)
    assert len(compounds) <= 2


def test_find_compounds_prioritizes_text_words(dictionary):
    text_words = {"学问", "学校"}
    compounds = dictionary.find_compounds("学", limit=3, text_words=text_words)
    # Words from the text should appear first
    assert compounds[0].word in text_words


def test_find_compounds_shorter_first(dictionary):
    compounds = dictionary.find_compounds("吃", limit=5)
    # 吃 itself shouldn't be in compounds, but 吃饭 and 吃惊 should
    words = [c.word for c in compounds]
    assert "吃饭" in words
    assert "吃惊" in words


def test_find_compounds_excludes_self(dictionary):
    compounds = dictionary.find_compounds("学习", limit=5)
    compound_words = [c.word for c in compounds]
    assert "学习" not in compound_words
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_dictionary.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement the dictionary**

```python
# src/ankigen/languages/mandarin/dictionary.py
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

                # Build compound index: for each character in the word,
                # record that this word contains it
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

        # Also find words that START with this word (for multi-char lookups)
        # Already covered by the character index above

        # Sort: text_words first, then by length (shorter first)
        def sort_key(w: str) -> tuple[int, int]:
            in_text = 0 if (text_words and w in text_words) else 1
            return (in_text, len(w))

        sorted_words = sorted(candidates, key=sort_key)
        return [self._entries[w] for w in sorted_words[:limit] if w in self._entries]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_dictionary.py -v`
Expected: All passed

- [ ] **Step 6: Commit**

```bash
git add src/ankigen/languages/mandarin/dictionary.py tests/test_dictionary.py tests/fixtures/cedict_sample.u8
git commit -m "feat: add CC-CEDICT parser with lookup and compound word index"
```

---

### Task 6: HSK Proficiency Filter

**Files:**
- Create: `tests/fixtures/hsk_sample.json`
- Create: `src/ankigen/languages/mandarin/proficiency.py`
- Create: `tests/test_proficiency.py`

- [ ] **Step 1: Create the HSK test fixture**

```json
{
    "你好": 1,
    "好": 1,
    "学习": 1,
    "学生": 1,
    "吃": 1,
    "电脑": 2,
    "学校": 2,
    "吃饭": 2,
    "暗示": 6,
    "暗中": 6
}
```

Save to `tests/fixtures/hsk_sample.json`.

- [ ] **Step 2: Write failing tests**

```python
# tests/test_proficiency.py
from pathlib import Path

import pytest

from ankigen.languages.mandarin.proficiency import MandarinProficiency

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


@pytest.fixture
def hsk():
    return MandarinProficiency(hsk_path=FIXTURE_PATH)


def test_get_level_known_word(hsk):
    assert hsk.get_level("学习") == 1
    assert hsk.get_level("电脑") == 2
    assert hsk.get_level("暗示") == 6


def test_get_level_unknown_word(hsk):
    assert hsk.get_level("不存在") is None


def test_filter_all_levels(hsk):
    words = [("学习", 10), ("电脑", 5), ("暗示", 3)]
    result = hsk.filter(words, min_level=1, max_level=6, include_ungraded=True)
    assert len(result) == 3


def test_filter_max_level(hsk):
    words = [("学习", 10), ("电脑", 5), ("暗示", 3)]
    result = hsk.filter(words, min_level=1, max_level=2, include_ungraded=False)
    result_words = [w for w, _ in result]
    assert "学习" in result_words
    assert "电脑" in result_words
    assert "暗示" not in result_words


def test_filter_min_level(hsk):
    words = [("学习", 10), ("电脑", 5), ("暗示", 3)]
    result = hsk.filter(words, min_level=6, max_level=6, include_ungraded=False)
    result_words = [w for w, _ in result]
    assert result_words == ["暗示"]


def test_filter_range(hsk):
    words = [("学习", 10), ("电脑", 5), ("暗示", 3)]
    result = hsk.filter(words, min_level=2, max_level=5, include_ungraded=False)
    result_words = [w for w, _ in result]
    assert result_words == ["电脑"]


def test_filter_include_ungraded(hsk):
    words = [("学习", 10), ("未知词", 5)]
    result = hsk.filter(words, min_level=1, max_level=6, include_ungraded=True)
    result_words = [w for w, _ in result]
    assert "未知词" in result_words


def test_filter_exclude_ungraded(hsk):
    words = [("学习", 10), ("未知词", 5)]
    result = hsk.filter(words, min_level=1, max_level=6, include_ungraded=False)
    result_words = [w for w, _ in result]
    assert "未知词" not in result_words


def test_filter_preserves_frequency_order(hsk):
    words = [("电脑", 20), ("学习", 10), ("好", 5)]
    result = hsk.filter(words, min_level=1, max_level=6, include_ungraded=True)
    assert result == [("电脑", 20), ("学习", 10), ("好", 5)]
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_proficiency.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Implement the proficiency filter**

```python
# src/ankigen/languages/mandarin/proficiency.py
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_proficiency.py -v`
Expected: All passed

- [ ] **Step 6: Commit**

```bash
git add src/ankigen/languages/mandarin/proficiency.py tests/test_proficiency.py tests/fixtures/hsk_sample.json
git commit -m "feat: add HSK proficiency filter with level range support"
```

---

### Task 7: Mandarin Tokenizer

**Files:**
- Create: `src/ankigen/languages/mandarin/tokenizer.py`
- Create: `tests/test_tokenizer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_tokenizer.py
from ankigen.languages.mandarin.tokenizer import MandarinTokenizer


def test_basic_segmentation():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("我在学校学习")
    assert "学校" in tokens
    assert "学习" in tokens


def test_filters_punctuation():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("你好，世界！")
    assert "，" not in tokens
    assert "！" not in tokens


def test_filters_stop_words():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("我的学校是很好的")
    assert "的" not in tokens
    assert "是" not in tokens


def test_filters_numbers():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("我有123个苹果")
    assert "123" not in tokens


def test_filters_ascii():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("Hello你好World世界")
    assert "Hello" not in tokens
    assert "World" not in tokens
    # Chinese words should remain
    assert "你好" in tokens or "世界" in tokens


def test_empty_input():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("")
    assert tokens == []


def test_returns_list_of_strings():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("学习很重要")
    assert isinstance(tokens, list)
    assert all(isinstance(t, str) for t in tokens)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_tokenizer.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement the tokenizer**

```python
# src/ankigen/languages/mandarin/tokenizer.py
import re

import jieba

from ankigen.languages.base import Tokenizer

STOP_WORDS = frozenset({
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "都",
    "一", "个", "上", "也", "到", "你", "会", "着", "这", "那",
    "被", "把", "让", "给", "对", "从", "向", "与", "而", "但",
    "他", "她", "它", "们", "地", "得", "过", "呢", "吗", "吧",
    "啊", "哦", "呀", "么", "之", "所", "以", "如", "为",
})

_CHINESE_CHAR = re.compile(r"[\u4e00-\u9fff]")


class MandarinTokenizer(Tokenizer):
    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        words = jieba.cut(text)
        return [
            w
            for w in words
            if _CHINESE_CHAR.search(w) and w not in STOP_WORDS
        ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_tokenizer.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add src/ankigen/languages/mandarin/tokenizer.py tests/test_tokenizer.py
git commit -m "feat: add Mandarin tokenizer with jieba segmentation and stop word filtering"
```

---

### Task 8: TSV Exporter

**Files:**
- Create: `src/ankigen/exporters/tsv.py`
- Create: `tests/test_exporter.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_exporter.py
import io

from ankigen.exporters.tsv import TsvExporter
from ankigen.languages.base import FlashcardEntry


def test_export_header():
    exporter = TsvExporter()
    output = io.StringIO()
    exporter.export([], output)
    output.seek(0)
    header = output.readline()
    assert header.startswith("#")
    assert "word" in header
    assert "pinyin" in header
    assert "definition" in header
    assert "hsk_level" in header
    assert "frequency" in header
    assert "compounds" in header


def test_export_single_entry():
    exporter = TsvExporter()
    entries = [
        FlashcardEntry(
            word="学习",
            pinyin="xué xí",
            definition="to learn; to study",
            hsk_level="1",
            frequency=47,
            compounds="学生 (xué shēng) student",
        )
    ]
    output = io.StringIO()
    exporter.export(entries, output)
    output.seek(0)
    lines = output.readlines()
    assert len(lines) == 2  # header + 1 entry
    fields = lines[1].strip().split("\t")
    assert fields[0] == "学习"
    assert fields[1] == "xué xí"
    assert fields[2] == "to learn; to study"
    assert fields[3] == "1"
    assert fields[4] == "47"
    assert fields[5] == "学生 (xué shēng) student"


def test_export_multiple_entries():
    exporter = TsvExporter()
    entries = [
        FlashcardEntry("学习", "xué xí", "to learn", "1", 47, ""),
        FlashcardEntry("吃", "chī", "to eat", "1", 32, ""),
    ]
    output = io.StringIO()
    exporter.export(entries, output)
    output.seek(0)
    lines = output.readlines()
    assert len(lines) == 3  # header + 2 entries


def test_export_ungraded_level():
    exporter = TsvExporter()
    entries = [
        FlashcardEntry("罕见词", "", "", "—", 2, ""),
    ]
    output = io.StringIO()
    exporter.export(entries, output)
    output.seek(0)
    lines = output.readlines()
    fields = lines[1].strip().split("\t")
    assert fields[3] == "—"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_exporter.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement the exporter**

```python
# src/ankigen/exporters/tsv.py
from typing import IO

from ankigen.languages.base import FlashcardEntry

HEADER = "#word\tpinyin\tdefinition\thsk_level\tfrequency\tcompounds\n"


class TsvExporter:
    def export(self, entries: list[FlashcardEntry], output: IO[str]) -> None:
        output.write(HEADER)
        for entry in entries:
            line = "\t".join([
                entry.word,
                entry.pinyin,
                entry.definition,
                entry.hsk_level,
                str(entry.frequency),
                entry.compounds,
            ])
            output.write(line + "\n")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_exporter.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add src/ankigen/exporters/tsv.py tests/test_exporter.py
git commit -m "feat: add TSV exporter for Anki-importable flashcard output"
```

---

### Task 9: Language Registry

**Files:**
- Modify: `src/ankigen/languages/__init__.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_registry.py
from pathlib import Path

import pytest

from ankigen.languages import get_language, LanguageModule
from ankigen.languages.mandarin.tokenizer import MandarinTokenizer
from ankigen.languages.mandarin.proficiency import MandarinProficiency
from ankigen.languages.mandarin.dictionary import MandarinDictionary

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


def test_get_mandarin(monkeypatch):
    # Patch data paths so tests use fixtures
    monkeypatch.setattr(
        "ankigen.languages.mandarin.dictionary.DATA_DIR",
        CEDICT_PATH.parent,
    )
    monkeypatch.setattr(
        "ankigen.languages.mandarin.proficiency.DATA_DIR",
        HSK_PATH.parent,
    )
    # Rename fixture files to match expected names for this test
    # Instead, pass paths explicitly via the registry
    lang = get_language(
        "mandarin",
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    assert isinstance(lang, LanguageModule)
    assert isinstance(lang.tokenizer, MandarinTokenizer)
    assert isinstance(lang.proficiency, MandarinProficiency)
    assert isinstance(lang.dictionary, MandarinDictionary)


def test_get_unknown_language():
    with pytest.raises(ValueError, match="Unknown language"):
        get_language("klingon")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_registry.py -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement the language registry**

```python
# src/ankigen/languages/__init__.py
from dataclasses import dataclass
from pathlib import Path

from ankigen.languages.base import Tokenizer, ProficiencyFilter, DictionaryLookup


@dataclass
class LanguageModule:
    tokenizer: Tokenizer
    proficiency: ProficiencyFilter
    dictionary: DictionaryLookup


def get_language(
    name: str,
    dict_path: Path | None = None,
    hsk_path: Path | None = None,
) -> LanguageModule:
    if name == "mandarin":
        from ankigen.languages.mandarin.tokenizer import MandarinTokenizer
        from ankigen.languages.mandarin.proficiency import MandarinProficiency
        from ankigen.languages.mandarin.dictionary import MandarinDictionary

        return LanguageModule(
            tokenizer=MandarinTokenizer(),
            proficiency=MandarinProficiency(hsk_path=hsk_path),
            dictionary=MandarinDictionary(dict_path=dict_path),
        )
    available = ["mandarin"]
    raise ValueError(
        f"Unknown language '{name}'. Available: {', '.join(available)}"
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_registry.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add src/ankigen/languages/__init__.py tests/test_registry.py
git commit -m "feat: add language registry with Mandarin module support"
```

---

### Task 10: Pipeline Orchestrator

**Files:**
- Create: `src/ankigen/pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pipeline.py
import io
from pathlib import Path

import pytest

from ankigen.pipeline import run_pipeline

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


@pytest.fixture
def chinese_txt(tmp_path):
    path = tmp_path / "book.txt"
    # Repeat words to create frequency differences
    text = "学习学习学习学校学校电脑吃饭吃饭暗示你好你好你好你好"
    path.write_text(text, encoding="utf-8")
    return path


def test_pipeline_produces_output(chinese_txt):
    output = io.StringIO()
    run_pipeline(
        input_path=str(chinese_txt),
        output=output,
        language="mandarin",
        top_n=10,
        level_min=1,
        level_max=6,
        include_ungraded=True,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    output.seek(0)
    content = output.read()
    assert "#word" in content  # header present
    assert "学习" in content


def test_pipeline_respects_top_n(chinese_txt):
    output = io.StringIO()
    run_pipeline(
        input_path=str(chinese_txt),
        output=output,
        language="mandarin",
        top_n=2,
        level_min=1,
        level_max=6,
        include_ungraded=True,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    output.seek(0)
    lines = [l for l in output.readlines() if not l.startswith("#")]
    assert len(lines) <= 2


def test_pipeline_hsk_filtering(chinese_txt):
    output = io.StringIO()
    run_pipeline(
        input_path=str(chinese_txt),
        output=output,
        language="mandarin",
        top_n=100,
        level_min=1,
        level_max=1,
        include_ungraded=False,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    output.seek(0)
    content = output.read()
    # 学习 is HSK 1, should be included
    assert "学习" in content
    # 暗示 is HSK 6, should be excluded
    assert "暗示" not in content


def test_pipeline_returns_not_found_count(chinese_txt):
    output = io.StringIO()
    not_found = run_pipeline(
        input_path=str(chinese_txt),
        output=output,
        language="mandarin",
        top_n=100,
        level_min=1,
        level_max=6,
        include_ungraded=True,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    assert isinstance(not_found, int)
    assert not_found >= 0


def test_pipeline_empty_text(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    output = io.StringIO()
    with pytest.raises(ValueError, match="No text could be extracted"):
        run_pipeline(
            input_path=str(path),
            output=output,
            language="mandarin",
            top_n=10,
            level_min=1,
            level_max=6,
            include_ungraded=True,
            dict_path=CEDICT_PATH,
            hsk_path=HSK_PATH,
        )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_pipeline.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement the pipeline**

```python
# src/ankigen/pipeline.py
from collections import Counter
from pathlib import Path
from typing import IO

from ankigen.languages import get_language
from ankigen.languages.base import DictEntry, FlashcardEntry
from ankigen.parsers import get_parser
from ankigen.exporters.tsv import TsvExporter


def _format_level(level: int | None) -> str:
    return str(level) if level is not None else "\u2014"  # em dash


def _format_compounds(compounds: list[DictEntry]) -> str:
    parts: list[str] = []
    for c in compounds:
        defs = "; ".join(c.definitions[:2])
        parts.append(f"{c.word} ({c.pronunciation}) {defs}")
    return "; ".join(parts)


def run_pipeline(
    input_path: str,
    output: IO[str],
    language: str,
    top_n: int,
    level_min: int,
    level_max: int,
    include_ungraded: bool,
    dict_path: Path | None = None,
    hsk_path: Path | None = None,
) -> int:
    """Run the full ankigen pipeline. Returns count of words not found in dictionary."""

    # Stage 1: Parse
    parser = get_parser(input_path)
    text = parser.parse(input_path)
    if not text.strip():
        raise ValueError(
            "No text could be extracted. If this is a scanned document, "
            "OCR is not currently supported."
        )

    # Stage 2: Tokenize
    lang = get_language(language, dict_path=dict_path, hsk_path=hsk_path)
    tokens = lang.tokenizer.tokenize(text)

    # Stage 3: Frequency analysis
    counter = Counter(tokens)
    ranked = counter.most_common()

    # Stage 4: Proficiency filter
    filtered = lang.proficiency.filter(
        ranked, level_min, level_max, include_ungraded
    )
    top = filtered[:top_n]

    # Stage 5: Dictionary lookup
    text_words = set(counter.keys())
    entries: list[FlashcardEntry] = []
    not_found = 0

    for word, count in top:
        dict_entry = lang.dictionary.lookup(word)
        compounds = lang.dictionary.find_compounds(
            word, limit=5, text_words=text_words
        )
        level = lang.proficiency.get_level(word)

        if dict_entry is None:
            not_found += 1
            entries.append(FlashcardEntry(
                word=word,
                pinyin="",
                definition="",
                hsk_level=_format_level(level),
                frequency=count,
                compounds=_format_compounds(compounds),
            ))
        else:
            entries.append(FlashcardEntry(
                word=word,
                pinyin=dict_entry.pronunciation,
                definition="; ".join(dict_entry.definitions),
                hsk_level=_format_level(level),
                frequency=count,
                compounds=_format_compounds(compounds),
            ))

    # Stage 6: Export
    exporter = TsvExporter()
    exporter.export(entries, output)

    return not_found
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_pipeline.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add src/ankigen/pipeline.py tests/test_pipeline.py
git commit -m "feat: add pipeline orchestrator connecting all 6 stages"
```

---

### Task 11: CLI Entry Point

**Files:**
- Create: `src/ankigen/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cli.py
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from ankigen.cli import build_parser, main

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["input.txt"])
    assert args.input == "input.txt"
    assert args.output is None
    assert args.top == 200
    assert args.hsk_min == 1
    assert args.hsk_max == 6
    assert args.no_ungraded is False
    assert args.lang == "mandarin"


def test_parser_all_flags():
    parser = build_parser()
    args = parser.parse_args([
        "book.epub",
        "-o", "deck.txt",
        "--top", "300",
        "--hsk-min", "2",
        "--hsk-max", "5",
        "--no-ungraded",
        "--lang", "mandarin",
    ])
    assert args.input == "book.epub"
    assert args.output == "deck.txt"
    assert args.top == 300
    assert args.hsk_min == 2
    assert args.hsk_max == 5
    assert args.no_ungraded is True
    assert args.lang == "mandarin"


def test_parser_requires_input():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_main_with_txt_file(tmp_path):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习学习学校电脑你好你好", encoding="utf-8")
    output_file = tmp_path / "deck.txt"

    with patch("ankigen.cli.CEDICT_PATH", CEDICT_PATH), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file), "-o", str(output_file)]
        main()

    content = output_file.read_text(encoding="utf-8")
    assert "#word" in content
    assert "学习" in content


def test_main_outputs_to_stdout(tmp_path, capsys):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习学校电脑", encoding="utf-8")

    with patch("ankigen.cli.CEDICT_PATH", CEDICT_PATH), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file)]
        main()

    captured = capsys.readouterr()
    assert "#word" in captured.out


def test_main_missing_dictionary(tmp_path, capsys):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习", encoding="utf-8")
    missing_dict = tmp_path / "nonexistent" / "cedict.u8"

    with patch("ankigen.cli.CEDICT_PATH", missing_dict), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file)]
        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()
    assert "update-dict" in captured.err


def test_main_prints_not_found_summary(tmp_path, capsys):
    input_file = tmp_path / "book.txt"
    # Use a word that's not in our test fixture dictionary
    input_file.write_text("学习罕见词罕见词罕见词", encoding="utf-8")

    with patch("ankigen.cli.CEDICT_PATH", CEDICT_PATH), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file)]
        main()

    captured = capsys.readouterr()
    assert "not found in dictionary" in captured.err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement the CLI**

```python
# src/ankigen/cli.py
import argparse
import sys
from pathlib import Path

from ankigen.pipeline import run_pipeline

# Default data paths (overridable for testing)
_DATA_DIR = Path(__file__).parent / "languages" / "mandarin" / "data"
CEDICT_PATH = _DATA_DIR / "cedict_ts.u8"
HSK_PATH = _DATA_DIR / "hsk.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ankigen",
        description="Extract vocabulary from foreign-language texts and generate Anki flashcard decks.",
    )
    parser.add_argument(
        "input",
        help="Path to .epub, .pdf, or .txt file",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=200,
        help="Number of top-frequency words to include (default: 200)",
    )
    parser.add_argument(
        "--hsk-min",
        type=int,
        default=1,
        help="Minimum HSK level to include (default: 1)",
    )
    parser.add_argument(
        "--hsk-max",
        type=int,
        default=6,
        help="Maximum HSK level to include (default: 6)",
    )
    parser.add_argument(
        "--no-ungraded",
        action="store_true",
        default=False,
        help="Exclude words not in any HSK level",
    )
    parser.add_argument(
        "--lang",
        default="mandarin",
        help="Language module to use (default: mandarin)",
    )
    return parser


def main() -> None:
    # Handle update-dict subcommand
    if len(sys.argv) > 1 and sys.argv[1] == "update-dict":
        _update_dict()
        return

    parser = build_parser()
    args = parser.parse_args()

    if args.output:
        output = open(args.output, "w", encoding="utf-8")
    else:
        output = sys.stdout

    try:
        not_found = run_pipeline(
            input_path=args.input,
            output=output,
            language=args.lang,
            top_n=args.top,
            level_min=args.hsk_min,
            level_max=args.hsk_max,
            include_ungraded=not args.no_ungraded,
            dict_path=CEDICT_PATH,
            hsk_path=HSK_PATH,
        )

        if not_found > 0:
            print(
                f"{not_found} words not found in dictionary — marked with empty fields in output.",
                file=sys.stderr,
            )
    except FileNotFoundError:
        print(
            "Error: Dictionary data files not found. "
            "Run 'ankigen update-dict' to download them, "
            "or run 'python scripts/download_data.py' for initial setup.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.output and output is not sys.stdout:
            output.close()


def _update_dict() -> None:
    """Download the latest CC-CEDICT dictionary."""
    import gzip
    import urllib.request

    url = "https://www.mdbg.net/chinese/export/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    dest = CEDICT_PATH

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading CC-CEDICT from {url}...")

    try:
        response = urllib.request.urlopen(url)
        compressed = response.read()
        data = gzip.decompress(compressed)
        dest.write_bytes(data)
        print(f"Dictionary saved to {dest} ({len(data)} bytes)")
    except Exception as e:
        print(f"Error downloading dictionary: {e}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add src/ankigen/cli.py tests/test_cli.py
git commit -m "feat: add CLI entry point with argument parsing and update-dict subcommand"
```

---

### Task 12: End-to-End Integration Test

**Files:**
- Create: `tests/test_integration.py`

This test verifies the full pipeline from a realistic Chinese text through to the final output.

- [ ] **Step 1: Write the integration test**

```python
# tests/test_integration.py
import io
from pathlib import Path

from ankigen.pipeline import run_pipeline

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


def test_full_pipeline_txt(tmp_path):
    """Full pipeline integration test with a realistic Chinese text."""
    input_file = tmp_path / "story.txt"
    input_file.write_text(
        "你好！我是一个学生。我在学校学习。"
        "学习很好。我每天都去学校学习。"
        "我喜欢吃饭。吃饭以后我看电脑。"
        "学校的电脑很好。暗示暗示。",
        encoding="utf-8",
    )

    output = io.StringIO()
    not_found = run_pipeline(
        input_path=str(input_file),
        output=output,
        language="mandarin",
        top_n=10,
        level_min=1,
        level_max=6,
        include_ungraded=True,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )

    output.seek(0)
    content = output.read()
    lines = content.strip().split("\n")

    # Header is present
    assert lines[0].startswith("#word")

    # At least some words extracted
    data_lines = [l for l in lines if not l.startswith("#")]
    assert len(data_lines) > 0

    # Check that the most frequent word (学习) is present
    assert "学习" in content

    # Check that output is tab-separated with correct column count
    for line in data_lines:
        fields = line.split("\t")
        assert len(fields) == 6, f"Expected 6 columns, got {len(fields)}: {line}"

    # Check that a known word has pinyin
    for line in data_lines:
        fields = line.split("\t")
        if fields[0] == "学习":
            assert fields[1] == "xué xí"
            assert "to learn" in fields[2] or "to study" in fields[2]
            break


def test_full_pipeline_hsk_only_level_1(tmp_path):
    """Test that HSK filtering correctly limits to level 1."""
    input_file = tmp_path / "story.txt"
    input_file.write_text(
        "学习学习学校电脑暗示暗示暗示",
        encoding="utf-8",
    )

    output = io.StringIO()
    run_pipeline(
        input_path=str(input_file),
        output=output,
        language="mandarin",
        top_n=100,
        level_min=1,
        level_max=1,
        include_ungraded=False,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )

    output.seek(0)
    content = output.read()
    # 学习 is HSK 1
    assert "学习" in content
    # 暗示 is HSK 6, should not appear
    assert "暗示" not in content
    # 电脑 is HSK 2, should not appear
    assert "电脑" not in content


def test_full_pipeline_empty_after_filter(tmp_path):
    """When all words are filtered out, raise a helpful error."""
    input_file = tmp_path / "story.txt"
    # Only HSK 1 words, but we filter for level 6 only
    input_file.write_text("学习学习你好你好", encoding="utf-8")

    output = io.StringIO()
    run_pipeline(
        input_path=str(input_file),
        output=output,
        language="mandarin",
        top_n=100,
        level_min=6,
        level_max=6,
        include_ungraded=False,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )

    output.seek(0)
    lines = [l for l in output.readlines() if not l.startswith("#")]
    # No data lines — just the header
    assert len(lines) == 0
```

- [ ] **Step 2: Run the integration test**

Run: `uv run pytest tests/test_integration.py -v`
Expected: All passed

- [ ] **Step 3: Run the full test suite**

Run: `uv run pytest -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration tests for the full pipeline"
```

---

### Task 13: Download Data Files and Smoke Test

This task downloads the real CC-CEDICT dictionary and creates the HSK word list, then runs a smoke test against a real file.

**Files:**
- Create: `scripts/download_data.py`
- Create: `src/ankigen/languages/mandarin/data/hsk.json`
- Download: `src/ankigen/languages/mandarin/data/cedict_ts.u8`

- [ ] **Step 1: Create HSK 2.0 word list**

Create `scripts/download_data.py`:

```python
#!/usr/bin/env python3
"""Download and prepare data files for ankigen."""
import gzip
import json
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "ankigen" / "languages" / "mandarin" / "data"


def download_cedict():
    url = "https://www.mdbg.net/chinese/export/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    dest = DATA_DIR / "cedict_ts.u8"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading CC-CEDICT from {url}...")
    response = urllib.request.urlopen(url)
    compressed = response.read()
    data = gzip.decompress(compressed)
    dest.write_bytes(data)
    print(f"Saved to {dest} ({len(data):,} bytes)")


def create_hsk_json():
    """Create HSK 2.0 word list.

    Source: HSK 2.0 standard word lists (levels 1-6).
    This is a curated subset. The full list has ~5,000 words.
    For the complete list, replace this with an authoritative source.
    """
    # HSK 2.0 Level 1 (150 words) - representative sample
    hsk1 = [
        "爱", "八", "爸爸", "杯子", "北京", "本", "不", "不客气", "菜", "茶",
        "吃", "出租车", "打电话", "大", "的", "点", "电脑", "电视", "电影",
        "东西", "都", "读", "对不起", "多", "多少", "儿子", "二", "饭店",
        "飞机", "分钟", "高兴", "个", "工作", "狗", "汉语", "好", "号",
        "喝", "和", "很", "后面", "回", "会", "几", "家", "叫", "今天",
        "九", "开", "看", "看见", "块", "来", "老师", "了", "冷", "里",
        "六", "妈妈", "吗", "买", "猫", "没", "没关系", "米饭", "名字",
        "明天", "哪", "那", "呢", "能", "你", "你好", "年", "女儿",
        "朋友", "漂亮", "苹果", "七", "前面", "钱", "请", "去", "热",
        "人", "认识", "三", "商店", "上", "上午", "少", "谁", "什么",
        "十", "时候", "是", "书", "水", "水果", "睡觉", "说", "四",
        "岁", "他", "她", "太", "天气", "听", "同学", "喂", "我",
        "我们", "五", "喜欢", "下", "下午", "下雨", "先生", "现在",
        "想", "小", "小姐", "些", "写", "谢谢", "星期", "学生",
        "学习", "学校", "一", "衣服", "医生", "医院", "椅子", "有",
        "月", "在", "再见", "怎么", "怎么样", "这", "中国", "中午",
        "住", "桌子", "字", "昨天", "坐", "做",
    ]
    # HSK 2.0 Level 2 (150 words) - representative sample
    hsk2 = [
        "吧", "白", "百", "帮助", "报纸", "比", "别", "长", "唱歌", "出",
        "穿", "次", "从", "错", "打篮球", "大家", "到", "得", "等", "弟弟",
        "第一", "懂", "对", "房间", "非常", "服务员", "高", "告诉", "哥哥",
        "给", "公共汽车", "公司", "贵", "过", "还", "孩子", "好吃", "黑",
        "红", "火车站", "机场", "鸡蛋", "件", "教室", "姐姐", "介绍", "进",
        "近", "就", "觉得", "咖啡", "开始", "考试", "可能", "可以", "课",
        "快", "快乐", "累", "离", "两", "零", "路", "旅游", "卖", "慢",
        "忙", "每", "妹妹", "门", "面条", "男", "您", "牛奶", "女", "旁边",
        "跑步", "便宜", "票", "妻子", "起床", "千", "铅笔", "晴", "让",
        "日", "上班", "身体", "生病", "生日", "时间", "事情", "手表", "手机",
        "说话", "送", "虽然", "它", "踢足球", "题", "跳舞", "外", "完",
        "玩", "晚上", "为什么", "问", "问题", "西瓜", "希望", "洗", "小时",
        "笑", "新", "姓", "休息", "雪", "颜色", "眼睛", "羊肉", "药",
        "要", "也", "已经", "一起", "意思", "因为", "阴", "游泳", "右边",
        "鱼", "远", "运动", "再", "早上", "丈夫", "找", "着", "真",
        "正在", "知道", "准备", "走", "最", "左边", "昨天",
    ]

    hsk_data = {}
    for word in hsk1:
        hsk_data[word] = 1
    for word in hsk2:
        hsk_data[word] = 2
    # NOTE: This only includes HSK levels 1-2 (~300 words) as a starting point.
    # The full HSK 2.0 has ~5,000 words across levels 1-6.
    # Source complete word lists from: https://github.com/gigacool/hanern-hsk
    # or another authoritative HSK word list repository, and add levels 3-6.

    dest = DATA_DIR / "hsk.json"
    dest.write_text(json.dumps(hsk_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"HSK data saved to {dest} ({len(hsk_data)} words)")


if __name__ == "__main__":
    download_cedict()
    create_hsk_json()
    print("Done! Data files are ready.")
```

- [ ] **Step 2: Run the data download script**

Run: `cd /Users/georgeliu/src/ankigen && uv run python scripts/download_data.py`
Expected: Both files created in `src/ankigen/languages/mandarin/data/`

- [ ] **Step 3: Add data directory to .gitignore (large binary data)**

Create `.gitignore`:

```
# Data files (downloaded via scripts/download_data.py or ankigen update-dict)
src/ankigen/languages/mandarin/data/cedict_ts.u8

# Python
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/
```

- [ ] **Step 4: Smoke test with a real file**

Create a quick test file and run:

```bash
echo "你好，我是一个学生。我在学校学习中文。学习很有意思。我每天都去学校。我喜欢吃中国菜，特别是饺子和面条。电脑也很有用，我用电脑做作业。" > /tmp/test_chinese.txt
cd /Users/georgeliu/src/ankigen && uv run ankigen /tmp/test_chinese.txt --top 10
```

Expected: Tab-separated output to stdout with Chinese words, pinyin, definitions, HSK levels, frequencies, and compounds.

- [ ] **Step 5: Run the full test suite one final time**

Run: `uv run pytest -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add scripts/download_data.py .gitignore src/ankigen/languages/mandarin/data/hsk.json
git commit -m "feat: add data download script and HSK word list, gitignore large dictionary file"
```

---

## Spec Coverage Checklist

| Spec Requirement | Task |
|---|---|
| CLI tool with argparse | Task 11 |
| Parse .txt, .pdf, .epub | Task 3 |
| jieba word segmentation | Task 7 |
| Frequency ranking (Counter) | Task 10 (in pipeline) |
| HSK level filtering (min/max/range) | Task 6 |
| Ungraded words included by default | Task 6 |
| CC-CEDICT offline dictionary | Task 5 |
| Pinyin number → tone mark conversion | Task 4 |
| Compound word lookup with text prioritization | Task 5 |
| Tab-separated Anki-importable output | Task 8 |
| Language extensibility (ABCs) | Task 2 |
| Language registry | Task 9 |
| Error handling (unsupported format, empty text, etc.) | Tasks 3, 10, 11 |
| `update-dict` subcommand | Task 11 |
| Testing (unit + integration) | All tasks + Task 12 |
| `pyproject.toml` with entry point | Task 1 |
