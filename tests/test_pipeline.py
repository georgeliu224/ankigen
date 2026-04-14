import io
from pathlib import Path
import pytest
from ankigen.pipeline import run_pipeline

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


@pytest.fixture
def chinese_txt(tmp_path):
    path = tmp_path / "book.txt"
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
    assert "#word" in content
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
    assert "学习" in content
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
