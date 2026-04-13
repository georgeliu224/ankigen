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
    assert compounds[0].word in text_words


def test_find_compounds_shorter_first(dictionary):
    compounds = dictionary.find_compounds("吃", limit=5)
    words = [c.word for c in compounds]
    assert "吃饭" in words
    assert "吃惊" in words


def test_find_compounds_excludes_self(dictionary):
    compounds = dictionary.find_compounds("学习", limit=5)
    compound_words = [c.word for c in compounds]
    assert "学习" not in compound_words
