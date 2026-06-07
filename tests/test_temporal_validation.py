from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.temporal_validation import (
    run_temporal_validation_command,
    temporal_holdout_validate_candidates,
    validate_temporal_validation_inputs,
)


def _modeling_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2019-01-01", "2020-01-01", "2021-01-01", "2022-01-01"],
            "pixel_id": ["p1", "p1", "p1", "p1"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2, 0.9, 1.0],
            "soil_moisture_anomaly_lag_16d": [0.4, 0.3, 0.2, 0.1],
            "stress_event": [0, 0, 1, 1],
        }
    )


def _candidates() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "feature": ["2m_temperature_anomaly_lag_16d", "soil_moisture_anomaly_lag_16d"],
            "absolute_correlation": [0.9, 0.4],
        }
    )


def test_temporal_holdout_validate_candidates_outputs_train_and_holdout_metrics() -> None:
    result = temporal_holdout_validate_candidates(
        _modeling_frame(),
        _candidates(),
        holdout_range=(2021, 2025),
        top_n=1,
    )

    assert result.qc["selected_features"] == 1
    assert set(result.metrics["split"]) == {"train", "holdout"}
    assert result.metrics["model"].str.contains("2m_temperature").all()


def test_temporal_holdout_validate_candidates_requires_present_features() -> None:
    with pytest.raises(ValueError, match="No candidate features"):
        temporal_holdout_validate_candidates(
            _modeling_frame(),
            pd.DataFrame({"feature": ["missing_lag_16d"]}),
            holdout_range=(2021, 2025),
        )


def test_validate_temporal_validation_inputs_requires_candidate_feature_column() -> None:
    with pytest.raises(ValueError, match="feature"):
        validate_temporal_validation_inputs(_modeling_frame(), pd.DataFrame({"bad": ["x"]}))


def test_temporal_validation_command_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    completed, report_path = run_temporal_validation_command(
        modeling_path=tmp_path / "missing_modeling.csv",
        candidates_path=tmp_path / "missing_candidates.csv",
        output_path=tmp_path / "validation" / "temporal_holdout_metrics.csv",
        report_path=tmp_path / "validation" / "temporal_holdout_report.md",
        config_path="config/study.yaml",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "validation" / "temporal_holdout_metrics.csv").exists()


def test_temporal_validation_command_writes_metrics_for_valid_inputs(tmp_path: Path) -> None:
    modeling_path = tmp_path / "modeling_dataset.csv"
    candidates_path = tmp_path / "feature_attribution_table.csv"
    output_path = tmp_path / "validation" / "temporal_holdout_metrics.csv"
    report_path = tmp_path / "validation" / "temporal_holdout_report.md"
    _modeling_frame().to_csv(modeling_path, index=False)
    _candidates().to_csv(candidates_path, index=False)

    completed, written_report = run_temporal_validation_command(
        modeling_path=modeling_path,
        candidates_path=candidates_path,
        output_path=output_path,
        report_path=report_path,
        config_path="config/study.yaml",
        top_n=1,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert "holdout" in set(output["split"])
