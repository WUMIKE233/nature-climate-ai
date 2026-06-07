from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import load_study_config
from .metrics import binary_event_metrics
from .splits import label_year_split


@dataclass(frozen=True)
class BaselineEvaluationResult:
    metrics: pd.DataFrame
    qc: dict[str, int | str]


FAMILY_KEYWORDS = {
    "temperature_only": ("temperature", "temp", "2m_temperature", "t2m"),
    "precipitation_only": ("precipitation", "precip", "rain", "tp"),
    "soil_moisture_only": ("soil_moisture", "soil_water", "swvl", "soil"),
    "vpd_only": ("vpd", "vapour_pressure_deficit", "vapor_pressure_deficit", "vapour", "vapor"),
}

DROUGHT_FAMILIES = ("precipitation_only", "soil_moisture_only", "vpd_only")


def validate_modeling_dataset_frame(
    frame: pd.DataFrame,
    date_col: str = "date",
    label_col: str = "stress_event",
) -> None:
    required = {date_col, label_col}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Modeling dataset is missing required columns: {sorted(missing)}")
    feature_columns = [column for column in frame.columns if "_lag_" in column and column.endswith("d")]
    if not feature_columns:
        raise ValueError("Modeling dataset must include lag-feature columns.")
    if frame.empty:
        raise ValueError("Modeling dataset is empty.")


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    truth = np.asarray(y_true, dtype=bool)
    pred = np.asarray(y_pred, dtype=bool)
    return float((truth == pred).mean()) if truth.size else 0.0


def _row(model: str, split: str, y_true: np.ndarray, y_pred: np.ndarray, notes: str) -> dict[str, float | int | str]:
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


def _feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if "_lag_" in column and column.endswith("d")]


def _numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame[column], errors="coerce")


def _threshold_prediction(train: pd.DataFrame, data: pd.DataFrame, feature: str) -> tuple[np.ndarray, float]:
    threshold = float(_numeric_series(train, feature).median())
    pred = (_numeric_series(data, feature) >= threshold).fillna(False).astype(int).to_numpy()
    return pred, threshold


def _columns_for_family(feature_columns: list[str], family: str) -> list[str]:
    keywords = FAMILY_KEYWORDS[family]
    return [column for column in feature_columns if any(keyword in column.lower() for keyword in keywords)]


def _family_score(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    numeric = pd.concat((_numeric_series(frame, column) for column in columns), axis=1)
    return numeric.mean(axis=1)


def _compound_columns(feature_columns: list[str]) -> tuple[list[str], list[str]]:
    heat = _columns_for_family(feature_columns, "temperature_only")
    drought: list[str] = []
    for family in DROUGHT_FAMILIES:
        drought.extend(_columns_for_family(feature_columns, family))
    return heat, sorted(set(drought))


def evaluate_baselines(
    frame: pd.DataFrame,
    holdout_range: tuple[int, int],
    date_col: str = "date",
    label_col: str = "stress_event",
    unit_col: str = "pixel_id",
) -> BaselineEvaluationResult:
    validate_modeling_dataset_frame(frame, date_col, label_col)

    working = frame.copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[label_col] = pd.to_numeric(working[label_col], errors="coerce")
    working = working.dropna(subset=[date_col, label_col]).copy()
    working[label_col] = working[label_col].astype(int)
    sort_cols = [column for column in (unit_col, date_col) if column in working.columns]
    if sort_cols:
        working = working.sort_values(sort_cols).copy()
    working["split"] = label_year_split(working[date_col], holdout_range)

    train = working[working["split"] == "train"]
    holdout = working[working["split"] == "holdout"]
    if train.empty:
        raise ValueError("Baseline evaluation requires at least one training row.")
    if holdout.empty:
        raise ValueError("Baseline evaluation requires at least one holdout row.")

    rows: list[dict[str, float | int | str]] = []
    train_y = train[label_col].to_numpy()
    holdout_y = holdout[label_col].to_numpy()

    majority_value = int(train[label_col].mean() >= 0.5)
    for split_name, data, y_true in (("train", train, train_y), ("holdout", holdout, holdout_y)):
        pred = np.full(len(data), majority_value, dtype=int)
        rows.append(_row("majority_class", split_name, y_true, pred, f"constant={majority_value}"))

    prevalence_threshold = float(train[label_col].mean())
    prevalence_value = int(prevalence_threshold >= 0.5)
    for split_name, data, y_true in (("train", train, train_y), ("holdout", holdout, holdout_y)):
        pred = np.full(len(data), prevalence_value, dtype=int)
        rows.append(_row("training_prevalence", split_name, y_true, pred, f"prevalence={prevalence_threshold:.6f}"))

    if unit_col in working.columns:
        previous = working.groupby(unit_col, sort=False)[label_col].shift(1)
    else:
        previous = working[label_col].shift(1)
    working["previous_stress_event"] = previous.fillna(majority_value).astype(int)
    train = working[working["split"] == "train"]
    holdout = working[working["split"] == "holdout"]
    for split_name, data, y_true in (("train", train, train_y), ("holdout", holdout, holdout_y)):
        rows.append(
            _row(
                "persistence_previous_event",
                split_name,
                y_true,
                data["previous_stress_event"].to_numpy(),
                "previous observed stress_event within unit; fallback=training_majority",
            )
        )

    feature_columns = _feature_columns(working)
    for feature in feature_columns:
        train_pred, threshold = _threshold_prediction(train, train, feature)
        holdout_pred, _ = _threshold_prediction(train, holdout, feature)
        rows.append(_row(f"threshold:{feature}", "train", train_y, train_pred, f"median_threshold={threshold:.6f}"))
        rows.append(_row(f"threshold:{feature}", "holdout", holdout_y, holdout_pred, f"median_threshold={threshold:.6f}"))

    family_count = 0
    for family in FAMILY_KEYWORDS:
        family_columns = _columns_for_family(feature_columns, family)
        if not family_columns:
            continue
        family_count += 1
        train_score = _family_score(train, family_columns)
        threshold = float(train_score.median())
        for split_name, data, y_true in (("train", train, train_y), ("holdout", holdout, holdout_y)):
            pred = (_family_score(data, family_columns) >= threshold).fillna(False).astype(int).to_numpy()
            rows.append(
                _row(
                    f"family_threshold:{family}",
                    split_name,
                    y_true,
                    pred,
                    f"median_threshold={threshold:.6f}; features={len(family_columns)}",
                )
            )

    heat_columns, drought_columns = _compound_columns(feature_columns)
    compound_baseline_count = 0
    if heat_columns and drought_columns:
        compound_baseline_count = 1
        train_score = _family_score(train, heat_columns) + _family_score(train, drought_columns)
        threshold = float(train_score.median())
        for split_name, data, y_true in (("train", train, train_y), ("holdout", holdout, holdout_y)):
            score = _family_score(data, heat_columns) + _family_score(data, drought_columns)
            pred = (score >= threshold).fillna(False).astype(int).to_numpy()
            rows.append(
                _row(
                    "family_threshold:compound_heat_drought",
                    split_name,
                    y_true,
                    pred,
                    f"median_threshold={threshold:.6f}; heat_features={len(heat_columns)}; drought_features={len(drought_columns)}",
                )
            )

    metrics = pd.DataFrame(rows)
    qc = {
        "input_rows": int(len(frame)),
        "valid_rows": int(len(working)),
        "train_rows": int(len(train)),
        "holdout_rows": int(len(holdout)),
        "feature_count": int(len(feature_columns)),
        "family_baseline_count": int(family_count),
        "compound_baseline_count": int(compound_baseline_count),
        "holdout_range": f"{holdout_range[0]}-{holdout_range[1]}",
    }
    return BaselineEvaluationResult(metrics=metrics, qc=qc)


def render_baseline_report(result: BaselineEvaluationResult, input_path: str | Path) -> str:
    lines = [
        "# Baseline evaluation report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report summarizes simple baseline models for the supplied modeling dataset. It does not establish an AI-discovery claim or manuscript-ready result.",
        "",
        f"- Modeling dataset: {Path(input_path).as_posix()}",
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
            "Do not claim model improvement until AI models are evaluated on the same splits and compared against these baselines with uncertainty estimates.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_baseline_readiness_report(input_path: str | Path) -> str:
    return "\n".join(
        [
            "# Baseline evaluation readiness report",
            "",
            "Status: NOT_READY",
            "",
            f"Expected input table: {Path(input_path).as_posix()}",
            "",
            "The command did not generate baseline metrics because the modeling dataset is missing.",
            "",
            "Required input columns:",
            "",
            "- `date`",
            "- `stress_event`",
            "- at least one lag-feature column containing `_lag_` and ending in `d`",
        ]
    ) + "\n"


def run_baseline_evaluation_command(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    config_path: str | Path = "config/study.yaml",
) -> tuple[bool, Path]:
    input_file = Path(input_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        report_file.write_text(render_baseline_readiness_report(input_file), encoding="utf-8")
        return False, report_file

    config = load_study_config(config_path)
    holdout_range = tuple(config["validation"]["temporal_holdout_years"])
    result = evaluate_baselines(pd.read_csv(input_file), holdout_range=holdout_range)
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(render_baseline_report(result, input_file), encoding="utf-8")
    return True, report_file
