from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class FluxnetValidationResult:
    metrics: pd.DataFrame
    qc: dict[str, int | str]


def validate_fluxnet_frame(
    frame: pd.DataFrame,
    site_col: str = "site_id",
    date_col: str = "date",
    gpp_col: str = "gpp_anomaly",
) -> None:
    required = {site_col, date_col, gpp_col}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"FLUXNET anomaly table is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("FLUXNET anomaly table is empty.")


def validate_window_frame(
    frame: pd.DataFrame,
    site_col: str = "site_id",
) -> None:
    required = {site_col, "start_date", "end_date"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Predicted stress-window table is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Predicted stress-window table is empty.")


def label_predicted_windows(
    fluxnet: pd.DataFrame,
    windows: pd.DataFrame,
    site_col: str = "site_id",
    date_col: str = "date",
) -> pd.Series:
    dates = pd.to_datetime(fluxnet[date_col], errors="coerce")
    labels = pd.Series(False, index=fluxnet.index)

    working_windows = windows[[site_col, "start_date", "end_date"]].copy()
    working_windows["start_date"] = pd.to_datetime(working_windows["start_date"], errors="coerce")
    working_windows["end_date"] = pd.to_datetime(working_windows["end_date"], errors="coerce")
    working_windows = working_windows.dropna(subset=[site_col, "start_date", "end_date"])

    for site, site_windows in working_windows.groupby(site_col, sort=False):
        site_mask = fluxnet[site_col] == site
        if not site_mask.any():
            continue
        site_dates = dates[site_mask]
        site_labels = pd.Series(False, index=site_dates.index)
        for _, window in site_windows.iterrows():
            site_labels |= site_dates.between(window["start_date"], window["end_date"], inclusive="both")
        labels.loc[site_labels.index] = site_labels

    return labels.astype(int)


def _mean_or_na(values: pd.Series) -> float | str:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return "NA"
    return float(clean.mean())


def validate_fluxnet_ecosystem_response(
    fluxnet: pd.DataFrame,
    windows: pd.DataFrame,
    site_col: str = "site_id",
    date_col: str = "date",
    gpp_col: str = "gpp_anomaly",
    le_col: str = "le_anomaly",
) -> FluxnetValidationResult:
    validate_fluxnet_frame(fluxnet, site_col, date_col, gpp_col)
    validate_window_frame(windows, site_col)

    working = fluxnet.copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[gpp_col] = pd.to_numeric(working[gpp_col], errors="coerce")
    if le_col in working.columns:
        working[le_col] = pd.to_numeric(working[le_col], errors="coerce")
    working = working.dropna(subset=[site_col, date_col, gpp_col]).copy()
    working["predicted_window"] = label_predicted_windows(working, windows, site_col, date_col)

    rows: list[dict[str, float | int | str]] = []
    for site, site_frame in working.groupby(site_col, sort=True):
        inside = site_frame[site_frame["predicted_window"] == 1]
        outside = site_frame[site_frame["predicted_window"] == 0]
        gpp_inside = _mean_or_na(inside[gpp_col])
        gpp_outside = _mean_or_na(outside[gpp_col])
        row: dict[str, float | int | str] = {
            "site_id": site,
            "rows": int(len(site_frame)),
            "inside_window_rows": int(len(inside)),
            "outside_window_rows": int(len(outside)),
            "gpp_inside_mean": gpp_inside,
            "gpp_outside_mean": gpp_outside,
            "gpp_inside_minus_outside": (
                float(gpp_inside) - float(gpp_outside)
                if isinstance(gpp_inside, float) and isinstance(gpp_outside, float)
                else "NA"
            ),
        }
        if le_col in working.columns:
            le_inside = _mean_or_na(inside[le_col])
            le_outside = _mean_or_na(outside[le_col])
            row["le_inside_mean"] = le_inside
            row["le_outside_mean"] = le_outside
            row["le_inside_minus_outside"] = (
                float(le_inside) - float(le_outside)
                if isinstance(le_inside, float) and isinstance(le_outside, float)
                else "NA"
            )
        rows.append(row)

    metrics = pd.DataFrame(rows)
    qc = {
        "fluxnet_rows": int(len(fluxnet)),
        "valid_fluxnet_rows": int(len(working)),
        "window_rows": int(len(windows)),
        "sites": int(working[site_col].nunique()),
        "sites_with_predicted_windows": int(working.loc[working["predicted_window"] == 1, site_col].nunique()),
        "inside_window_rows": int((working["predicted_window"] == 1).sum()),
        "outside_window_rows": int((working["predicted_window"] == 0).sum()),
    }
    return FluxnetValidationResult(metrics=metrics, qc=qc)


def render_fluxnet_report(result: FluxnetValidationResult, fluxnet_path: str | Path, windows_path: str | Path) -> str:
    lines = [
        "# FLUXNET ecosystem validation report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report compares FLUXNET ecosystem-function anomalies inside versus outside predicted stress windows. It does not certify FLUXNET policy compliance or establish a manuscript-ready mechanism claim.",
        "",
        f"- FLUXNET anomalies: {Path(fluxnet_path).as_posix()}",
        f"- Predicted windows: {Path(windows_path).as_posix()}",
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
            "Do not claim independent ecosystem validation until FLUXNET data policy, site representativeness, uncertainty and model-window provenance are documented.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_fluxnet_readiness_report(fluxnet_path: str | Path, windows_path: str | Path) -> str:
    missing = [Path(path).as_posix() for path in (fluxnet_path, windows_path) if not Path(path).exists()]
    lines = [
        "# FLUXNET ecosystem validation readiness report",
        "",
        "Status: NOT_READY",
        "",
        "The command did not generate FLUXNET validation metrics because required inputs are missing.",
        "",
        "Required inputs:",
        "",
        f"- FLUXNET anomaly table: {Path(fluxnet_path).as_posix()}",
        f"- Predicted stress windows: {Path(windows_path).as_posix()}",
        "",
        "Required FLUXNET columns:",
        "",
        "- `site_id`",
        "- `date`",
        "- `gpp_anomaly`",
        "- optional `le_anomaly`",
        "",
        "Required window columns:",
        "",
        "- `site_id`",
        "- `start_date`",
        "- `end_date`",
        "",
        "Missing inputs:",
        "",
    ]
    lines.extend(f"- {path}" for path in missing)
    return "\n".join(lines) + "\n"


def run_fluxnet_validation_command(
    fluxnet_path: str | Path,
    windows_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> tuple[bool, Path]:
    fluxnet_file = Path(fluxnet_path)
    windows_file = Path(windows_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not fluxnet_file.exists() or not windows_file.exists():
        report_file.write_text(render_fluxnet_readiness_report(fluxnet_file, windows_file), encoding="utf-8")
        return False, report_file

    result = validate_fluxnet_ecosystem_response(
        fluxnet=pd.read_csv(fluxnet_file),
        windows=pd.read_csv(windows_file),
    )
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(render_fluxnet_report(result, fluxnet_file, windows_file), encoding="utf-8")
    return True, report_file
