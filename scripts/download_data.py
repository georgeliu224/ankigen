#!/usr/bin/env python3
"""Download and prepare data files for ankigen."""
import gzip
import json
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "ankigen" / "languages" / "mandarin" / "data"


def download_cedict():
    url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    dest = DATA_DIR / "cedict_ts.u8"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading CC-CEDICT from {url}...")
    response = urllib.request.urlopen(url)
    compressed = response.read()
    data = gzip.decompress(compressed)
    dest.write_bytes(data)
    print(f"Saved to {dest} ({len(data):,} bytes)")


def create_hsk_json():
    """Create HSK 2.0 word list (levels 1-2 representative sample).

    NOTE: This only includes HSK levels 1-2 (~300 words) as a starting point.
    The full HSK 2.0 has ~5,000 words across levels 1-6.
    Source complete word lists from an authoritative HSK word list repository
    and add levels 3-6.
    """
    hsk1 = [
        "爱", "八", "爸爸", "杯子", "北京", "本", "不", "不客气", "菜", "茶",
        "吃", "出租车", "打电话", "大", "的", "点", "电脑", "电视", "电影",
        "东西", "都", "读", "对不起", "多", "多少", "儿子", "二", "饭店",
        "飞机", "分钟", "高兴", "个", "工作", "狗", "汉语", "好", "号",
        "喝", "和", "很", "后面", "回", "会", "几", "家", "叫", "今天",
        "九", "开", "看", "看见", "块", "来", "老师", "了", "冷", "里",
        "六", "妈妈", "吗", "买", "猫", "没", "没关系", "米饭", "名字",
        "明天", "哪", "那", "呢", "能", "你", "你好", "年", "女儿",
        "朋友", "漂亮", "苹果", "七", "前面", "钱", "请", "去", "热",
        "人", "认识", "三", "商店", "上", "上午", "少", "谁", "什么",
        "十", "时候", "是", "书", "水", "水果", "睡觉", "说", "四",
        "岁", "他", "她", "太", "天气", "听", "同学", "喂", "我",
        "我们", "五", "喜欢", "下", "下午", "下雨", "先生", "现在",
        "想", "小", "小姐", "些", "写", "谢谢", "星期", "学生",
        "学习", "学校", "一", "衣服", "医生", "医院", "椅子", "有",
        "月", "在", "再见", "怎么", "怎么样", "这", "中国", "中午",
        "住", "桌子", "字", "昨天", "坐", "做",
    ]
    hsk2 = [
        "吧", "白", "百", "帮助", "报纸", "比", "别", "长", "唱歌", "出",
        "穿", "次", "从", "错", "打篮球", "大家", "到", "得", "等", "弟弟",
        "第一", "懂", "对", "房间", "非常", "服务员", "高", "告诉", "哥哥",
        "给", "公共汽车", "公司", "贵", "过", "还", "孩子", "好吃", "黑",
        "红", "火车站", "机场", "鸡蛋", "件", "教室", "姐姐", "介绍", "进",
        "近", "就", "觉得", "咖啡", "开始", "考试", "可能", "可以", "课",
        "快", "快乐", "累", "离", "两", "零", "路", "旅游", "卖", "慢",
        "忙", "每", "妹妹", "门", "面条", "男", "您", "牛奶", "女", "旁边",
        "跑步", "便宜", "票", "妻子", "起床", "千", "铅笔", "晴", "让",
        "日", "上班", "身体", "生病", "生日", "时间", "事情", "手表", "手机",
        "说话", "送", "虽然", "它", "踢足球", "题", "跳舞", "外", "完",
        "玩", "晚上", "为什么", "问", "问题", "西瓜", "希望", "洗", "小时",
        "笑", "新", "姓", "休息", "雪", "颜色", "眼睛", "羊肉", "药",
        "要", "也", "已经", "一起", "意思", "因为", "阴", "游泳", "右边",
        "鱼", "远", "运动", "再", "早上", "丈夫", "找", "着", "真",
        "正在", "知道", "准备", "走", "最", "左边",
    ]

    hsk_data = {}
    for word in hsk1:
        hsk_data[word] = 1
    for word in hsk2:
        hsk_data[word] = 2

    dest = DATA_DIR / "hsk.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(hsk_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"HSK data saved to {dest} ({len(hsk_data)} words)")


if __name__ == "__main__":
    download_cedict()
    create_hsk_json()
    print("Done! Data files are ready.")
