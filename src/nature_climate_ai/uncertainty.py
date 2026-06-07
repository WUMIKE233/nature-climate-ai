from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


CONFUSION_COLUMNS = {"true_positive", "false_positive", "false_negative", "true_negative"}


@dataclass(frozen=True)
class UncertaintyAuditResult:
    intervals: pd.DataFrame
    qc: dict[str, int | str]


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials < 0 or successes < 0:
        raise ValueError("successes and trials must be non-negative.")
    if successes > trials:
        raise ValueError("successes cannot exceed trials.")
    if trials == 0:
        return 0.0, 0.0
    phat = successes / trials
    denom = 1 + z**2 / trials
    centre = (phat + z**2 / (2 * trials)) / denom
    margin = z * ((phat * (1 - phat) + z**2 / (4 * trials)) / trials) ** 0.5 / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def _require_confusion_counts(frame: pd.DataFrame, name: str) -> None:
    missing = CONFUSION_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"{name} metrics are missing confusion-count columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"{name} metrics are empty.")


def _interval_rows(frame: pd.DataFrame, evidence_type: str, split_filter: str | None = None) -> list[dict[str, float | int | str]]:
    working = frame.copy()
    if split_filter is not None and "split" in working.columns:
        working = working[working["split"].astype(str) == split_filter]
    rows: list[dict[str, float | int | str]] = []
    for _, row in working.iterrows():
        tp = int(row["true_positive"])
        fp = int(row["false_positive"])
        fn = int(row["false_negative"])
        tn = int(row["true_negative"])
        definitions = {
            "precision": (tp, tp + fp),
            "recall": (tp, tp + fn),
            "false_alarm_rate": (fp, fp + tn),
            "accuracy": (tp + tn, tp + fp + fn + tn),
        }
        for metric, (successes, trials) in definitions.items():
            low, high = wilson_interval(successes, trials)
            output = {
                "evidence_type": evidence_type,
                "model": row.get("model", "unknown"),
                "metric": metric,
                "successes": successes,
                "trials": trials,
                "estimate": float(successes / trials) if trials else 0.0,
                "ci_low": low,
                "ci_high": high,
            }
            if "split" in row:
                output["split"] = row["split"]
            if "heldout_region" in row:
                output["heldout_region"] = row["heldout_region"]
            rows.append(output)
    return rows


def audit_validation_uncertainty(
    baseline_metrics: pd.DataFrame,
    temporal_metrics: pd.DataFrame,
    spatial_metrics: pd.DataFrame,
) -> UncertaintyAuditResult:
    _require_confusion_counts(baseline_metrics, "Baseline")
    _require_confusion_counts(temporal_metrics, "Temporal holdout")
    _require_confusion_counts(spatial_metrics, "Spatial holdout")

    rows: list[dict[str, float | int | str]] = []
    rows.extend(_interval_rows(baseline_metrics, "baseline_holdout", split_filter="holdout"))
    rows.extend(_interval_rows(temporal_metrics, "temporal_holdout", split_filter="holdout"))
    rows.extend(_interval_rows(spatial_metrics, "spatial_holdout"))
    intervals = pd.DataFrame(rows)
    qc = {
        "baseline_rows": int(len(baseline_metrics)),
        "temporal_rows": int(len(temporal_metrics)),
        "spatial_rows": int(len(spatial_metrics)),
        "interval_rows": int(len(intervals)),
        "confidence_method": "Wilson score interval, z=1.96",
    }
    return UncertaintyAuditResult(intervals=intervals, qc=qc)


def render_uncertainty_report(result: UncertaintyAuditResult, baseline_path: str | Path, temporal_path: str | Path, spatial_path: str | Path) -> str:
    lines = [
        "# Validation uncertainty audit",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report computes Wilson score intervals from saved confusion-count metrics. It does not replace block bootstrap, spatial autocorrelation checks or final manuscript uncertainty analysis.",
        "",
        f"- Baseline metrics: {Path(baseline_path).as_posix()}",
        f"- Temporal holdout metrics: {Path(temporal_path).as_posix()}",
        f"- Spatial holdout metrics: {Path(spatial_path).as_posix()}",
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
            "Use these intervals as an initial event-metric uncertainty audit only. Nature/Science-level claims still require resampling that respects spatial and temporal dependence.",
            "",
            "## 中文审阅说明",
            "",
            "本报告根据混淆矩阵计数生成 Wilson 区间，只能作为预测指标不确定性的初步审计。最终论文仍需要考虑空间和时间相关性的 bootstrap 或同等方法。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_uncertainty_readiness_report(baseline_path: str | Path, temporal_path: str | Path, spatial_path: str | Path) -> str:
    missing = [Path(path).as_posix() for path in (baseline_path, temporal_path, spatial_path) if not Path(path).exists()]
    lines = [
        "# Validation uncertainty readiness report",
        "",
        "Status: NOT_READY",
        "",
        "The command did not generate uncertainty intervals because required metric artifacts are missing.",
        "",
        "Required inputs:",
        "",
        f"- Baseline metrics: {Path(baseline_path).as_posix()}",
        f"- Temporal holdout metrics: {Path(temporal_path).as_posix()}",
        f"- Spatial holdout metrics: {Path(spatial_path).as_posix()}",
        "",
        "Required metric columns:",
        "",
        "- true_positive",
        "- false_positive",
        "- false_negative",
        "- true_negative",
        "",
        "Missing inputs:",
        "",
    ]
    lines.extend(f"- {path}" for path in missing)
    return "\n".join(lines) + "\n"


def run_uncertainty_audit_command(
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
        report_file.write_text(render_uncertainty_readiness_report(baseline_file, temporal_file, spatial_file), encoding="utf-8")
        return False, report_file

    result = audit_validation_uncertainty(
        baseline_metrics=pd.read_csv(baseline_file),
        temporal_metrics=pd.read_csv(temporal_file),
        spatial_metrics=pd.read_csv(spatial_file),
    )
    result.intervals.to_csv(output_file, index=False)
    report_file.write_text(render_uncertainty_report(result, baseline_file, temporal_file, spatial_file), encoding="utf-8")
    return True, report_file
