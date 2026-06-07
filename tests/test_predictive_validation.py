from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.predictive_validation import (
    run_predictive_validation_summary_command,
    summarize_predictive_validation,
)


def _baseline_metrics() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "split": ["train", "holdout"],
            "model": ["majority_class", "majority_class"],
            "rows": [10, 5],
            "precision": [0.5, 0.4],
            "recall": [0.6, 0.3],
            "false_alarm_rate": [0.2, 0.4],
            "accuracy": [0.7, 0.6],
        }
    )


def _temporal_metrics() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "split": ["holdout", "holdout"],
            "model": ["precursor_threshold", "precursor_threshold"],
            "rows": [4, 6],
            "precision": [0.7, 0.9],
            "recall": [0.5, 0.7],
            "false_alarm_rate": [0.1, 0.2],
            "accuracy": [0.75, 0.85],
        }
    )


def _spatial_metrics() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "heldout_region": ["north", "south"],
            "model": ["precursor_threshold", "precursor_threshold"],
            "rows": [8, 8],
            "precision": [0.8, 0.6],
            "recall": [0.4, 0.5],
            "false_alarm_rate": [0.15, 0.25],
            "accuracy": [0.8, 0.7],
        }
    )


def test_summarize_predictive_validation_outputs_all_evidence_types() -> None:
    result = summarize_predictive_validation(_baseline_metrics(), _temporal_metrics(), _spatial_metrics())

    assert set(result.summary["evidence_type"]) == {
        "baseline_holdout",
        "temporal_holdout",
        "spatial_holdout",
    }
    baseline = result.summary[result.summary["evidence_type"] == "baseline_holdout"].iloc[0]
    assert baseline["total_rows"] == 5
    assert baseline["mean_precision"] == pytest.approx(0.4)


def test_summarize_predictive_validation_requires_metric_columns() -> None:
    with pytest.raises(ValueError, match="required columns"):
        summarize_predictive_validation(
            _baseline_metrics().drop(columns=["accuracy"]),
            _temporal_metrics(),
            _spatial_metrics(),
        )


def test_predictive_validation_command_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    completed, report_path = run_predictive_validation_summary_command(
        baseline_path=tmp_path / "missing_baseline.csv",
        temporal_path=tmp_path / "missing_temporal.csv",
        spatial_path=tmp_path / "missing_spatial.csv",
        output_path=tmp_path / "validation" / "predictive_validation_summary.csv",
        report_path=tmp_path / "validation" / "predictive_validation_summary.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "validation" / "predictive_validation_summary.csv").exists()


def test_predictive_validation_command_writes_summary_for_valid_inputs(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline_metrics.csv"
    temporal_path = tmp_path / "temporal_holdout_metrics.csv"
    spatial_path = tmp_path / "spatial_holdout_metrics.csv"
    output_path = tmp_path / "validation" / "predictive_validation_summary.csv"
    report_path = tmp_path / "validation" / "predictive_validation_summary.md"
    _baseline_metrics().to_csv(baseline_path, index=False)
    _temporal_metrics().to_csv(temporal_path, index=False)
    _spatial_metrics().to_csv(spatial_path, index=False)

    completed, written_report = run_predictive_validation_summary_command(
        baseline_path=baseline_path,
        temporal_path=temporal_path,
        spatial_path=spatial_path,
        output_path=output_path,
        report_path=report_path,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert set(output["evidence_type"]) == {"baseline_holdout", "temporal_holdout", "spatial_holdout"}
