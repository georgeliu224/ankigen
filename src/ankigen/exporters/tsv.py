from typing import IO
from ankigen.languages.base import FlashcardEntry

HEADER = "#word\tpinyin\tdefinition\thsk_level\tfrequency\tcompounds\n"


class TsvExporter:
    def export(self, entries: list[FlashcardEntry], output: IO[str]) -> None:
        output.write(HEADER)
        for entry in entries:
            line = "\t".join([
                entry.word,
                entry.pinyin,
                entry.definition,
                entry.hsk_level,
                str(entry.frequency),
                entry.compounds,
            ])
            output.write(line + "\n")
