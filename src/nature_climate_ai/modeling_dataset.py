from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ModelingDatasetResult:
    dataset: pd.DataFrame
    qc: dict[str, int | str]


def derive_grid_block_regions(
    unit_values: pd.Series,
    row_block_size: int = 30,
    col_block_size: int = 40,
) -> pd.Series | None:
    """Derive coarse spatial blocks from GEE-style pixel ids like p00012c00034."""
    unique_units = pd.Series(unit_values.dropna().unique(), name="pixel_id")
    if unique_units.empty:
        return None

    parts = unique_units.astype(str).str.extract(r"^p(?P<row>\d+)c(?P<col>\d+)$")
    if parts.isna().any(axis=None):
        return None

    row_block = (parts["row"].astype(int) // row_block_size).astype(str).str.zfill(2)
    col_block = (parts["col"].astype(int) // col_block_size).astype(str).str.zfill(2)
    mapping = dict(zip(unique_units, "grid_r" + row_block + "_c" + col_block, strict=True))
    return unit_values.map(mapping)


def validate_climate_features_frame(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
) -> None:
    required = {date_col, unit_col}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Climate feature table is missing required columns: {sorted(missing)}")
    feature_columns = [column for column in frame.columns if "_lag_" in column and column.endswith("d")]
    if not feature_columns:
        raise ValueError("Climate feature table must include lag-feature columns ending in `d`.")
    if frame.empty:
        raise ValueError("Climate feature table is empty.")


def validate_event_catalogue_frame(
    frame: pd.DataFrame,
    unit_col: str = "pixel_id",
) -> None:
    required = {unit_col, "start_date", "end_date"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Event catalogue is missing required columns: {sorted(missing)}")


def label_stress_events(
    climate_features: pd.DataFrame,
    event_catalogue: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
) -> pd.Series:
    climate_dates = pd.to_datetime(climate_features[date_col], errors="coerce")
    labels = pd.Series(False, index=climate_features.index)

    if event_catalogue.empty:
        return labels.astype(int)

    events = event_catalogue[[unit_col, "start_date", "end_date"]].copy()
    events["start_date"] = pd.to_datetime(events["start_date"], errors="coerce")
    events["end_date"] = pd.to_datetime(events["end_date"], errors="coerce")
    events = events.dropna(subset=[unit_col, "start_date", "end_date"])

    event_intervals: dict[object, tuple[np.ndarray, np.ndarray]] = {}
    for unit, unit_events in events.groupby(unit_col, sort=False):
        ordered = unit_events.sort_values("start_date")
        starts = ordered["start_date"].to_numpy(dtype="datetime64[ns]").astype("int64")
        ends = ordered["end_date"].to_numpy(dtype="datetime64[ns]").astype("int64")
        event_intervals[unit] = (starts, np.maximum.accumulate(ends))

    for unit, index in climate_features.groupby(unit_col, sort=False).groups.items():
        intervals = event_intervals.get(unit)
        if intervals is None:
            continue
        starts, cumulative_ends = intervals
        unit_dates = climate_dates.loc[index].to_numpy(dtype="datetime64[ns]").astype("int64")
        positions = np.searchsorted(starts, unit_dates, side="right") - 1
        matched = positions >= 0
        unit_labels = np.zeros(len(unit_dates), dtype=bool)
        unit_labels[matched] = unit_dates[matched] <= cumulative_ends[positions[matched]]
        labels.loc[index] = unit_labels

    return labels.astype(int)


def build_modeling_dataset(
    climate_features: pd.DataFrame,
    event_catalogue: pd.DataFrame,
    anomalies: pd.DataFrame | None = None,
    date_col: str = "date",
    unit_col: str = "pixel_id",
) -> ModelingDatasetResult:
    validate_climate_features_frame(climate_features, date_col, unit_col)
    validate_event_catalogue_frame(event_catalogue, unit_col)

    dataset = climate_features.copy()
    dataset[date_col] = pd.to_datetime(dataset[date_col], errors="coerce")
    dataset = dataset.dropna(subset=[date_col, unit_col]).copy()
    dataset["stress_event"] = label_stress_events(dataset, event_catalogue, date_col, unit_col)

    anomaly_columns_added = 0
    if anomalies is not None and not anomalies.empty:
        anomaly_frame = anomalies.copy()
        if {date_col, unit_col}.issubset(anomaly_frame.columns):
            anomaly_frame[date_col] = pd.to_datetime(anomaly_frame[date_col], errors="coerce")
            optional_columns = [
                column
                for column in ("evi_anomaly", "ndvi_anomaly")
                if column in anomaly_frame.columns
            ]
            if optional_columns:
                dataset = dataset.merge(
                    anomaly_frame[[date_col, unit_col, *optional_columns]],
                    on=[date_col, unit_col],
                    how="left",
                )
                anomaly_columns_added = len(optional_columns)

    region_source = "not_added"
    if "region" not in dataset.columns and unit_col in dataset.columns:
        derived_region = derive_grid_block_regions(dataset[unit_col])
        if derived_region is not None:
            dataset["region"] = derived_region
            region_source = "derived_from_pixel_id_grid_blocks_row30_col40"

    dataset = dataset.sort_values([unit_col, date_col]).reset_index(drop=True)
    dataset[date_col] = dataset[date_col].dt.date.astype(str)
    qc = {
        "climate_feature_rows": int(len(climate_features)),
        "event_catalogue_rows": int(len(event_catalogue)),
        "output_rows": int(len(dataset)),
        "positive_labels": int(dataset["stress_event"].sum()),
        "negative_labels": int((dataset["stress_event"] == 0).sum()),
        "unique_units": int(dataset[unit_col].nunique()) if not dataset.empty else 0,
        "anomaly_columns_added": int(anomaly_columns_added),
        "region_source": region_source,
        "region_count": int(dataset["region"].nunique()) if "region" in dataset.columns else 0,
        "date_min": str(dataset[date_col].min()) if not dataset.empty else "NA",
        "date_max": str(dataset[date_col].max()) if not dataset.empty else "NA",
    }
    return ModelingDatasetResult(dataset=dataset, qc=qc)


def render_modeling_dataset_report(result: ModelingDatasetResult, climate_path: str | Path, events_path: str | Path) -> str:
    lines = [
        "# Modeling dataset QC report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes assembly of the supervised model dataset from lagged climate features and vegetation-stress events. It does not certify that upstream data cover the full study domain.",
        "",
        f"- Climate features: {Path(climate_path).as_posix()}",
        f"- Event catalogue: {Path(events_path).as_posix()}",
        "",
        "## Summary",
        "",
        "metric | value",
        "--- | ---",
    ]
    for key, value in result.qc.items():
        lines.append(f"{key} | {value}")
    lines.extend(
        [
            "",
            "## Manuscript-use warning",
            "",
            "Do not use this model dataset as manuscript evidence until upstream MODIS and ERA5 evidence items are complete and leakage checks are documented.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_modeling_dataset_readiness_report(climate_path: str | Path, events_path: str | Path) -> str:
    missing = [Path(path).as_posix() for path in (climate_path, events_path) if not Path(path).exists()]
    lines = [
        "# Modeling dataset readiness report",
        "",
        "Status: NOT_READY",
        "",
        "The command did not generate `data/processed/modeling_dataset.csv` because required inputs are missing.",
        "",
        "Required inputs:",
        "",
        f"- Climate lag features: {Path(climate_path).as_posix()}",
        f"- Stress-event catalogue: {Path(events_path).as_posix()}",
        "",
        "Missing inputs:",
        "",
    ]
    lines.extend(f"- {path}" for path in missing)
    return "\n".join(lines) + "\n"


def run_modeling_dataset_command(
    climate_path: str | Path,
    events_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    anomalies_path: str | Path | None = None,
) -> tuple[bool, Path]:
    climate_file = Path(climate_path)
    events_file = Path(events_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not climate_file.exists() or not events_file.exists():
        report_file.write_text(render_modeling_dataset_readiness_report(climate_file, events_file), encoding="utf-8")
        return False, report_file

    anomalies = None
    if anomalies_path is not None and Path(anomalies_path).exists():
        anomalies = pd.read_csv(anomalies_path)

    result = build_modeling_dataset(
        climate_features=pd.read_csv(climate_file),
        event_catalogue=pd.read_csv(events_file),
        anomalies=anomalies,
    )
    result.dataset.to_csv(output_file, index=False)
    report_file.write_text(render_modeling_dataset_report(result, climate_file, events_file), encoding="utf-8")
    return True, report_file
