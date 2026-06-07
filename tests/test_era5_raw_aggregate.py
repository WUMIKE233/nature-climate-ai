from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from nature_climate_ai.era5_raw_aggregate import aggregate_era5_raw, run_era5_raw_aggregate_command


def _write_dataset(path: Path) -> None:
    times = pd.date_range("2000-01-01", periods=4, freq="6h")
    latitudes = [0.0, 60.0]
    longitudes = [0.0, 1.0]
    shape = (len(times), len(latitudes), len(longitudes))
    dataset = xr.Dataset(
        {
            "t2m": (("valid_time", "latitude", "longitude"), np.full(shape, 300.0)),
            "d2m": (("valid_time", "latitude", "longitude"), np.full(shape, 290.0)),
            "tp": (("valid_time", "latitude", "longitude"), np.full(shape, 0.001)),
            "ssr": (("valid_time", "latitude", "longitude"), np.full(shape, 10.0)),
        },
        coords={"valid_time": times, "latitude": latitudes, "longitude": longitudes},
    )
    dataset.to_netcdf(path)


def _write_land_dataset(path: Path) -> None:
    times = pd.date_range("2000-01-01", periods=4, freq="6h")
    latitudes = [0.0, 60.0]
    longitudes = [0.0, 1.0]
    shape = (len(times), len(latitudes), len(longitudes))
    dataset = xr.Dataset(
        {
            "swvl1": (("valid_time", "latitude", "longitude"), np.full(shape, 0.20)),
            "swvl2": (("valid_time", "latitude", "longitude"), np.full(shape, 0.40)),
        },
        coords={"valid_time": times, "latitude": latitudes, "longitude": longitudes},
    )
    dataset.to_netcdf(path)


def test_aggregate_era5_raw_writes_available_project_variables(tmp_path: Path) -> None:
    input_dir = tmp_path / "era5"
    input_dir.mkdir()
    _write_dataset(input_dir / "sample.nc")

    frame, missing = aggregate_era5_raw(
        input_dir,
        configured_variables=("2m_temperature", "total_precipitation", "surface_net_solar_radiation", "vapour_pressure_deficit", "soil_moisture"),
    )

    assert len(frame) == 1
    assert frame.loc[0, "pixel_id"] == "global_area_weighted_mean"
    assert frame.loc[0, "2m_temperature"] == 300.0
    assert frame.loc[0, "total_precipitation"] == 0.004
    assert "vapour_pressure_deficit" in frame.columns
    assert missing == ("soil_moisture",)


def test_era5_raw_aggregate_command_reports_partial_available_variables(tmp_path: Path) -> None:
    input_dir = tmp_path / "era5"
    input_dir.mkdir()
    _write_dataset(input_dir / "sample.nc")
    config = tmp_path / "study.yaml"
    config.write_text(
        "\n".join(
            [
                "project: {}",
                "data_sources:",
                "  era5:",
                "    variables: [2m_temperature, total_precipitation, surface_net_solar_radiation, vapour_pressure_deficit, soil_moisture]",
                "stress_event_definition: {}",
                "modeling: {}",
                "validation: {}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_era5_raw_aggregate_command(
        input_dir=input_dir,
        output_path=tmp_path / "interim" / "era5_composite_climate.csv",
        report_path=tmp_path / "qc" / "era5_raw_aggregate_report.md",
        config_path=config,
    )

    assert result.status == "PARTIAL_FOR_AVAILABLE_VARIABLES"
    assert result.output_path.exists()
    assert "soil_moisture" in result.report_path.read_text(encoding="utf-8")


def test_aggregate_era5_raw_derives_soil_moisture_from_land_layers(tmp_path: Path) -> None:
    input_dir = tmp_path / "era5"
    input_dir.mkdir()
    _write_dataset(input_dir / "single.nc")
    _write_land_dataset(input_dir / "land.nc")

    frame, missing = aggregate_era5_raw(
        input_dir,
        configured_variables=("2m_temperature", "total_precipitation", "surface_net_solar_radiation", "vapour_pressure_deficit", "soil_moisture"),
    )

    assert missing == ()
    assert frame.loc[0, "soil_moisture"] == pytest.approx(0.30)


def test_aggregate_era5_raw_recursively_reads_nested_archives(tmp_path: Path) -> None:
    input_dir = tmp_path / "era5"
    nested_dir = input_dir / "cds_archive"
    nested_dir.mkdir(parents=True)
    _write_dataset(nested_dir / "single.nc")
    _write_land_dataset(input_dir / "land.nc")

    frame, missing = aggregate_era5_raw(
        input_dir,
        configured_variables=("2m_temperature", "total_precipitation", "surface_net_solar_radiation", "vapour_pressure_deficit", "soil_moisture"),
    )

    assert missing == ()
    assert frame.loc[0, "2m_temperature"] == 300.0
    assert frame.loc[0, "soil_moisture"] == pytest.approx(0.30)


def test_aggregate_era5_raw_accepts_spatial_stride(tmp_path: Path) -> None:
    input_dir = tmp_path / "era5"
    input_dir.mkdir()
    _write_dataset(input_dir / "single.nc")
    _write_land_dataset(input_dir / "land.nc")

    frame, missing = aggregate_era5_raw(
        input_dir,
        configured_variables=("2m_temperature", "soil_moisture"),
        spatial_stride=2,
    )

    assert missing == ()
    assert frame.loc[0, "2m_temperature"] == 300.0
    assert frame.loc[0, "soil_moisture"] == pytest.approx(0.30)
