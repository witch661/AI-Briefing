# -*- coding: utf-8 -*-
"""
RSS 新闻抓取脚本
从多个 RSS 订阅源抓取 AI 相关新闻，按模块分类后保存为 JSON。
仅抓取本周发布的新闻。
"""

import feedparser
import json
import os
import re
from datetime import datetime, timedelta

# RSS 源配置
RSS_SOURCES = [
    ("https://feeds.arstechnica.com/arstechnica/technology-lab", "Ars Technica"),
    ("https://www.ainews.com/feed", "AI News"),
    ("https://www.technologyreview.com/feed/", "MIT Technology Review"),
    ("https://venturebeat.com/feed/", "VentureBeat"),
    ("https://www.unite.ai/feed/", "Unite.AI"),
    ("https://www.ifanr.com/feed", "爱范儿"),
    ("https://www.pingwest.com/feed", "品玩"),
]

# 模块关键词分类
MODULE_KEYWORDS = {
    "政声传递": ["政策", "法规", "国务院", "工信部", "发改委", "监管", "备案", "治理", "规划", "标准", "部委", "政府"],
    "他山之石": ["深圳", "上海", "北京", "杭州", "试点", "示范区", "区域", "地方", "城市", "特区"],
    "产业动态": ["发布", "推出", "融资", "收购", "上市", "产品", "技术", "突破", "模型", "算力", "芯片", "开源", "商用"],
    "综合关注": ["伦理", "安全", "医疗", "教育", "就业", "社会", "研究", "论文", "峰会", "会议"],
}

# 重要性关键词
HIGH_KEYWORDS = ["突破", "重大", "里程碑", "首个", "开源", "重磅", "首次", "大幅提升", "领先", "获批", "发布", "认证"]
LOW_KEYWORDS = ["融资", "人事", "合作", "签约", "投资", "估值", "完成"]


def get_week_range():
    """获取本周的日期范围"""
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start.date(), end.date()


def parse_date(entry):
    """解析 RSS 条目的发布时间"""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6]).date()
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6]).date()
    return None


def classify_module(title, summary):
    """根据关键词将新闻分类到对应模块"""
    text = (title + " " + summary).lower()
    scores = {}
    for module, keywords in MODULE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[module] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "综合关注"


def judge_importance(title, summary):
    """判断新闻重要性"""
    text = title + " " + summary
    for kw in HIGH_KEYWORDS:
        if kw in text:
            return "high"
    for kw in LOW_KEYWORDS:
        if kw in text:
            return "low"
    return "medium"


def clean_html(text):
    """清理 HTML 标签"""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:300]


def fetch_all_news():
    """从所有 RSS 源抓取本周新闻"""
    start_date, end_date = get_week_range()
    all_news = {"政声传递": [], "他山之石": [], "产业动态": [], "综合关注": []}

    for url, source_name in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub_date = parse_date(entry)
                if pub_date and start_date <= pub_date <= end_date:
                    title = clean_html(entry.get("title", ""))
                    summary = clean_html(entry.get("summary", entry.get("description", "")))
                    link = entry.get("link", "")
                    if not title:
                        continue
                    module = classify_module(title, summary)
                    importance = judge_importance(title, summary)
                    all_news[module].append({
                        "title": title,
                        "source": source_name,
                        "importance": importance,
                        "summary": summary,
                        "link": link,
                        "publishedAt": str(pub_date),
                    })
        except Exception as e:
            print(f"[WARN] 抓取 {source_name} 失败: {e}")

    return all_news, start_date, end_date


def build_output(all_news, start_date, end_date):
    """构建最终 JSON 结构"""
    modules = []
    module_order = ["政声传递", "他山之石", "产业动态", "综合关注"]
    module_desc = {
        "政声传递": "政府政策、法规、顶层设计、部委动态",
        "他山之石": "外地区/城市经验、试点示范、区域发展",
        "产业动态": "企业产品发布、技术突破、市场融资、行业会议",
        "综合关注": "其他 AI 相关新闻",
    }
    for name in module_order:
        modules.append({
            "name": name,
            "description": module_desc[name],
            "news": all_news[name],
        })

    now = datetime.now()
    week_num = now.isocalendar()[1]
    return {
        "week": f"{now.year}年第{week_num}周",
        "dateRange": f"{start_date} 至 {end_date}",
        "generatedAt": now.isoformat() + "Z",
        "modules": modules,
    }


def main():
    print("[INFO] 开始抓取 RSS 新闻...")
    all_news, start_date, end_date = fetch_all_news()
    output = build_output(all_news, start_date, end_date)
    total = sum(len(m["news"]) for m in output["modules"])
    print(f"[INFO] 共抓取 {total} 条本周新闻")
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "weekly_news.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 数据已保存到 {out_path}")


if __name__ == "__main__":
    main()
