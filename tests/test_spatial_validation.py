from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.spatial_validation import (
    run_spatial_validation_command,
    spatial_holdout_validate_candidates,
    validate_spatial_validation_inputs,
)


def _modeling_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18"],
            "pixel_id": ["p1", "p2", "p3", "p4"],
            "region": ["north", "north", "south", "south"],
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


def test_spatial_holdout_validate_candidates_outputs_region_metrics() -> None:
    result = spatial_holdout_validate_candidates(_modeling_frame(), _candidates(), top_n=1)

    assert result.qc["regions"] == 2
    assert result.qc["selected_features"] == 1
    assert set(result.metrics["heldout_region"]) == {"north", "south"}
    assert result.metrics["model"].str.contains("2m_temperature").all()


def test_spatial_validation_requires_region_column() -> None:
    frame = _modeling_frame().drop(columns=["region"])
    with pytest.raises(ValueError, match="spatial holdout column"):
        validate_spatial_validation_inputs(frame, _candidates())


def test_spatial_validation_requires_at_least_two_regions() -> None:
    frame = _modeling_frame()
    frame["region"] = "north"
    with pytest.raises(ValueError, match="at least two regions"):
        spatial_holdout_validate_candidates(frame, _candidates())


def test_spatial_validation_command_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    completed, report_path = run_spatial_validation_command(
        modeling_path=tmp_path / "missing_modeling.csv",
        candidates_path=tmp_path / "missing_candidates.csv",
        output_path=tmp_path / "validation" / "spatial_holdout_metrics.csv",
        report_path=tmp_path / "validation" / "spatial_holdout_report.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "validation" / "spatial_holdout_metrics.csv").exists()


def test_spatial_validation_command_writes_metrics_for_valid_inputs(tmp_path: Path) -> None:
    modeling_path = tmp_path / "modeling_dataset.csv"
    candidates_path = tmp_path / "feature_attribution_table.csv"
    output_path = tmp_path / "validation" / "spatial_holdout_metrics.csv"
    report_path = tmp_path / "validation" / "spatial_holdout_report.md"
    _modeling_frame().to_csv(modeling_path, index=False)
    _candidates().to_csv(candidates_path, index=False)

    completed, written_report = run_spatial_validation_command(
        modeling_path=modeling_path,
        candidates_path=candidates_path,
        output_path=output_path,
        report_path=report_path,
        region_col="region",
        top_n=1,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert set(output["heldout_region"]) == {"north", "south"}
