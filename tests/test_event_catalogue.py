from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.event_catalogue import (
    build_event_catalogue,
    run_event_catalogue_command,
    validate_anomaly_frame,
)


def test_event_catalogue_detects_persistent_low_anomaly_runs() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=6, freq="16D"),
            "pixel_id": ["p1"] * 6,
            "evi_anomaly": [0.2, -2.0, -1.8, 0.1, -1.9, -2.1],
        }
    )
    result = build_event_catalogue(frame, percentile=70, minimum_duration=2)

    assert result.event_count == 2
    assert result.qc["input_rows"] == 6
    assert result.qc["units_with_events"] == 1
    assert result.events["duration_observations"].tolist() == [2, 2]


def test_event_catalogue_drops_short_runs() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=4, freq="16D"),
            "pixel_id": ["p1"] * 4,
            "evi_anomaly": [0.2, -2.0, 0.1, -1.9],
        }
    )
    result = build_event_catalogue(frame, percentile=60, minimum_duration=2)
    assert result.event_count == 0


def test_validate_anomaly_frame_requires_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_anomaly_frame(pd.DataFrame({"date": ["2020-01-01"]}))


def test_e01_command_writes_readiness_report_when_input_missing(tmp_path: Path) -> None:
    completed, report_path = run_event_catalogue_command(
        input_path=tmp_path / "missing.csv",
        output_dir=tmp_path / "out",
    )
    assert not completed
    assert report_path.name == "e01_event_catalogue_readiness_report.md"
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "out" / "event_catalogue_summary.csv").exists()


def test_e01_command_writes_artifacts_for_valid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "modis_anomalies.csv"
    pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=4, freq="16D"),
            "pixel_id": ["p1"] * 4,
            "evi_anomaly": [-2.0, -1.8, 0.3, 0.4],
        }
    ).to_csv(input_path, index=False)

    completed, report_path = run_event_catalogue_command(
        input_path=input_path,
        output_dir=tmp_path / "out",
        percentile=60,
        minimum_duration=2,
    )

    assert completed
    assert report_path.name == "quality_control_report.md"
    assert (tmp_path / "out" / "event_catalogue_summary.csv").exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
