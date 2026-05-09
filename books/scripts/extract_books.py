#!/usr/bin/env python3
"""Extract readable text from a folder of book files and write a manifest."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from html import unescape
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


BOOK_EXTS = {".epub", ".pdf", ".txt", ".md", ".html", ".htm", ".xhtml", ".docx"}
DEFAULT_SKIP_DIR_MARKERS = {
    "整理输出",
    "整理版",
    "book_summaries",
    "summaries",
    "output",
    "outputs",
    "extracted_text",
    "markdown",
    "epub",
    "self_check",
}


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def html_to_text(data: bytes) -> str:
    html = data.decode("utf-8", errors="ignore")
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav"]):
            tag.decompose()
        return clean_text(soup.get_text("\n"))
    except Exception:
        html = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
        html = re.sub(r"(?s)<[^>]+>", "\n", html)
        return clean_text(unescape(html))


def iter_sources(source_dir: Path, recursive: bool) -> Iterable[Path]:
    iterator = source_dir.rglob("*") if recursive else source_dir.iterdir()
    for path in iterator:
        if path.is_dir():
            continue
        dir_parts = {p.lower() for p in path.parent.parts}
        if any(marker.lower() in part for marker in DEFAULT_SKIP_DIR_MARKERS for part in dir_parts):
            continue
        if path.suffix.lower() in BOOK_EXTS:
            yield path


def extract_epub(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        opf_name = None
        if "META-INF/container.xml" in names:
            root = ET.fromstring(zf.read("META-INF/container.xml"))
            ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
            elem = root.find(".//c:rootfile", ns)
            if elem is not None:
                opf_name = elem.attrib.get("full-path")

        ordered = []
        if opf_name and opf_name in names:
            opf_root = ET.fromstring(zf.read(opf_name))
            opf_ns = {"opf": "http://www.idpf.org/2007/opf"}
            manifest = {}
            for item in opf_root.findall(".//opf:item", opf_ns):
                href = item.attrib.get("href")
                item_id = item.attrib.get("id")
                media = item.attrib.get("media-type", "")
                if item_id and href and "html" in media:
                    base = str(Path(opf_name).parent).replace("\\", "/")
                    full = f"{base}/{href}" if base != "." else href
                    manifest[item_id] = full.replace("\\", "/")
            for itemref in opf_root.findall(".//opf:itemref", opf_ns):
                href = manifest.get(itemref.attrib.get("idref", ""))
                if href and href in names:
                    ordered.append(href)

        if not ordered:
            ordered = [
                n
                for n in names
                if n.lower().endswith((".html", ".htm", ".xhtml"))
                and "cover" not in n.lower()
            ]
            ordered.sort()

        parts = []
        for name in ordered:
            text = html_to_text(zf.read(name))
            if text:
                parts.append(f"===== {name} =====\n{text}")
        return clean_text("\n\n".join(parts))


def extract_pdf(path: Path, min_page_chars: int, scanned_ratio: float) -> tuple[str, bool, str]:
    try:
        import fitz
    except Exception as exc:
        return "", False, f"PyMuPDF not available: {exc}"

    doc = fitz.open(path)
    page_texts = []
    low_text_pages = 0
    for page in doc:
        text = page.get_text("text") or ""
        text = clean_text(text)
        if len(text) < min_page_chars:
            low_text_pages += 1
        page_texts.append(f"===== page {page.number + 1} =====\n{text}")
    if doc.page_count and low_text_pages / doc.page_count >= scanned_ratio:
        return "", True, f"likely scanned PDF: {low_text_pages}/{doc.page_count} low-text pages"
    return clean_text("\n\n".join(page_texts)), False, ""


def extract_docx(path: Path) -> str:
    import docx

    doc = docx.Document(path)
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    return clean_text("\n".join(parts))


def extract_plain(path: Path) -> str:
    if path.suffix.lower() in {".html", ".htm", ".xhtml"}:
        return html_to_text(path.read_bytes())
    return clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def safe_stem(index: int, path: Path) -> str:
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", path.stem).strip()
    return f"{index:03d}_{stem or 'book'}.txt"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--exclude", action="append", default=[], help="Substring to exclude; repeatable")
    parser.add_argument("--min-pdf-page-chars", type=int, default=30)
    parser.add_argument("--scanned-ratio", type=float, default=0.6)
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()
    text_dir = output_dir / "extracted_text"
    text_dir.mkdir(parents=True, exist_ok=True)

    items = []
    sources = sorted(iter_sources(source_dir, args.recursive), key=lambda p: p.name.lower())
    for index, path in enumerate(sources, start=1):
        rel = path.resolve()
        title = path.stem
        entry = {
            "index": index,
            "title": title,
            "source_path": str(rel),
            "format": path.suffix.lower().lstrip("."),
            "status": "pending",
            "reason": "",
            "text_path": None,
            "char_count": 0,
        }
        if any(token.lower() in path.name.lower() for token in args.exclude):
            entry["status"] = "excluded"
            entry["reason"] = "matched exclude rule"
            items.append(entry)
            continue

        try:
            suffix = path.suffix.lower()
            scanned = False
            reason = ""
            if suffix == ".epub":
                text = extract_epub(path)
            elif suffix == ".pdf":
                text, scanned, reason = extract_pdf(
                    path, args.min_pdf_page_chars, args.scanned_ratio
                )
            elif suffix == ".docx":
                text = extract_docx(path)
            elif suffix in {".txt", ".md", ".html", ".htm", ".xhtml"}:
                text = extract_plain(path)
            else:
                text = ""
                reason = "unsupported file type"

            if scanned:
                entry["status"] = "abandoned_scanned"
                entry["reason"] = reason
            elif not text:
                entry["status"] = "failed"
                entry["reason"] = reason or "no text extracted"
            else:
                out_path = text_dir / safe_stem(index, path)
                out_path.write_text(text, encoding="utf-8")
                entry["status"] = "extracted"
                entry["text_path"] = str(out_path)
                entry["char_count"] = len(text)
        except Exception as exc:
            entry["status"] = "failed"
            entry["reason"] = f"{type(exc).__name__}: {exc}"
        items.append(entry)

    manifest = {"source_dir": str(source_dir), "output_dir": str(output_dir), "items": items}
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
