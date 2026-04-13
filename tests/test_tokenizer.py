from ankigen.languages.mandarin.tokenizer import MandarinTokenizer


def test_basic_segmentation():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("我在学校学习")
    assert "学校" in tokens
    assert "学习" in tokens


def test_filters_punctuation():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("你好，世界！")
    assert "，" not in tokens
    assert "！" not in tokens


def test_filters_stop_words():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("我的学校是很好的")
    assert "的" not in tokens
    assert "是" not in tokens


def test_filters_numbers():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("我有123个苹果")
    assert "123" not in tokens


def test_filters_ascii():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("Hello你好World世界")
    assert "Hello" not in tokens
    assert "World" not in tokens
    assert "你好" in tokens or "世界" in tokens


def test_empty_input():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("")
    assert tokens == []


def test_returns_list_of_strings():
    tokenizer = MandarinTokenizer()
    tokens = tokenizer.tokenize("学习很重要")
    assert isinstance(tokens, list)
    assert all(isinstance(t, str) for t in tokens)
