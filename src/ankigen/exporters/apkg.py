from pathlib import Path

import genanki

from ankigen.languages.base import FlashcardEntry

# Fixed IDs so Anki recognizes re-imports as updates, not duplicates.
_MODEL_ID = 1607392319
_DECK_ID = 2059400110

_CSS = """\
.card {
    font-family: "Noto Sans SC", "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 24px;
    text-align: center;
    color: #333;
}
.word { font-size: 48px; margin-bottom: 0.5em; }
.pinyin { font-size: 20px; color: #666; margin-bottom: 0.3em; }
.definition { font-size: 18px; margin-bottom: 0.5em; }
.meta { font-size: 14px; color: #999; }
.compounds { font-size: 14px; color: #555; text-align: left; margin-top: 1em; }
"""

_MODEL = genanki.Model(
    _MODEL_ID,
    "AnkiGen Chinese Vocab",
    fields=[
        {"name": "Word"},
        {"name": "Pinyin"},
        {"name": "Definition"},
        {"name": "HSKLevel"},
        {"name": "Frequency"},
        {"name": "Compounds"},
    ],
    templates=[
        {
            "name": "Recognition",
            "qfmt": '<div class="word">{{Word}}</div>',
            "afmt": (
                '{{FrontSide}}<hr id="answer">'
                '<div class="pinyin">{{Pinyin}}</div>'
                '<div class="definition">{{Definition}}</div>'
                '<div class="meta">HSK {{HSKLevel}} &bull; Frequency: {{Frequency}}</div>'
                '{{#Compounds}}<div class="compounds"><b>Compounds:</b><br>{{Compounds}}</div>{{/Compounds}}'
            ),
        },
    ],
    css=_CSS,
)


class ApkgExporter:
    def __init__(self, deck_name: str = "AnkiGen Deck", deck_id: int | None = None):
        self._deck_name = deck_name
        self._deck_id = deck_id or _DECK_ID

    def export(self, entries: list[FlashcardEntry], output_path: str | Path) -> None:
        """Export entries to an .apkg file at the given path."""
        deck = genanki.Deck(self._deck_id, self._deck_name)

        for entry in entries:
            note = genanki.Note(
                model=_MODEL,
                fields=[
                    entry.word,
                    entry.pinyin,
                    entry.definition,
                    entry.hsk_level,
                    str(entry.frequency),
                    entry.compounds,
                ],
            )
            deck.add_note(note)

        package = genanki.Package(deck)
        package.write_to_file(str(output_path))
