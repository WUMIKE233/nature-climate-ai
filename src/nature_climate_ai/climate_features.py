from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import load_study_config


@dataclass(frozen=True)
class ClimateFeatureResult:
    features: pd.DataFrame
    qc: dict[str, int | str]


def climate_variables_from_config(config: dict) -> tuple[str, ...]:
    return tuple(config["data_sources"]["era5"]["variables"])


def lead_times_from_config(config: dict) -> tuple[int, ...]:
    return tuple(int(value) for value in config["temporal_domain"]["lead_time_days"])


def validate_climate_frame(
    frame: pd.DataFrame,
    variables: tuple[str, ...],
    date_col: str = "date",
    unit_col: str = "pixel_id",
) -> None:
    required = {date_col, unit_col, *variables}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Climate table is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Climate table is empty.")


def compute_climate_lag_features(
    frame: pd.DataFrame,
    variables: tuple[str, ...],
    lead_times_days: tuple[int, ...],
    date_col: str = "date",
    unit_col: str = "pixel_id",
    min_climatology_samples: int = 2,
) -> ClimateFeatureResult:
    """Compute day-of-year climate anomalies and align them to future target dates."""
    validate_climate_frame(frame, variables, date_col, unit_col)
    if not lead_times_days:
        raise ValueError("At least one lead time is required.")
    if min_climatology_samples < 1:
        raise ValueError("min_climatology_samples must be at least 1.")

    working = frame[[date_col, unit_col, *variables]].copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    for variable in variables:
        working[variable] = pd.to_numeric(working[variable], errors="coerce")
    valid = working.dropna(subset=[date_col, unit_col, *variables]).copy()
    valid["day_of_year"] = valid[date_col].dt.dayofyear

    grouped = valid.groupby([unit_col, "day_of_year"], sort=False)
    for variable in variables:
        climatology_col = f"{variable}_climatology"
        anomaly_col = f"{variable}_anomaly"
        samples_col = f"{variable}_climatology_samples"
        valid[climatology_col] = grouped[variable].transform("mean")
        valid[samples_col] = grouped[variable].transform("count")
        valid[anomaly_col] = valid[variable] - valid[climatology_col]

    sample_cols = [f"{variable}_climatology_samples" for variable in variables]
    valid = valid[(valid[sample_cols] >= min_climatology_samples).all(axis=1)].copy()

    feature_frames: list[pd.DataFrame] = []
    for lead_days in lead_times_days:
        lead = valid[[date_col, unit_col, *[f"{variable}_anomaly" for variable in variables]]].copy()
        lead[date_col] = lead[date_col] + pd.to_timedelta(lead_days, unit="D")
        rename = {
            f"{variable}_anomaly": f"{variable}_anomaly_lag_{lead_days}d"
            for variable in variables
        }
        lead = lead.rename(columns=rename)
        feature_frames.append(lead)

    features = feature_frames[0]
    for next_features in feature_frames[1:]:
        features = features.merge(next_features, on=[date_col, unit_col], how="outer")

    features = features.sort_values([unit_col, date_col]).reset_index(drop=True)
    qc = {
        "input_rows": int(len(frame)),
        "valid_rows_before_climatology_filter": int(len(working.dropna(subset=[date_col, unit_col, *variables]))),
        "output_rows": int(len(features)),
        "dropped_rows": int(len(frame) - len(valid)),
        "unique_units": int(features[unit_col].nunique()) if not features.empty else 0,
        "variables": ",".join(variables),
        "lead_times_days": ",".join(str(value) for value in lead_times_days),
        "min_climatology_samples": int(min_climatology_samples),
        "date_min": features[date_col].min().date().isoformat() if not features.empty else "NA",
        "date_max": features[date_col].max().date().isoformat() if not features.empty else "NA",
    }
    return ClimateFeatureResult(features=features, qc=qc)


def render_climate_feature_report(result: ClimateFeatureResult, input_path: str | Path) -> str:
    lines = [
        "# ERA5 climate lag-feature QC report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes lagged climate-feature generation for the supplied aggregated ERA5/ERA5-Land table. It does not certify provider access, global coverage or correct hourly-to-composite aggregation.",
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
            "Do not use these features as manuscript evidence until ERA5/ERA5-Land request parameters, aggregation windows, spatial alignment and leakage checks are documented.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_climate_feature_readiness_report(
    input_path: str | Path,
    variables: tuple[str, ...],
    reason: str = "The command did not generate `data/processed/climate_lag_features.csv` because the aggregated ERA5/ERA5-Land input table is missing.",
) -> str:
    lines = [
        "# ERA5 climate lag-feature readiness report",
        "",
        "Status: NOT_READY",
        "",
        f"Expected input table: {Path(input_path).as_posix()}",
        "",
        reason,
        "",
        "Required input columns:",
        "",
        "- `date`: climate aggregation window date aligned to the MODIS compositing cadence.",
        "- `pixel_id`: stable pixel, site or region identifier aligned with MODIS.",
    ]
    lines.extend(f"- `{variable}`" for variable in variables)
    return "\n".join(lines) + "\n"


def run_climate_feature_command(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    config_path: str | Path = "config/study.yaml",
    min_climatology_samples: int = 2,
    variables_override: tuple[str, ...] | None = None,
) -> tuple[bool, Path]:
    config = load_study_config(config_path)
    variables = variables_override if variables_override is not None else climate_variables_from_config(config)
    lead_times = lead_times_from_config(config)

    input_file = Path(input_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        report_file.write_text(render_climate_feature_readiness_report(input_file, variables), encoding="utf-8")
        return False, report_file

    frame = pd.read_csv(input_file)
    try:
        result = compute_climate_lag_features(
            frame,
            variables=variables,
            lead_times_days=lead_times,
            min_climatology_samples=min_climatology_samples,
        )
    except ValueError as exc:
        report_file.write_text(
            render_climate_feature_readiness_report(
                input_file,
                variables,
                reason=f"The command did not generate `{output_file.as_posix()}` because input validation failed: {exc}",
            ),
            encoding="utf-8",
        )
        return False, report_file
    result.features.to_csv(output_file, index=False)
    report_file.write_text(render_climate_feature_report(result, input_file), encoding="utf-8")
    return True, report_file
