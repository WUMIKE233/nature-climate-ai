from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .config import load_study_config


PENDING_ACCESS_STATUS = "PENDING_ACCESS_CONFIRMATION"
CHINESE_REVIEW_HEADING = "\u4e2d\u6587\u5ba1\u9605\u8bf4\u660e"
CHINESE_REVIEW_NOTE = "\u672c\u62a5\u544a\u751f\u6210 ERA5\u3001MODIS \u548c FLUXNET \u7684\u8bbf\u95ee\u8bf7\u6c42\u6a21\u677f\uff0c\u7528\u4e8e\u540e\u7eed\u4eba\u5de5\u786e\u8ba4\u8d26\u53f7\u3001\u4ea7\u54c1\u3001\u8bf7\u6c42\u53c2\u6570\u3001\u653f\u7b56\u548c\u4e0b\u8f7d\u8bb0\u5f55\u3002\u5b83\u4e0d\u4e0b\u8f7d\u6570\u636e\uff0c\u4e0d\u9a8c\u8bc1\u51ed\u636e\uff0c\u4e5f\u4e0d\u4ee3\u8868\u6570\u636e\u5df2\u53ef\u7528\u3002"


@dataclass(frozen=True)
class ProviderRequestArtifact:
    source: str
    provider: str
    template_path: str
    access_status: str
    next_human_action: str


def _year_values(year_range: Any) -> list[str]:
    if isinstance(year_range, list) and len(year_range) == 2:
        return [str(year) for year in range(int(year_range[0]), int(year_range[1]) + 1)]
    return [PENDING_ACCESS_STATUS]


def _month_values() -> list[str]:
    return [f"{month:02d}" for month in range(1, 13)]


def _day_values() -> list[str]:
    return [f"{day:02d}" for day in range(1, 32)]


def _hour_values() -> list[str]:
    return [f"{hour:02d}:00" for hour in range(24)]


def _era5_variables(config_variables: list[str]) -> list[str]:
    mapped: list[str] = []
    for variable in config_variables:
        if variable == "soil_moisture":
            mapped.extend(["volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2"])
        elif variable == "vapour_pressure_deficit":
            mapped.append("2m_dewpoint_temperature")
        else:
            mapped.append(variable)
    return sorted(set(mapped))


def build_provider_request_templates(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    temporal = config["temporal_domain"]
    data_sources = config["data_sources"]
    spatial = config["spatial_domain"]

    era5 = data_sources["era5"]
    modis = data_sources["modis"]
    fluxnet = data_sources["fluxnet"]

    era5_variables = _era5_variables(list(era5.get("variables", ())))
    return {
        "era5": {
            "provider": era5["provider"],
            "source_url": era5["source_url"],
            "access_status": PENDING_ACCESS_STATUS,
            "credential_policy": "Do not store CDS credentials in this repository.",
            "dataset_candidates": ["reanalysis-era5-single-levels", "reanalysis-era5-land"],
            "cds_request_template": {
                "product_type": "reanalysis",
                "variable": era5_variables,
                "year": _year_values(temporal.get("era5_years")),
                "month": _month_values(),
                "day": _day_values(),
                "time": _hour_values(),
                "format": "netcdf",
            },
            "derived_variables": {
                "vapour_pressure_deficit": "derive after download from 2m_temperature and 2m_dewpoint_temperature",
                "soil_moisture_deficit": "derive from configured ERA5-Land soil-water layers after climatology construction",
            },
            "spatial_scope": spatial["scope"],
            "next_human_action": "Confirm CDS account, exact dataset IDs, request payload, local storage path, download date and checksums.",
        },
        "modis": {
            "provider": modis["provider"],
            "source_url": modis["source_url"],
            "access_status": PENDING_ACCESS_STATUS,
            "credential_policy": "Do not store NASA Earthdata credentials or tokens in this repository.",
            "products": modis.get("products", ()),
            "indices": modis.get("indices", ()),
            "target_years": _year_values(temporal.get("modis_years")),
            "quality_filters": modis.get("quality_filters", ()),
            "request_template": {
                "access_route": "NASA Earthdata, LAADS or LP DAAC route to be confirmed",
                "tile_strategy": "PENDING_TILE_STRATEGY",
                "collection": "PENDING_PRODUCT_COLLECTION",
                "local_raw_artifact": "data/raw/modis_observations.csv",
            },
            "next_human_action": "Confirm MODIS collection, tile list, download route, quality-bit interpretation, local artifact path and checksums.",
        },
        "fluxnet": {
            "provider": fluxnet["provider"],
            "source_url": fluxnet["source_url"],
            "access_status": PENDING_ACCESS_STATUS,
            "credential_policy": "Do not store FLUXNET credentials, restricted files or private access links in this repository.",
            "variables": fluxnet.get("variables", ()),
            "policy_review_template": {
                "dataset_version": "PENDING_POLICY_REVIEW",
                "site_list": "PENDING_SITE_SELECTION",
                "redistribution_limits": "PENDING_POLICY_REVIEW",
                "required_acknowledgements": "PENDING_POLICY_REVIEW",
                "required_citations": "PENDING_POLICY_REVIEW",
                "local_processed_artifact": "data/processed/fluxnet_anomalies.csv",
            },
            "next_human_action": "Confirm FLUXNET dataset/version, policy, site-years, citation requirements, redistribution limits and derived-metric sharing rules.",
        },
    }


def write_provider_request_templates(
    config_path: str | Path,
    output_dir: str | Path,
    manifest_path: str | Path,
    report_path: str | Path,
) -> tuple[tuple[ProviderRequestArtifact, ...], Path, Path]:
    config = load_study_config(config_path)
    templates = build_provider_request_templates(config)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    artifacts: list[ProviderRequestArtifact] = []
    for source, template in templates.items():
        template_path = output_root / f"{source}_request_template.yaml"
        template_path.write_text(yaml.safe_dump(template, allow_unicode=True, sort_keys=False), encoding="utf-8")
        artifacts.append(
            ProviderRequestArtifact(
                source=source,
                provider=str(template["provider"]),
                template_path=template_path.as_posix(),
                access_status=str(template["access_status"]),
                next_human_action=str(template["next_human_action"]),
            )
        )

    manifest = write_provider_request_manifest(tuple(artifacts), manifest_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_provider_request_report(tuple(artifacts), manifest), encoding="utf-8")
    return tuple(artifacts), manifest, report


def write_provider_request_manifest(artifacts: tuple[ProviderRequestArtifact, ...], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["source", "provider", "template_path", "access_status", "next_human_action"],
        )
        writer.writeheader()
        for artifact in artifacts:
            writer.writerow(artifact.__dict__)
    return output


def render_provider_request_report(artifacts: tuple[ProviderRequestArtifact, ...], manifest_path: str | Path) -> str:
    status = "NOT_READY" if any(artifact.access_status == PENDING_ACCESS_STATUS for artifact in artifacts) else "READY_FOR_DOWNLOAD_REVIEW"
    lines = [
        "# Provider request templates",
        "",
        f"Status: {status}",
        f"Manifest: {Path(manifest_path).as_posix()}",
        "",
        "source | provider | access status | template",
        "--- | --- | --- | ---",
    ]
    for artifact in artifacts:
        lines.append(f"{artifact.source} | {artifact.provider} | {artifact.access_status} | {artifact.template_path}")
    lines.extend(["", "## Required human actions", ""])
    lines.extend(f"- {artifact.source}: {artifact.next_human_action}" for artifact in artifacts)
    lines.extend(["", f"## {CHINESE_REVIEW_HEADING}", "", CHINESE_REVIEW_NOTE])
    return "\n".join(lines) + "\n"


def run_provider_request_templates_command(
    config_path: str | Path,
    output_dir: str | Path,
    manifest_path: str | Path,
    report_path: str | Path,
) -> tuple[tuple[ProviderRequestArtifact, ...], Path, Path]:
    return write_provider_request_templates(
        config_path=config_path,
        output_dir=output_dir,
        manifest_path=manifest_path,
        report_path=report_path,
    )
