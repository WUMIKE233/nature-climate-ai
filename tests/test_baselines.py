from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.baselines import (
    evaluate_baselines,
    run_baseline_evaluation_command,
    validate_modeling_dataset_frame,
)


def _modeling_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2019-01-01", "2020-01-01", "2021-01-01", "2022-01-01"],
            "pixel_id": ["p1", "p1", "p1", "p1"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2, 0.8, 0.9],
            "total_precipitation_deficit_lag_16d": [0.0, 0.1, 0.5, 0.4],
            "soil_moisture_deficit_lag_32d": [0.2, 0.3, 0.8, 0.7],
            "vapour_pressure_deficit_lag_16d": [0.1, 0.2, 0.9, 1.0],
            "stress_event": [0, 1, 1, 0],
        }
    )


def test_evaluate_baselines_uses_temporal_holdout() -> None:
    result = evaluate_baselines(_modeling_frame(), holdout_range=(2021, 2025))

    assert result.qc["train_rows"] == 2
    assert result.qc["holdout_rows"] == 2
    assert set(result.metrics["split"]) == {"train", "holdout"}
    assert "majority_class" in set(result.metrics["model"])


def test_evaluate_baselines_includes_threshold_feature_model() -> None:
    result = evaluate_baselines(_modeling_frame(), holdout_range=(2021, 2025))
    threshold_rows = result.metrics[result.metrics["model"].str.startswith("threshold:")]

    assert not threshold_rows.empty
    assert {"precision", "recall", "false_alarm_rate", "accuracy"}.issubset(result.metrics.columns)


def test_evaluate_baselines_includes_persistence_and_family_models() -> None:
    result = evaluate_baselines(_modeling_frame(), holdout_range=(2021, 2025))
    models = set(result.metrics["model"])

    assert "persistence_previous_event" in models
    assert "family_threshold:temperature_only" in models
    assert "family_threshold:precipitation_only" in models
    assert "family_threshold:soil_moisture_only" in models
    assert "family_threshold:vpd_only" in models
    assert "family_threshold:compound_heat_drought" in models
    assert result.qc["family_baseline_count"] >= 4
    assert result.qc["compound_baseline_count"] == 1


def test_validate_modeling_dataset_frame_requires_lag_feature() -> None:
    with pytest.raises(ValueError, match="lag-feature"):
        validate_modeling_dataset_frame(pd.DataFrame({"date": ["2020-01-01"], "stress_event": [0]}))


def test_evaluate_baselines_requires_holdout_rows() -> None:
    with pytest.raises(ValueError, match="holdout"):
        evaluate_baselines(_modeling_frame(), holdout_range=(2025, 2026))


def test_baseline_command_writes_readiness_report_when_input_missing(tmp_path: Path) -> None:
    completed, report_path = run_baseline_evaluation_command(
        input_path=tmp_path / "missing.csv",
        output_path=tmp_path / "validation" / "baseline_metrics.csv",
        report_path=tmp_path / "validation" / "baseline_comparison.md",
        config_path="config/study.yaml",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "validation" / "baseline_metrics.csv").exists()


def test_baseline_command_writes_metrics_for_valid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "modeling_dataset.csv"
    _modeling_frame().to_csv(input_path, index=False)
    output_path = tmp_path / "validation" / "baseline_metrics.csv"
    report_path = tmp_path / "validation" / "baseline_comparison.md"

    completed, written_report = run_baseline_evaluation_command(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        config_path="config/study.yaml",
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert "holdout" in set(output["split"])
