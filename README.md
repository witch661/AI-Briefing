# News - AI 新闻简报系统

全自动 AI 新闻抓取、分类、简报生成与播报系统。从多个 RSS 订阅源抓取 AI 相关新闻，按模块和重要性整理成精美 PDF 简报，支持 AI 朗读视频生成和网页浏览。

## 项目结构

```
Catch/
├── index.html              # 主页面（含新闻展示、下载链接、TTS朗读）
├── styles.css              # 蓝粉渐变玻璃拟态样式
├── script.js               # 客户端 JavaScript
├── data/
│   └── weekly_news.json    # 新闻数据（自动生成/更新）
├── downloads/              # 生成的 PDF 和 MP4
├── scripts/
│   ├── fetch_news.py       # RSS 新闻抓取
│   ├── generate_pdf.py     # PDF 简报生成
│   └── generate_video.py   # AI 朗读视频生成
├── .github/workflows/
│   └── weekly.yml          # GitHub Actions 自动化
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 本地预览网页

```bash
cd Catch
python -m http.server 8080
```

浏览器打开 `http://localhost:8080`

### 2. 命令行生成简报

```bash
pip install -r requirements.txt

# 抓取新闻
python scripts/fetch_news.py

# 生成 PDF
python scripts/generate_pdf.py

# 生成视频
python scripts/generate_video.py
```

## 功能说明

### 网页浏览

- 自动加载 `weekly_news.json` 并按模块分类展示
- 支持 PDF 打印下载（点击"下载 PDF 简报"）
- 支持 MP4 视频下载（点击"下载朗读视频"）
- 支持浏览器 TTS 语音朗读（点击"朗读简报"）

### 模块分类

| 模块 | 说明 |
|------|------|
| 政声传递 | 政府政策、法规、顶层设计、部委动态 |
| 他山之石 | 外地区/城市经验、试点示范、区域发展 |
| 产业动态 | 企业产品发布、技术突破、市场融资、行业会议 |
| 综合关注 | 其他 AI 相关新闻 |

### 重要性评级

- **高**（红色）：突破、重大、里程碑、首个、开源、重磅等
- **中**（橙色）：默认级别
- **低**（灰色）：融资、人事变动、合作签约等

### 数据源

- Ars Technica
- AI News
- MIT Technology Review
- VentureBeat
- Unite.AI
- 爱范儿
- 品玩

## 自动化

GitHub Actions 每周一 08:00 UTC 自动运行：

1. 从 RSS 源抓取本周新闻
2. 生成 PDF 简报
3. 生成 AI 朗读视频
4. 提交到仓库

可在 Actions 页面手动触发。

## 自定义配置

### 修改 RSS 源

编辑 `scripts/fetch_news.py` 中的 `RSS_SOURCES` 列表。

### 修改模块关键词

编辑 `scripts/fetch_news.py` 中的 `MODULE_KEYWORDS` 字典。

### 修改重要性关键词

编辑 `scripts/fetch_news.py` 中的 `HIGH_KEYWORDS` 和 `LOW_KEYWORDS` 列表。

## License

MIT License
