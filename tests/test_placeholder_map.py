from pathlib import Path

from nature_climate_ai.placeholder_map import build_placeholder_map, run_placeholder_map_command


def test_placeholder_map_counts_nature_draft_placeholders() -> None:
    mapping = build_placeholder_map("manuscript/nature_article_draft.md")

    assert mapping.mapped_count == 21
    assert sum(row.token == "RESULT_REQUIRED" for row in mapping.rows) == 16
    assert sum(row.token == "AUTHOR_REQUIRED" for row in mapping.rows) == 3
    assert sum(row.token == "DATA_ACCESS_REQUIRED" for row in mapping.rows) == 2


def test_placeholder_map_links_ecosystem_result_rows_to_ecosystem_validation() -> None:
    mapping = build_placeholder_map("manuscript/nature_article_draft.md")

    ecosystem_rows = [
        row
        for row in mapping.rows
        if row.token == "RESULT_REQUIRED" and ("Figure 4" in row.context or "ecosystem-function" in row.context)
    ]

    assert ecosystem_rows
    assert any("ecosystem_validation" in row.linked_evidence_ids for row in ecosystem_rows)


def test_placeholder_map_keeps_author_inputs_separate_from_evidence_items() -> None:
    mapping = build_placeholder_map("manuscript/nature_article_draft.md")

    author_rows = [row for row in mapping.rows if row.token == "AUTHOR_REQUIRED"]

    assert author_rows
    assert {row.linked_evidence_ids for row in author_rows} == {"AUTHOR_INPUT_REQUIRED"}


def test_placeholder_map_command_writes_report_and_csv(tmp_path: Path) -> None:
    manuscript = tmp_path / "draft.md"
    manuscript.write_text(
        "# Draft\n\nAUTHOR_REQUIRED\n\nRESULT_REQUIRED: report validation.\n\nDATA_ACCESS_REQUIRED.\n",
        encoding="utf-8",
    )

    mapping, report, csv_output = run_placeholder_map_command(
        manuscript_path=manuscript,
        output_path=tmp_path / "placeholder_map.md",
        csv_path=tmp_path / "placeholder_map.csv",
    )

    assert mapping.mapped_count == 3
    assert report.exists()
    assert csv_output.exists()
    assert "Manuscript placeholder evidence map" in report.read_text(encoding="utf-8")
    assert "linked_evidence_ids" in csv_output.read_text(encoding="utf-8")
