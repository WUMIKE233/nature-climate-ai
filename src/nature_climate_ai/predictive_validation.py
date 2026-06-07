from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PredictiveValidationSummary:
    summary: pd.DataFrame
    qc: dict[str, int | str]


def _require_metric_columns(frame: pd.DataFrame, name: str) -> None:
    required = {"model", "rows", "precision", "recall", "false_alarm_rate", "accuracy"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{name} metrics are missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"{name} metrics are empty.")


def _mean_metric_rows(frame: pd.DataFrame, evidence_type: str, filter_col: str | None = None, filter_value: str | None = None) -> list[dict[str, float | int | str]]:
    working = frame.copy()
    if filter_col is not None and filter_value is not None and filter_col in working.columns:
        working = working[working[filter_col].astype(str) == filter_value]
    rows: list[dict[str, float | int | str]] = []
    for model, group in working.groupby("model", sort=True):
        rows.append(
            {
                "evidence_type": evidence_type,
                "model": model,
                "metric_rows": int(len(group)),
                "total_rows": int(pd.to_numeric(group["rows"], errors="coerce").fillna(0).sum()),
                "mean_precision": float(pd.to_numeric(group["precision"], errors="coerce").mean()),
                "mean_recall": float(pd.to_numeric(group["recall"], errors="coerce").mean()),
                "mean_false_alarm_rate": float(pd.to_numeric(group["false_alarm_rate"], errors="coerce").mean()),
                "mean_accuracy": float(pd.to_numeric(group["accuracy"], errors="coerce").mean()),
            }
        )
    return rows


def summarize_predictive_validation(
    baseline_metrics: pd.DataFrame,
    temporal_metrics: pd.DataFrame,
    spatial_metrics: pd.DataFrame,
) -> PredictiveValidationSummary:
    _require_metric_columns(baseline_metrics, "Baseline")
    _require_metric_columns(temporal_metrics, "Temporal holdout")
    _require_metric_columns(spatial_metrics, "Spatial holdout")

    rows: list[dict[str, float | int | str]] = []
    rows.extend(_mean_metric_rows(baseline_metrics, "baseline_holdout", "split", "holdout"))
    rows.extend(_mean_metric_rows(temporal_metrics, "temporal_holdout", "split", "holdout"))
    rows.extend(_mean_metric_rows(spatial_metrics, "spatial_holdout"))
    summary = pd.DataFrame(rows)
    qc = {
        "baseline_metric_rows": int(len(baseline_metrics)),
        "temporal_metric_rows": int(len(temporal_metrics)),
        "spatial_metric_rows": int(len(spatial_metrics)),
        "summary_rows": int(len(summary)),
        "evidence_types": ",".join(sorted(summary["evidence_type"].unique())) if not summary.empty else "NA",
    }
    return PredictiveValidationSummary(summary=summary, qc=qc)


def render_predictive_validation_report(
    result: PredictiveValidationSummary,
    baseline_path: str | Path,
    temporal_path: str | Path,
    spatial_path: str | Path,
) -> str:
    lines = [
        "# Predictive validation summary report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes baseline, temporal-holdout and spatial-holdout metrics. It does not prove manuscript-ready improvement without uncertainty analysis and final model comparison.",
        "",
        f"- Baseline metrics: {Path(baseline_path).as_posix()}",
        f"- Temporal holdout metrics: {Path(temporal_path).as_posix()}",
        f"- Spatial holdout metrics: {Path(spatial_path).as_posix()}",
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
            "Do not claim predictive superiority until uncertainty intervals, matched baselines, temporal holdout, spatial holdout and ecological validation are complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_predictive_validation_readiness_report(
    baseline_path: str | Path,
    temporal_path: str | Path,
    spatial_path: str | Path,
) -> str:
    missing = [Path(path).as_posix() for path in (baseline_path, temporal_path, spatial_path) if not Path(path).exists()]
    lines = [
        "# Predictive validation summary readiness report",
        "",
        "Status: NOT_READY",
        "",
        "The command did not generate a predictive validation summary because required metric artifacts are missing.",
        "",
        "Required inputs:",
        "",
        f"- Baseline metrics: {Path(baseline_path).as_posix()}",
        f"- Temporal holdout metrics: {Path(temporal_path).as_posix()}",
        f"- Spatial holdout metrics: {Path(spatial_path).as_posix()}",
        "",
        "Missing inputs:",
        "",
    ]
    lines.extend(f"- {path}" for path in missing)
    return "\n".join(lines) + "\n"


def run_predictive_validation_summary_command(
    baseline_path: str | Path,
    temporal_path: str | Path,
    spatial_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> tuple[bool, Path]:
    baseline_file = Path(baseline_path)
    temporal_file = Path(temporal_path)
    spatial_file = Path(spatial_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not baseline_file.exists() or not temporal_file.exists() or not spatial_file.exists():
        report_file.write_text(
            render_predictive_validation_readiness_report(baseline_file, temporal_file, spatial_file),
            encoding="utf-8",
        )
        return False, report_file

    result = summarize_predictive_validation(
        baseline_metrics=pd.read_csv(baseline_file),
        temporal_metrics=pd.read_csv(temporal_file),
        spatial_metrics=pd.read_csv(spatial_file),
    )
    result.summary.to_csv(output_file, index=False)
    report_file.write_text(
        render_predictive_validation_report(result, baseline_file, temporal_file, spatial_file),
        encoding="utf-8",
    )
    return True, report_file
