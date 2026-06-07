from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


VALID_STATUSES = {"pending", "in_progress", "complete", "blocked"}
PLACEHOLDER_TOKENS = ("DATA_ACCESS_REQUIRED", "AUTHOR_REQUIRED", "RESULT_REQUIRED")
TEXT_EXTENSIONS = {".csv", ".json", ".md", ".txt", ".yaml", ".yml"}
PLACEHOLDER_DIAGNOSTIC_FILES = {"placeholder_evidence_map.md", "placeholder_evidence_map.csv"}


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    status: str
    manuscript_claim: str
    required_artifacts: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"


@dataclass(frozen=True)
class EvidenceReport:
    path: Path
    items: tuple[EvidenceItem, ...]

    @property
    def complete_count(self) -> int:
        return sum(item.is_complete for item in self.items)

    @property
    def pending_claims(self) -> tuple[EvidenceItem, ...]:
        return tuple(item for item in self.items if not item.is_complete)


@dataclass(frozen=True)
class ArtifactAuditRow:
    evidence_id: str
    evidence_status: str
    artifact: str
    exists: bool
    placeholder_count: int
    issue: str


@dataclass(frozen=True)
class EvidenceArtifactAudit:
    registry: Path
    root: Path
    rows: tuple[ArtifactAuditRow, ...]

    @property
    def missing_count(self) -> int:
        return sum(not row.exists for row in self.rows)

    @property
    def placeholder_file_count(self) -> int:
        return sum(row.placeholder_count > 0 for row in self.rows)

    @property
    def ready(self) -> bool:
        return self.missing_count == 0 and self.placeholder_file_count == 0


def load_evidence_registry(path: str | Path) -> EvidenceReport:
    registry_path = Path(path)
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(registry, dict) or not isinstance(registry.get("items"), list):
        raise ValueError("Evidence registry must contain an items list.")

    items: list[EvidenceItem] = []
    for raw in registry["items"]:
        status = raw.get("status")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid evidence status for {raw.get('id')}: {status}")
        artifacts = tuple(raw.get("required_artifacts", ()))
        if not artifacts:
            raise ValueError(f"Evidence item {raw.get('id')} must list required artifacts.")
        items.append(
            EvidenceItem(
                id=raw["id"],
                status=status,
                manuscript_claim=raw["manuscript_claim"],
                required_artifacts=artifacts,
            )
        )

    return EvidenceReport(path=registry_path, items=tuple(items))


def render_evidence_status(report: EvidenceReport) -> str:
    lines = [
        f"Evidence registry: {report.path}",
        f"Complete items: {report.complete_count}/{len(report.items)}",
        "",
        "id | status | required artifacts",
        "--- | --- | ---",
    ]
    for item in report.items:
        lines.append(f"{item.id} | {item.status} | {len(item.required_artifacts)}")
    return "\n".join(lines)


def _count_placeholders(path: Path) -> int:
    if path.name in PLACEHOLDER_DIAGNOSTIC_FILES:
        return 0
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return 0
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
    return sum(text.count(token) for token in PLACEHOLDER_TOKENS)


def audit_evidence_artifacts(registry_path: str | Path, root: str | Path = ".") -> EvidenceArtifactAudit:
    report = load_evidence_registry(registry_path)
    root_path = Path(root)
    rows: list[ArtifactAuditRow] = []
    for item in report.items:
        for artifact in item.required_artifacts:
            artifact_path = root_path / artifact
            exists = artifact_path.exists()
            placeholders = _count_placeholders(artifact_path) if exists and artifact_path.is_file() else 0
            issue_parts: list[str] = []
            if not exists:
                issue_parts.append("missing")
            if placeholders:
                issue_parts.append("contains_placeholders")
            if item.status == "complete" and issue_parts:
                issue_parts.append("status_complete_but_artifact_not_ready")
            if not issue_parts:
                issue_parts.append("ok")
            rows.append(
                ArtifactAuditRow(
                    evidence_id=item.id,
                    evidence_status=item.status,
                    artifact=artifact,
                    exists=exists,
                    placeholder_count=placeholders,
                    issue=";".join(issue_parts),
                )
            )
    return EvidenceArtifactAudit(registry=Path(registry_path), root=root_path, rows=tuple(rows))


def write_evidence_artifact_audit_csv(audit: EvidenceArtifactAudit, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["evidence_id", "evidence_status", "artifact", "exists", "placeholder_count", "issue"]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in audit.rows:
            writer.writerow(row.__dict__)
    return output


def render_evidence_artifact_audit(audit: EvidenceArtifactAudit, csv_path: str | Path) -> str:
    status = "READY_FOR_STATUS_REVIEW" if audit.ready else "NOT_READY"
    lines = [
        "# Evidence artifact audit",
        "",
        f"Status: {status}",
        f"Registry: {audit.registry.as_posix()}",
        f"Root: {audit.root.as_posix()}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"artifact_rows | {len(audit.rows)}",
        f"missing_artifacts | {audit.missing_count}",
        f"placeholder_files | {audit.placeholder_file_count}",
        "",
        "## Blocking artifacts",
        "",
    ]
    blocking = [row for row in audit.rows if row.issue != "ok"]
    if blocking:
        lines.extend(
            f"- {row.evidence_id}: {row.artifact} ({row.issue}, placeholders={row.placeholder_count})"
            for row in blocking[:100]
        )
        if len(blocking) > 100:
            lines.append(f"- ... {len(blocking) - 100} additional blocking artifacts")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计逐项检查证据注册表中的必需文件是否存在，以及文本型证据文件中是否仍含 DATA_ACCESS_REQUIRED、AUTHOR_REQUIRED 或 RESULT_REQUIRED 占位符。它不自动把证据项标记为完成；最终仍需要人工确认科学结果和数据政策。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_evidence_artifact_audit_command(
    registry_path: str | Path,
    root: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[EvidenceArtifactAudit, Path, Path]:
    audit = audit_evidence_artifacts(registry_path, root)
    csv_output = write_evidence_artifact_audit_csv(audit, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_evidence_artifact_audit(audit, csv_output), encoding="utf-8")
    return audit, report_output, csv_output
