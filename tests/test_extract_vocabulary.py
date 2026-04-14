from pathlib import Path

import pytest

from ankigen.languages.base import FlashcardEntry
from ankigen.pipeline import extract_vocabulary

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


@pytest.fixture
def chinese_txt(tmp_path):
    path = tmp_path / "book.txt"
    path.write_text("学习学习学习学校学校电脑暗示你好你好你好", encoding="utf-8")
    return path


def test_returns_entries_and_count(chinese_txt):
    entries, not_found = extract_vocabulary(
        input_path=str(chinese_txt),
        language="mandarin",
        top_n=10,
        level_min=1,
        level_max=6,
        include_ungraded=True,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    assert isinstance(entries, list)
    assert all(isinstance(e, FlashcardEntry) for e in entries)
    assert isinstance(not_found, int)
    assert len(entries) > 0


def test_not_found_count(chinese_txt):
    entries, not_found = extract_vocabulary(
        input_path=str(chinese_txt),
        language="mandarin",
        top_n=100,
        level_min=1,
        level_max=6,
        include_ungraded=True,
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    assert not_found >= 0


def test_empty_text_raises(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="No text could be extracted"):
        extract_vocabulary(
            input_path=str(path),
            language="mandarin",
            top_n=10,
            level_min=1,
            level_max=6,
            include_ungraded=True,
            dict_path=CEDICT_PATH,
            hsk_path=HSK_PATH,
        )
