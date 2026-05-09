# Codex Book Skill

一个通用的 Codex 书籍整理 skill，用于把单本书或一整个文件夹的书籍资料整理成可学习、可复查、可导出的 Markdown 与 EPUB。

它不是普通摘要模板。这个 skill 的目标是让读者在不打开原书的情况下，尽可能吸收原书的结构、观点、方法、案例、证据、练习、叙事脉络和限制。

## 功能特色

- 支持常见书籍格式：`EPUB`、`PDF`、`DOCX`、`TXT`、`Markdown`、`HTML/XHTML`。
- 自动抽取正文并生成 `manifest.json`，记录每本书的来源、状态、文本路径和字数。
- 识别扫描版或低质量文字层 PDF，避免用不可读文本硬凑总结。
- 按书籍类型自适应整理：非虚构、教材、方法书、小说、传记、论文集、Q&A、访谈、参考书、工作手册等。
- 输出详细 Markdown、EPUB、自检报告和批处理报告。
- 内置质量审计脚本，检查过短、重复、模板化、方法/案例/边界密度不足等问题。
- 强调内容质量：要求先读书、建立内容地图、再写学习型整理稿。
- 支持跨环境使用：不绑定固定用户名、目录、操作系统或本地项目。

## 适合场景

- “帮我整理这本 EPUB/PDF。”
- “把这个文件夹里的书逐本整理成 Markdown 和 EPUB。”
- “这本书很长，帮我做成可学习的精读笔记。”
- “这批资料有 PDF、EPUB、DOCX，帮我抽取正文、总结并自检。”
- “保留原书结构、方法、案例和限制，不要只给关键词摘要。”

## 安装

把仓库里的 `book/` 文件夹复制到 Codex 的 skills 目录。

Windows PowerShell：

```powershell
git clone https://github.com/vsunsky567-droid/codex-book-skill.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Path ".\codex-book-skill\book" -Destination "$env:USERPROFILE\.codex\skills" -Recurse -Force
```

macOS / Linux：

```bash
git clone https://github.com/vsunsky567-droid/codex-book-skill.git
mkdir -p ~/.codex/skills
cp -R codex-book-skill/book ~/.codex/skills/book
```

重启或刷新 Codex 后，就可以用 `$book` 触发这个 skill。

## 依赖

基础依赖是 Python 3.10+。按需要安装以下包：

```bash
python -m pip install pymupdf beautifulsoup4 lxml python-docx ebooklib
```

其中：

- `pymupdf` 用于 PDF 文字层抽取和扫描版初判。
- `beautifulsoup4`、`lxml` 用于 EPUB/HTML 清理。
- `python-docx` 用于 DOCX 抽取。
- `ebooklib` 是可选依赖，脚本主要使用 Python 标准库 `zipfile` 处理 EPUB。

可以运行：

```bash
python book/scripts/check_environment.py
```

查看当前环境缺少哪些依赖。

## 输出结构

默认输出到用户指定目录；如果用户未指定输出目录，skill 会在源文件夹旁边或内部创建一个容易找到的输出目录，例如：

```text
<source-folder>_book_summaries/
|-- markdown/
|-- epub/
|-- self_check/
|-- extracted_text/
|-- manifest.json
`-- batch_report.md
```

每本完成的书通常会有：

- 一份 Markdown 精读整理稿。
- 一份 EPUB。
- 一份自检报告。
- 批处理报告中的一条状态记录。

## 工作流

1. 确认处理范围、排除项、输出目录和排序方式。
2. 检查环境和依赖。
3. 抽取源文本，生成 `manifest.json`。
4. 逐本阅读正文，而不是只看目录或标题。
5. 建立内容地图：章节、主张、方法、案例、证据、练习、重复内容、弱抽取区域。
6. 写详细 Markdown 整理稿。
7. 做密度编辑：去重复、删空话、补方法/案例/限制。
8. 运行内容质量审计。
9. 清理排版噪声并加入适度重点加粗。
10. 生成 EPUB。
11. 运行输出审计。
12. 写自检报告和批处理报告。

## 质量标准

合格整理稿必须做到：

- 覆盖原书主要结构和内容群。
- 讲清作者观点、论证、方法、案例、练习、限制和递进关系。
- 不用关键词列表替代阅读。
- 不用模板化句子填充章节。
- 不把目录、网页导航、OCR 噪声或抽取日志写进正文。
- 对高风险或高影响内容保留作者观点，同时标明证据强度、限制和误用风险。
- 对小说、传记、叙事非虚构保留人物、冲突、关键场景、叙事节奏和主题。

## 项目结构

```text
codex-book-skill/
|-- README.md
|-- .gitignore
`-- book/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- references/
    |   |-- content-quality-workflow.md
    |   |-- lessons-learned.md
    |   |-- self-check.md
    |   |-- tools-and-environment.md
    |   `-- writing-standards.md
    `-- scripts/
        |-- audit_outputs.py
        |-- check_environment.py
        |-- content_quality_audit.py
        |-- extract_books.py
        `-- markdown_to_epub.py
```

## 验证

如果你本地有 Codex 的 `skill-creator` 校验脚本，可以运行：

```bash
python path/to/skill-creator/scripts/quick_validate.py book
```

本仓库中的 `book` skill 已按 Codex skill 结构组织，包含必需的 `SKILL.md` frontmatter、脚本和参考资料。

