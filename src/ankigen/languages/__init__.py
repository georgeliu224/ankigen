from dataclasses import dataclass
from pathlib import Path

from ankigen.languages.base import Tokenizer, ProficiencyFilter, DictionaryLookup


@dataclass
class LanguageModule:
    tokenizer: Tokenizer
    proficiency: ProficiencyFilter
    dictionary: DictionaryLookup


def get_language(
    name: str,
    dict_path: Path | None = None,
    hsk_path: Path | None = None,
) -> LanguageModule:
    if name == "mandarin":
        from ankigen.languages.mandarin.tokenizer import MandarinTokenizer
        from ankigen.languages.mandarin.proficiency import MandarinProficiency
        from ankigen.languages.mandarin.dictionary import MandarinDictionary

        return LanguageModule(
            tokenizer=MandarinTokenizer(),
            proficiency=MandarinProficiency(hsk_path=hsk_path),
            dictionary=MandarinDictionary(dict_path=dict_path),
        )
    available = ["mandarin"]
    raise ValueError(
        f"Unknown language '{name}'. Available: {', '.join(available)}"
    )
