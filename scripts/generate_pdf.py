# -*- coding: utf-8 -*-
"""
PDF 简报生成脚本
读取 weekly_news.json，生成公文风格 PDF 简报。
输出 ai_news_brief.pdf 到 downloads/ 目录。
"""

import json
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# 颜色定义
COLOR_BLUE = HexColor("#1e3a5f")
COLOR_GOLD = HexColor("#d4a843")
COLOR_RED = HexColor("#c0392b")
COLOR_ORANGE = HexColor("#e67e22")
COLOR_GRAY = HexColor("#7f8c8d")
COLOR_LIGHT_GRAY = HexColor("#ecf0f1")


def register_chinese_font():
    """注册中文字体"""
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", path))
                return "ChineseFont"
            except Exception:
                continue
    return "Helvetica"


def build_styles(font_name):
    """构建段落样式"""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName=font_name,
        fontSize=24,
        textColor=COLOR_BLUE,
        alignment=1,
        spaceAfter=10,
        leading=30,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName=font_name,
        fontSize=16,
        textColor=COLOR_RED,
        spaceBefore=20,
        spaceAfter=10,
        leading=22,
        borderPadding=(0, 0, 0, 8),
        borderColor=COLOR_RED,
        borderWidth=3,
        borderRadius=0,
    ))
    styles.add(ParagraphStyle(
        name="NewsTitle",
        fontName=font_name,
        fontSize=12,
        textColor=COLOR_BLUE,
        spaceBefore=8,
        spaceAfter=4,
        leading=16,
    ))
    styles.add(ParagraphStyle(
        name="NewsSummary",
        fontName=font_name,
        fontSize=10,
        textColor=HexColor("#333333"),
        spaceAfter=6,
        leading=16,
    ))
    styles.add(ParagraphStyle(
        name="MetaInfo",
        fontName=font_name,
        fontSize=9,
        textColor=COLOR_GRAY,
        alignment=1,
        leading=12,
    ))
    return styles


def get_importance_color(importance):
    """获取重要性对应颜色"""
    if importance == "high":
        return COLOR_RED
    elif importance == "low":
        return COLOR_GRAY
    return COLOR_ORANGE


def build_pdf(data, output_path, font_name):
    """生成 PDF 文件"""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )
    styles = build_styles(font_name)
    story = []

    # 封面信息
    story.append(Spacer(1, 20))
    story.append(Paragraph("AI 新闻周报", styles["CoverTitle"]))
    story.append(Paragraph(
        f"{data.get('week', '')}  |  {data.get('dateRange', '')}",
        styles["MetaInfo"],
    ))
    story.append(Paragraph(
        "内部资料 · 自动生成",
        styles["MetaInfo"],
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_GOLD))
    story.append(Spacer(1, 10))

    # 各模块
    for module in data.get("modules", []):
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"■ {module['name']}", styles["SectionTitle"]))
        if module.get("description"):
            story.append(Paragraph(module["description"], styles["MetaInfo"]))
            story.append(Spacer(1, 6))

        if not module.get("news"):
            story.append(Paragraph("本周暂无相关新闻", styles["NewsSummary"]))
            continue

        for item in module["news"]:
            importance = item.get("importance", "medium")
            imp_label = {"high": "高", "medium": "中", "low": "低"}.get(importance, "中")
            color = get_importance_color(importance)
            color_hex = color.hexval() if hasattr(color, "hexval") else "#e67e22"
            title_text = f"<font color='{color_hex}'><b>[{imp_label}]</b></font>  {item['title']}  <font color='#999999'>({item.get('source', '')})</font>"
            story.append(Paragraph(title_text, styles["NewsTitle"]))
            story.append(Paragraph(item.get("summary", ""), styles["NewsSummary"]))
            story.append(HRFlowable(width="80%", thickness=0.5, color=COLOR_LIGHT_GRAY))

    doc.build(story)


def main():
    if not HAS_REPORTLAB:
        print("[ERROR] 缺少 reportlab 库，请运行: pip install reportlab")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "..", "data", "weekly_news.json")
    output_dir = os.path.join(script_dir, "..", "downloads")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ai_news_brief.pdf")

    if not os.path.exists(json_path):
        print(f"[ERROR] 未找到 {json_path}，请先运行 fetch_news.py")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    font_name = register_chinese_font()
    print(f"[INFO] 使用字体: {font_name}")
    build_pdf(data, output_path, font_name)
    print(f"[INFO] PDF 已生成: {output_path}")


if __name__ == "__main__":
    main()
