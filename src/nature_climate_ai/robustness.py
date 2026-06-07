from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .event_catalogue import build_event_catalogue
from .metrics import binary_event_metrics


@dataclass(frozen=True)
class RobustnessResult:
    metrics: pd.DataFrame
    qc: dict[str, int | float | str]


def _lag_features(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if "_lag_" in column and column.endswith("d")]


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    truth = np.asarray(y_true, dtype=bool)
    pred = np.asarray(y_pred, dtype=bool)
    return float((truth == pred).mean()) if truth.size else 0.0


def _metric_row(test: str, group: str, feature: str, y_true: np.ndarray, y_pred: np.ndarray, notes: str) -> dict[str, float | int | str]:
    metrics = binary_event_metrics(y_true, y_pred)
    return {
        "test": test,
        "group": group,
        "feature": feature,
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


def _validate_modeling(frame: pd.DataFrame, label_col: str = "stress_event") -> list[str]:
    if frame.empty:
        raise ValueError("Modeling dataset is empty.")
    if label_col not in frame.columns:
        raise ValueError(f"Modeling dataset is missing label column: {label_col}")
    features = _lag_features(frame)
    if not features:
        raise ValueError("Modeling dataset must include lag-feature columns.")
    return features


def placebo_validate(frame: pd.DataFrame, label_col: str = "stress_event", unit_col: str = "pixel_id", top_n: int = 10) -> RobustnessResult:
    features = _validate_modeling(frame, label_col)
    working = frame.copy()
    working[label_col] = pd.to_numeric(working[label_col], errors="coerce")
    working = working.dropna(subset=[label_col]).copy()
    working[label_col] = working[label_col].astype(int)
    if "date" in working.columns:
        working["date"] = pd.to_datetime(working["date"], errors="coerce")
        sort_cols = [column for column in (unit_col, "date") if column in working.columns]
        if sort_cols:
            working = working.sort_values(sort_cols).copy()

    selected = features[:top_n]
    if unit_col in working.columns:
        placebo = working.groupby(unit_col, sort=False)[label_col].shift(1)
        fallback = working.groupby(unit_col, sort=False)[label_col].transform("last")
        working["placebo_label"] = placebo.fillna(fallback).astype(int)
    else:
        working["placebo_label"] = working[label_col].shift(1, fill_value=working[label_col].iloc[-1]).astype(int)

    rows: list[dict[str, float | int | str]] = []
    for feature in selected:
        values = pd.to_numeric(working[feature], errors="coerce")
        threshold = float(values.median())
        pred = (values >= threshold).fillna(False).astype(int).to_numpy()
        rows.append(
            _metric_row(
                test="lag-shift placebo",
                group="all",
                feature=feature,
                y_true=working["placebo_label"].to_numpy(),
                y_pred=pred,
                notes=f"label_shift=one_previous_observation; median_threshold={threshold:.6f}",
            )
        )

    return RobustnessResult(
        metrics=pd.DataFrame(rows),
        qc={
            "input_rows": int(len(frame)),
            "valid_rows": int(len(working)),
            "features_tested": int(len(selected)),
            "unit_column_present": str(unit_col in working.columns),
        },
    )


def threshold_sensitivity(
    anomalies: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    value_col: str = "evi_anomaly",
    percentiles: tuple[float, ...] = (5, 10, 15, 20),
    minimum_duration: int = 2,
) -> RobustnessResult:
    rows: list[dict[str, int | float | str]] = []
    for percentile in percentiles:
        result = build_event_catalogue(
            anomalies,
            date_col=date_col,
            unit_col=unit_col,
            value_col=value_col,
            percentile=percentile,
            minimum_duration=minimum_duration,
        )
        rows.append(
            {
                "test": "threshold_sensitivity",
                "percentile": float(percentile),
                "minimum_duration": int(minimum_duration),
                "event_count": result.event_count,
                "units_with_events": result.qc["units_with_events"],
                "input_rows": result.qc["input_rows"],
                "valid_rows": result.qc["valid_rows"],
            }
        )
    return RobustnessResult(
        metrics=pd.DataFrame(rows),
        qc={
            "input_rows": int(len(anomalies)),
            "percentiles_tested": int(len(percentiles)),
            "minimum_duration": int(minimum_duration),
        },
    )


def biome_stratified_validate(
    modeling: pd.DataFrame,
    biome_col: str = "biome",
    label_col: str = "stress_event",
    top_n: int = 10,
) -> RobustnessResult:
    features = _validate_modeling(modeling, label_col)
    if biome_col not in modeling.columns:
        raise ValueError(f"Modeling dataset is missing biome column: {biome_col}")
    working = modeling.copy()
    working[label_col] = pd.to_numeric(working[label_col], errors="coerce")
    working = working.dropna(subset=[biome_col, label_col]).copy()
    working[label_col] = working[label_col].astype(int)
    selected = features[:top_n]
    rows: list[dict[str, float | int | str]] = []
    for biome, group in working.groupby(biome_col, sort=True):
        y_true = group[label_col].to_numpy()
        for feature in selected:
            values = pd.to_numeric(group[feature], errors="coerce")
            threshold = float(values.median())
            pred = (values >= threshold).fillna(False).astype(int).to_numpy()
            rows.append(_metric_row("biome_stratified", str(biome), feature, y_true, pred, f"within_biome_median={threshold:.6f}"))
    return RobustnessResult(
        metrics=pd.DataFrame(rows),
        qc={
            "input_rows": int(len(modeling)),
            "valid_rows": int(len(working)),
            "biomes": int(working[biome_col].nunique()),
            "features_tested": int(len(selected)),
            "biome_column": biome_col,
        },
    )


def sensor_cross_validate(
    modis: pd.DataFrame,
    external: pd.DataFrame,
    date_col: str = "date",
    unit_col: str = "pixel_id",
    modis_value_col: str = "evi_anomaly",
    external_value_col: str = "external_anomaly",
    percentile: float = 10,
) -> RobustnessResult:
    required_modis = {date_col, unit_col, modis_value_col}
    required_external = {date_col, unit_col, external_value_col}
    missing_modis = required_modis.difference(modis.columns)
    missing_external = required_external.difference(external.columns)
    if missing_modis:
        raise ValueError(f"MODIS anomaly table is missing required columns: {sorted(missing_modis)}")
    if missing_external:
        raise ValueError(f"External anomaly table is missing required columns: {sorted(missing_external)}")

    left = modis[[date_col, unit_col, modis_value_col]].copy()
    right = external[[date_col, unit_col, external_value_col]].copy()
    left[date_col] = pd.to_datetime(left[date_col], errors="coerce")
    right[date_col] = pd.to_datetime(right[date_col], errors="coerce")
    merged = left.merge(right, on=[date_col, unit_col], how="inner").dropna()
    if merged.empty:
        raise ValueError("No overlapping MODIS and external anomaly observations.")

    modis_values = pd.to_numeric(merged[modis_value_col], errors="coerce")
    external_values = pd.to_numeric(merged[external_value_col], errors="coerce")
    merged = merged.assign(modis_value=modis_values, external_value=external_values).dropna(subset=["modis_value", "external_value"])
    if merged.empty:
        raise ValueError("No numeric overlapping anomaly observations.")

    modis_threshold = float(np.nanpercentile(merged["modis_value"], percentile))
    external_threshold = float(np.nanpercentile(merged["external_value"], percentile))
    modis_stress = (merged["modis_value"] <= modis_threshold).astype(int).to_numpy()
    external_stress = (merged["external_value"] <= external_threshold).astype(int).to_numpy()
    metrics = binary_event_metrics(external_stress, modis_stress)
    correlation = float(merged["modis_value"].corr(merged["external_value"]))
    rows = [
        {
            "test": "sensor_cross_validation",
            "rows": int(len(merged)),
            "units": int(merged[unit_col].nunique()),
            "percentile": float(percentile),
            "modis_threshold": modis_threshold,
            "external_threshold": external_threshold,
            "correlation": correlation,
            "true_positive": metrics.true_positive,
            "false_positive": metrics.false_positive,
            "false_negative": metrics.false_negative,
            "true_negative": metrics.true_negative,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "false_alarm_rate": metrics.false_alarm_rate,
        }
    ]
    return RobustnessResult(
        metrics=pd.DataFrame(rows),
        qc={
            "modis_rows": int(len(modis)),
            "external_rows": int(len(external)),
            "overlap_rows": int(len(merged)),
            "overlap_units": int(merged[unit_col].nunique()),
        },
    )


def _render_report(title: str, status: str, result: RobustnessResult | None, input_lines: list[str], warning: str) -> str:
    lines = [f"# {title}", "", f"Status: {status}", "", *input_lines]
    if result is not None:
        lines.extend(["", "## Summary", "", "metric | value", "--- | ---"])
        for key, value in result.qc.items():
            lines.append(f"{key} | {value}")
    lines.extend(["", "## Manuscript-use warning", "", warning, "", "## 中文审阅说明", "", "本报告用于稳健性或证伪检查。只有在真实输入数据、基线比较、不确定性分析和独立验证都完成后，才可以把相关结果写入主稿。"])
    return "\n".join(lines) + "\n"


def _write_readiness(report_file: Path, title: str, input_lines: list[str]) -> tuple[bool, Path]:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        _render_report(
            title=title,
            status="NOT_READY",
            result=None,
            input_lines=input_lines + ["", "Required inputs are missing, so no manuscript evidence was generated."],
            warning="This is a readiness report only.",
        ),
        encoding="utf-8",
    )
    return False, report_file


def run_placebo_validation_command(input_path: str | Path, output_path: str | Path, report_path: str | Path, top_n: int = 10) -> tuple[bool, Path]:
    input_file = Path(input_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    if not input_file.exists():
        return _write_readiness(report_file, "Placebo validation readiness report", [f"Expected modeling dataset: {input_file.as_posix()}"])
    result = placebo_validate(pd.read_csv(input_file), top_n=top_n)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(
        _render_report("Placebo validation report", "COMPLETE_FOR_INPUT_DATA", result, [f"Modeling dataset: {input_file.as_posix()}"], "Placebo metrics should be weak; strong placebo performance indicates leakage, persistence artifacts or an invalid precursor claim."),
        encoding="utf-8",
    )
    return True, report_file


def run_threshold_sensitivity_command(input_path: str | Path, output_path: str | Path, report_path: str | Path, minimum_duration: int = 2) -> tuple[bool, Path]:
    input_file = Path(input_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    if not input_file.exists():
        return _write_readiness(report_file, "Threshold sensitivity readiness report", [f"Expected MODIS anomaly table: {input_file.as_posix()}"])
    result = threshold_sensitivity(pd.read_csv(input_file), minimum_duration=minimum_duration)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(
        _render_report("Threshold sensitivity report", "COMPLETE_FOR_INPUT_DATA", result, [f"MODIS anomaly table: {input_file.as_posix()}"], "Stress-event conclusions should not depend on one arbitrary anomaly percentile."),
        encoding="utf-8",
    )
    return True, report_file


def run_biome_stratified_validation_command(modeling_path: str | Path, biome_col: str, output_path: str | Path, report_path: str | Path, top_n: int = 10) -> tuple[bool, Path]:
    modeling_file = Path(modeling_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    if not modeling_file.exists():
        return _write_readiness(report_file, "Biome-stratified validation readiness report", [f"Expected modeling dataset: {modeling_file.as_posix()}", f"Biome column: {biome_col}"])
    result = biome_stratified_validate(pd.read_csv(modeling_file), biome_col=biome_col, top_n=top_n)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(
        _render_report("Biome-stratified validation report", "COMPLETE_FOR_INPUT_DATA", result, [f"Modeling dataset: {modeling_file.as_posix()}", f"Biome column: {biome_col}"], "Biome metrics are descriptive robustness checks and do not replace spatial holdout validation."),
        encoding="utf-8",
    )
    return True, report_file


def run_sensor_cross_validation_command(modis_path: str | Path, external_path: str | Path, output_path: str | Path, report_path: str | Path) -> tuple[bool, Path]:
    modis_file = Path(modis_path)
    external_file = Path(external_path)
    output_file = Path(output_path)
    report_file = Path(report_path)
    if not modis_file.exists() or not external_file.exists():
        return _write_readiness(
            report_file,
            "Sensor cross-validation readiness report",
            [f"Expected MODIS anomaly table: {modis_file.as_posix()}", f"Expected external anomaly table: {external_file.as_posix()}"],
        )
    result = sensor_cross_validate(pd.read_csv(modis_file), pd.read_csv(external_file))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    result.metrics.to_csv(output_file, index=False)
    report_file.write_text(
        _render_report("Sensor cross-validation report", "COMPLETE_FOR_INPUT_DATA", result, [f"MODIS anomaly table: {modis_file.as_posix()}", f"External anomaly table: {external_file.as_posix()}"], "Cross-sensor agreement supports event-definition robustness but does not by itself prove a climate precursor mechanism."),
        encoding="utf-8",
    )
    return True, report_file
