# ankigen

Extract vocabulary from Chinese-language books and generate Anki-compatible flashcard decks.

ankigen parses `.epub`, `.pdf`, and `.txt` files, segments the text into words using [jieba](https://github.com/fxsjy/jieba), ranks words by frequency, filters by [HSK](https://en.wikipedia.org/wiki/Hanyu_Shuiping_Kaoshi) proficiency level, enriches each word with dictionary definitions, tone-marked pinyin, and compound words from [CC-CEDICT](https://cc-cedict.org/), and outputs a tab-separated file you can import directly into [Anki](https://apps.ankiweb.net/).

## Quick Start

```bash
# Clone and install
git clone https://github.com/georgeliu224/ankigen.git
cd ankigen
uv venv && uv pip install -e ".[dev]"

# Download the CC-CEDICT dictionary (~4MB)
uv run ankigen update-dict

# Generate a flashcard deck from a Chinese book
uv run ankigen book.epub -o deck.txt
```

Then open Anki, go to **File > Import**, select `deck.txt`, and map the columns to your card fields.

## Usage

```bash
# Basic usage — outputs to stdout
ankigen input.txt

# Save to file
ankigen input.epub -o deck.txt

# Top 300 words, HSK levels 2-5 only
ankigen input.pdf --top 300 --hsk-min 2 --hsk-max 5 -o deck.txt

# Only HSK level 1 words (beginner)
ankigen input.epub --hsk-max 1 -o beginner_deck.txt

# Exclude words not in any HSK level
ankigen input.txt --no-ungraded -o deck.txt

# Update the dictionary to the latest version
ankigen update-dict
```

### Options

| Flag | Default | Description |
|---|---|---|
| `<input>` | (required) | Path to `.epub`, `.pdf`, or `.txt` file |
| `-o, --output` | stdout | Output file path |
| `--top` | 200 | Number of top-frequency words to include |
| `--hsk-min` | 1 | Minimum HSK level to include |
| `--hsk-max` | 6 | Maximum HSK level to include |
| `--no-ungraded` | false | Exclude words not in any HSK level |
| `--lang` | mandarin | Language module to use |

### HSK Filtering

HSK (Hanyu Shuiping Kaoshi) is the standardized Chinese proficiency test with 6 levels. ankigen uses HSK levels to let you target vocabulary at your skill level:

| Goal | Command |
|---|---|
| All words up to level 3 | `ankigen book.epub --hsk-max 3` |
| Only level 4 words | `ankigen book.epub --hsk-min 4 --hsk-max 4` |
| Levels 2 through 5 | `ankigen book.epub --hsk-min 2 --hsk-max 5` |

Words not in any HSK level (domain-specific or literary vocabulary) are included by default and tagged as ungraded. Use `--no-ungraded` to exclude them.

## Output Format

ankigen produces a tab-separated file with 6 columns:

```
#word   pinyin      definition              hsk_level  frequency  compounds
学校    xué xiào    school                  1          2          技术学校 (jì shù xué xiào) vocational high school; ...
学习    xué xí      to learn; to study      1          2          深度学习 (shēn dù xué xí) deep learning; ...
电脑    diàn nǎo    computer                1          2          微电脑 (wēi diàn nǎo) microcomputer; ...
暗示    àn shì      to hint; to suggest     6          1          暗 (àn) dark; 暗中 (àn zhōng) in secret
```

| Column | Description |
|---|---|
| **word** | The Chinese word |
| **pinyin** | Tone-marked pronunciation |
| **definition** | English definitions, semicolon-separated |
| **hsk_level** | HSK level (1-6) or "—" if ungraded |
| **frequency** | Number of occurrences in the source text |
| **compounds** | Up to 5 related compound words with pinyin and meaning |

### Importing into Anki

1. Open Anki and go to **File > Import**
2. Select your `.txt` file
3. Set the separator to **Tab**
4. Check **Allow HTML in fields** if you want formatting
5. Map each column to the corresponding field in your note type
6. Click **Import**

## How It Works

ankigen processes text through a 6-stage pipeline:

```
Input File (.epub/.pdf/.txt)
    |
    v
[1. Parse]         Extract raw text from the file format
    |
    v
[2. Tokenize]      Segment text into words using jieba
    |
    v
[3. Frequency]     Count word occurrences, rank by frequency
    |
    v
[4. HSK Filter]    Filter by proficiency level, take top N
    |
    v
[5. Dictionary]    Look up pinyin, definitions, and compounds in CC-CEDICT
    |
    v
[6. Export]         Write tab-separated Anki-importable file
```

### Data Sources

- **[CC-CEDICT](https://cc-cedict.org/)** — Community-maintained Chinese-English dictionary with ~120,000 entries. Provides simplified/traditional characters, pinyin, and English definitions. Downloaded via `ankigen update-dict` and cached locally.
- **HSK 2.0 Word Lists** — Standardized Chinese proficiency levels 1-6 (~5,000 words total). Bundled with the package.

## Project Structure

```
ankigen/
├── src/ankigen/
│   ├── cli.py                          # CLI entry point
│   ├── pipeline.py                     # 6-stage pipeline orchestrator
│   ├── parsers/                        # File format parsers
│   │   ├── txt.py, pdf.py, epub.py
│   ├── languages/
│   │   ├── base.py                     # Abstract interfaces (Tokenizer, etc.)
│   │   └── mandarin/
│   │       ├── tokenizer.py            # jieba-based segmentation
│   │       ├── proficiency.py          # HSK level filtering
│   │       ├── dictionary.py           # CC-CEDICT lookup + compound index
│   │       ├── pinyin.py               # Numbered → tone-marked conversion
│   │       └── data/                   # Dictionary + HSK data files
│   └── exporters/
│       └── tsv.py                      # Tab-separated output
└── tests/                              # 70 tests (unit + integration)
```

## Extending to Other Languages

ankigen is designed to support multiple languages. Each language implements three interfaces:

- **Tokenizer** — Splits raw text into words
- **ProficiencyFilter** — Tags and filters words by proficiency level
- **DictionaryLookup** — Provides definitions, pronunciation, and compound words

To add a new language (e.g., Japanese):

1. Create `src/ankigen/languages/japanese/` with implementations using appropriate tools (e.g., `fugashi` for tokenization, JLPT for proficiency levels, JMdict for dictionary)
2. Register the language in `src/ankigen/languages/__init__.py`
3. Use it with `ankigen input.txt --lang japanese`

## Development

```bash
# Install with dev dependencies
uv venv && uv pip install -e ".[dev]"

# Run tests
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_dictionary.py -v
```

### Dependencies

| Package | Purpose |
|---|---|
| [jieba](https://github.com/fxsjy/jieba) | Chinese word segmentation |
| [ebooklib](https://github.com/aerkalov/ebooklib) | EPUB parsing |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML stripping from EPUB content |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | PDF text extraction |
| [lxml](https://lxml.de/) | XML parsing |

## License

MIT
