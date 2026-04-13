# ankigen — Design Spec

**Date:** 2026-04-13
**Status:** Approved

## Overview

ankigen is a CLI tool that extracts vocabulary from foreign-language books (EPUB, PDF, TXT) and generates Anki-compatible flashcard decks. It targets Mandarin Chinese first but is designed to be extensible to other languages.

The user uploads a file, and ankigen parses the text, segments it into words, ranks by frequency, filters by proficiency level (HSK for Mandarin), enriches with dictionary data (definitions, pronunciation, compound words), and outputs a tab-separated file importable into Anki.

## Decisions

| Decision            | Choice                                          |
|---------------------|--------------------------------------------------|
| Interface           | CLI tool                                         |
| Language            | Python                                           |
| Dictionary source   | CC-CEDICT (offline, bundled)                     |
| Word selection      | Top N by frequency + HSK-level filtering         |
| Output format       | Tab-separated plain text (Anki importable)       |
| Word pairings       | Dictionary compound lookups from CC-CEDICT       |
| Ungraded words      | Included by default (`--no-ungraded` to exclude) |
| HSK version         | HSK 2.0 (levels 1-6) initially                  |

## CLI Interface

```bash
# Basic usage
ankigen input.epub -o deck.txt

# With options
ankigen input.pdf --top 300 --hsk-min 2 --hsk-max 5 --lang mandarin -o deck.txt

# Defaults: --top 200, --hsk-min 1, --hsk-max 6, --lang mandarin
```

### Flags

| Flag              | Default    | Description                                        |
|-------------------|------------|----------------------------------------------------|
| `<input>`         | (required) | Path to .epub, .pdf, or .txt file                  |
| `-o, --output`    | stdout     | Output file path                                   |
| `--top`           | 200        | Number of top-frequency words to include           |
| `--hsk-min`       | 1          | Minimum HSK level to include                       |
| `--hsk-max`       | 6          | Maximum HSK level to include                       |
| `--no-ungraded`   | false      | Exclude words not in any HSK level                 |
| `--lang`          | mandarin   | Language module to use                             |

> **Note on flag naming:** `--hsk-min`/`--hsk-max` are Mandarin-specific. When adding a second language, generalize to `--level-min`/`--level-max` and keep the HSK names as aliases. Not worth abstracting for MVP with a single language.

### HSK Filtering Examples

| Use case                | Command                                      |
|-------------------------|----------------------------------------------|
| All words up to level 3 | `ankigen input.epub --hsk-max 3`            |
| Only level 4 words      | `ankigen input.epub --hsk-min 4 --hsk-max 4`|
| Levels 2 through 5      | `ankigen input.epub --hsk-min 2 --hsk-max 5`|

## Project Structure

```
ankigen/
├── pyproject.toml
├── src/
│   └── ankigen/
│       ├── __init__.py
│       ├── cli.py                  # CLI entry point (argparse)
│       ├── pipeline.py             # Orchestrates the 6 stages
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract file parser
│       │   ├── epub.py
│       │   ├── pdf.py
│       │   └── txt.py
│       ├── languages/
│       │   ├── __init__.py         # Language registry
│       │   ├── base.py             # Abstract interfaces
│       │   └── mandarin/
│       │       ├── __init__.py
│       │       ├── tokenizer.py    # jieba-based word segmentation
│       │       ├── proficiency.py  # HSK level filtering
│       │       ├── dictionary.py   # CC-CEDICT loader + lookup
│       │       └── data/           # Bundled data files
│       │           ├── cedict_ts.u8
│       │           └── hsk.json
│       └── exporters/
│           ├── __init__.py
│           └── csv.py              # Tab-separated Anki output
└── tests/
```

## Data Pipeline

6 sequential stages, each transforming the output of the previous:

```
Input File → [1. Parse] → raw text
           → [2. Tokenize] → list of words
           → [3. Frequency Analysis] → {word: count} ranked
           → [4. Proficiency Filter] → filtered word list
           → [5. Dictionary Lookup] → enriched entries
           → [6. Export] → Anki-importable TSV
```

### Stage 1: Parse

Detect file type by extension, delegate to the appropriate parser. Each parser returns a single string of raw text.

- `.epub` — `ebooklib` + `BeautifulSoup` to strip HTML
- `.pdf` — `pdfplumber` for text extraction
- `.txt` — `open().read()`

### Stage 2: Tokenize (language-specific)

For Mandarin, `jieba` segments the raw text into words. Filter out:
- Punctuation (Chinese and ASCII)
- Numbers
- Whitespace
- Single-character stop words (的, 了, 是, etc. — hardcoded default list bundled in the Mandarin tokenizer module)

Returns `list[str]`.

### Stage 3: Frequency Analysis (shared)

`collections.Counter` on the token list. Sort descending by count. Language-agnostic.

### Stage 4: Proficiency Filter (language-specific)

For Mandarin, load HSK word lists (levels 1-6). Apply the user's `--hsk-min` / `--hsk-max` range. Take the top N after filtering.

- Words within the HSK range are included and tagged with their level.
- Words not in any HSK level are tagged as ungraded ("—") and included by default. The `--no-ungraded` flag excludes them.

### Stage 5: Dictionary Lookup (language-specific)

For each word in the filtered list, look up in CC-CEDICT:

- **Pinyin** — tone-marked (xué xí), converted from CC-CEDICT's numbered format (xue2 xi2)
- **English definitions** — semicolon-separated
- **Compound words** — other CC-CEDICT entries whose simplified field contains the target word, limited to 5, prioritized by:
  1. Words that also appear in the uploaded text (most contextually relevant)
  2. Shorter compounds first (2-char > 3-char > 4-char)

Words not found in CC-CEDICT are kept with empty definition/pinyin fields. A summary is printed at the end: "N words not found in dictionary."

### Stage 6: Export (shared)

Write a tab-separated file with a header comment:

```
#word	pinyin	definition	hsk_level	frequency	compounds
```

One row per word.

## Output Format

| Column     | Example                                                              |
|------------|----------------------------------------------------------------------|
| Word       | 学习                                                                  |
| Pinyin     | xué xí                                                               |
| Definition | to learn; to study                                                   |
| HSK Level  | 1                                                                    |
| Frequency  | 47                                                                   |
| Compounds  | 学生 (xué shēng) student; 学校 (xué xiào) school                     |

Example rows:

```
学习	xué xí	to learn; to study	1	47	学生 (xué shēng) student; 学校 (xué xiào) school; 学问 (xué wèn) learning
吃	chī	to eat; to consume	1	32	吃饭 (chī fàn) to eat a meal; 吃惊 (chī jīng) to be startled
暗示	àn shì	to hint; to suggest	6	8	暗 (àn) dark; 暗中 (àn zhōng) in secret
```

## Data Sources

### CC-CEDICT

- Community-maintained Chinese-English dictionary, ~120k entries
- Format: `Traditional Simplified [pinyin] /definition1/definition2/`
- ~4MB uncompressed, bundled in `languages/mandarin/data/`
- A snapshot ships with the package for offline use
- `ankigen update-dict` command downloads the latest version from `https://www.mdbg.net/chinese/export/cedict_1_0_ts_utf-8_mdbg.txt.gz`

### Pinyin Conversion

CC-CEDICT stores numbered pinyin (xue2 xi2). Convert to tone-marked pinyin (xué xí) using a character + tone number → accented character mapping.

### HSK Word Lists

- HSK 2.0 (classic), levels 1-6, ~5,000 words total
- Bundled as a single JSON file: `{word: level}`
- HSK 3.0 (levels 1-9) can be added later as a flag

### Compound Word Index

Pre-build an inverted index at dictionary load time: character → list of CC-CEDICT entries containing that character. This makes compound lookups O(1) per character.

## Language Extensibility

Three abstract interfaces in `languages/base.py`:

```python
class Tokenizer(ABC):
    def tokenize(self, text: str) -> list[str]: ...

class ProficiencyFilter(ABC):
    def get_level(self, word: str) -> int | None: ...
    def filter(self, words: list[tuple[str, int]],
               min_level: int, max_level: int,
               include_ungraded: bool) -> list[tuple[str, int]]: ...

class DictionaryLookup(ABC):
    def lookup(self, word: str) -> DictEntry | None: ...
    def find_compounds(self, word: str, limit: int = 5) -> list[DictEntry]: ...
```

Shared dataclass:

```python
@dataclass
class DictEntry:
    word: str
    pronunciation: str
    definitions: list[str]
    level: int | None
```

Language registry in `languages/__init__.py`: a dict mapping language name → (Tokenizer, ProficiencyFilter, DictionaryLookup) classes. Adding a language means implementing three classes and adding one registry entry.

**Example — adding Japanese:**
- Tokenizer: `fugashi` (MeCab wrapper) instead of jieba
- ProficiencyFilter: JLPT levels (N5-N1) instead of HSK
- DictionaryLookup: JMdict instead of CC-CEDICT

## Error Handling

| Scenario                          | Behavior                                                                 |
|-----------------------------------|--------------------------------------------------------------------------|
| Unsupported file type             | Error listing supported formats (.epub, .pdf, .txt)                     |
| No extractable text (scanned PDF) | "No text could be extracted. OCR is not currently supported."            |
| Word not in CC-CEDICT             | Kept with empty fields; summary printed: "N words not found"            |
| Empty result after filtering      | Warning: "No words matched your HSK filter. Try widening the range."    |
| Dictionary data file missing      | Error with instructions to run `ankigen update-dict`                    |

No silent failures. The CLI always explains what happened and what to do.

## Dependencies

| Package         | Purpose                           |
|-----------------|-----------------------------------|
| `jieba`         | Chinese word segmentation         |
| `ebooklib`      | EPUB parsing                      |
| `beautifulsoup4`| HTML stripping from EPUB content  |
| `pdfplumber`    | PDF text extraction               |
| `lxml`          | XML parsing (ebooklib dependency) |

5 runtime dependencies. No web frameworks, no API clients.

## Testing Strategy

- **Unit tests per stage:** parser returns text, tokenizer returns tokens, frequency counter is correct, HSK filter respects bounds, dictionary lookups return expected entries
- **Integration test:** small fixture files (.txt, .epub, .pdf) run through the full pipeline, assert output has expected rows
- **CC-CEDICT parser:** tested against known entries
- **Pinyin conversion:** tested against known tone number → accent mappings
- **Test runner:** pytest

## Package Management

`pyproject.toml` with `uv` for dependency resolution. Compatible with pip — no lock-in.

Entry point configured via `[project.scripts]`:

```toml
[project.scripts]
ankigen = "ankigen.cli:main"
```
