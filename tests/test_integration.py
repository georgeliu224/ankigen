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
    lines = [l.rstrip("\n") for l in content.splitlines()]

    # Header is present
    assert lines[0].startswith("#word")

    # At least some words extracted
    data_lines = [l for l in lines if l and not l.startswith("#")]
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
    assert "学习" in content
    assert "暗示" not in content
    assert "电脑" not in content


def test_full_pipeline_empty_after_filter(tmp_path):
    """When all words are filtered out, output has only header."""
    input_file = tmp_path / "story.txt"
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
    assert len(lines) == 0
