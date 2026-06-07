from pathlib import Path

import yaml

from nature_climate_ai.evidence import audit_evidence_artifacts, load_evidence_registry, run_evidence_artifact_audit_command


def test_evidence_registry_tracks_submission_claims() -> None:
    report = load_evidence_registry("evidence/registry.yaml")
    assert len(report.items) >= 8
    assert report.complete_count == 0
    assert {item.status for item in report.items} == {"pending"}


def test_evidence_items_have_required_artifacts() -> None:
    report = load_evidence_registry("evidence/registry.yaml")
    for item in report.items:
        assert item.manuscript_claim
        assert item.required_artifacts


def test_evidence_artifact_audit_finds_missing_artifacts() -> None:
    audit = audit_evidence_artifacts("evidence/registry.yaml", ".")

    assert not audit.ready
    assert audit.missing_count > 0
    assert any(row.artifact == "data/processed/modeling_dataset.csv" for row in audit.rows)


def test_evidence_artifact_audit_counts_placeholders(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.md"
    artifact.write_text("RESULT_REQUIRED", encoding="utf-8")
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump(
            {
                "items": [
                    {
                        "id": "example",
                        "status": "pending",
                        "manuscript_claim": "claim",
                        "required_artifacts": ["artifact.md"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    audit = audit_evidence_artifacts(registry, tmp_path)

    assert audit.placeholder_file_count == 1
    assert audit.rows[0].issue == "contains_placeholders"


def test_evidence_artifact_audit_ignores_placeholder_map_diagnostic_tokens(tmp_path: Path) -> None:
    artifact = tmp_path / "placeholder_evidence_map.md"
    artifact.write_text("RESULT_REQUIRED AUTHOR_REQUIRED DATA_ACCESS_REQUIRED", encoding="utf-8")
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump(
            {
                "items": [
                    {
                        "id": "example",
                        "status": "pending",
                        "manuscript_claim": "claim",
                        "required_artifacts": ["placeholder_evidence_map.md"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    audit = audit_evidence_artifacts(registry, tmp_path)

    assert audit.placeholder_file_count == 0
    assert audit.rows[0].issue == "ok"


def test_evidence_artifact_audit_command_writes_report_and_csv(tmp_path: Path) -> None:
    output = tmp_path / "artifact_audit.md"
    csv_output = tmp_path / "artifact_audit.csv"
    audit, report_path, csv_path = run_evidence_artifact_audit_command(
        registry_path="evidence/registry.yaml",
        root=".",
        output_path=output,
        csv_path=csv_output,
    )

    assert not audit.ready
    assert report_path == output
    assert csv_path == csv_output
    assert "Evidence artifact audit" in output.read_text(encoding="utf-8")
    assert "evidence_id,evidence_status,artifact" in csv_output.read_text(encoding="utf-8")
