from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.climate_features import (
    compute_climate_lag_features,
    run_climate_feature_command,
    validate_climate_frame,
)


VARIABLES = ("2m_temperature", "total_precipitation")


def test_climate_lag_features_align_anomalies_to_future_target_dates() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01", "2020-01-17", "2021-01-17"],
            "pixel_id": ["p1", "p1", "p1", "p1"],
            "2m_temperature": [280.0, 284.0, 282.0, 286.0],
            "total_precipitation": [1.0, 3.0, 2.0, 4.0],
        }
    )
    result = compute_climate_lag_features(
        frame,
        variables=VARIABLES,
        lead_times_days=(16,),
        min_climatology_samples=2,
    )

    target = result.features[result.features["date"] == pd.Timestamp("2020-01-17")].iloc[0]
    assert target["2m_temperature_anomaly_lag_16d"] == -2.0
    assert target["total_precipitation_anomaly_lag_16d"] == -1.0


def test_climate_lag_features_support_multiple_leads() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01"],
            "pixel_id": ["p1", "p1"],
            "2m_temperature": [280.0, 284.0],
            "total_precipitation": [1.0, 3.0],
        }
    )
    result = compute_climate_lag_features(
        frame,
        variables=VARIABLES,
        lead_times_days=(16, 32),
        min_climatology_samples=2,
    )

    assert "2m_temperature_anomaly_lag_16d" in result.features.columns
    assert "2m_temperature_anomaly_lag_32d" in result.features.columns


def test_validate_climate_frame_requires_variables() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_climate_frame(pd.DataFrame({"date": ["2020-01-01"]}), variables=VARIABLES)


def test_climate_feature_command_writes_readiness_report_when_input_missing(tmp_path: Path) -> None:
    completed, report_path = run_climate_feature_command(
        input_path=tmp_path / "missing.csv",
        output_path=tmp_path / "processed" / "climate_lag_features.csv",
        report_path=tmp_path / "qc" / "era5_climate_feature_report.md",
        config_path="config/study.yaml",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "processed" / "climate_lag_features.csv").exists()


def test_climate_feature_command_writes_features_for_valid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "era5_composite_climate.csv"
    pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01"],
            "pixel_id": ["p1", "p1"],
            "2m_temperature": [280.0, 284.0],
            "total_precipitation": [1.0, 3.0],
            "soil_moisture": [0.2, 0.4],
            "surface_net_solar_radiation": [100.0, 120.0],
            "vapour_pressure_deficit": [0.8, 1.2],
        }
    ).to_csv(input_path, index=False)
    output_path = tmp_path / "processed" / "climate_lag_features.csv"
    report_path = tmp_path / "qc" / "era5_climate_feature_report.md"

    completed, written_report = run_climate_feature_command(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        config_path="config/study.yaml",
        min_climatology_samples=2,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert "2m_temperature_anomaly_lag_16d" in output.columns


def test_climate_feature_command_writes_readiness_report_when_columns_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "era5_composite_climate.csv"
    pd.DataFrame(
        {
            "date": ["2020-01-01"],
            "pixel_id": ["p1"],
            "2m_temperature": [280.0],
        }
    ).to_csv(input_path, index=False)
    output_path = tmp_path / "processed" / "climate_lag_features.csv"
    report_path = tmp_path / "qc" / "era5_climate_feature_report.md"

    completed, written_report = run_climate_feature_command(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        config_path="config/study.yaml",
    )

    assert not completed
    assert written_report == report_path
    assert not output_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "input validation failed" in text
    assert "soil_moisture" in text


def test_climate_feature_command_accepts_explicit_pilot_variable_subset(tmp_path: Path) -> None:
    input_path = tmp_path / "era5_composite_climate.csv"
    pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02"],
            "pixel_id": ["p1", "p1"],
            "2m_temperature": [280.0, 281.0],
        }
    ).to_csv(input_path, index=False)
    output_path = tmp_path / "processed" / "climate_lag_features.csv"
    report_path = tmp_path / "qc" / "era5_climate_feature_report.md"

    completed, _ = run_climate_feature_command(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        config_path="config/study.yaml",
        min_climatology_samples=1,
        variables_override=("2m_temperature",),
    )

    assert completed
    output = pd.read_csv(output_path)
    assert "2m_temperature_anomaly_lag_16d" in output.columns
