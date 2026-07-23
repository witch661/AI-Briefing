# -*- coding: utf-8 -*-
"""
AI 朗读视频生成脚本
读取 weekly_news.json，使用 edge-tts 生成语音，moviepy 合成 MP4 视频。
输出 ai_news_brief.mp4 到 downloads/ 目录。
"""

import asyncio
import json
import os
import textwrap
from datetime import datetime

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from moviepy.editor import (
        ImageClip,
        AudioFileClip,
        CompositeVideoClip,
        concatenate_videoclips,
    )
    from moviepy.video.fx.fadein import fadein
    from moviepy.video.fx.fadeout import fadeout
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


VOICE = "zh-CN-XiaoxiaoNeural"
FONT_PATHS = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",
    "C:\\Windows\\Fonts\\simhei.ttf",
]

WIDTH, HEIGHT = 1280, 720
BG_COLOR = (30, 58, 95)
TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (212, 168, 67)


def find_font():
    """查找可用中文字体"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    return None


def generate_speech_text(data):
    """从 JSON 数据生成朗读文本"""
    lines = []
    lines.append(f"AI 新闻周报，{data.get('week', '')}。")
    lines.append(f"日期范围：{data.get('dateRange', '')}。")
    lines.append("")
    for module in data.get("modules", []):
        lines.append(f"{module['name']}。")
        for item in module.get("news", []):
            lines.append(f"{item['title']}。{item['summary']}。")
        lines.append("")
    return "\n".join(lines)


def split_text_to_segments(text, max_len=200):
    """将长文本按句子切分为多个片段"""
    segments = []
    current = ""
    for char in text:
        current += char
        if char in "。！？\n" and len(current) >= 50:
            segments.append(current.strip())
            current = ""
    if current.strip():
        segments.append(current.strip())
    return segments


async def text_to_speech(text, output_path):
    """使用 edge-tts 生成语音"""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)


def create_slide_image(text, font_path, slide_type="content"):
    """生成一张幻灯片图片"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        if slide_type == "title":
            font = ImageFont.truetype(font_path, 48) if font_path else ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, 32) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # 标题装饰线
    draw.rectangle([0, 0, WIDTH, 8], fill=TITLE_COLOR)

    # 文本自动换行
    wrapper = textwrap.TextWrapper(width=30)
    lines = []
    for raw_line in text.split("\n"):
        lines.extend(wrapper.wrap(raw_line) or [""])

    total_height = len(lines) * 50
    y_start = max((HEIGHT - total_height) // 2, 80)

    for i, line in enumerate(lines):
        color = TITLE_COLOR if slide_type == "title" else TEXT_COLOR
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_start + i * 50), line, fill=color, font=font)

    # 底部标注
    try:
        small_font = ImageFont.truetype(font_path, 18) if font_path else ImageFont.load_default()
    except Exception:
        small_font = ImageFont.load_default()
    draw.text((WIDTH - 200, HEIGHT - 40), "AI 新闻周报", fill=(150, 150, 150), font=small_font)

    return img


def build_video(data, output_path, font_path):
    """合成 MP4 视频"""
    segments_text = []
    segments_text.append(f"{data.get('week', '')}\n{data.get('dateRange', '')}")
    for module in data.get("modules", []):
        segments_text.append(module["name"])
        for item in module.get("news", []):
            segments_text.append(f"{item['title']}\n{item['summary'][:80]}...")

    # 生成语音
    full_text = generate_speech_text(data)
    temp_audio = output_path.replace(".mp4", "_temp.mp3")

    print("[INFO] 正在生成语音...")
    asyncio.run(text_to_speech(full_text, temp_audio))

    audio_clip = AudioFileClip(temp_audio)
    total_duration = audio_clip.duration

    # 为每段分配时间
    n_segments = len(segments_text)
    per_seg = total_duration / max(n_segments, 1)

    slides = []
    for i, seg_text in enumerate(segments_text):
        slide_type = "title" if i < 2 else "content"
        img = create_slide_image(seg_text, font_path, slide_type)
        tmp_img_path = output_path.replace(".mp4", f"_slide_{i}.png")
        img.save(tmp_img_path)
        clip = ImageClip(tmp_img_path).set_duration(per_seg)
        clip = fadein(clip, 0.3)
        clip = fadeout(clip, 0.3)
        slides.append(clip)

    video = concatenate_videoclips(slides, method="compose")
    video = video.set_audio(audio_clip)

    print("[INFO] 正在合成视频...")
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )

    # 清理临时文件
    for f in os.listdir(os.path.dirname(output_path)):
        if "_temp." in f or "_slide_" in f:
            try:
                os.remove(os.path.join(os.path.dirname(output_path), f))
            except Exception:
                pass

    print(f"[INFO] 视频已生成: {output_path}")


def main():
    missing = []
    if not HAS_EDGE_TTS:
        missing.append("edge-tts")
    if not HAS_MOVIEPY:
        missing.append("moviepy")
    if not HAS_PIL:
        missing.append("Pillow")
    if missing:
        print(f"[ERROR] 缺少依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "..", "data", "weekly_news.json")
    output_dir = os.path.join(script_dir, "..", "downloads")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ai_news_brief.mp4")

    if not os.path.exists(json_path):
        print(f"[ERROR] 未找到 {json_path}，请先运行 fetch_news.py")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    font_path = find_font()
    print(f"[INFO] 使用字体: {font_path or '系统默认'}")
    build_video(data, output_path, font_path)


if __name__ == "__main__":
    main()
