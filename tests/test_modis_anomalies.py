from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.modis_anomalies import (
    compute_modis_anomalies,
    run_modis_anomaly_command,
    validate_quality_filtered_modis_frame,
)


def test_compute_modis_anomalies_by_pixel_and_day_of_year() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01", "2020-01-17", "2021-01-17"],
            "pixel_id": ["p1", "p1", "p1", "p1"],
            "evi": [0.2, 0.4, 0.3, 0.7],
            "ndvi": [0.5, 0.7, 0.4, 0.8],
            "quality_ok": [True, True, True, True],
        }
    )
    result = compute_modis_anomalies(frame, min_climatology_samples=2)

    assert len(result.anomalies) == 4
    assert result.qc["output_rows"] == 4
    day_one = result.anomalies[result.anomalies["day_of_year"] == 1]
    assert day_one["evi_anomaly"].round(6).tolist() == [-0.1, 0.1]


def test_compute_modis_anomalies_uses_quality_flag() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01", "2022-01-01"],
            "pixel_id": ["p1", "p1", "p1"],
            "evi": [0.2, 0.4, 0.8],
            "ndvi": [0.5, 0.7, 0.9],
            "quality_ok": [True, True, False],
        }
    )
    result = compute_modis_anomalies(frame, min_climatology_samples=2)

    assert result.qc["rows_after_quality_filter"] == 2
    assert result.qc["output_rows"] == 2


def test_validate_quality_filtered_modis_frame_requires_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_quality_filtered_modis_frame(pd.DataFrame({"date": ["2020-01-01"]}))


def test_modis_anomaly_command_writes_readiness_report_when_input_missing(tmp_path: Path) -> None:
    completed, report_path = run_modis_anomaly_command(
        input_path=tmp_path / "missing.csv",
        output_path=tmp_path / "processed" / "modis_anomalies.csv",
        report_path=tmp_path / "qc" / "modis_anomaly_qc_report.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "processed" / "modis_anomalies.csv").exists()


def test_modis_anomaly_command_writes_processed_anomalies(tmp_path: Path) -> None:
    input_path = tmp_path / "modis_quality_filtered.csv"
    pd.DataFrame(
        {
            "date": ["2020-01-01", "2021-01-01"],
            "pixel_id": ["p1", "p1"],
            "evi": [0.2, 0.4],
            "ndvi": [0.5, 0.7],
        }
    ).to_csv(input_path, index=False)
    output_path = tmp_path / "processed" / "modis_anomalies.csv"
    report_path = tmp_path / "qc" / "modis_anomaly_qc_report.md"

    completed, written_report = run_modis_anomaly_command(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
        min_climatology_samples=2,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert {"evi_anomaly", "ndvi_anomaly"}.issubset(output.columns)
