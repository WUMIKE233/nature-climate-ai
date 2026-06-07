from pathlib import Path

from nature_climate_ai.submission_package import audit_submission_package, run_submission_package_audit_command


def test_submission_package_audit_detects_current_placeholders() -> None:
    audit = audit_submission_package(".")

    assert not audit.ready
    assert audit.missing_count == 0
    assert audit.placeholder_file_count > 0
    assert any(item.path == "manuscript/cover_letter.md" for item in audit.files)


def test_submission_package_audit_command_writes_report_and_csv(tmp_path: Path) -> None:
    report, output, csv_output = run_submission_package_audit_command(
        root=".",
        output_path=tmp_path / "submission_package_audit.md",
        csv_path=tmp_path / "submission_package_status.csv",
    )

    assert not report.ready
    assert output.exists()
    assert csv_output.exists()
    assert "Submission package audit" in output.read_text(encoding="utf-8")
    assert "manuscript/nature_article_draft.md" in csv_output.read_text(encoding="utf-8")
