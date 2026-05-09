---
name: book
description: Universal high-quality single-book and batch-book summarization workflow for EPUB, PDF, DOCX, TXT, Markdown, HTML, and similar book sources. Use when Codex must adapt to the user's language, environment, file formats, book genre, and requested output; extract reliable text; detect scanned or low-quality sources; produce detailed Markdown and EPUB study summaries; run strict self-checks; maintain no-omission/no-duplicate status; and deliver a complete workflow report.
---

# Book

## Purpose

Use this skill to turn one book or a folder of books into high-quality, readable, self-checked study summaries. The workflow covers environment checks, text extraction, scanned-PDF handling, book-type-aware writing, Markdown/EPUB export, self-check, retry, and final completeness reporting.

Adapt to the user's context instead of assuming a local project:

- Use the user's requested language; if unspecified, use the source book's primary language.
- Use the user's requested output folder; if unspecified, create an output folder beside or inside the source path, choosing the least surprising writable location.
- Use available tools first. If optional dependencies, network, OCR engines, or write permissions are missing, use a reasonable fallback, request approval only when required by the active environment, and document unresolved limits.
- Adjust the structure to the book type: nonfiction, textbook, manual, fiction, anthology, essay collection, Q&A collection, transcript, reference work, workbook, or mixed material.
- For sensitive or high-impact material, preserve the author's claims while adding clear limits, uncertainty, and ethical/safety boundaries.

## Core Rule

Process books one by one. Do not move to the next book until the current book has:

1. reliable source text or a documented abandon reason;
2. a detailed Markdown summary that can teach the book's core knowledge without requiring the reader to open the source;
3. an EPUB generated from that Markdown;
4. a self-check report marked qualified;
5. status recorded in the batch report.

If a PDF is scanned or OCR quality is poor, stop that book, write an abandon note, and do not fabricate a summary.

Content quality is always more important than speed, formatting, or count completion. A summary that only lists keywords, gives a few generic sentences per chapter, or repeats a template is a failed output even if the audit script passes.

Use maximum autonomous quality control. Do not hand quality, ordering, rewrite, compression, expansion, prioritization, or exception-handling decisions back to the user when any responsible path exists. Red flags, warnings, repetition, thin chapters, formatting problems, source defects, missing files, dependency gaps, and quality-vs-quantity tradeoffs should be diagnosed and handled by the agent. If quality conflicts with speed or completion count, choose quality and document the tradeoff. If a hard blocker appears, do not interrupt the workflow by default: choose a fallback, mark the item blocked/abandoned with a reason, continue with other books, and report it at the end.

## Folder Layout

Create this structure under the user-requested output folder. If the user does not specify an output folder and the source is a folder, create the output folder inside the source folder and name it `<source-folder-name>_book_summaries`.

```text
output-folder/
|-- markdown/
|-- epub/
|-- self_check/
|-- extracted_text/
|-- manifest.json
`-- batch_report.md
```

Use stable book titles in filenames. Avoid duplicate outputs for the same source.

## Workflow

1. **Clarify scope only if needed.** Determine source folder/files, exclusions, output folder, and desired ordering. If not specified, use filesystem order and an output folder named `<source-folder-name>_book_summaries` inside the source folder.
2. **Check environment.** Run `scripts/check_environment.py`. If extraction needs missing packages, install or request approval as required by the active environment.
3. **Extract source text.** Run `scripts/extract_books.py`. Review `manifest.json`; do not summarize sources marked scanned, failed, or unsupported. Verify source count against the folder count, especially EPUB files.
4. **Read the book, not just headings.** For each book, inspect the extracted text deeply enough to understand its real structure, arguments, examples, exercises, dialogue/script sections, warnings, and special sections. For long books, read beginning, chapter openings, chapter endings, representative middle sections, and all detected chapter titles before writing.
5. **Build a content map before writing.** Follow `references/content-quality-workflow.md`. Identify the book's real claims, methods, examples, exercises, repeated parts, weak extraction zones, and chapter-to-chapter progression before drafting. The content map may stay internal, but the final summary must reflect it.
6. **Write one detailed Markdown summary.** Follow `references/writing-standards.md`. Preserve the book's own structure where possible; for anthologies or Q&A collections, rebuild a truthful structure by content clusters. The output should make a reader feel they learned the author's actual ideas, methods, examples, and reasoning.
7. **Edit for density and non-repetition.** After drafting, do a second pass: remove duplicated explanations, collapse repeated source fragments, cut empty transition sentences, and fill missing method/case/boundary details. A long but repetitive summary is not qualified; a short but under-explained summary is not qualified either.
8. **Self-check before export.** Use `references/self-check.md`. If content is thin, generic, template-like, keyword-based, poorly formatted, repetitive, or misses important chapters, revise before generating EPUB.
9. **Run content quality audit.** Run `scripts/content_quality_audit.py` on the Markdown folder or output folder. Treat red flags as automatic revision blockers. Treat warnings as prompts for agent self-review against source text; resolve or document them before export. Do not ask the user to decide audit outcomes; decide, revise, skip, or document internally.
10. **Polish typography and emphasis.** Before EPUB export, remove OCR/table-of-contents artifacts such as long dot leaders, repeated ellipses, repeated underscores/dashes, advertisement tails, and stray control characters. Add moderate bold emphasis to core concepts, model names, key methods, and decisive cautions so the Markdown has visible reading focus.
11. **Generate EPUB.** Run `scripts/markdown_to_epub.py` after the Markdown is qualified enough to export.
12. **Audit outputs.** Run `scripts/audit_outputs.py`; fix failures before continuing.
13. **Write self-check report.** Put a per-book report in `self_check/`. It must state qualified or abandoned and explain content quality, fidelity, structure, typography, EPUB, and remaining risks.
14. **Write batch report.** After all books are handled, list every source once with status: completed, abandoned, excluded, or unsupported.

## Required Markdown Shape

Each completed book summary should normally contain exactly these four top-level sections:

```markdown
# Source Structure
# Detailed Structured Summary
# Overall Synthesis
# Score
```

Translate these section names naturally when the user or source language is not English.

## Quality Bar

- Put content first. Do not output extraction logs, file hashes, OCR notes, or process metadata inside the book summary.
- Do not use generic filler such as "this section revolves around..." or keyword-statistics style summaries.
- Do not write a chapter as a few keywords plus a fixed sentence. Each major chapter/content group must explain the author's point, why it matters, how the method works, what examples or exercises show, and where the limits are.
- The reader should be able to absorb the book's main knowledge, viewpoint, and practical methods from the summary alone. If the output would not help someone learn without opening the source, it is not qualified.
- Balance depth and density. Do not pad with repetitive paragraphs, and do not compress important chapters into bare conclusions. Every paragraph should either explain a claim, teach a method, unpack a case, define a concept, warn about a boundary, or connect the structure.
- For methods, procedures, examples, exercises, and dialogue scripts, preserve the operating logic: goal, context, steps, feedback signals, failure modes, and ethical/practical boundaries.
- For examples and cases, preserve the learning mechanism: situation, action, response/result, and what the author wants the reader to learn from it.
- Use moderate Markdown emphasis for core concepts, key methods, and decisive sentences; do not bold whole paragraphs.
- Make the Markdown visually learnable: important frameworks, method names, warnings, and section labels should be easy to scan through bold text and clear subheadings.
- Remove long punctuation runs from extracted text. Lines or fragments such as `………………………………………………………………………`, `....................`, `__________`, and repeated dash rules are extraction noise unless the original meaning depends on them. Collapse ordinary conversational pauses to `……` at most.
- Lists are for steps, exercises, frameworks, examples, and checks. Main explanations should remain readable prose.
- Preserve concrete methods, cases, arguments, exercises, warnings, examples, and follow-up actions.
- For scanned PDFs or poor OCR, abandon with a clear note instead of forcing a low-quality summary.

## Lessons Learned

- EPUB files can be accidentally skipped if output-directory markers such as `epub` are matched against file names instead of directory parts. Source-count verification is mandatory after extraction.
- A structural audit can pass while the content is still bad. Run a content audit for specificity, fidelity, non-template language, and usefulness before exporting.
- Heuristic keyword aggregation is not an acceptable substitute for reading. It may help locate topics, but the final Markdown must be written from the book's actual arguments, examples, and methods.
- Long does not mean deep. Repeated paragraphs, copied source fragments, and reusable section templates can make an output bulky while still failing to teach the book.
- Short does not mean concise when important methods, cases, and boundaries are missing. If a chapter is short, verify whether the source is genuinely thin or the reading pass missed material.
- Avoid workflow interruption. The agent owns quality triage, reasonable tradeoffs, and exception handling: revise red-flagged files, inspect warning files, compare against extracted text, reduce batch scope if needed for quality, skip unrecoverable items with clear abandon notes, and continue the batch. Report unresolved blockers after the work, not mid-work.
- Default output should be easy to find beside the source material. For folder batches, put `<source-folder-name>_book_summaries` inside the source folder unless the user says otherwise.
- OCR and PDF table-of-contents extraction often preserve page leaders as long strings of dots, ellipses, underscores, or dashes. These make Markdown and EPUB look unfinished. Always run a typography pass before export and verify no long punctuation runs remain.
- A readable Markdown file needs focus markers, not only headings. If core concepts and method names are not bolded at all, readers cannot scan the file efficiently even when the content is detailed.

## Bundled Resources

- `scripts/check_environment.py`: report optional dependencies and suggested install command.
- `scripts/extract_books.py`: scan source folder, extract text, detect scanned PDFs, and write `manifest.json`.
- `scripts/markdown_to_epub.py`: convert Markdown summaries to simple EPUB files while preserving headings, lists, and bold text.
- `scripts/audit_outputs.py`: check Markdown/EPUB/self-check output consistency and common quality failures.
- `scripts/content_quality_audit.py`: flag possible thin, repetitive, template-like, or low-method/case-density Markdown files, assign an action gate, and guide agent self-revision before export.
- `references/tools-and-environment.md`: dependency setup and extraction tool notes.
- `references/writing-standards.md`: high-quality summary writing rules.
- `references/content-quality-workflow.md`: content mapping, learning-oriented writing, and density editing workflow.
- `references/self-check.md`: strict self-check and retry criteria.
- `references/lessons-learned.md`: known workflow failures and corrections.
