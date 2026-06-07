from __future__ import annotations

import csv
import platform
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path


CORE_PACKAGES = ("nature-climate-ai", "numpy", "pandas", "pyyaml", "pytest", "xarray", "netCDF4", "cdsapi", "earthaccess")
CHINESE_REVIEW_HEADING = "\u4e2d\u6587\u5ba1\u9605\u8bf4\u660e"
CHINESE_SEED_NOTE = "\u968f\u673a\u79cd\u5b50\u6e05\u5355\u7528\u4e8e\u590d\u73b0\u5b9e\u9a8c\u6d41\u7a0b\uff0c\u4f46\u4e0d\u80fd\u66ff\u4ee3\u4e0d\u786e\u5b9a\u6027\u5206\u6790\u3001\u7a33\u5065\u6027\u68c0\u9a8c\u6216\u72ec\u7acb\u9a8c\u8bc1\u3002"
CHINESE_COMPUTE_NOTE = "\u672c\u6587\u4ef6\u8bb0\u5f55\u8ba1\u7b97\u8d44\u6e90\u8ba1\u5212\u3002\u5f53\u524d\u53ea\u8bc1\u660e\u811a\u624b\u67b6\u53ef\u4ee5\u5728\u672c\u5730\u73af\u5883\u8fd0\u884c\uff0c\u4e0d\u4ee3\u8868\u771f\u5b9e\u5168\u7403\u5206\u6790\u5df2\u7ecf\u5b8c\u6210\uff1b\u6b63\u5f0f\u6295\u7a3f\u524d\u5fc5\u987b\u8865\u5145\u5b9e\u9645 CPU/GPU\u3001\u8fd0\u884c\u65f6\u95f4\u3001\u5185\u5b58\u3001\u5b58\u50a8\u548c\u8bad\u7ec3\u8bbe\u7f6e\u3002"
CHINESE_ENV_REPORT_NOTE = "\u672c\u62a5\u544a\u8bb0\u5f55\u5f53\u524d Python \u73af\u5883\u3001\u6838\u5fc3\u5305\u7248\u672c\u3001\u590d\u73b0\u547d\u4ee4\u6e05\u5355\u3001\u73af\u5883\u6587\u4ef6\u3001\u9501\u5b9a\u6587\u4ef6\u3001\u968f\u673a\u79cd\u5b50\u548c\u8ba1\u7b97\u8d44\u6e90\u8ba1\u5212\u3002\u5b83\u8bc1\u660e\u5f53\u524d\u811a\u624b\u67b6\u53ef\u8fd0\u884c\uff0c\u4e0d\u4ee3\u8868\u771f\u5b9e\u6570\u636e\u3001\u6a21\u578b\u7ed3\u679c\u6216\u8bba\u6587\u7ed3\u8bba\u5df2\u7ecf\u5b8c\u6210\u3002"


@dataclass(frozen=True)
class EnvironmentAudit:
    python_version: str
    platform: str
    executable: str
    package_versions: dict[str, str]
    missing_packages: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.missing_packages


@dataclass(frozen=True)
class ReproducibilityCommand:
    stage: str
    command: str
    expected_current_status: str


DEFAULT_REPRO_COMMANDS = (
    ReproducibilityCommand("test", r".\.venv\Scripts\python -m pytest -q --basetemp .test_tmp -p no:cacheprovider", "PASS"),
    ReproducibilityCommand("manuscript", "python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/nature_article_draft.md --journal nature --output results/submission/manuscript_format_audit.md", "NOT_READY"),
    ReproducibilityCommand("references", "python -m nature_climate_ai.cli reference-audit --metadata manuscript/reference_metadata.yaml --output manuscript/reference_audit.md --status-csv manuscript/reference_status.csv", "NOT_READY"),
    ReproducibilityCommand("authors", "python -m nature_climate_ai.cli author-metadata-audit --metadata manuscript/author_metadata.yaml --output manuscript/author_metadata_audit.md --csv manuscript/author_metadata_status.csv", "NOT_READY"),
    ReproducibilityCommand("placeholder_map", "python -m nature_climate_ai.cli placeholder-map --manuscript manuscript/nature_article_draft.md --output manuscript/placeholder_evidence_map.md --csv manuscript/placeholder_evidence_map.csv", "NOT_READY"),
    ReproducibilityCommand("figures", "python -m nature_climate_ai.cli generate-figure-assets --config config/study.yaml --output-dir figures/generated --manifest figures/generated/figure_manifest.csv --report figures/generated/figure_generation_report.md", "PARTIAL_READY"),
    ReproducibilityCommand("evidence", "python -m nature_climate_ai.cli evidence-artifact-audit --registry evidence/registry.yaml --root . --output evidence/artifact_audit.md --csv evidence/artifact_audit.csv", "NOT_READY"),
    ReproducibilityCommand("checksums", "python -m nature_climate_ai.cli checksum-audit --root data --output data/checksums/data_checksum_audit.md --csv data/checksums/data_checksums.csv", "NOT_READY"),
    ReproducibilityCommand("smoke", "python -m nature_climate_ai.cli pipeline-smoke-test --output-dir outputs/smoke --report reproducibility/pipeline_smoke_report.md --manifest reproducibility/pipeline_smoke_manifest.csv", "COMPLETE_FOR_SYNTHETIC_DATA"),
    ReproducibilityCommand("data", "python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md", "NOT_READY"),
    ReproducibilityCommand("era5_download_status", "python -m nature_climate_ai.cli download-status --log data/metadata/era5_download_log.csv --output data/metadata/era5_download_status.md", "NOT_READY"),
    ReproducibilityCommand("era5_land_smoke_download", "python -m nature_climate_ai.cli download-era5 --year-start 2000 --year-end 2000 --months 1 --only land --dry-run", "READY_TO_REQUEST_AFTER_HUMAN_CONFIRMATION"),
    ReproducibilityCommand("provider_requests", "python -m nature_climate_ai.cli provider-request-templates --config config/study.yaml --output-dir data/metadata/provider_requests --manifest data/metadata/provider_request_manifest.csv --report data/metadata/provider_request_templates.md", "NOT_READY"),
    ReproducibilityCommand("data_templates", "python -m nature_climate_ai.cli data-access-template-audit --root . --output data/metadata/data_access_template_audit.md --csv data/metadata/data_access_template_status.csv", "NOT_READY"),
    ReproducibilityCommand("public_release", "python -m nature_climate_ai.cli public-release-audit --root . --output reproducibility/public_release_audit.md --csv reproducibility/public_release_status.csv", "NOT_READY"),
    ReproducibilityCommand("dashboard", "python -m nature_climate_ai.cli readiness-dashboard --root . --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml --config config/study.yaml --reference-metadata manuscript/reference_metadata.yaml --output reproducibility/readiness_dashboard.md --csv reproducibility/readiness_dashboard.csv", "NOT_READY"),
    ReproducibilityCommand("qc", "python -m nature_climate_ai.cli e00-data-qc --output results/qc/e00_data_qc_report.md", "NOT_READY"),
    ReproducibilityCommand("era5_raw_aggregate", "python -m nature_climate_ai.cli era5-raw-aggregate --input-dir data/raw/era5/cds_8c5868ad2f6b9db27f57ebaaeb460755 --output data/interim/era5_composite_climate.csv --report results/qc/era5_raw_aggregate_report.md", "PARTIAL_FOR_AVAILABLE_VARIABLES"),
    ReproducibilityCommand("modeling", "python -m nature_climate_ai.cli modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv --anomalies data/processed/modis_anomalies.csv --output data/processed/modeling_dataset.csv --report results/qc/modeling_dataset_report.md", "NOT_READY"),
    ReproducibilityCommand("validation", "python -m nature_climate_ai.cli predictive-validation-summary --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/predictive_validation_summary.csv --report results/validation/predictive_validation_summary.md", "NOT_READY"),
    ReproducibilityCommand("robustness_placebo", "python -m nature_climate_ai.cli placebo-validation --input data/processed/modeling_dataset.csv --output results/validation/placebo_metrics.csv --report results/validation/placebo_validation.md", "NOT_READY"),
    ReproducibilityCommand("robustness_thresholds", "python -m nature_climate_ai.cli threshold-sensitivity --input data/processed/modis_anomalies.csv --output results/validation/threshold_sensitivity.csv --report results/validation/threshold_sensitivity.md", "NOT_READY"),
    ReproducibilityCommand("robustness_biome", "python -m nature_climate_ai.cli biome-stratified-validation --modeling data/processed/modeling_dataset.csv --biome-col biome --output results/validation/biome_metrics.csv --report results/validation/biome_validation.md", "NOT_READY"),
    ReproducibilityCommand("robustness_sensor", "python -m nature_climate_ai.cli sensor-cross-validation --modis data/processed/modis_anomalies.csv --external data/processed/external_vegetation_anomalies.csv --output results/validation/sensor_cross_validation.csv --report results/validation/sensor_cross_validation.md", "NOT_READY"),
    ReproducibilityCommand("pilot_figures", "python -m nature_climate_ai.cli generate-pilot-figures --events results/stress_events/event_catalogue_summary.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --predictive results/validation/predictive_validation_summary.csv --output-dir figures/generated --manifest figures/generated/pilot_figure_manifest.csv --report figures/generated/pilot_figure_generation_report.md", "NOT_READY"),
    ReproducibilityCommand("pilot_gate", "python -m nature_climate_ai.cli minimum-evidence-slice --root . --output results/pilot/minimum_evidence_slice_report.md --csv results/pilot/minimum_evidence_slice_status.csv", "NOT_READY"),
    ReproducibilityCommand("submission", "python -m nature_climate_ai.cli submission-gate --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml", "NOT_READY"),
)


def audit_environment(packages: tuple[str, ...] = CORE_PACKAGES) -> EnvironmentAudit:
    versions: dict[str, str] = {}
    missing: list[str] = []
    for package in packages:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            missing.append(package)
    return EnvironmentAudit(
        python_version=sys.version.replace("\n", " "),
        platform=platform.platform(),
        executable=sys.executable,
        package_versions=versions,
        missing_packages=tuple(missing),
    )


def write_command_manifest(path: str | Path, commands: tuple[ReproducibilityCommand, ...] = DEFAULT_REPRO_COMMANDS) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["stage", "command", "expected_current_status"])
        writer.writeheader()
        for command in commands:
            writer.writerow(command.__dict__)
    return output


def write_environment_yml(path: str | Path, audit: EnvironmentAudit) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    python_major_minor = ".".join(audit.python_version.split()[0].split(".")[:2])
    pip_packages = [
        f"{package}=={version}"
        for package, version in sorted(audit.package_versions.items())
        if package != "nature-climate-ai"
    ]
    lines = [
        "name: nature-climate-ai",
        "channels:",
        "  - conda-forge",
        "dependencies:",
        f"  - python={python_major_minor}",
        "  - pip",
        "  - pip:",
        "    - -e .[dev]",
    ]
    lines.extend(f"    - {package}" for package in pip_packages)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_requirements_lock(path: str | Path, audit: EnvironmentAudit) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Current local scaffold lockfile.",
        "# Regenerate after dependency updates and before any public code release.",
    ]
    for package, version in sorted(audit.package_versions.items()):
        if package == "nature-climate-ai":
            lines.append(f"# {package}=={version}  # local editable project")
        else:
            lines.append(f"{package}=={version}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_seed_manifest(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "global_seed: 20260605",
                "policy: \"Use fixed seeds for stochastic preprocessing, model training, validation resampling and figure sampling where scientifically appropriate.\"",
                "stages:",
                "  preprocessing: 20260605",
                "  baseline_models: 20260606",
                "  ai_model_training: 20260607",
                "  bootstrap_uncertainty: 20260608",
                "  placebo_tests: 20260609",
                "  pilot_figures: 20260610",
                "notes:",
                "  - \"Seeds do not replace reporting uncertainty intervals or robustness checks.\"",
                "  - \"Record any non-deterministic GPU kernels or distributed-training settings before manuscript submission.\"",
                f"{CHINESE_REVIEW_HEADING}: \"{CHINESE_SEED_NOTE}\"",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return output


def write_compute_budget(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "# Compute budget",
                "",
                "Status: PLANNED_NOT_MEASURED",
                "",
                "The current scaffold and tests run on CPU. Real global analysis will require recording the actual compute environment before any Nature/Science submission claim is finalized.",
                "",
                "## Planned records",
                "",
                "- CPU model, RAM and operating system.",
                "- GPU model, count, memory and driver/CUDA stack if neural models are trained.",
                "- Wall-clock time for data preprocessing, feature generation, model training, validation, robustness checks and figure generation.",
                "- Peak memory/storage use and intermediate-data footprint.",
                "- Any cloud, cluster or local workstation identifiers that can be shared publicly.",
                "",
                "## Current local scaffold",
                "",
                "- Tests and readiness commands run in the local Python environment recorded by `reproducibility/environment_report.md`.",
                "- No manuscript result has been generated from GPU training yet.",
                "",
                f"## {CHINESE_REVIEW_HEADING}",
                "",
                CHINESE_COMPUTE_NOTE,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return output


def render_environment_report(
    audit: EnvironmentAudit,
    command_manifest: str | Path,
    environment_yml: str | Path,
    requirements_lock: str | Path,
    seed_manifest: str | Path,
    compute_budget: str | Path,
) -> str:
    status = "READY_FOR_CURRENT_ENVIRONMENT" if audit.ready else "NOT_READY"
    lines = [
        "# Reproducibility environment audit",
        "",
        f"Status: {status}",
        "",
        "metric | value",
        "--- | ---",
        f"python_version | {audit.python_version}",
        f"platform | {audit.platform}",
        f"executable | {audit.executable}",
        f"command_manifest | {Path(command_manifest).as_posix()}",
        f"environment_yml | {Path(environment_yml).as_posix()}",
        f"requirements_lock | {Path(requirements_lock).as_posix()}",
        f"seed_manifest | {Path(seed_manifest).as_posix()}",
        f"compute_budget | {Path(compute_budget).as_posix()}",
        "",
        "## Package versions",
        "",
        "package | version",
        "--- | ---",
    ]
    for package, version in sorted(audit.package_versions.items()):
        lines.append(f"{package} | {version}")
    lines.extend(["", "## Missing packages", ""])
    if audit.missing_packages:
        lines.extend(f"- {package}" for package in audit.missing_packages)
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Current-state warning",
            "",
            "This environment can run the scaffold tests and readiness commands, but the manuscript remains non-submission-ready until data access, result artifacts, uncertainty analysis, figures and author metadata are complete.",
            "",
            f"## {CHINESE_REVIEW_HEADING}",
            "",
            CHINESE_ENV_REPORT_NOTE,
        ]
    )
    return "\n".join(lines) + "\n"


def run_reproducibility_audit_command(
    report_path: str | Path,
    command_manifest_path: str | Path,
    environment_yml_path: str | Path = "reproducibility/environment.yml",
    requirements_lock_path: str | Path = "reproducibility/requirements-lock.txt",
    seed_manifest_path: str | Path = "reproducibility/random_seed_manifest.yaml",
    compute_budget_path: str | Path = "reproducibility/compute_budget.md",
) -> tuple[EnvironmentAudit, Path, Path]:
    audit = audit_environment()
    manifest = write_command_manifest(command_manifest_path)
    environment_yml = write_environment_yml(environment_yml_path, audit)
    requirements_lock = write_requirements_lock(requirements_lock_path, audit)
    seed_manifest = write_seed_manifest(seed_manifest_path)
    compute_budget = write_compute_budget(compute_budget_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        render_environment_report(
            audit,
            manifest,
            environment_yml,
            requirements_lock,
            seed_manifest,
            compute_budget,
        ),
        encoding="utf-8",
    )
    return audit, report, manifest
