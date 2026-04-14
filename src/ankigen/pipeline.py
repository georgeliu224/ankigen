from collections import Counter
from pathlib import Path
from typing import IO

from ankigen.languages import get_language
from ankigen.languages.base import DictEntry, FlashcardEntry
from ankigen.parsers import get_parser
from ankigen.exporters.tsv import TsvExporter


def _format_level(level: int | None) -> str:
    return str(level) if level is not None else "\u2014"


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
