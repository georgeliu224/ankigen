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
