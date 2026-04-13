TONE_MARKS: dict[str, tuple[str, str, str, str]] = {
    "a": ("ā", "á", "ǎ", "à"),
    "e": ("ē", "é", "ě", "è"),
    "i": ("ī", "í", "ǐ", "ì"),
    "o": ("ō", "ó", "ǒ", "ò"),
    "u": ("ū", "ú", "ǔ", "ù"),
    "ü": ("ǖ", "ǘ", "ǚ", "ǜ"),
}


def _convert_syllable(syllable: str) -> str:
    # Normalize ü representations
    syllable = syllable.replace("u:", "ü").replace("v", "ü")

    if not syllable or not syllable[-1].isdigit():
        return syllable

    tone = int(syllable[-1])
    base = syllable[:-1]

    if tone == 5 or tone == 0:
        return base

    # Rule 1: 'a' or 'e' always gets the tone mark
    for i, ch in enumerate(base):
        if ch in ("a", "e"):
            return base[:i] + TONE_MARKS[ch][tone - 1] + base[i + 1:]

    # Rule 2: 'ou' → tone mark on 'o'
    if "ou" in base:
        i = base.index("o")
        return base[:i] + TONE_MARKS["o"][tone - 1] + base[i + 1:]

    # Rule 3: tone mark on the last vowel
    for i in range(len(base) - 1, -1, -1):
        if base[i] in TONE_MARKS:
            return base[:i] + TONE_MARKS[base[i]][tone - 1] + base[i + 1:]

    return base


def numbered_to_marked(pinyin: str) -> str:
    """Convert numbered pinyin to tone-marked pinyin.
    Example: 'xue2 xi2' → 'xué xí'
    """
    if not pinyin:
        return ""
    syllables = pinyin.split()
    return " ".join(_convert_syllable(s) for s in syllables)
