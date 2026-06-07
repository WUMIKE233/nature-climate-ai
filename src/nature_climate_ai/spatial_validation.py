from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .metrics import binary_event_metrics


@dataclass(frozen=True)
class SpatialValidationResult:
    metrics: pd.DataFrame
    qc: dict[str, int | str]


def validate_spatial_validation_inputs(
    modeling: pd.DataFrame,
    candidates: pd.DataFrame,
    region_col: str = "region",
    label_col: str = "stress_event",
) -> None:
    if label_col not in modeling.columns:
        raise ValueError(f"Modeling dataset is missing label column: {label_col}")
    if region_col not in modeling.columns:
        raise ValueError(f"Modeling dataset is missing spatial holdout column: {region_col}")
    if "feature" not in candidates.columns:
        raise ValueError("Candidate table is missing required column: feature")
    if modeling.empty:
        raise ValueError("Modeling dataset is empty.")
    if candidates.empty:
        raise ValueError("Candidate table is empty.")


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    truth = np.asarray(y_true, dtype=bool)
    pred = np.asarray(y_pred, dtype=bool)
    return float((truth == pred).mean()) if truth.size else 0.0


def _metric_row(
    model: str,
    heldout_region: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    notes: str,
) -> dict[str, float | int | str]:
    metrics = binary_event_metrics(y_true, y_pred)
    return {
        "model": model,
        "heldout_region": heldout_region,
        "rows": int(len(y_true)),
        "positive_labels": int(np.asarray(y_true, dtype=bool).sum()),
        "true_positive": metrics.true_positive,
        "false_positive": metrics.false_positive,
        "false_negative": metrics.false_negative,
        "true_negative": metrics.true_negative,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "false_alarm_rate": metrics.false_alarm_rate,
        "accuracy": _accuracy(y_true, y_pred),
        "notes": notes,
    }


def spatial_holdout_validate_candidates(
    modeling: pd.DataFrame,
    candidates: pd.DataFrame,
    region_col: str = "region",
    label_col: str = "stress_event",
    top_n: int = 10,
) -> SpatialValidationResult:
    validate_spatial_validation_inputs(modeling, candidates, region_col, label_col)
    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    working = modeling.copy()
    working[label_col] = pd.to_numeric(working[label_col], errors="coerce")
    working = working.dropna(subset=[region_col, label_col]).copy()
    working[label_col] = working[label_col].astype(int)
    regions = sorted(str(region) for region in working[region_col].dropna().unique())
    if len(regions) < 2:
        raise ValueError("Spatial holdout validation requires at least two regions.")

    ordered_candidates = candidates.copy()
    if "absolute_correlation" in ordered_candidates.columns:
        ordered_candidates["absolute_correlation"] = pd.to_numeric(
            ordered_candidates["absolute_correlation"],
            errors="coerce",
        ).fillna(0.0)
        ordered_candidates = ordered_candidates.sort_values("absolute_correlation", ascending=False)

    selected_features = [
        feature
        for feature in ordered_candidates["feature"].astype(str).tolist()
        if feature in working.columns
    ][:top_n]
    if not selected_features:
        raise ValueError("No candidate features are present in the modeling dataset.")

    rows: list[dict[str, float | int | str]] = []
    for region in regions:
        holdout = working[working[region_col].astype(str) == region]
        train = working[working[region_col].astype(str) != region]
        if train.empty or holdout.empty:
            continue
        y_true = holdout[label_col].to_numpy()
        for feature in selected_features:
            threshold = float(pd.to_numeric(train[feature], errors="coerce").median())
            pred = (pd.to_numeric(holdout[feature], errors="coerce") >= threshold).fillna(False).astype(int).to_numpy()
            rows.append(
                _metric_row(
                    model=f"candidate_threshold:{feature}",
                    heldout_region=region,
                    y_true=y_true,
                    y_pred=pred,
                    notes=f"median_threshold={threshold:.6f}",
                )
            )

    metrics = pd.DataFrame(rows)
    qc = {
        "modeling_rows": int(len(modeling)),
        "candidate_rows": int(len(candidates)),
        "selected_features": int(len(selected_features)),
        "regions": int(len(regions)),
        "metric_rows": int(len(metrics)),
        "region_column": region_col,
    }
    return SpatialValidationResult(metrics=metrics, qc=qc)


def render_spatial_validation_report(result: SpatialValidationResult, modeling_path: str | Path, candidates_path: str | Path) -> str:
    lines = [
        "# Spatial holdout validation report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report evaluates ranked precursor candidates under leave-one-region-out validation. It does not establish full predictive validation without temporal holdout, baseline comparison and uncertainty analysis.",
        "",
        f"- Modeling dataset: {Path(modeling_path).as_posix()}",
        f"- Candidate table: {Path(candidates_path).as_posix()}",
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
            "Do not claim spatial generalization until region definitions, spatial coverage, baseline comparisons and uncertainty estimates are complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_spatial_validation_readiness_report(modeling_path: str | Path, candidates_path: str | Path, region_col: str) -> str:
    missing = [Path(path).as_posix() for path in (modeling_path, candidates_path) if not Path(path).exists()]
    lines = [
        "# Spatial holdout validation readiness report",
        "",
        "Status: NOT_READY",
        "",
        "The command did not generate spatial holdout metrics because required inputs are missing.",
        "",
        "Required inputs:",
        "",
        f"- Modeling dataset: {Path(modeling_path).as_posix()}",
        f"- Candidate table: {Path(candidates_path).as_posix()}",
        "",
        "Required modeling-dataset columns:",
        "",
        "- `stress_event`",
        f"- `{region_col}`",
        "- candidate lag-feature columns",
        "",
        "Missing inputs:",
        "",
    ]
    lines.extend(f"- {path}" for path in missing)
    return "\n".join(lines) + "\n"


def run_spatial_validation_command(
    modeling_path: str | Path,
    candidates_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    region_col: str = "region",
    top_n: int = 10,
) -> tuple[bool, Path]:
    modeling_file = Path(modeling_path)
    candidates_file = Path(candidates_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not modeling_file.exists() or not candidates_file.exists():
        report_file.write_text(render_spatial_validation_readiness_report(modeling_file, candidates_file, region_col), encoding="utf-8")
        return False, report_file

    result = spatial_holdout_validate_candidates(
        modeling=pd.read_csv(modeling_file),
        candidates=pd.read_csv(candidates_file),
        region_col=region_col,
        top_n=top_n,
    )
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(render_spatial_validation_report(result, modeling_file, candidates_file), encoding="utf-8")
    return True, report_file
