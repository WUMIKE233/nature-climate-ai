from pathlib import Path

import pandas as pd

from nature_climate_ai.robustness import (
    biome_stratified_validate,
    placebo_validate,
    run_placebo_validation_command,
    run_sensor_cross_validation_command,
    run_threshold_sensitivity_command,
    sensor_cross_validate,
    threshold_sensitivity,
)


def _modeling_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18", "2021-01-01", "2021-01-17"],
            "pixel_id": ["p1", "p1", "p1", "p2", "p2", "p2"],
            "biome": ["grassland", "grassland", "grassland", "forest", "forest", "forest"],
            "temperature_anomaly_lag_16d": [0.1, 0.7, 0.8, 0.2, 0.9, 1.1],
            "soil_moisture_deficit_lag_32d": [0.2, 0.4, 0.9, 0.1, 0.8, 0.7],
            "stress_event": [0, 1, 1, 0, 1, 0],
        }
    )


def _anomaly_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18"] * 2,
            "pixel_id": ["p1"] * 4 + ["p2"] * 4,
            "evi_anomaly": [-0.8, -0.9, 0.1, 0.2, -0.7, -0.6, 0.3, 0.4],
        }
    )


def test_placebo_validate_writes_metric_rows() -> None:
    result = placebo_validate(_modeling_frame(), top_n=1)

    assert result.qc["features_tested"] == 1
    assert {"precision", "recall", "false_alarm_rate", "accuracy"}.issubset(result.metrics.columns)


def test_threshold_sensitivity_counts_events_across_percentiles() -> None:
    result = threshold_sensitivity(_anomaly_frame(), percentiles=(10, 20), minimum_duration=1)

    assert result.qc["percentiles_tested"] == 2
    assert set(result.metrics["percentile"]) == {10.0, 20.0}
    assert "event_count" in result.metrics.columns


def test_biome_stratified_validate_groups_by_biome() -> None:
    result = biome_stratified_validate(_modeling_frame(), biome_col="biome", top_n=1)

    assert result.qc["biomes"] == 2
    assert set(result.metrics["group"]) == {"forest", "grassland"}


def test_sensor_cross_validate_compares_overlap() -> None:
    modis = _anomaly_frame()
    external = modis.rename(columns={"evi_anomaly": "external_anomaly"}).copy()
    external["external_anomaly"] = external["external_anomaly"] * 0.9

    result = sensor_cross_validate(modis, external)

    assert result.qc["overlap_rows"] == len(modis)
    assert result.metrics.loc[0, "correlation"] > 0.99


def test_robustness_commands_write_readiness_reports_when_inputs_missing(tmp_path: Path) -> None:
    completed, report = run_placebo_validation_command(
        input_path=tmp_path / "missing_modeling.csv",
        output_path=tmp_path / "placebo_metrics.csv",
        report_path=tmp_path / "placebo_validation.md",
    )
    assert not completed
    assert "Status: NOT_READY" in report.read_text(encoding="utf-8")

    completed, report = run_threshold_sensitivity_command(
        input_path=tmp_path / "missing_anomalies.csv",
        output_path=tmp_path / "threshold_sensitivity.csv",
        report_path=tmp_path / "threshold_sensitivity.md",
    )
    assert not completed
    assert "Status: NOT_READY" in report.read_text(encoding="utf-8")

    completed, report = run_sensor_cross_validation_command(
        modis_path=tmp_path / "missing_modis.csv",
        external_path=tmp_path / "missing_external.csv",
        output_path=tmp_path / "sensor.csv",
        report_path=tmp_path / "sensor.md",
    )
    assert not completed
    assert "Status: NOT_READY" in report.read_text(encoding="utf-8")
