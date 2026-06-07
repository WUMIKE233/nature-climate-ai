from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import load_study_config

PENDING_ACCESS_STATUS = "PENDING_ACCESS_CONFIRMATION"


@dataclass(frozen=True)
class DataAccessPlanRow:
    source: str
    provider: str
    source_url: str
    access_status: str
    target_years: str
    requested_variables: str
    required_metadata: str
    expected_local_artifact: str
    next_action: str


def _year_range(value: Any) -> str:
    if isinstance(value, list) and len(value) == 2:
        return f"{value[0]}-{value[1]}"
    return "DATA_ACCESS_REQUIRED"


def _join_values(values: Any) -> str:
    if isinstance(values, list):
        return "; ".join(str(value) for value in values)
    if values:
        return str(values)
    return "DATA_ACCESS_REQUIRED"


def _display_access_status(status: str) -> str:
    if status == "DATA_ACCESS_REQUIRED":
        return PENDING_ACCESS_STATUS
    return status


def _has_pending_access(status: str) -> bool:
    return status in {"DATA_ACCESS_REQUIRED", PENDING_ACCESS_STATUS}


def build_data_access_plan(config: dict[str, Any]) -> list[DataAccessPlanRow]:
    data_sources = config["data_sources"]
    temporal = config.get("temporal_domain", {})
    rows: list[DataAccessPlanRow] = []

    era5 = data_sources["era5"]
    rows.append(
        DataAccessPlanRow(
            source="era5",
            provider=era5["provider"],
            source_url=era5["source_url"],
            access_status=_display_access_status(era5["access_status"]),
            target_years=_year_range(temporal.get("era5_years")),
            requested_variables=_join_values(era5.get("variables")),
            required_metadata="data/metadata/era5_request_parameters.yaml; data/metadata/era5_access_log.md",
            expected_local_artifact="data/interim/era5_composite_climate.csv",
            next_action="Confirm CDS account, dataset IDs, request payloads, download dates and checksums.",
        )
    )

    modis = data_sources["modis"]
    rows.append(
        DataAccessPlanRow(
            source="modis",
            provider=modis["provider"],
            source_url=modis["source_url"],
            access_status=_display_access_status(modis["access_status"]),
            target_years=_year_range(temporal.get("modis_years")),
            requested_variables=_join_values(modis.get("indices")),
            required_metadata="data/metadata/modis_products.yaml; data/metadata/modis_quality_flags.md",
            expected_local_artifact="data/raw/modis_observations.csv",
            next_action="Confirm product collection, tile strategy, download route and quality-bit interpretation.",
        )
    )

    fluxnet = data_sources["fluxnet"]
    rows.append(
        DataAccessPlanRow(
            source="fluxnet",
            provider=fluxnet["provider"],
            source_url=fluxnet["source_url"],
            access_status=_display_access_status(fluxnet["access_status"]),
            target_years="site-years after policy review",
            requested_variables=_join_values(fluxnet.get("variables")),
            required_metadata="data/metadata/fluxnet_sites.csv; data/metadata/fluxnet_policy_review.md",
            expected_local_artifact="data/processed/fluxnet_anomalies.csv",
            next_action="Confirm data policy, site list, citation requirements and redistribution limits.",
        )
    )
    return rows


def write_manifest(rows: list[DataAccessPlanRow], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(DataAccessPlanRow.__dataclass_fields__)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    return output


def render_data_access_report(rows: list[DataAccessPlanRow]) -> str:
    missing_access = [row for row in rows if _has_pending_access(row.access_status)]
    status = "NOT_READY" if missing_access else "READY_FOR_DATA_DOWNLOAD"
    lines = [
        "# Public data-access plan",
        "",
        f"Status: {status}",
        "",
        "This report records the public-data access work required before any manuscript claim can be promoted from placeholders to results. It does not certify that data have been downloaded.",
        "",
        "source | provider | access | years | expected local artifact",
        "--- | --- | --- | --- | ---",
    ]
    for row in rows:
        lines.append(
            f"{row.source} | {row.provider} | {row.access_status} | {row.target_years} | {row.expected_local_artifact}"
        )
    lines.extend(
        [
            "",
            "## Required actions",
            "",
        ]
    )
    for row in rows:
        lines.append(f"- {row.source}: {row.next_action}")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本报告只记录公共数据访问和元数据审计计划，不代表数据已经下载，也不能作为论文结果证据。只有账号、数据政策、请求参数、下载日期、校验信息和质量控制记录都完成后，相关证据项才可以进入完成状态。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_data_access_plan_command(
    config_path: str | Path,
    manifest_path: str | Path,
    report_path: str | Path,
) -> tuple[Path, Path]:
    config = load_study_config(config_path)
    rows = build_data_access_plan(config)
    manifest = write_manifest(rows, manifest_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_data_access_report(rows), encoding="utf-8")
    return manifest, report
