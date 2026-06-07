from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.uncertainty import (
    audit_validation_uncertainty,
    run_uncertainty_audit_command,
    wilson_interval,
)


def _metrics(split: str | None = None) -> pd.DataFrame:
    row = {
        "model": "candidate",
        "rows": 20,
        "positive_labels": 8,
        "true_positive": 6,
        "false_positive": 2,
        "false_negative": 2,
        "true_negative": 10,
        "precision": 0.75,
        "recall": 0.75,
        "false_alarm_rate": 2 / 12,
        "accuracy": 0.8,
    }
    if split is not None:
        row["split"] = split
    return pd.DataFrame([row])


def test_wilson_interval_bounds_estimate() -> None:
    low, high = wilson_interval(6, 8)

    assert low < 0.75 < high
    assert 0 <= low <= high <= 1


def test_uncertainty_audit_outputs_metric_intervals() -> None:
    result = audit_validation_uncertainty(
        baseline_metrics=_metrics("holdout"),
        temporal_metrics=_metrics("holdout"),
        spatial_metrics=_metrics(),
    )

    assert result.qc["interval_rows"] == 12
    assert set(result.intervals["metric"]) == {"precision", "recall", "false_alarm_rate", "accuracy"}


def test_uncertainty_audit_requires_confusion_counts() -> None:
    with pytest.raises(ValueError, match="confusion-count"):
        audit_validation_uncertainty(
            baseline_metrics=_metrics("holdout").drop(columns=["true_positive"]),
            temporal_metrics=_metrics("holdout"),
            spatial_metrics=_metrics(),
        )


def test_uncertainty_command_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    completed, report = run_uncertainty_audit_command(
        baseline_path=tmp_path / "baseline.csv",
        temporal_path=tmp_path / "temporal.csv",
        spatial_path=tmp_path / "spatial.csv",
        output_path=tmp_path / "uncertainty.csv",
        report_path=tmp_path / "uncertainty.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report.read_text(encoding="utf-8")
    assert not (tmp_path / "uncertainty.csv").exists()


def test_uncertainty_command_writes_intervals_for_valid_inputs(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.csv"
    temporal = tmp_path / "temporal.csv"
    spatial = tmp_path / "spatial.csv"
    _metrics("holdout").to_csv(baseline, index=False)
    _metrics("holdout").to_csv(temporal, index=False)
    _metrics().to_csv(spatial, index=False)

    completed, report = run_uncertainty_audit_command(
        baseline_path=baseline,
        temporal_path=temporal,
        spatial_path=spatial,
        output_path=tmp_path / "uncertainty.csv",
        report_path=tmp_path / "uncertainty.md",
    )

    assert completed
    assert "COMPLETE_FOR_INPUT_DATA" in report.read_text(encoding="utf-8")
    assert (tmp_path / "uncertainty.csv").exists()
