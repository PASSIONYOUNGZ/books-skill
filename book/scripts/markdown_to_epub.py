#!/usr/bin/env python3
"""Convert Markdown summaries to simple EPUB files."""

from __future__ import annotations

import argparse
import html
import re
import uuid
import zipfile
from pathlib import Path


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def markdown_body(markdown: str) -> str:
    body = []
    in_ul = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            if in_ul:
                body.append("</ul>")
                in_ul = False
            continue
        if line.startswith("# "):
            if in_ul:
                body.append("</ul>")
                in_ul = False
            body.append(f"<h1>{inline_markup(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            if in_ul:
                body.append("</ul>")
                in_ul = False
            body.append(f"<h2>{inline_markup(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            if in_ul:
                body.append("</ul>")
                in_ul = False
            body.append(f"<h3>{inline_markup(line[4:].strip())}</h3>")
        elif line.startswith("- "):
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            body.append(f"<li>{inline_markup(line[2:].strip())}</li>")
        else:
            if in_ul:
                body.append("</ul>")
                in_ul = False
            body.append(f"<p>{inline_markup(line.strip())}</p>")
    if in_ul:
        body.append("</ul>")
    return "\n".join(body)


def write_epub(md_path: Path, epub_path: Path) -> None:
    title = md_path.stem
    uid = str(uuid.uuid4())
    body = markdown_body(md_path.read_text(encoding="utf-8"))
    chapter = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">'
        f"<head><title>{html.escape(title)}</title>"
        '<link rel="stylesheet" type="text/css" href="style.css" /></head>'
        f"<body>{body}</body></html>"
    )
    nav = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN">'
        "<head><title>目录</title></head><body>"
        '<nav epub:type="toc" id="toc"><h1>目录</h1><ol>'
        f'<li><a href="chapter.xhtml">{html.escape(title)}</a></li>'
        "</ol></nav></body></html>"
    )
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="BookId" xml:lang="zh-CN">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:identifier id="BookId">urn:uuid:{uid}</dc:identifier>'
        f"<dc:title>{html.escape(title)}</dc:title>"
        "<dc:language>zh-CN</dc:language></metadata><manifest>"
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        '<item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>'
        '<item id="css" href="style.css" media-type="text/css"/>'
        '</manifest><spine><itemref idref="chapter"/></spine></package>'
    )
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="EPUB/content.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    css = (
        "body{font-family:serif;line-height:1.75;margin:5%;}"
        "h1,h2,h3{line-height:1.35;}p{margin:0.75em 0;}"
        "li{margin:0.35em 0;}strong{font-weight:700;}"
    )
    epub_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(epub_path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("EPUB/content.opf", opf)
        zf.writestr("EPUB/nav.xhtml", nav)
        zf.writestr("EPUB/chapter.xhtml", chapter)
        zf.writestr("EPUB/style.css", css)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown_dir", type=Path)
    parser.add_argument("epub_dir", type=Path)
    parser.add_argument("--pattern", default="*.md")
    args = parser.parse_args()

    for md_path in sorted(args.markdown_dir.glob(args.pattern), key=lambda p: p.name):
        epub_path = args.epub_dir / (md_path.stem + ".epub")
        write_epub(md_path, epub_path)
        print(f"{epub_path}\t{epub_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
