from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .stress_events import percentile_stress_events


@dataclass(frozen=True)
class EventCatalogueResult:
    events: pd.DataFrame
    qc: dict[str, int | float | str]

    @property
    def event_count(self) -> int:
        return int(len(self.events))


def _required_columns(date_col: str, unit_col: str, value_col: str) -> set[str]:
    return {date_col, unit_col, value_col}


def validate_anomaly_frame(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    value_col: str = "evi_anomaly",
) -> None:
    missing = _required_columns(date_col, unit_col, value_col).difference(frame.columns)
    if missing:
        raise ValueError(f"Input anomaly table is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Input anomaly table is empty.")


def build_event_catalogue(
    frame: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    value_col: str = "evi_anomaly",
    percentile: float = 10,
    minimum_duration: int = 2,
) -> EventCatalogueResult:
    """Build a persistent low-vegetation anomaly event catalogue.

    The input is expected to be quality-filtered and anomaly-normalized before
    this function is called. This keeps the event catalogue step auditable and
    avoids treating raw satellite retrieval noise as ecological evidence.
    """
    validate_anomaly_frame(frame, date_col, unit_col, value_col)

    working = frame[[date_col, unit_col, value_col]].copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[value_col] = pd.to_numeric(working[value_col], errors="coerce")
    valid = working.dropna(subset=[date_col, unit_col, value_col]).sort_values([unit_col, date_col])

    rows: list[dict[str, object]] = []
    for unit, group in valid.groupby(unit_col, sort=True):
        values = group.set_index(date_col)[value_col]
        flags = percentile_stress_events(values, percentile=percentile, minimum_duration=minimum_duration)
        if not flags.any():
            continue

        event_breaks = (flags != flags.shift(fill_value=False)).cumsum()
        for event_index, event_values in values[flags].groupby(event_breaks[flags]):
            start = event_values.index.min()
            end = event_values.index.max()
            rows.append(
                {
                    "event_id": f"{unit}_{int(event_index)}",
                    unit_col: unit,
                    "start_date": start.date().isoformat(),
                    "end_date": end.date().isoformat(),
                    "duration_observations": int(event_values.shape[0]),
                    "min_anomaly": float(event_values.min()),
                    "mean_anomaly": float(event_values.mean()),
                }
            )

    events = pd.DataFrame(
        rows,
        columns=[
            "event_id",
            unit_col,
            "start_date",
            "end_date",
            "duration_observations",
            "min_anomaly",
            "mean_anomaly",
        ],
    )
    qc = {
        "input_rows": int(len(frame)),
        "valid_rows": int(len(valid)),
        "dropped_rows": int(len(frame) - len(valid)),
        "unique_units": int(valid[unit_col].nunique()),
        "units_with_events": int(events[unit_col].nunique()) if not events.empty else 0,
        "event_count": int(len(events)),
        "percentile": float(percentile),
        "minimum_duration": int(minimum_duration),
        "date_min": valid[date_col].min().date().isoformat(),
        "date_max": valid[date_col].max().date().isoformat(),
    }
    return EventCatalogueResult(events=events, qc=qc)


def render_quality_control_report(result: EventCatalogueResult, input_path: str | Path) -> str:
    lines = [
        "# E01 stress-event catalogue quality-control report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes event-catalogue construction for the supplied quality-filtered anomaly table. It does not certify that the input table covers the full global study domain.",
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
            "Do not promote this event catalogue into the Nature or Science manuscript unless the input data are confirmed to be quality-filtered MODIS anomalies for the intended study domain and years.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_event_catalogue_readiness_report(input_path: str | Path) -> str:
    return "\n".join(
        [
            "# E01 stress-event catalogue readiness report",
            "",
            "Status: NOT_READY",
            "",
            f"Expected input table: {Path(input_path).as_posix()}",
            "",
            "The event-catalogue command did not create manuscript evidence artifacts because the input anomaly table is missing.",
            "",
            "Required input columns:",
            "",
            "- `date`: MODIS composite date.",
            "- `pixel_id`: stable pixel, site or region identifier.",
            "- `evi_anomaly`: quality-filtered EVI anomaly.",
            "",
            "Optional next step: generate a small pilot table after MODIS access is confirmed, then rerun `e01-event-catalogue`.",
        ]
    ) + "\n"


def run_event_catalogue_command(
    input_path: str | Path,
    output_dir: str | Path,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    value_col: str = "evi_anomaly",
    percentile: float = 10,
    minimum_duration: int = 2,
) -> tuple[bool, Path]:
    input_file = Path(input_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        report_path = output / "e01_event_catalogue_readiness_report.md"
        report_path.write_text(render_event_catalogue_readiness_report(input_file), encoding="utf-8")
        return False, report_path

    frame = pd.read_csv(input_file)
    result = build_event_catalogue(
        frame,
        date_col=date_col,
        unit_col=unit_col,
        value_col=value_col,
        percentile=percentile,
        minimum_duration=minimum_duration,
    )
    event_path = output / "event_catalogue_summary.csv"
    qc_path = output / "quality_control_report.md"
    result.events.to_csv(event_path, index=False)
    qc_path.write_text(render_quality_control_report(result, input_file), encoding="utf-8")
    return True, qc_path
