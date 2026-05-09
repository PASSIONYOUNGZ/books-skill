from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


GENERIC_PHRASES = [
    "本节围绕",
    "主题线索",
    "关键词集中",
    "内容归入",
    "可以帮助读者",
    "有助于我们理解",
    "这一章主要讲了",
    "本章主要讲",
    "从而提升",
    "具有重要意义",
]

METHOD_TERMS = [
    "方法",
    "步骤",
    "模型",
    "练习",
    "清单",
    "框架",
    "操作",
    "流程",
    "判断标准",
    "反馈信号",
    "失败信号",
    "复盘",
]

CASE_TERMS = [
    "案例",
    "例子",
    "情境",
    "场景",
    "对话",
    "脚本",
    "表达",
    "脚本",
    "练习",
    "故事",
    "结果",
]

BOUNDARY_TERMS = [
    "边界",
    "限制",
    "风险",
    "误区",
    "失败",
    "不适用",
    "尊重",
    "自愿",
    "可拒绝",
]

PROCESS_LEAK_TERMS = [
    "OCR 状态",
    "来源统计",
    "哈希",
    "抽取日志",
    "文件路径",
]

ACTION_REVISE = "revise_before_export"
ACTION_AGENT_REVIEW = "agent_self_review"
ACTION_PASS = "pass_with_sampling"


def markdown_dir_for(target: Path) -> Path:
    return target / "markdown" if (target / "markdown").is_dir() else target


def count_terms(text: str, terms: list[str]) -> int:
    return sum(text.count(term) for term in terms)


def normalize_paragraph(paragraph: str) -> str:
    paragraph = re.sub(r"\*\*", "", paragraph)
    paragraph = re.sub(r"\s+", "", paragraph)
    paragraph = re.sub(r"[，。！？；：、“”‘’（）()\[\]【】\-—….,!?;:\"']", "", paragraph)
    return paragraph


def paragraph_stats(text: str) -> tuple[int, int, float, list[str]]:
    raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    normalized = [normalize_paragraph(p) for p in raw_paragraphs]
    normalized = [p for p in normalized if len(p) >= 80]
    counts = Counter(normalized)
    duplicate_items = [(p, c) for p, c in counts.items() if c > 1]
    duplicate_count = sum(c - 1 for _, c in duplicate_items)
    ratio = duplicate_count / max(1, len(normalized))
    samples = [p[:120] for p, _ in duplicate_items[:5]]
    return len(normalized), duplicate_count, ratio, samples


def repeated_subheadings(text: str) -> dict[str, int]:
    headings = re.findall(r"(?m)^###\s+(.+)$", text)
    counts = Counter(h.strip() for h in headings)
    return {heading: count for heading, count in counts.items() if count >= 4}


def audit_markdown(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    char_count = len(text)
    h1_count = len(re.findall(r"(?m)^#\s+", text))
    h2_count = len(re.findall(r"(?m)^##\s+", text))
    h3_count = len(re.findall(r"(?m)^###\s+", text))
    paragraph_count, duplicate_count, duplicate_ratio, duplicate_samples = paragraph_stats(text)

    generic_count = count_terms(text, GENERIC_PHRASES)
    method_count = count_terms(text, METHOD_TERMS)
    case_count = count_terms(text, CASE_TERMS)
    boundary_count = count_terms(text, BOUNDARY_TERMS)
    process_leak_count = count_terms(text, PROCESS_LEAK_TERMS)
    density_base = max(1, char_count / 10000)

    repeated_h3 = repeated_subheadings(text)
    red_flags: list[str] = []
    warnings: list[str] = []

    if char_count < 5000:
        red_flags.append("too_short_under_5000_chars")
    elif char_count < 9000:
        warnings.append("possibly_thin_under_9000_chars")

    if duplicate_ratio >= 0.08 or duplicate_count >= 8:
        red_flags.append("high_duplicate_paragraph_ratio")
    elif duplicate_count >= 3:
        warnings.append("some_duplicate_paragraphs")

    if generic_count >= 12:
        red_flags.append("many_generic_template_phrases")
    elif generic_count >= 5:
        warnings.append("some_generic_template_phrases")

    if method_count / density_base < 6:
        warnings.append("low_method_signal_density")
    if case_count / density_base < 4:
        warnings.append("low_case_or_talktrack_signal_density")
    if boundary_count / density_base < 3:
        warnings.append("low_boundary_signal_density")
    if repeated_h3:
        warnings.append("repeated_subheading_template")
    if process_leak_count:
        red_flags.append("process_or_extraction_terms_present")
    if h1_count != 4:
        red_flags.append("unexpected_h1_count")
    if h2_count < 4:
        warnings.append("low_h2_structure")

    if red_flags:
        recommended_action = ACTION_REVISE
        gate_status = "blocked"
    elif warnings:
        recommended_action = ACTION_AGENT_REVIEW
        gate_status = "review"
    else:
        recommended_action = ACTION_PASS
        gate_status = "pass"

    return {
        "file": path.name,
        "char_count": char_count,
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "paragraphs_checked": paragraph_count,
        "duplicate_paragraph_count": duplicate_count,
        "duplicate_paragraph_ratio": round(duplicate_ratio, 4),
        "duplicate_samples": duplicate_samples,
        "generic_phrase_count": generic_count,
        "method_signal_count": method_count,
        "case_signal_count": case_count,
        "boundary_signal_count": boundary_count,
        "repeated_h3": repeated_h3,
        "red_flags": red_flags,
        "warnings": warnings,
        "gate_status": gate_status,
        "recommended_action": recommended_action,
        "agent_quality_owner": True,
        "needs_manual_review": bool(red_flags or warnings),
        "needs_agent_review": bool(red_flags or warnings),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="Output folder containing markdown/, or a markdown folder")
    parser.add_argument("--write-json", type=Path, default=None)
    args = parser.parse_args()

    markdown_dir = markdown_dir_for(args.target)
    if not markdown_dir.is_dir():
        raise SystemExit(f"Markdown directory not found: {markdown_dir}")

    items = [audit_markdown(path) for path in sorted(markdown_dir.glob("*.md"))]
    red_flag_count = sum(bool(item["red_flags"]) for item in items)
    warning_count = sum(bool(item["warnings"]) for item in items)
    blocked_count = sum(item["gate_status"] == "blocked" for item in items)
    review_count = sum(item["gate_status"] == "review" for item in items)
    pass_count = sum(item["gate_status"] == "pass" for item in items)
    audit = {
        "markdown_dir": str(markdown_dir),
        "file_count": len(items),
        "files_with_red_flags": red_flag_count,
        "files_with_warnings": warning_count,
        "gate_summary": {
            "blocked_revise_before_export": blocked_count,
            "agent_self_review": review_count,
            "pass_with_sampling": pass_count,
        },
        "quality_owner": "agent",
        "items": items,
    }

    write_path = args.write_json
    if write_path is None:
        output_root = args.target if (args.target / "markdown").is_dir() else markdown_dir.parent
        write_path = output_root / "content_quality_audit.json"
    write_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "file_count": audit["file_count"],
        "files_with_red_flags": red_flag_count,
        "files_with_warnings": warning_count,
        "gate_summary": audit["gate_summary"],
        "wrote": str(write_path),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
