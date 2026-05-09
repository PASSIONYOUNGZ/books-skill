# 工具与环境

## 推荐环境

- Windows PowerShell 或 POSIX shell。
- Python 3.10+。
- 按需使用这些 Python 包：
  - `pymupdf`：PDF 文字层抽取、页数检查、扫描版初判。
  - `beautifulsoup4`、`lxml`：EPUB/HTML 清理。
  - `python-docx`：DOCX 抽取。
  - `ebooklib`：可选；脚本主要用 `zipfile` 解析 EPUB。

建议安装命令：

```bash
python -m pip install pymupdf beautifulsoup4 lxml python-docx ebooklib
```

## 抽取原则

- EPUB：优先按 OPF spine 顺序抽取；没有 spine 时按 HTML/XHTML 文件顺序兜底。
- PDF：先检查文字层。大部分页面文字极少时，标记为扫描版；除非用户明确要求 OCR 且 OCR 质量可接受，否则放弃。
- DOCX/TXT/HTML/Markdown：直接抽取可读文本。
- 不要把目录页、版权页、广告页、重复 TOC 当作正文替代。

## OCR 规则

只有同时满足以下条件才考虑 OCR：

- OCR 引擎和语言数据已安装。
- 渲染和识别速度可接受。
- 抽样页能产生连续、可读、噪声少的文本。
- 用户明确要求 OCR，或当前任务规则允许 OCR。

如果 OCR 不可用、过慢、噪声大、连续失败，直接写扫描版放弃说明，不硬凑整理。

## 状态词

- `completed`：Markdown、EPUB、自检都已完成。
- `abandoned_scanned`：扫描版或 OCR 质量差，未生成伪整理。
- `excluded`：用户要求排除。
- `unsupported`：当前流程暂不支持的格式。
- `failed`：抽取或生成失败，需要人工处理。
