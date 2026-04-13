from ankigen.languages.mandarin.pinyin import numbered_to_marked


def test_single_syllable_tone1():
    assert numbered_to_marked("ma1") == "mā"


def test_single_syllable_tone2():
    assert numbered_to_marked("ma2") == "má"


def test_single_syllable_tone3():
    assert numbered_to_marked("ma3") == "mǎ"


def test_single_syllable_tone4():
    assert numbered_to_marked("ma4") == "mà"


def test_neutral_tone():
    assert numbered_to_marked("ma5") == "ma"


def test_multi_syllable():
    assert numbered_to_marked("xue2 xi2") == "xué xí"


def test_tone_on_a():
    assert numbered_to_marked("bai2") == "bái"


def test_tone_on_e():
    assert numbered_to_marked("mei2") == "méi"


def test_tone_on_ou():
    assert numbered_to_marked("gou3") == "gǒu"


def test_tone_on_last_vowel():
    assert numbered_to_marked("liu2") == "liú"


def test_u_colon_becomes_u_umlaut():
    assert numbered_to_marked("lv4") == "lǜ"
    assert numbered_to_marked("lu:4") == "lǜ"


def test_full_pinyin_phrase():
    assert numbered_to_marked("ni3 hao3") == "nǐ hǎo"


def test_no_tone_number():
    assert numbered_to_marked("a") == "a"


def test_empty_string():
    assert numbered_to_marked("") == ""
