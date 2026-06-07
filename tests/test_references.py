from pathlib import Path

from nature_climate_ai.references import (
    audit_references,
    load_reference_metadata,
    run_reference_audit_command,
)


def test_reference_metadata_loads_seed_references() -> None:
    metadata = load_reference_metadata("manuscript/reference_metadata.yaml")

    assert len(metadata["references"]) >= 4
    assert any(entry["doi"] == "10.1038/s41586-019-0912-1" for entry in metadata["references"])


def test_reference_audit_flags_targeted_literature_gaps() -> None:
    metadata = load_reference_metadata("manuscript/reference_metadata.yaml")
    report = audit_references(metadata, "manuscript/reference_metadata.yaml")

    assert not report.ready
    assert report.checked_references == 4
    assert report.literature_gaps


def test_reference_audit_command_writes_report_and_csv(tmp_path: Path) -> None:
    report_path = tmp_path / "reference_audit.md"
    status_csv = tmp_path / "reference_status.csv"

    report, output, csv_path = run_reference_audit_command(
        metadata_path="manuscript/reference_metadata.yaml",
        report_path=report_path,
        status_csv_path=status_csv,
    )

    assert not report.ready
    assert output == report_path
    assert csv_path == status_csv
    assert "Reference audit" in output.read_text(encoding="utf-8")
    assert "reichstein_deep_learning_2019" in csv_path.read_text(encoding="utf-8")
