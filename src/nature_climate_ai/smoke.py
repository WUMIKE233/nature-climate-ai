from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .baselines import run_baseline_evaluation_command
from .climate_features import run_climate_feature_command
from .event_catalogue import run_event_catalogue_command
from .modeling_dataset import run_modeling_dataset_command
from .modis_anomalies import run_modis_anomaly_command
from .modis_quality import run_modis_quality_command
from .precursor_discovery import run_precursor_discovery_command
from .predictive_validation import run_predictive_validation_summary_command
from .spatial_validation import run_spatial_validation_command
from .temporal_validation import run_temporal_validation_command
from .uncertainty import run_uncertainty_audit_command


@dataclass(frozen=True)
class SmokeWorkflowResult:
    output_dir: Path
    report_path: Path
    manifest_path: Path
    artifacts: tuple[Path, ...]


def _write_synthetic_modis(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dates = ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18", "2021-01-01", "2021-01-17", "2021-02-02", "2021-02-18"]
    rows: list[dict[str, object]] = []
    for pixel, offset in (("p1", 0.0), ("p2", 0.03)):
        for date in dates:
            stress = date in {"2021-01-17", "2021-02-02"}
            rows.append(
                {
                    "date": date,
                    "pixel_id": pixel,
                    "evi": (0.22 if stress else 0.62) + offset,
                    "ndvi": (0.30 if stress else 0.72) + offset,
                    "vi_quality": 0,
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _write_synthetic_climate(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dates = ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18", "2021-01-01", "2021-01-17", "2021-02-02", "2021-02-18"]
    rows: list[dict[str, object]] = []
    for pixel, region_offset in (("p1", 0.0), ("p2", 0.2)):
        for date in dates:
            precursor = date in {"2021-01-01", "2021-01-17"}
            rows.append(
                {
                    "date": date,
                    "pixel_id": pixel,
                    "2m_temperature": (305.0 if precursor else 295.0) + region_offset,
                    "total_precipitation": 0.05 if precursor else 1.0,
                    "soil_moisture": 0.08 if precursor else 0.30,
                    "surface_net_solar_radiation": 220.0 if precursor else 180.0,
                    "vapour_pressure_deficit": 2.2 if precursor else 0.8,
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _add_regions(modeling_path: Path) -> None:
    frame = pd.read_csv(modeling_path)
    frame["region"] = frame["pixel_id"].map({"p1": "north", "p2": "south"}).fillna("unknown")
    frame.to_csv(modeling_path, index=False)


def _write_manifest(paths: tuple[Path, ...], manifest_path: Path) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["artifact", "bytes"])
        writer.writeheader()
        for path in paths:
            writer.writerow({"artifact": path.as_posix(), "bytes": path.stat().st_size if path.exists() else 0})
    return manifest_path


def _render_report(result: SmokeWorkflowResult) -> str:
    return "\n".join(
        [
            "# Synthetic pipeline smoke-test report",
            "",
            "Status: COMPLETE_FOR_SYNTHETIC_DATA",
            "",
            "This report verifies that the local scaffold can run an end-to-end synthetic workflow. The generated data are artificial and must not be used as manuscript evidence or scientific results.",
            "",
            f"- Smoke output directory: {result.output_dir.as_posix()}",
            f"- Artifact manifest: {result.manifest_path.as_posix()}",
            "",
            "## Generated artifacts",
            "",
            "artifact | exists",
            "--- | ---",
            *[f"{path.as_posix()} | {path.exists()}" for path in result.artifacts],
            "",
            "## Manuscript-use warning",
            "",
            "Do not cite, plot or promote smoke-test outputs in the Nature or Science manuscript. This workflow is an engineering reproducibility check only.",
            "",
            "## 中文审阅说明",
            "",
            "本报告只证明项目脚手架可以用合成数据端到端运行。合成数据和 smoke-test 输出不能作为论文结果、图件或科学结论。",
        ]
    ) + "\n"


def run_pipeline_smoke_test_command(
    output_dir: str | Path = "outputs/smoke",
    report_path: str | Path = "reproducibility/pipeline_smoke_report.md",
    manifest_path: str | Path = "reproducibility/pipeline_smoke_manifest.csv",
    config_path: str | Path = "config/study.yaml",
) -> SmokeWorkflowResult:
    root = Path(output_dir)
    raw = root / "raw"
    interim = root / "interim"
    processed = root / "processed"
    validation = root / "validation"
    modeling = root / "modeling"
    stress = root / "stress_events"
    qc = root / "qc"

    modis_raw = _write_synthetic_modis(raw / "modis_observations.csv")
    climate_raw = _write_synthetic_climate(interim / "era5_composite_climate.csv")

    modis_filtered = interim / "modis_quality_filtered.csv"
    modis_anomalies = processed / "modis_anomalies.csv"
    event_catalogue = stress / "event_catalogue_summary.csv"
    climate_features = processed / "climate_lag_features.csv"
    modeling_dataset = processed / "modeling_dataset.csv"
    baseline_metrics = validation / "baseline_metrics.csv"
    attribution = modeling / "feature_attribution_table.csv"
    lag_response = modeling / "lag_response_summary.csv"
    temporal_metrics = validation / "temporal_holdout_metrics.csv"
    spatial_metrics = validation / "spatial_holdout_metrics.csv"
    predictive_summary = validation / "predictive_validation_summary.csv"
    uncertainty_intervals = validation / "uncertainty_intervals.csv"

    run_modis_quality_command(modis_raw, modis_filtered, qc / "modis_quality_filter_report.md")
    run_modis_anomaly_command(modis_filtered, modis_anomalies, qc / "modis_anomaly_qc_report.md", min_climatology_samples=1)
    run_event_catalogue_command(modis_anomalies, stress, percentile=55, minimum_duration=2)
    run_climate_feature_command(climate_raw, climate_features, qc / "era5_climate_feature_report.md", config_path=config_path, min_climatology_samples=1)
    run_modeling_dataset_command(climate_features, event_catalogue, modeling_dataset, qc / "modeling_dataset_report.md", anomalies_path=modis_anomalies)
    _add_regions(modeling_dataset)
    run_baseline_evaluation_command(modeling_dataset, baseline_metrics, validation / "baseline_comparison.md", config_path=config_path)
    run_precursor_discovery_command(modeling_dataset, attribution, lag_response, modeling / "precursor_discovery_report.md")
    run_temporal_validation_command(modeling_dataset, attribution, temporal_metrics, validation / "temporal_holdout_report.md", config_path=config_path, top_n=3)
    run_spatial_validation_command(modeling_dataset, attribution, spatial_metrics, validation / "spatial_holdout_report.md", region_col="region", top_n=3)
    run_predictive_validation_summary_command(baseline_metrics, temporal_metrics, spatial_metrics, predictive_summary, validation / "predictive_validation_summary.md")
    run_uncertainty_audit_command(baseline_metrics, temporal_metrics, spatial_metrics, uncertainty_intervals, validation / "uncertainty_audit.md")

    artifacts = (
        modis_raw,
        modis_filtered,
        modis_anomalies,
        event_catalogue,
        climate_raw,
        climate_features,
        modeling_dataset,
        baseline_metrics,
        attribution,
        lag_response,
        temporal_metrics,
        spatial_metrics,
        predictive_summary,
        uncertainty_intervals,
    )
    manifest = _write_manifest(artifacts, Path(manifest_path))
    result = SmokeWorkflowResult(output_dir=root, report_path=Path(report_path), manifest_path=manifest, artifacts=artifacts)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    result.report_path.write_text(_render_report(result), encoding="utf-8")
    return result
