#!/usr/bin/env python3
"""Report optional dependencies for the book batch summarizer skill."""

from __future__ import annotations

import importlib.util
import json
import sys


PACKAGES = {
    "fitz": "pymupdf",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "docx": "python-docx",
    "ebooklib": "ebooklib",
}


def main() -> int:
    results = {}
    missing = []
    for module, package in PACKAGES.items():
        ok = importlib.util.find_spec(module) is not None
        results[module] = {"package": package, "available": ok}
        if not ok:
            missing.append(package)

    payload = {
        "python": sys.version,
        "dependencies": results,
        "missing_packages": missing,
        "suggested_install": (
            f"{sys.executable} -m pip install " + " ".join(missing)
            if missing
            else None
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
