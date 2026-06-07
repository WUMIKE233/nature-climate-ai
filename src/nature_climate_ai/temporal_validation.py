from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import load_study_config
from .metrics import binary_event_metrics
from .splits import label_year_split


@dataclass(frozen=True)
class TemporalValidationResult:
    metrics: pd.DataFrame
    qc: dict[str, int | str]


def validate_temporal_validation_inputs(
    modeling: pd.DataFrame,
    candidates: pd.DataFrame,
    label_col: str = "stress_event",
) -> None:
    if label_col not in modeling.columns:
        raise ValueError(f"Modeling dataset is missing label column: {label_col}")
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


def _metric_row(model: str, split: str, y_true: np.ndarray, y_pred: np.ndarray, notes: str) -> dict[str, float | int | str]:
    metrics = binary_event_metrics(y_true, y_pred)
    return {
        "model": model,
        "split": split,
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


def temporal_holdout_validate_candidates(
    modeling: pd.DataFrame,
    candidates: pd.DataFrame,
    holdout_range: tuple[int, int],
    top_n: int = 10,
    date_col: str = "date",
    label_col: str = "stress_event",
) -> TemporalValidationResult:
    validate_temporal_validation_inputs(modeling, candidates, label_col)
    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    working = modeling.copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[label_col] = pd.to_numeric(working[label_col], errors="coerce")
    working = working.dropna(subset=[date_col, label_col]).copy()
    working[label_col] = working[label_col].astype(int)
    working["split"] = label_year_split(working[date_col], holdout_range)
    train = working[working["split"] == "train"]
    holdout = working[working["split"] == "holdout"]
    if train.empty:
        raise ValueError("Temporal validation requires at least one training row.")
    if holdout.empty:
        raise ValueError("Temporal validation requires at least one holdout row.")

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
    train_y = train[label_col].to_numpy()
    holdout_y = holdout[label_col].to_numpy()
    for feature in selected_features:
        threshold = float(pd.to_numeric(train[feature], errors="coerce").median())
        train_pred = (pd.to_numeric(train[feature], errors="coerce") >= threshold).fillna(False).astype(int).to_numpy()
        holdout_pred = (pd.to_numeric(holdout[feature], errors="coerce") >= threshold).fillna(False).astype(int).to_numpy()
        rows.append(_metric_row(f"candidate_threshold:{feature}", "train", train_y, train_pred, f"median_threshold={threshold:.6f}"))
        rows.append(_metric_row(f"candidate_threshold:{feature}", "holdout", holdout_y, holdout_pred, f"median_threshold={threshold:.6f}"))

    metrics = pd.DataFrame(rows)
    qc = {
        "modeling_rows": int(len(modeling)),
        "candidate_rows": int(len(candidates)),
        "selected_features": int(len(selected_features)),
        "train_rows": int(len(train)),
        "holdout_rows": int(len(holdout)),
        "holdout_range": f"{holdout_range[0]}-{holdout_range[1]}",
    }
    return TemporalValidationResult(metrics=metrics, qc=qc)


def render_temporal_validation_report(result: TemporalValidationResult, modeling_path: str | Path, candidates_path: str | Path) -> str:
    lines = [
        "# Temporal holdout validation report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report evaluates ranked precursor candidates on the configured temporal holdout. It does not establish full predictive validation without spatial holdout and uncertainty analysis.",
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
            "Do not claim predictive improvement until temporal holdout, spatial holdout, baseline comparison and uncertainty estimates are all complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_temporal_validation_readiness_report(modeling_path: str | Path, candidates_path: str | Path) -> str:
    missing = [Path(path).as_posix() for path in (modeling_path, candidates_path) if not Path(path).exists()]
    lines = [
        "# Temporal holdout validation readiness report",
        "",
        "Status: NOT_READY",
        "",
        "The command did not generate temporal holdout metrics because required inputs are missing.",
        "",
        "Required inputs:",
        "",
        f"- Modeling dataset: {Path(modeling_path).as_posix()}",
        f"- Candidate table: {Path(candidates_path).as_posix()}",
        "",
        "Missing inputs:",
        "",
    ]
    lines.extend(f"- {path}" for path in missing)
    return "\n".join(lines) + "\n"


def run_temporal_validation_command(
    modeling_path: str | Path,
    candidates_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    config_path: str | Path = "config/study.yaml",
    top_n: int = 10,
) -> tuple[bool, Path]:
    modeling_file = Path(modeling_path)
    candidates_file = Path(candidates_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not modeling_file.exists() or not candidates_file.exists():
        report_file.write_text(render_temporal_validation_readiness_report(modeling_file, candidates_file), encoding="utf-8")
        return False, report_file

    config = load_study_config(config_path)
    holdout_range = tuple(config["validation"]["temporal_holdout_years"])
    result = temporal_holdout_validate_candidates(
        modeling=pd.read_csv(modeling_file),
        candidates=pd.read_csv(candidates_file),
        holdout_range=holdout_range,
        top_n=top_n,
    )
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(render_temporal_validation_report(result, modeling_file, candidates_file), encoding="utf-8")
    return True, report_file
