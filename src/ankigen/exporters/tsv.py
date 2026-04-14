from typing import IO
from ankigen.languages.base import FlashcardEntry

HEADER = "#word\tmeaning\thsk_level\tfrequency\tcompounds\n"


class TsvExporter:
    def export(self, entries: list[FlashcardEntry], output: IO[str]) -> None:
        output.write(HEADER)
        for entry in entries:
            # Combine pinyin and definition with <br> for Anki HTML rendering
            if entry.pinyin and entry.definition:
                meaning = f"{entry.pinyin}<br>{entry.definition}"
            elif entry.pinyin:
                meaning = entry.pinyin
            else:
                meaning = entry.definition

            line = "\t".join([
                entry.word,
                meaning,
                entry.hsk_level,
                str(entry.frequency),
                entry.compounds,
            ])
            output.write(line + "\n")
