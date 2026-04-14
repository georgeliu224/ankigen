import sys
from pathlib import Path
from unittest.mock import patch
import pytest
from ankigen.cli import build_parser, main

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["input.txt"])
    assert args.input == "input.txt"
    assert args.output is None
    assert args.top == 200
    assert args.hsk_min == 1
    assert args.hsk_max == 6
    assert args.no_ungraded is False
    assert args.lang == "mandarin"


def test_parser_all_flags():
    parser = build_parser()
    args = parser.parse_args([
        "book.epub",
        "-o", "deck.txt",
        "--top", "300",
        "--hsk-min", "2",
        "--hsk-max", "5",
        "--no-ungraded",
        "--lang", "mandarin",
    ])
    assert args.input == "book.epub"
    assert args.output == "deck.txt"
    assert args.top == 300
    assert args.hsk_min == 2
    assert args.hsk_max == 5
    assert args.no_ungraded is True
    assert args.lang == "mandarin"


def test_parser_requires_input():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_main_with_txt_file(tmp_path):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习学习学校电脑你好你好", encoding="utf-8")
    output_file = tmp_path / "deck.txt"

    with patch("ankigen.cli.CEDICT_PATH", CEDICT_PATH), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file), "-o", str(output_file)]
        main()

    content = output_file.read_text(encoding="utf-8")
    assert "#word" in content
    assert "学习" in content


def test_main_outputs_to_stdout(tmp_path, capsys):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习学校电脑", encoding="utf-8")

    with patch("ankigen.cli.CEDICT_PATH", CEDICT_PATH), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file)]
        main()

    captured = capsys.readouterr()
    assert "#word" in captured.out


def test_main_missing_dictionary(tmp_path, capsys):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习", encoding="utf-8")
    missing_dict = tmp_path / "nonexistent" / "cedict.u8"

    with patch("ankigen.cli.CEDICT_PATH", missing_dict), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file)]
        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()
    assert "update-dict" in captured.err


def test_main_prints_not_found_summary(tmp_path, capsys):
    input_file = tmp_path / "book.txt"
    input_file.write_text("学习罕见词罕见词罕见词", encoding="utf-8")

    with patch("ankigen.cli.CEDICT_PATH", CEDICT_PATH), \
         patch("ankigen.cli.HSK_PATH", HSK_PATH):
        sys.argv = ["ankigen", str(input_file)]
        main()

    captured = capsys.readouterr()
    assert "not found in dictionary" in captured.err
