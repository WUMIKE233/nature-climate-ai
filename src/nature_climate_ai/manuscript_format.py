from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .claim_gate import inspect_manuscript


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


@dataclass(frozen=True)
class JournalFormatLimits:
    journal: str
    summary_heading: str
    summary_max_words: int
    main_text_min_words: int
    main_text_max_words: int
    display_min: int
    display_max: int
    reference_max: int


@dataclass(frozen=True)
class ManuscriptFormatReport:
    manuscript: Path
    journal: str
    status: str
    summary_words: int
    main_text_words: int
    methods_words: int
    display_items: int
    references: int
    required_sections_present: tuple[str, ...]
    missing_sections: tuple[str, ...]
    issues: tuple[str, ...]


NATURE_LIMITS = JournalFormatLimits(
    journal="nature",
    summary_heading="Summary",
    summary_max_words=220,
    main_text_min_words=2500,
    main_text_max_words=4300,
    display_min=4,
    display_max=6,
    reference_max=50,
)

SCIENCE_FALLBACK_LIMITS = JournalFormatLimits(
    journal="science",
    summary_heading="Abstract",
    summary_max_words=250,
    main_text_min_words=2500,
    main_text_max_words=5000,
    display_min=3,
    display_max=6,
    reference_max=50,
)

LIMITS = {
    "nature": NATURE_LIMITS,
    "science": SCIENCE_FALLBACK_LIMITS,
}


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def _section(text: str, heading: str, next_headings: tuple[str, ...]) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_positions: list[int] = []
    for next_heading in next_headings:
        next_match = re.search(rf"^## {re.escape(next_heading)}\s*$", text[start:], flags=re.MULTILINE)
        if next_match:
            next_positions.append(start + next_match.start())
    end = min(next_positions) if next_positions else len(text)
    return text[start:end].strip()


def _subsection(text: str, heading: str, next_markdown_heading: str = "## ") -> str:
    pattern = rf"^### {re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(rf"^{re.escape(next_markdown_heading)}", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _main_text_without_methods(text: str) -> str:
    main = _section(text, "Main text", ("Figure legends", "Data availability", "Code availability"))
    if not main:
        main = "\n\n".join(
            section
            for section in (
                _section(text, "Introduction", ("Results", "Discussion", "Materials and methods", "References")),
                _section(text, "Results", ("Discussion", "Materials and methods", "References")),
                _section(text, "Discussion", ("Materials and methods", "References")),
            )
            if section
        )
    methods_match = re.search(r"^### Methods\s*$", main, flags=re.MULTILINE)
    if methods_match:
        return main[: methods_match.start()].strip()
    return main


def _count_display_items(text: str) -> int:
    figure_labels = set(re.findall(r"\bFigure\s+(\d+)\b", text))
    table_labels = set(re.findall(r"\bTable\s+(\d+)\b", text))
    return len(figure_labels) + len(table_labels)


def _count_references(text: str) -> int:
    references = _section(text, "References", ())
    if not references:
        references = _section(text, "References to verify before submission", ())
    return len(re.findall(r"^\s*\d+\.\s+", references, flags=re.MULTILINE))


def audit_manuscript_format(path: str | Path, journal: str = "nature") -> ManuscriptFormatReport:
    journal_key = journal.lower()
    if journal_key not in LIMITS:
        raise ValueError(f"Unsupported journal target: {journal}")
    limits = LIMITS[journal_key]
    manuscript = Path(path)
    text = manuscript.read_text(encoding="utf-8")
    claim_report = inspect_manuscript(manuscript)

    summary = _section(text, limits.summary_heading, ("Main text", "Introduction", "Results", "Materials and methods"))
    main_text = _main_text_without_methods(text)
    methods = _subsection(text, "Methods")
    if not methods:
        methods = _section(text, "Materials and methods", ("References",))

    required = (
        limits.summary_heading,
        "Data availability",
        "Code availability",
        "Acknowledgements",
        "Author contributions",
        "Competing interests",
    )
    present = tuple(section for section in required if _section(text, section, ()))
    missing = tuple(section for section in required if section not in present)

    summary_words = count_words(summary)
    main_words = count_words(main_text)
    methods_words = count_words(methods)
    display_items = _count_display_items(text)
    references = _count_references(text)

    issues: list[str] = []
    if summary_words == 0:
        issues.append(f"Missing {limits.summary_heading} section.")
    elif summary_words > limits.summary_max_words:
        issues.append(f"{limits.summary_heading} is {summary_words} words; limit is {limits.summary_max_words}.")
    if main_words < limits.main_text_min_words:
        issues.append(f"Main text is {main_words} words; target minimum is {limits.main_text_min_words}.")
    if main_words > limits.main_text_max_words:
        issues.append(f"Main text is {main_words} words; target maximum is {limits.main_text_max_words}.")
    if display_items < limits.display_min or display_items > limits.display_max:
        issues.append(f"Display items count is {display_items}; target range is {limits.display_min}-{limits.display_max}.")
    if references > limits.reference_max:
        issues.append(f"Reference count is {references}; target maximum is {limits.reference_max}.")
    for section in missing:
        issues.append(f"Missing required section: {section}.")
    if claim_report.result_placeholders or claim_report.author_placeholders or claim_report.data_placeholders:
        issues.append("Manuscript still contains evidence, author or data-access placeholders.")

    return ManuscriptFormatReport(
        manuscript=manuscript,
        journal=journal_key,
        status="READY_FOR_FORMAT_REVIEW" if not issues else "NOT_READY",
        summary_words=summary_words,
        main_text_words=main_words,
        methods_words=methods_words,
        display_items=display_items,
        references=references,
        required_sections_present=present,
        missing_sections=missing,
        issues=tuple(issues),
    )


def render_manuscript_format_report(report: ManuscriptFormatReport) -> str:
    lines = [
        "# Manuscript format audit",
        "",
        f"Status: {report.status}",
        f"Journal target: {report.journal}",
        f"Manuscript: {report.manuscript.as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"summary_words | {report.summary_words}",
        f"main_text_words | {report.main_text_words}",
        f"methods_words | {report.methods_words}",
        f"display_items | {report.display_items}",
        f"references | {report.references}",
        "",
        "## Issues",
        "",
    ]
    if report.issues:
        lines.extend(f"- {issue}" for issue in report.issues)
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计只检查稿件结构、字数、图表数量、参考文献数量和占位符风险，不证明科学结果已经成立。即使格式通过，仍必须等待证据注册表、数据访问、统计验证和投稿门控全部通过后才能提交。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_manuscript_format_audit_command(
    manuscript_path: str | Path,
    output_path: str | Path,
    journal: str = "nature",
) -> tuple[ManuscriptFormatReport, Path]:
    report = audit_manuscript_format(manuscript_path, journal=journal)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_manuscript_format_report(report), encoding="utf-8")
    return report, output
