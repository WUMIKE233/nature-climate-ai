from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.modeling_dataset import (
    build_modeling_dataset,
    derive_grid_block_regions,
    label_stress_events,
    run_modeling_dataset_command,
    validate_climate_features_frame,
)


def test_label_stress_events_marks_dates_inside_event_interval() -> None:
    climate = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17", "2020-02-02"],
            "pixel_id": ["p1", "p1", "p1"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2, 0.3],
        }
    )
    events = pd.DataFrame(
        {
            "pixel_id": ["p1"],
            "start_date": ["2020-01-17"],
            "end_date": ["2020-02-02"],
        }
    )
    labels = label_stress_events(climate, events)
    assert labels.tolist() == [0, 1, 1]


def test_build_modeling_dataset_merges_optional_anomalies() -> None:
    climate = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17"],
            "pixel_id": ["p1", "p1"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2],
        }
    )
    events = pd.DataFrame(
        {
            "pixel_id": ["p1"],
            "start_date": ["2020-01-17"],
            "end_date": ["2020-01-17"],
        }
    )
    anomalies = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17"],
            "pixel_id": ["p1", "p1"],
            "evi_anomaly": [0.0, -1.2],
            "ndvi_anomaly": [0.1, -0.8],
        }
    )
    result = build_modeling_dataset(climate, events, anomalies=anomalies)

    assert result.qc["positive_labels"] == 1
    assert result.qc["anomaly_columns_added"] == 2
    assert {"evi_anomaly", "ndvi_anomaly"}.issubset(result.dataset.columns)


def test_build_modeling_dataset_derives_grid_region_from_pixel_id() -> None:
    climate = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17"],
            "pixel_id": ["p00029c00039", "p00030c00040"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2],
        }
    )
    events = pd.DataFrame(columns=["pixel_id", "start_date", "end_date"])

    result = build_modeling_dataset(climate, events)

    assert result.dataset["region"].tolist() == ["grid_r00_c00", "grid_r01_c01"]
    assert result.qc["region_source"] == "derived_from_pixel_id_grid_blocks_row30_col40"
    assert result.qc["region_count"] == 2


def test_derive_grid_block_regions_returns_none_for_unknown_pixel_ids() -> None:
    assert derive_grid_block_regions(pd.Series(["site-a", "site-b"])) is None


def test_validate_climate_features_frame_requires_lag_columns() -> None:
    with pytest.raises(ValueError, match="lag-feature"):
        validate_climate_features_frame(pd.DataFrame({"date": ["2020-01-01"], "pixel_id": ["p1"]}))


def test_modeling_dataset_command_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    completed, report_path = run_modeling_dataset_command(
        climate_path=tmp_path / "missing_climate.csv",
        events_path=tmp_path / "missing_events.csv",
        output_path=tmp_path / "processed" / "modeling_dataset.csv",
        report_path=tmp_path / "qc" / "modeling_dataset_report.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "processed" / "modeling_dataset.csv").exists()


def test_modeling_dataset_command_writes_dataset_for_valid_inputs(tmp_path: Path) -> None:
    climate_path = tmp_path / "climate_lag_features.csv"
    events_path = tmp_path / "event_catalogue_summary.csv"
    output_path = tmp_path / "processed" / "modeling_dataset.csv"
    report_path = tmp_path / "qc" / "modeling_dataset_report.md"
    pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17"],
            "pixel_id": ["p1", "p1"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2],
        }
    ).to_csv(climate_path, index=False)
    pd.DataFrame(
        {
            "pixel_id": ["p1"],
            "start_date": ["2020-01-17"],
            "end_date": ["2020-01-17"],
        }
    ).to_csv(events_path, index=False)

    completed, written_report = run_modeling_dataset_command(
        climate_path=climate_path,
        events_path=events_path,
        output_path=output_path,
        report_path=report_path,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert output["stress_event"].tolist() == [0, 1]
