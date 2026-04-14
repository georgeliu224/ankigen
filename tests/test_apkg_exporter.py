import sqlite3
import zipfile
from pathlib import Path

import pytest

from ankigen.exporters.apkg import ApkgExporter
from ankigen.languages.base import FlashcardEntry


@pytest.fixture
def sample_entries():
    return [
        FlashcardEntry(
            word="学习",
            pinyin="xué xí",
            definition="to learn; to study",
            hsk_level="1",
            frequency=47,
            compounds="学生 (xué shēng) student",
        ),
        FlashcardEntry(
            word="电脑",
            pinyin="diàn nǎo",
            definition="computer",
            hsk_level="2",
            frequency=12,
            compounds="",
        ),
    ]


def test_export_creates_file(tmp_path, sample_entries):
    path = tmp_path / "deck.apkg"
    exporter = ApkgExporter(deck_name="Test Deck")
    exporter.export(sample_entries, path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_export_is_valid_zip(tmp_path, sample_entries):
    path = tmp_path / "deck.apkg"
    exporter = ApkgExporter(deck_name="Test Deck")
    exporter.export(sample_entries, path)
    assert zipfile.is_zipfile(path)


def test_export_empty_entries(tmp_path):
    path = tmp_path / "empty.apkg"
    exporter = ApkgExporter(deck_name="Empty Deck")
    exporter.export([], path)
    assert path.exists()
    assert zipfile.is_zipfile(path)


def test_export_note_count(tmp_path, sample_entries):
    path = tmp_path / "deck.apkg"
    exporter = ApkgExporter(deck_name="Test Deck")
    exporter.export(sample_entries, path)

    note_count = _count_notes(path)
    assert note_count == 2


def test_export_custom_deck_name(tmp_path, sample_entries):
    path = tmp_path / "deck.apkg"
    exporter = ApkgExporter(deck_name="My Chinese Vocab")
    exporter.export(sample_entries, path)

    deck_name = _get_deck_name(path)
    assert deck_name == "My Chinese Vocab"


def test_export_field_content(tmp_path, sample_entries):
    path = tmp_path / "deck.apkg"
    exporter = ApkgExporter(deck_name="Test Deck")
    exporter.export(sample_entries, path)

    fields = _get_note_fields(path)
    # Check that our entries are present in the notes
    words = [f[0] for f in fields]
    assert "学习" in words
    assert "电脑" in words


def _extract_db(apkg_path: Path) -> Path:
    """Extract the SQLite database from an .apkg file."""
    db_path = apkg_path.parent / "collection.anki21"
    with zipfile.ZipFile(apkg_path) as z:
        # genanki uses collection.anki21 or collection.anki2
        for name in z.namelist():
            if name.startswith("collection"):
                with z.open(name) as src:
                    db_path.write_bytes(src.read())
                return db_path
    raise FileNotFoundError("No collection database found in .apkg")


def _count_notes(apkg_path: Path) -> int:
    db_path = _extract_db(apkg_path)
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    conn.close()
    return count


def _get_deck_name(apkg_path: Path) -> str:
    import json
    db_path = _extract_db(apkg_path)
    conn = sqlite3.connect(db_path)
    decks_json = conn.execute("SELECT decks FROM col").fetchone()[0]
    conn.close()
    decks = json.loads(decks_json)
    # Filter out the default deck (id=1)
    for deck_id, deck in decks.items():
        if deck_id != "1":
            return deck["name"]
    return ""


def _get_note_fields(apkg_path: Path) -> list[list[str]]:
    db_path = _extract_db(apkg_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT flds FROM notes").fetchall()
    conn.close()
    # Fields are separated by \x1f in Anki's SQLite format
    return [row[0].split("\x1f") for row in rows]
