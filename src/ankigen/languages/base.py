from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DictEntry:
    word: str
    pronunciation: str
    definitions: list[str]
    level: int | None


@dataclass
class FlashcardEntry:
    word: str
    pinyin: str
    definition: str
    hsk_level: str
    frequency: int
    compounds: str


class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, text: str) -> list[str]: ...


class ProficiencyFilter(ABC):
    @abstractmethod
    def get_level(self, word: str) -> int | None: ...

    @abstractmethod
    def filter(
        self,
        words: list[tuple[str, int]],
        min_level: int,
        max_level: int,
        include_ungraded: bool,
    ) -> list[tuple[str, int]]: ...


class DictionaryLookup(ABC):
    @abstractmethod
    def lookup(self, word: str) -> DictEntry | None: ...

    @abstractmethod
    def find_compounds(
        self, word: str, limit: int = 5, text_words: set[str] | None = None
    ) -> list[DictEntry]: ...
