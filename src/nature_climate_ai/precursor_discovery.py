from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


LAG_PATTERN = re.compile(r"^(?P<variable>.+)_anomaly_lag_(?P<lag_days>\d+)d$")


@dataclass(frozen=True)
class PrecursorDiscoveryResult:
    attribution: pd.DataFrame
    lag_response: pd.DataFrame
    qc: dict[str, int | str]


def lag_feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if LAG_PATTERN.match(column)]


def parse_lag_feature(column: str) -> tuple[str, int]:
    match = LAG_PATTERN.match(column)
    if not match:
        raise ValueError(f"Not a supported lag feature column: {column}")
    return match.group("variable"), int(match.group("lag_days"))


def validate_precursor_frame(
    frame: pd.DataFrame,
    label_col: str = "stress_event",
) -> None:
    if label_col not in frame.columns:
        raise ValueError(f"Modeling dataset is missing required label column: {label_col}")
    if frame.empty:
        raise ValueError("Modeling dataset is empty.")
    if not lag_feature_columns(frame):
        raise ValueError("Modeling dataset must include supported lag-feature columns.")


def _safe_correlation(values: pd.Series, labels: pd.Series) -> float:
    x = pd.to_numeric(values, errors="coerce")
    y = pd.to_numeric(labels, errors="coerce")
    valid = ~(x.isna() | y.isna())
    if valid.sum() < 2:
        return 0.0
    if x[valid].nunique() < 2 or y[valid].nunique() < 2:
        return 0.0
    return float(np.corrcoef(x[valid].to_numpy(), y[valid].to_numpy())[0, 1])


def discover_precursor_candidates(
    frame: pd.DataFrame,
    label_col: str = "stress_event",
) -> PrecursorDiscoveryResult:
    validate_precursor_frame(frame, label_col)

    working = frame.copy()
    working[label_col] = pd.to_numeric(working[label_col], errors="coerce")
    working = working.dropna(subset=[label_col]).copy()
    working[label_col] = working[label_col].astype(int)

    rows: list[dict[str, float | int | str]] = []
    for feature in lag_feature_columns(working):
        variable, lag_days = parse_lag_feature(feature)
        values = pd.to_numeric(working[feature], errors="coerce")
        positive = values[working[label_col] == 1].dropna()
        negative = values[working[label_col] == 0].dropna()
        positive_mean = float(positive.mean()) if not positive.empty else 0.0
        negative_mean = float(negative.mean()) if not negative.empty else 0.0
        mean_difference = positive_mean - negative_mean
        correlation = _safe_correlation(values, working[label_col])
        rows.append(
            {
                "feature": feature,
                "variable": variable,
                "lag_days": lag_days,
                "rows_used": int(values.notna().sum()),
                "positive_rows": int(positive.shape[0]),
                "negative_rows": int(negative.shape[0]),
                "positive_mean": positive_mean,
                "negative_mean": negative_mean,
                "mean_difference": float(mean_difference),
                "absolute_mean_difference": float(abs(mean_difference)),
                "correlation_with_label": correlation,
                "absolute_correlation": float(abs(correlation)),
            }
        )

    attribution = pd.DataFrame(rows).sort_values(
        ["absolute_correlation", "absolute_mean_difference", "feature"],
        ascending=[False, False, True],
    )
    lag_response = (
        attribution.groupby(["variable", "lag_days"], as_index=False)
        .agg(
            feature_count=("feature", "count"),
            mean_absolute_correlation=("absolute_correlation", "mean"),
            mean_absolute_difference=("absolute_mean_difference", "mean"),
            max_absolute_correlation=("absolute_correlation", "max"),
        )
        .sort_values(["max_absolute_correlation", "mean_absolute_difference"], ascending=[False, False])
    )
    qc = {
        "input_rows": int(len(frame)),
        "valid_rows": int(len(working)),
        "feature_count": int(len(attribution)),
        "positive_labels": int((working[label_col] == 1).sum()),
        "negative_labels": int((working[label_col] == 0).sum()),
        "top_feature": str(attribution.iloc[0]["feature"]) if not attribution.empty else "NA",
    }
    return PrecursorDiscoveryResult(attribution=attribution, lag_response=lag_response, qc=qc)


def render_precursor_report(result: PrecursorDiscoveryResult, input_path: str | Path) -> str:
    lines = [
        "# Interpretable precursor-discovery report",
        "",
        "Status: COMPLETE_FOR_INPUT_DATA",
        "",
        "This report ranks lagged climate features as candidate vegetation-stress precursors. It does not establish a manuscript-ready discovery claim.",
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
            "Do not promote ranked precursor candidates into the Nature or Science manuscript until baseline comparison, temporal holdout, spatial holdout, uncertainty analysis and FLUXNET validation are complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_precursor_readiness_report(input_path: str | Path) -> str:
    return "\n".join(
        [
            "# Interpretable precursor-discovery readiness report",
            "",
            "Status: NOT_READY",
            "",
            f"Expected input table: {Path(input_path).as_posix()}",
            "",
            "The command did not generate precursor-discovery artifacts because the modeling dataset is missing.",
            "",
            "Required input columns:",
            "",
            "- `stress_event`",
            "- at least one lag-feature column like `<variable>_anomaly_lag_<days>d`",
        ]
    ) + "\n"


def run_precursor_discovery_command(
    input_path: str | Path,
    attribution_path: str | Path,
    lag_response_path: str | Path,
    report_path: str | Path,
) -> tuple[bool, Path]:
    input_file = Path(input_path)
    attribution_file = Path(attribution_path)
    lag_file = Path(lag_response_path)
    report_file = Path(report_path)
    attribution_file.parent.mkdir(parents=True, exist_ok=True)
    lag_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        report_file.write_text(render_precursor_readiness_report(input_file), encoding="utf-8")
        return False, report_file

    result = discover_precursor_candidates(pd.read_csv(input_file))
    result.attribution.to_csv(attribution_file, index=False)
    result.lag_response.to_csv(lag_file, index=False)
    report_file.write_text(render_precursor_report(result, input_file), encoding="utf-8")
    return True, report_file
