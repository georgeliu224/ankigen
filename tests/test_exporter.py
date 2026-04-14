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
    assert "meaning" in header
    assert "hsk_level" in header
    assert "frequency" in header
    assert "compounds" in header


def test_export_combines_pinyin_and_definition():
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
    assert len(lines) == 2
    fields = lines[1].strip().split("\t")
    assert fields[0] == "学习"
    assert fields[1] == "xué xí<br>to learn; to study"
    assert fields[2] == "1"
    assert fields[3] == "47"
    assert fields[4] == "学生 (xué shēng) student"


def test_export_pinyin_only():
    exporter = TsvExporter()
    entries = [
        FlashcardEntry("学习", "xué xí", "", "1", 47, ""),
    ]
    output = io.StringIO()
    exporter.export(entries, output)
    output.seek(0)
    lines = output.readlines()
    fields = lines[1].strip().split("\t")
    assert fields[1] == "xué xí"


def test_export_definition_only():
    exporter = TsvExporter()
    entries = [
        FlashcardEntry("学习", "", "to learn", "1", 47, ""),
    ]
    output = io.StringIO()
    exporter.export(entries, output)
    output.seek(0)
    lines = output.readlines()
    fields = lines[1].strip().split("\t")
    assert fields[1] == "to learn"


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
    assert len(lines) == 3


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
    assert fields[2] == "—"
