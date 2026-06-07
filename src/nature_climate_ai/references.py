from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ReferenceAuditReport:
    metadata_path: Path
    total_references: int
    checked_references: int
    missing_required_fields: tuple[str, ...]
    literature_gaps: tuple[str, ...]
    ready: bool


REQUIRED_REFERENCE_FIELDS = ("id", "authors", "year", "title", "journal", "doi", "role", "status")


def load_reference_metadata(path: str | Path) -> dict[str, Any]:
    metadata_path = Path(path)
    if not metadata_path.exists():
        raise FileNotFoundError(f"Reference metadata not found: {metadata_path}")
    data = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Reference metadata must be a YAML mapping.")
    if "references" not in data:
        raise ValueError("Reference metadata must contain a references list.")
    if not isinstance(data["references"], list):
        raise ValueError("references must be a list.")
    return data


def audit_references(metadata: dict[str, Any], metadata_path: str | Path) -> ReferenceAuditReport:
    missing: list[str] = []
    checked = 0
    for index, entry in enumerate(metadata.get("references", []), start=1):
        if not isinstance(entry, dict):
            missing.append(f"reference[{index}] is not a mapping")
            continue
        for field in REQUIRED_REFERENCE_FIELDS:
            if not entry.get(field):
                missing.append(f"{entry.get('id', f'reference[{index}]')} missing {field}")
        if entry.get("status") == "seed_metadata_checked":
            checked += 1

    gaps = tuple(
        f"{gap.get('topic', 'unknown topic')}: {gap.get('status', 'UNKNOWN')}"
        for gap in metadata.get("literature_gaps", [])
        if isinstance(gap, dict) and gap.get("status") != "complete"
    )
    return ReferenceAuditReport(
        metadata_path=Path(metadata_path),
        total_references=len(metadata.get("references", [])),
        checked_references=checked,
        missing_required_fields=tuple(missing),
        literature_gaps=gaps,
        ready=not missing and not gaps,
    )


def write_reference_status_csv(metadata: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "status", "authors", "year", "title", "journal", "doi", "role"]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in metadata.get("references", []):
            writer.writerow({field: entry.get(field, "") for field in fieldnames})
    return output


def render_reference_audit_report(report: ReferenceAuditReport, metadata: dict[str, Any], status_csv: Path) -> str:
    status = "READY_FOR_TARGETED_LITERATURE_REVIEW" if report.ready else "NOT_READY"
    lines = [
        "# Reference audit",
        "",
        f"Status: {status}",
        f"Metadata: {report.metadata_path.as_posix()}",
        f"Status CSV: {status_csv.as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"total_references | {report.total_references}",
        f"checked_seed_references | {report.checked_references}",
        f"literature_gaps | {len(report.literature_gaps)}",
        "",
        "## Seed references",
        "",
        "id | year | journal | doi | role",
        "--- | ---: | --- | --- | ---",
    ]
    for entry in metadata.get("references", []):
        lines.append(
            f"{entry.get('id', '')} | {entry.get('year', '')} | {entry.get('journal', '')} | "
            f"{entry.get('doi', '')} | {entry.get('role', '')}"
        )
    lines.extend(["", "## Issues", ""])
    if report.missing_required_fields:
        lines.extend(f"- {item}" for item in report.missing_required_fields)
    if report.literature_gaps:
        lines.extend(f"- Literature gap: {item}" for item in report.literature_gaps)
    if not report.missing_required_fields and not report.literature_gaps:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计只说明核心种子文献元数据已经结构化记录。它不代表文献综述已经完成；复合高温-干旱、生态早期预警、可解释机器学习和全球植被遥感等方向仍需要定向补充和人工核验。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_reference_audit_command(
    metadata_path: str | Path,
    report_path: str | Path,
    status_csv_path: str | Path,
) -> tuple[ReferenceAuditReport, Path, Path]:
    metadata = load_reference_metadata(metadata_path)
    report = audit_references(metadata, metadata_path)
    status_csv = write_reference_status_csv(metadata, status_csv_path)
    output = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_reference_audit_report(report, metadata, status_csv), encoding="utf-8")
    return report, output, status_csv
