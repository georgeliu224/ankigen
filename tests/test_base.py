from ankigen.languages.base import DictEntry, FlashcardEntry


def test_dict_entry_fields():
    entry = DictEntry(
        word="学习",
        pronunciation="xué xí",
        definitions=["to learn", "to study"],
        level=1,
    )
    assert entry.word == "学习"
    assert entry.pronunciation == "xué xí"
    assert entry.definitions == ["to learn", "to study"]
    assert entry.level == 1


def test_dict_entry_ungraded():
    entry = DictEntry(word="foo", pronunciation="", definitions=[], level=None)
    assert entry.level is None


def test_flashcard_entry_fields():
    entry = FlashcardEntry(
        word="学习",
        pinyin="xué xí",
        definition="to learn; to study",
        hsk_level="1",
        frequency=47,
        compounds="学生 (xué shēng) student",
    )
    assert entry.word == "学习"
    assert entry.hsk_level == "1"
    assert entry.frequency == 47
