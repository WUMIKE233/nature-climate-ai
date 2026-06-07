from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ModisAnomalyResult:
    anomalies: pd.DataFrame
    qc: dict[str, int | float | str]


def validate_quality_filtered_modis_frame(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    evi_col: str = "evi",
    ndvi_col: str = "ndvi",
) -> None:
    required = {date_col, unit_col, evi_col, ndvi_col}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"MODIS table is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("MODIS table is empty.")


def compute_modis_anomalies(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    evi_col: str = "evi",
    ndvi_col: str = "ndvi",
    quality_col: str = "quality_ok",
    min_climatology_samples: int = 2,
) -> ModisAnomalyResult:
    """Compute day-of-year vegetation-index anomalies by stable spatial unit.

    This function assumes the source table has already been harmonized to a
    consistent compositing cadence and spatial unit. If ``quality_ok`` exists,
    only rows where it is truthy are used.
    """
    validate_quality_filtered_modis_frame(frame, date_col, unit_col, evi_col, ndvi_col)
    if min_climatology_samples < 1:
        raise ValueError("min_climatology_samples must be at least 1.")

    working = frame.copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[evi_col] = pd.to_numeric(working[evi_col], errors="coerce")
    working[ndvi_col] = pd.to_numeric(working[ndvi_col], errors="coerce")
    before_quality = len(working)

    if quality_col in working.columns:
        working = working[working[quality_col].astype(bool)]

    valid = working.dropna(subset=[date_col, unit_col, evi_col, ndvi_col]).copy()
    valid["day_of_year"] = valid[date_col].dt.dayofyear

    grouped = valid.groupby([unit_col, "day_of_year"], sort=False)
    valid["evi_climatology"] = grouped[evi_col].transform("mean")
    valid["ndvi_climatology"] = grouped[ndvi_col].transform("mean")
    valid["climatology_samples"] = grouped[evi_col].transform("count")
    valid = valid[valid["climatology_samples"] >= min_climatology_samples].copy()

    valid["evi_anomaly"] = valid[evi_col] - valid["evi_climatology"]
    valid["ndvi_anomaly"] = valid[ndvi_col] - valid["ndvi_climatology"]

    anomalies = valid[
        [
            date_col,
            unit_col,
            "day_of_year",
            evi_col,
            ndvi_col,
            "evi_climatology",
            "ndvi_climatology",
            "climatology_samples",
            "evi_anomaly",
            "ndvi_anomaly",
        ]
    ].sort_values([unit_col, date_col])

    qc = {
        "input_rows": int(len(frame)),
        "rows_after_quality_filter": int(len(working)),
        "valid_rows_before_climatology_filter": int(len(working.dropna(subset=[date_col, unit_col, evi_col, ndvi_col]))),
        "output_rows": int(len(anomalies)),
        "dropped_rows": int(before_quality - len(anomalies)),
        "unique_units": int(anomalies[unit_col].nunique()) if not anomalies.empty else 0,
        "min_climatology_samples": int(min_climatology_samples),
        "date_min": anomalies[date_col].min().date().isoformat() if not anomalies.empty else "NA",
        "date_max": anomalies[date_col].max().date().isoformat() if not anomalies.empty else "NA",
    }
    return ModisAnomalyResult(anomalies=anomalies, qc=qc)


def render_modis_anomaly_qc_report(result: ModisAnomalyResult, input_path: str | Path) -> str:
    lines = [
        "# MODIS anomaly-generation QC report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes anomaly generation for the supplied quality-filtered MODIS table. It does not certify global coverage or provider-policy compliance.",
        "",
        f"- Input table: {Path(input_path).as_posix()}",
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
            "Do not use these anomalies as manuscript evidence until the input MODIS product collection, quality flags, temporal coverage and spatial domain have been verified.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_modis_anomaly_readiness_report(input_path: str | Path) -> str:
    return "\n".join(
        [
            "# MODIS anomaly-generation readiness report",
            "",
            "Status: NOT_READY",
            "",
            f"Expected input table: {Path(input_path).as_posix()}",
            "",
            "The command did not generate `data/processed/modis_anomalies.csv` because the quality-filtered MODIS input table is missing.",
            "",
            "Required input columns:",
            "",
            "- `date`: MODIS composite date.",
            "- `pixel_id`: stable pixel, site or region identifier.",
            "- `evi`: quality-filtered EVI value.",
            "- `ndvi`: quality-filtered NDVI value.",
            "- `quality_ok`: optional boolean quality flag; if present, only truthy rows are used.",
        ]
    ) + "\n"


def run_modis_anomaly_command(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    min_climatology_samples: int = 2,
) -> tuple[bool, Path]:
    input_file = Path(input_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        report_file.write_text(render_modis_anomaly_readiness_report(input_file), encoding="utf-8")
        return False, report_file

    frame = pd.read_csv(input_file)
    result = compute_modis_anomalies(frame, min_climatology_samples=min_climatology_samples)
    result.anomalies.to_csv(output_file, index=False)
    report_file.write_text(render_modis_anomaly_qc_report(result, input_file), encoding="utf-8")
    return True, report_file
