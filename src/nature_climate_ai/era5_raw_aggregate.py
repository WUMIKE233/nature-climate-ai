from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from .config import load_study_config


logger = logging.getLogger(__name__)

ERA5_SHORT_TO_PROJECT = {
    "t2m": "2m_temperature",
    "tp": "total_precipitation",
    "ssr": "surface_net_solar_radiation",
}
ERA5_SOIL_WATER_SHORT_NAMES = ("swvl1", "swvl2")
TIME_CHUNK_SIZE = 24


@dataclass(frozen=True)
class Era5RawAggregateResult:
    completed_for_input: bool
    rows: int
    variables: tuple[str, ...]
    missing_configured_variables: tuple[str, ...]
    output_path: Path
    report_path: Path
    spatial_stride: int = 1

    @property
    def status(self) -> str:
        if not self.completed_for_input:
            return "NOT_READY"
        if self.missing_configured_variables:
            return "PARTIAL_FOR_AVAILABLE_VARIABLES"
        return "COMPLETE_FOR_INPUT_DATA"


def _weighted_spatial_mean(data_array: xr.DataArray) -> xr.DataArray:
    if "latitude" not in data_array.dims or "longitude" not in data_array.dims:
        return data_array
    weights = np.cos(np.deg2rad(data_array["latitude"]))
    return data_array.weighted(weights).mean(dim=("latitude", "longitude"), skipna=True)


def _weighted_spatial_mean_series(data_array: xr.DataArray, time_coord: str, spatial_stride: int = 1) -> pd.Series:
    if spatial_stride < 1:
        raise ValueError("spatial_stride must be at least 1.")

    if "latitude" not in data_array.dims or "longitude" not in data_array.dims:
        series = data_array.to_series()
        series.index = pd.to_datetime(series.index)
        return series

    if spatial_stride > 1:
        data_array = data_array.isel(latitude=slice(None, None, spatial_stride), longitude=slice(None, None, spatial_stride))

    if time_coord not in data_array.dims:
        mean_value = float(_weighted_spatial_mean(data_array).values)
        index = pd.to_datetime([data_array[time_coord].values]) if time_coord in data_array.coords else pd.Index([0])
        return pd.Series([mean_value], index=index)

    times = pd.to_datetime(data_array[time_coord].values)
    weights = np.cos(np.deg2rad(data_array["latitude"].values)).astype("float32")
    weights_2d = weights[:, np.newaxis]
    static_valid = np.isfinite(data_array.isel({time_coord: 0}).values)
    denominator = float((static_valid * weights_2d).sum(dtype="float64"))
    values: list[float] = []

    for start in range(0, len(times), TIME_CHUNK_SIZE):
        subset = data_array.isel({time_coord: slice(start, start + TIME_CHUNK_SIZE)}).values
        subset = np.nan_to_num(np.asarray(subset), nan=0.0, copy=False)
        numerator = (subset * weights_2d).sum(axis=(1, 2), dtype="float64")
        chunk_values = np.divide(
            numerator,
            denominator,
            out=np.full_like(numerator, np.nan, dtype="float64"),
            where=denominator > 0,
        )
        values.extend(float(value) for value in chunk_values)

    return pd.Series(values, index=times)


def _time_name(dataset: xr.Dataset) -> str:
    for candidate in ("valid_time", "time"):
        if candidate in dataset.coords or candidate in dataset.dims:
            return candidate
    raise ValueError("ERA5 dataset is missing a valid_time/time coordinate.")


def _series_from_dataset(path: Path, spatial_stride: int = 1) -> pd.DataFrame:
    dataset = xr.open_dataset(path)
    try:
        time_coord = _time_name(dataset)
        frame = pd.DataFrame(index=pd.to_datetime(dataset[time_coord].values))
        for short_name, project_name in ERA5_SHORT_TO_PROJECT.items():
            if short_name not in dataset.data_vars:
                continue
            series = _weighted_spatial_mean_series(dataset[short_name], time_coord, spatial_stride=spatial_stride)
            frame[project_name] = series
        if "t2m" in dataset.data_vars and "d2m" in dataset.data_vars:
            temperature = _weighted_spatial_mean_series(dataset["t2m"], time_coord, spatial_stride=spatial_stride)
            dewpoint = _weighted_spatial_mean_series(dataset["d2m"], time_coord, spatial_stride=spatial_stride)
            frame["vapour_pressure_deficit"] = _vapour_pressure_deficit_kpa(temperature, dewpoint)
        soil_layers = []
        for short_name in ERA5_SOIL_WATER_SHORT_NAMES:
            if short_name not in dataset.data_vars:
                continue
            layer = _weighted_spatial_mean_series(dataset[short_name], time_coord, spatial_stride=spatial_stride)
            soil_layers.append(layer)
        if soil_layers:
            frame["soil_moisture"] = pd.concat(soil_layers, axis=1).mean(axis=1)
        return frame
    finally:
        dataset.close()


def _vapour_pressure_deficit_kpa(temperature_k: pd.Series, dewpoint_k: pd.Series) -> pd.Series:
    temperature_c = temperature_k - 273.15
    dewpoint_c = dewpoint_k - 273.15
    saturation = 0.6108 * np.exp((17.27 * temperature_c) / (temperature_c + 237.3))
    actual = 0.6108 * np.exp((17.27 * dewpoint_c) / (dewpoint_c + 237.3))
    return (saturation - actual).clip(lower=0)


def aggregate_era5_raw(
    input_dir: str | Path,
    configured_variables: tuple[str, ...],
    spatial_stride: int = 1,
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    root = Path(input_dir)
    files = sorted(root.rglob("*.nc"))
    if not files:
        raise FileNotFoundError(f"No NetCDF files found in {root}")

    hourly_frames = []
    for path in files:
        try:
            frame = _series_from_dataset(path, spatial_stride=spatial_stride)
        except Exception as exc:
            logger.warning("Skipping unreadable ERA5 NetCDF file %s: %s", path, exc)
            continue
        if not frame.empty and len(frame.columns) > 0:
            hourly_frames.append(frame)

    if not hourly_frames:
        raise FileNotFoundError(f"No readable ERA5 NetCDF files found in {root}")

    hourly = pd.concat(hourly_frames, axis=1)
    hourly = hourly.loc[:, ~hourly.columns.duplicated()]
    hourly.index.name = "datetime"

    daily_parts: dict[str, pd.Series] = {}
    for column in hourly.columns:
        if column in {"total_precipitation", "surface_net_solar_radiation"}:
            daily_parts[column] = hourly[column].resample("D").sum()
        else:
            daily_parts[column] = hourly[column].resample("D").mean()

    daily = pd.DataFrame(daily_parts).reset_index()
    daily = daily.rename(columns={"datetime": "date"})
    daily.insert(1, "pixel_id", "global_area_weighted_mean")
    daily["date"] = pd.to_datetime(daily["date"]).dt.date.astype(str)

    missing = tuple(variable for variable in configured_variables if variable not in daily.columns)
    return daily, missing


def render_era5_raw_aggregate_report(result: Era5RawAggregateResult, input_dir: str | Path) -> str:
    lines = [
        "# ERA5 raw aggregation QC report",
        "",
        f"Status: {result.status}",
        "",
        f"Input directory: {Path(input_dir).as_posix()}",
        f"Output table: {result.output_path.as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"rows | {result.rows}",
        f"variables | {','.join(result.variables) if result.variables else 'NA'}",
        f"missing_configured_variables | {','.join(result.missing_configured_variables) if result.missing_configured_variables else 'none'}",
        f"spatial_stride | {result.spatial_stride}",
        "",
        "## Method note",
        "",
        "This command creates a pilot global area-weighted daily aggregate from local ERA5 NetCDF files. Temperature and vapour-pressure deficit are daily means; total precipitation and surface net solar radiation are daily sums. The output is a QC/pipeline input, not final manuscript evidence, because it is not yet aligned to MODIS pixels or composite windows.",
        "",
        "## Manuscript-use warning",
        "",
        "Do not use this table as a Nature/Science result. It is only an intermediate check that raw ERA5 files can be opened and converted into a tabular climate input. Missing configured variables must be resolved or explicitly excluded in a separate pilot analysis decision.",
        "",
        "## 中文审阅说明",
        "",
        "本报告把本地 ERA5 NetCDF 原始文件聚合为 pilot 级日尺度全球面积加权表。它只证明原始数据可以进入后续流程，不代表 MODIS 网格对齐、完整 ERA5-Land 变量、泄漏检查或论文结果已经完成。",
    ]
    if result.spatial_stride > 1:
        lines.extend(
            [
                "",
                "## Spatial subsampling warning",
                "",
                f"This run used spatial_stride={result.spatial_stride}; only every {result.spatial_stride}th latitude/longitude cell was sampled before spatial aggregation. This is acceptable for pipeline smoke testing but not for final scientific inference.",
                "",
                "## 空间抽样警告",
                "",
                f"本次运行使用 spatial_stride={result.spatial_stride}，即仅抽取每 {result.spatial_stride} 个经纬度格点参与聚合。该结果只能用于流程烟测，不能作为最终科学推断。",
            ]
        )
    return "\n".join(lines) + "\n"


def run_era5_raw_aggregate_command(
    input_dir: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    config_path: str | Path = "config/study.yaml",
    spatial_stride: int = 1,
) -> Era5RawAggregateResult:
    config = load_study_config(config_path)
    configured_variables = tuple(config["data_sources"]["era5"]["variables"])
    output = Path(output_path)
    report = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    try:
        frame, missing = aggregate_era5_raw(input_dir, configured_variables, spatial_stride=spatial_stride)
    except FileNotFoundError:
        result = Era5RawAggregateResult(
            completed_for_input=False,
            rows=0,
            variables=(),
            missing_configured_variables=configured_variables,
            output_path=output,
            report_path=report,
            spatial_stride=spatial_stride,
        )
        report.write_text(render_era5_raw_aggregate_report(result, input_dir), encoding="utf-8")
        return result

    frame.to_csv(output, index=False)
    result = Era5RawAggregateResult(
        completed_for_input=True,
        rows=len(frame),
        variables=tuple(column for column in frame.columns if column not in {"date", "pixel_id"}),
        missing_configured_variables=missing,
        output_path=output,
        report_path=report,
        spatial_stride=spatial_stride,
    )
    report.write_text(render_era5_raw_aggregate_report(result, input_dir), encoding="utf-8")
    return result
