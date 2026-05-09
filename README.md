# Books Skill

把 agent 变成书籍整理员。**单本能精读，整批也能处理，输出 Markdown + EPUB。**

Books Skill 不做“目录扩写式摘要”。它会抽取可靠正文、识别坏源、建立内容地图、做质量自检，最后交付可学习、可复查、可归档的读书材料。

**最终产物不是普通 summary，而是接近“替代第一遍精读”的学习材料。**

任何的 agent 都能用；一句话安装。

## 它的价值

很多自动总结会失败在三个地方：

- 只看目录和关键词，没有真正读正文。
- 输出很长，但大部分是原文堆叠、重复段落、模板句和 OCR 噪声。
- 文件生成了，但没有检查内容是否真的能让人学到原书。

Books Skill 的设计目标是避免这些问题。它要求 agent 先抽取可靠文本、建立内容地图，再写学习型整理稿，并在导出前做内容质量审计、自检和排版清理。

## Agent 一句话安装

把下面这句话复制给你的 agent：

```text
请安装 Books Skill：克隆 https://github.com/PASSIONYOUNGZ/books-skill，把仓库里的 books/ 文件夹复制到你当前工具的 skills 目录并保持目录名为 books，然后运行 python books/scripts/check_environment.py 验证；如果你的工具没有 skills 目录，就把 books/SKILL.md 作为项目指令加载，最后告诉我安装路径和使用方式。
```

## 支持单本和批量

### 单本使用

适合处理一本 EPUB、PDF、DOCX、TXT、Markdown 或 HTML 书籍：

- 提取正文。
- 判断是否扫描版或低质量文本。
- 保留原书结构、观点、方法、案例、证据、练习、人物/情节或主题。
- 生成 Markdown 精读整理稿。
- 生成 EPUB。
- 生成自检报告。

### 批量使用

适合处理一个文件夹里的多本书：

- 扫描源文件并生成 `manifest.json`。
- 逐本处理，避免遗漏或重复。
- 每本书有独立 Markdown、EPUB、自检报告。
- 生成 `batch_report.md`，记录 completed、abandoned、excluded、unsupported、failed 等状态。
- 遇到扫描版、依赖缺失、格式不支持或单本失败时，不中断整批任务，记录原因后继续处理其它书。

## 核心功能

- **多格式抽取**：支持 `EPUB`、`PDF`、`DOCX`、`TXT`、`Markdown`、`HTML/XHTML`。
- **扫描 PDF 识别**：PDF 文字层过少时标记为扫描版，避免硬凑低质量总结。
- **结构化输出**：默认输出 Markdown、EPUB、自检报告、抽取文本、manifest 和批处理报告。
- **内容地图**：写作前要求识别章节、主张、方法、案例、证据、练习、重复内容和弱抽取区域。
- **书型自适应**：非虚构、教材、方法书、小说、传记、论文集、Q&A、访谈、参考书、工作手册等采用不同整理策略。
- **质量审计**：检查过短、重复、模板化、方法/案例/边界密度不足等风险。
- **排版清理**：清除目录点线、页码残留、长省略号、广告尾巴和 OCR 噪声。
- **EPUB 导出**：把合格 Markdown 转成可阅读的 EPUB，并保留标题、列表和加粗。
- **最大自治质量控制**：红旗默认返工，警告默认自审，质量优先于数量。

## 输出结构

默认输出到用户指定目录。若用户未指定，skill 会在源目录旁边或内部创建类似这样的目录：

```text
<source-folder>_book_summaries/
|-- markdown/
|-- epub/
|-- self_check/
|-- extracted_text/
|-- manifest.json
`-- batch_report.md
```

每本完成的书通常包括：

- `markdown/<title>.md`：详细精读整理稿。
- `epub/<title>.epub`：由 Markdown 导出的 EPUB。
- `self_check/<title>_self_check.md`：内容、忠实度、结构、排版和 EPUB 自检。
- `extracted_text/<title>.txt`：抽取出的源文本。
- `manifest.json`：源文件清单和处理状态。
- `batch_report.md`：批量处理总报告。

## 项目架构

```text
books-skill/
|-- README.md
|-- .gitignore
`-- books/
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

## 组成说明

### `books/SKILL.md`

主技能说明。它告诉 agent：

- 什么时候使用这个 skill。
- 单本和批量书籍整理的工作流。
- 默认输出结构。
- 必须遵守的质量标准。
- 如何处理扫描版、低质量 OCR、缺依赖、格式不支持和批量异常。

### `books/references/`

详细工作规范，按需读取，避免主 prompt 过长。

- `writing-standards.md`：整理稿写作标准，包括不同书型的展开方式、章节详细度、方法/案例/脚本/故事写法和排版规则。
- `content-quality-workflow.md`：内容地图、学习型整理、密度编辑、反模板化和最终读者测试。
- `self-check.md`：单本自检、批量最终检查、不合格返工标准。
- `tools-and-environment.md`：依赖、抽取原则、OCR 规则和状态词。
- `lessons-learned.md`：通用经验，记录抽取、质量、排版、自治控制和跨环境适配问题。

### `books/scripts/`

可独立运行的 Python 工具。

- `check_environment.py`：检查 Python 和可选依赖。
- `extract_books.py`：扫描源目录，抽取 EPUB/PDF/DOCX/TXT/Markdown/HTML 文本，生成 `manifest.json`。
- `markdown_to_epub.py`：把 Markdown 整理稿转换为 EPUB。
- `audit_outputs.py`：检查 Markdown、EPUB、自检报告是否匹配，并验证 EPUB 基本结构。
- `content_quality_audit.py`：检查整理稿是否过短、重复、模板化或缺少方法/案例/边界信号。

### `books/agents/openai.yaml`

可选的 UI 元数据。某些 agent 平台可用它展示 skill 名称、简短说明和默认提示。

## 关键 Prompt / 指令设计

Books Skill 的价值主要来自这些关键 prompt 规则。

### 1. 质量优先

```text
Content quality is always more important than speed, formatting, or count completion.
```

含义：宁愿少处理几本，也不能交付模板化、空泛、重复或低质量的整理稿。

### 2. 逐本闭环

```text
Process books one by one. Do not move to the next book until the current book has reliable source text, a detailed Markdown summary, an EPUB, a self-check report, and batch status.
```

含义：批量任务不能只追求“全部跑完”。每本书都必须形成闭环。

### 3. 不只看标题

```text
Read the book, not just headings.
```

含义：不能只用目录和章节标题扩写。长书必须抽样阅读开头、章节开头/结尾、中段代表内容和所有识别出的章节标题。

### 4. 先建立内容地图

```text
Build a content map before writing.
```

内容地图包括：

- 原书结构。
- 核心主张。
- 方法、模型、步骤和检查清单。
- 案例、故事、数据、证据和练习。
- 重复内容、广告内容、目录噪声和弱抽取区域。

### 5. 学习型整理，而不是摘要

```text
The output should make a reader feel they learned the author's actual ideas, methods, examples, and reasoning.
```

含义：整理稿的目标不是“告诉读者大概讲什么”，而是让读者真正吸收原书。

### 6. 四段式输出

```markdown
# Source Structure
# Detailed Structured Summary
# Overall Synthesis
# Score
```

这些标题可按用户语言自然翻译，例如中文可写：

```markdown
# 原书结构
# 详细逐章整理
# 全书综合
# 评分
```

### 7. 红旗自动返工

```text
Treat red flags as automatic revision blockers.
```

含义：如果出现过短、重复过高、模板短语多、结构异常、工具痕迹、EPUB 缺失等问题，agent 应自己回读原文并返工，不把质量责任交给用户。

### 8. 扫描版不硬凑

```text
If a PDF is scanned or OCR quality is poor, stop that book, write an abandon note, and do not fabricate a summary.
```

含义：没有可靠正文就不编造总结。

## 安装与使用

### 克隆仓库

```bash
git clone https://github.com/PASSIONYOUNGZ/books-skill.git
cd books-skill
```

### 通用 agent 使用方式

任何支持自定义指令或技能文件的 agent 都可以这样使用：

1. 加载 `books/SKILL.md`。
2. 让 agent 按需读取 `books/references/`。
3. 让 agent 调用 `books/scripts/` 里的脚本完成抽取、导出和审计。

### 兼容本地 skills 目录的工具

如果你的 agent 工具支持本地 skills 目录，可以把 `books/` 文件夹复制进去。

Windows PowerShell 示例：

```powershell
git clone https://github.com/PASSIONYOUNGZ/books-skill.git
Copy-Item -Path ".\books-skill\books" -Destination "<your-agent-skills-dir>" -Recurse -Force
```

macOS / Linux 示例：

```bash
git clone https://github.com/PASSIONYOUNGZ/books-skill.git
cp -R books-skill/books <your-agent-skills-dir>/books
```

## 依赖

基础依赖是 Python 3.10+。按需要安装：

```bash
python -m pip install pymupdf beautifulsoup4 lxml python-docx ebooklib
```

依赖用途：

- `pymupdf`：PDF 文字层抽取、页数检查、扫描版初判。
- `beautifulsoup4`、`lxml`：EPUB/HTML 清理。
- `python-docx`：DOCX 抽取。
- `ebooklib`：可选依赖；脚本主要用 Python 标准库 `zipfile` 解析 EPUB。

检查环境：

```bash
python books/scripts/check_environment.py
```

## 脚本示例

抽取一个文件夹里的书：

```bash
python books/scripts/extract_books.py ./my-books ./my-books_book_summaries --recursive
```

生成 EPUB：

```bash
python books/scripts/markdown_to_epub.py ./my-books_book_summaries/markdown ./my-books_book_summaries/epub
```

内容质量审计：

```bash
python books/scripts/content_quality_audit.py ./my-books_book_summaries
```

输出结构审计：

```bash
python books/scripts/audit_outputs.py ./my-books_book_summaries
```

## 适合谁

- 想批量整理个人电子书库的人。
- 想把专业书、教材、手册整理成可复习笔记的人。
- 想把小说、传记、论文集、访谈集做成结构化读书材料的人。
- 想给自己的 agent 增加“书籍精读整理”能力的人。
- 需要 Markdown + EPUB + 自检报告完整输出的人。

## 设计原则

- **忠实原书**：不编造原书没有的观点、案例或结论。
- **可学习**：读者不打开原书，也能理解核心内容。
- **可复查**：保留抽取文本、manifest、自检和批处理报告。
- **可导出**：Markdown 与 EPUB 都可交付。
- **可迁移**：不绑定特定 agent 工具或本地环境。
- **可自治**：常规质量问题由 agent 自己判断、修复和记录。
