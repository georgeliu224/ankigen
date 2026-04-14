import argparse
import sys
from pathlib import Path

from ankigen.exporters import get_export_format
from ankigen.exporters.apkg import ApkgExporter
from ankigen.pipeline import extract_vocabulary, run_pipeline

_DATA_DIR = Path(__file__).parent / "languages" / "mandarin" / "data"
CEDICT_PATH = _DATA_DIR / "cedict_ts.u8"
HSK_PATH = _DATA_DIR / "hsk.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ankigen",
        description="Extract vocabulary from foreign-language texts and generate Anki flashcard decks.",
    )
    parser.add_argument(
        "input",
        help="Path to .epub, .pdf, or .txt file",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=200,
        help="Number of top-frequency words to include (default: 200)",
    )
    parser.add_argument(
        "--hsk-min",
        type=int,
        default=1,
        help="Minimum HSK level to include (default: 1)",
    )
    parser.add_argument(
        "--hsk-max",
        type=int,
        default=6,
        help="Maximum HSK level to include (default: 6)",
    )
    parser.add_argument(
        "--no-ungraded",
        action="store_true",
        default=False,
        help="Exclude words not in any HSK level",
    )
    parser.add_argument(
        "--lang",
        default="mandarin",
        help="Language module to use (default: mandarin)",
    )
    parser.add_argument(
        "--deck-name",
        default=None,
        help="Name for the Anki deck (default: derived from input filename). "
             "Only used for .apkg output.",
    )
    return parser


def main() -> None:
    # Handle update-dict subcommand
    if len(sys.argv) > 1 and sys.argv[1] == "update-dict":
        _update_dict()
        return

    parser = build_parser()
    args = parser.parse_args()

    fmt = get_export_format(args.output)

    try:
        if fmt == "apkg":
            entries, not_found = extract_vocabulary(
                input_path=args.input,
                language=args.lang,
                top_n=args.top,
                level_min=args.hsk_min,
                level_max=args.hsk_max,
                include_ungraded=not args.no_ungraded,
                dict_path=CEDICT_PATH,
                hsk_path=HSK_PATH,
            )
            deck_name = args.deck_name or Path(args.input).stem
            exporter = ApkgExporter(deck_name=deck_name)
            exporter.export(entries, args.output)
        else:
            if args.output:
                output = open(args.output, "w", encoding="utf-8")
            else:
                output = sys.stdout
            try:
                not_found = run_pipeline(
                    input_path=args.input,
                    output=output,
                    language=args.lang,
                    top_n=args.top,
                    level_min=args.hsk_min,
                    level_max=args.hsk_max,
                    include_ungraded=not args.no_ungraded,
                    dict_path=CEDICT_PATH,
                    hsk_path=HSK_PATH,
                )
            finally:
                if args.output and output is not sys.stdout:
                    output.close()

        if not_found > 0:
            print(
                f"{not_found} words not found in dictionary — marked with empty fields in output.",
                file=sys.stderr,
            )
    except FileNotFoundError:
        print(
            "Error: Dictionary data files not found. "
            "Run 'ankigen update-dict' to download them, "
            "or run 'python scripts/download_data.py' for initial setup.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _update_dict() -> None:
    """Download the latest CC-CEDICT dictionary."""
    import gzip
    import urllib.request

    url = "https://www.mdbg.net/chinese/export/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    dest = CEDICT_PATH

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading CC-CEDICT from {url}...")

    try:
        response = urllib.request.urlopen(url)
        compressed = response.read()
        data = gzip.decompress(compressed)
        dest.write_bytes(data)
        print(f"Dictionary saved to {dest} ({len(data)} bytes)")
    except Exception as e:
        print(f"Error downloading dictionary: {e}", file=sys.stderr)
        sys.exit(1)
