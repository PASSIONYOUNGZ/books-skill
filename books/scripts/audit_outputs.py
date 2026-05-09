#!/usr/bin/env python3
"""Audit book-summary Markdown, EPUB, and self-check outputs."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path


FORBIDDEN = [
    "主题线索",
    "来源统计",
    "本节围绕",
    "OCR 状态",
    "原始文件名",
    "SHA256",
    "Table of Contents",
]


def check_epub(path: Path, markdown_has_bold: bool) -> dict:
    result = {
        "exists": path.exists(),
        "structure_ok": False,
        "bold_ok": False,
        "error": "",
    }
    if not path.exists():
        return result
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            chapter = zf.read("EPUB/chapter.xhtml").decode("utf-8")
        required = {"mimetype", "EPUB/nav.xhtml", "EPUB/chapter.xhtml", "EPUB/content.opf"}
        result["structure_ok"] = required.issubset(set(names))
        result["bold_ok"] = ("**" not in chapter) and (("<strong>" in chapter) == markdown_has_bold)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def audit(output_dir: Path) -> dict:
    markdown_dir = output_dir / "markdown"
    epub_dir = output_dir / "epub"
    self_dir = output_dir / "self_check"
    items = []
    for md_path in sorted(markdown_dir.glob("*.md"), key=lambda p: p.name):
        text = md_path.read_text(encoding="utf-8")
        h1 = re.findall(r"^# (.+)$", text, re.M)
        bad = [word for word in FORBIDDEN if word in text]
        bold_count = text.count("**") // 2
        epub = check_epub(epub_dir / (md_path.stem + ".epub"), bold_count > 0)
        self_exists = any(
            p.stem.startswith(md_path.stem.replace("_详细整理总结", ""))
            for p in self_dir.glob("*.md")
        )
        ok = len(h1) == 4 and not bad and epub["structure_ok"] and epub["bold_ok"]
        items.append(
            {
                "title": md_path.stem,
                "markdown": str(md_path),
                "char_count": len(text),
                "h1_count": len(h1),
                "h2_count": len(re.findall(r"^## ", text, re.M)),
                "bold_count": bold_count,
                "forbidden": bad,
                "epub": epub,
                "self_check_exists": self_exists,
                "ok": ok,
            }
        )
    return {
        "output_dir": str(output_dir),
        "markdown_count": len(list(markdown_dir.glob("*.md"))) if markdown_dir.exists() else 0,
        "epub_count": len(list(epub_dir.glob("*.epub"))) if epub_dir.exists() else 0,
        "self_check_count": len(list(self_dir.glob("*.md"))) if self_dir.exists() else 0,
        "items": items,
        "all_ok": all(item["ok"] for item in items),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--write-json", type=Path)
    args = parser.parse_args()

    result = audit(args.output_dir.resolve())
    if args.write_json:
        args.write_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
