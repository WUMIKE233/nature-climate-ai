from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.modis_quality import (
    compute_quality_filtered_modis,
    mod13_vi_quality_ok,
    run_modis_quality_command,
    validate_modis_observation_frame,
)


def test_mod13_vi_quality_ok_keeps_clean_records() -> None:
    quality = pd.Series([0, 1])
    assert mod13_vi_quality_ok(quality).tolist() == [True, True]


def test_mod13_vi_quality_ok_rejects_cloud_snow_shadow_and_high_aerosol() -> None:
    adjacent_cloud = 1 << 8
    mixed_cloud = 1 << 10
    snow_ice = 1 << 14
    shadow = 1 << 15
    high_aerosol = 2 << 6
    quality = pd.Series([adjacent_cloud, mixed_cloud, snow_ice, shadow, high_aerosol])
    assert mod13_vi_quality_ok(quality).tolist() == [False, False, False, False, False]


def test_compute_quality_filtered_modis_uses_vi_quality() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17"],
            "pixel_id": ["p1", "p1"],
            "evi": [0.2, 0.3],
            "ndvi": [0.5, 0.6],
            "vi_quality": [0, 1 << 8],
        }
    )
    result = compute_quality_filtered_modis(frame)

    assert len(result.filtered) == 1
    assert result.qc["quality_source"] == "vi_quality"
    assert result.qc["dropped_rows"] == 1


def test_compute_quality_filtered_modis_uses_boolean_bad_flags() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17", "2020-02-02"],
            "pixel_id": ["p1", "p1", "p1"],
            "evi": [0.2, 0.3, 0.4],
            "ndvi": [0.5, 0.6, 0.7],
            "cloud": [False, True, False],
            "snow_ice": [False, False, True],
        }
    )
    result = compute_quality_filtered_modis(frame)

    assert len(result.filtered) == 1
    assert result.qc["quality_source"] == "cloud,snow_ice"


def test_validate_modis_observation_frame_requires_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_modis_observation_frame(pd.DataFrame({"date": ["2020-01-01"]}))


def test_modis_quality_command_writes_readiness_report_when_input_missing(tmp_path: Path) -> None:
    completed, report_path = run_modis_quality_command(
        input_path=tmp_path / "missing.csv",
        output_path=tmp_path / "interim" / "modis_quality_filtered.csv",
        report_path=tmp_path / "qc" / "modis_quality_filter_report.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "interim" / "modis_quality_filtered.csv").exists()


def test_modis_quality_command_writes_filtered_table(tmp_path: Path) -> None:
    input_path = tmp_path / "modis_observations.csv"
    pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17"],
            "pixel_id": ["p1", "p1"],
            "evi": [0.2, 0.3],
            "ndvi": [0.5, 0.6],
            "vi_quality": [0, 1 << 8],
        }
    ).to_csv(input_path, index=False)
    output_path = tmp_path / "interim" / "modis_quality_filtered.csv"
    report_path = tmp_path / "qc" / "modis_quality_filter_report.md"

    completed, written_report = run_modis_quality_command(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert output["quality_ok"].tolist() == [True]
