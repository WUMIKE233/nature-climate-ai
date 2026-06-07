from pathlib import Path

from nature_climate_ai.manuscript_format import (
    audit_manuscript_format,
    count_words,
    run_manuscript_format_audit_command,
)


def test_count_words_handles_hyphenated_terms() -> None:
    assert count_words("AI-guided heat-drought early warning") == 6


def test_nature_format_audit_blocks_current_placeholder_draft() -> None:
    report = audit_manuscript_format("manuscript/nature_article_draft.md", journal="nature")

    assert report.status == "NOT_READY"
    assert report.display_items == 4
    assert any("placeholders" in issue for issue in report.issues)


def test_science_format_audit_reads_abstract() -> None:
    report = audit_manuscript_format("manuscript/science_research_article_draft.md", journal="science")

    assert report.summary_words > 0
    assert report.status == "NOT_READY"


def test_manuscript_format_audit_command_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "submission" / "format_audit.md"
    report, written = run_manuscript_format_audit_command(
        manuscript_path="manuscript/nature_article_draft.md",
        output_path=output,
        journal="nature",
    )

    assert report.status == "NOT_READY"
    assert written == output
    text = output.read_text(encoding="utf-8")
    assert "Manuscript format audit" in text
    assert "中文" in text
