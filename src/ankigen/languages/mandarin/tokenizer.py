import re
import jieba
from ankigen.languages.base import Tokenizer

STOP_WORDS = frozenset({
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "都",
    "一", "个", "上", "也", "很", "到", "你", "会", "着", "这",
    "那", "被", "把", "让", "给", "对", "从", "向", "与", "而",
    "但", "他", "她", "它", "们", "地", "得", "过", "呢", "吗",
    "吧", "啊", "哦", "呀", "么", "之", "所", "以", "如", "为",
})

_CHINESE_CHAR = re.compile(r"[\u4e00-\u9fff]")


class MandarinTokenizer(Tokenizer):
    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        words = jieba.cut(text)
        return [
            w
            for w in words
            if _CHINESE_CHAR.search(w) and w not in STOP_WORDS
        ]
