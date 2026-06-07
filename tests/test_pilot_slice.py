from pathlib import Path

from nature_climate_ai.pilot_slice import (
    DEFAULT_PILOT_ARTIFACTS,
    evaluate_minimum_evidence_slice,
    run_minimum_evidence_slice_command,
)


def test_minimum_evidence_slice_detects_missing_default_artifacts() -> None:
    result = evaluate_minimum_evidence_slice(".")

    assert not result.ready
    assert result.missing_count > 0
    assert any(item.group == "pilot_figures" for item in result.artifacts)


def test_minimum_evidence_slice_can_be_ready_for_complete_artifact_set(tmp_path: Path) -> None:
    artifacts = (
        ("stress_event_definition", "events.csv", "events"),
        ("pilot_figures", "fig1.png", "figure"),
    )
    for _, artifact, _ in artifacts:
        path = tmp_path / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok\n", encoding="utf-8")

    result = evaluate_minimum_evidence_slice(root=tmp_path, artifacts=artifacts)

    assert result.ready
    assert result.complete_count == 2


def test_minimum_evidence_slice_command_writes_report_and_csv(tmp_path: Path) -> None:
    report, output, csv_path = run_minimum_evidence_slice_command(
        root=".",
        output_path=tmp_path / "minimum_evidence_slice_report.md",
        csv_path=tmp_path / "minimum_evidence_slice_status.csv",
    )

    assert not report.ready
    assert output.exists()
    assert csv_path.exists()
    report_text = output.read_text(encoding="utf-8")
    assert "Minimum publishable evidence-slice gate" in report_text
    assert "中文审阅说明" in report_text
    csv_text = csv_path.read_text(encoding="utf-8")
    assert DEFAULT_PILOT_ARTIFACTS[0][1] in csv_text
