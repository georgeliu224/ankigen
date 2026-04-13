from pathlib import Path
import pytest
from ankigen.languages import get_language, LanguageModule
from ankigen.languages.mandarin.tokenizer import MandarinTokenizer
from ankigen.languages.mandarin.proficiency import MandarinProficiency
from ankigen.languages.mandarin.dictionary import MandarinDictionary

CEDICT_PATH = Path(__file__).parent / "fixtures" / "cedict_sample.u8"
HSK_PATH = Path(__file__).parent / "fixtures" / "hsk_sample.json"


def test_get_mandarin():
    lang = get_language(
        "mandarin",
        dict_path=CEDICT_PATH,
        hsk_path=HSK_PATH,
    )
    assert isinstance(lang, LanguageModule)
    assert isinstance(lang.tokenizer, MandarinTokenizer)
    assert isinstance(lang.proficiency, MandarinProficiency)
    assert isinstance(lang.dictionary, MandarinDictionary)


def test_get_unknown_language():
    with pytest.raises(ValueError, match="Unknown language"):
        get_language("klingon")
