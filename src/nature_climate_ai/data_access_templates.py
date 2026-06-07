from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REQUIRED_TEMPLATE_FILES = (
    "data/metadata/era5_request_parameters.yaml",
    "data/metadata/era5_access_log.md",
    "data/metadata/modis_products.yaml",
    "data/metadata/modis_quality_flags.md",
    "data/metadata/fluxnet_sites.csv",
    "data/metadata/fluxnet_policy_review.md",
)
PENDING_MARKERS = ("pending", "PENDING_", "\u5f85")


@dataclass(frozen=True)
class DataAccessTemplateIssue:
    template: str
    field: str
    issue: str
    value: str


@dataclass(frozen=True)
class DataAccessTemplateAudit:
    root: Path
    issues: tuple[DataAccessTemplateIssue, ...]

    @property
    def ready(self) -> bool:
        return not self.issues


def _value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return yaml.safe_dump(value, allow_unicode=True, sort_keys=True).strip().replace("\n", " ")
    return str(value)


def _is_pending(value: Any) -> bool:
    text = _value_text(value)
    lowered = text.lower()
    return not text.strip() or any(marker.lower() in lowered for marker in PENDING_MARKERS)


def _walk_yaml(value: Any, prefix: str, template: str) -> list[DataAccessTemplateIssue]:
    issues: list[DataAccessTemplateIssue] = []
    if isinstance(value, dict):
        if not value:
            return [DataAccessTemplateIssue(template, prefix, "empty_mapping", "")]
        for key, item in value.items():
            issues.extend(_walk_yaml(item, f"{prefix}.{key}" if prefix else str(key), template))
        return issues
    if isinstance(value, list):
        if not value:
            return [DataAccessTemplateIssue(template, prefix, "empty_list", "")]
        for index, item in enumerate(value):
            issues.extend(_walk_yaml(item, f"{prefix}[{index}]", template))
        return issues
    if _is_pending(value):
        return [DataAccessTemplateIssue(template, prefix, "pending_or_empty_value", _value_text(value))]
    return issues


def _audit_yaml(path: Path, template: str) -> list[DataAccessTemplateIssue]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _walk_yaml(data, "", template)


def _audit_csv(path: Path, template: str) -> list[DataAccessTemplateIssue]:
    issues: list[DataAccessTemplateIssue] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [DataAccessTemplateIssue(template, "csv", "missing_header", "")]
        for row_index, row in enumerate(reader, start=1):
            for field, value in row.items():
                if _is_pending(value):
                    issues.append(
                        DataAccessTemplateIssue(template, f"row[{row_index}].{field}", "pending_or_empty_value", _value_text(value))
                    )
    return issues


def _audit_markdown(path: Path, template: str) -> list[DataAccessTemplateIssue]:
    issues: list[DataAccessTemplateIssue] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        if _is_pending(line):
            issues.append(DataAccessTemplateIssue(template, f"line[{line_number}]", "pending_line", line.strip()))
    return issues


def audit_data_access_templates(
    root: str | Path = ".",
    templates: tuple[str, ...] = REQUIRED_TEMPLATE_FILES,
) -> DataAccessTemplateAudit:
    root_path = Path(root)
    issues: list[DataAccessTemplateIssue] = []
    for template in templates:
        path = root_path / template
        if not path.exists():
            issues.append(DataAccessTemplateIssue(template, "file", "missing_file", path.as_posix()))
            continue
        suffix = path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            issues.extend(_audit_yaml(path, template))
        elif suffix == ".csv":
            issues.extend(_audit_csv(path, template))
        elif suffix in {".md", ".txt"}:
            issues.extend(_audit_markdown(path, template))
        else:
            issues.append(DataAccessTemplateIssue(template, "file", "unsupported_template_type", suffix))
    return DataAccessTemplateAudit(root=root_path, issues=tuple(issues))


def write_data_access_template_audit_csv(audit: DataAccessTemplateAudit, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["template", "field", "issue", "value"])
        writer.writeheader()
        for issue in audit.issues:
            writer.writerow(issue.__dict__)
    return output


def render_data_access_template_audit(audit: DataAccessTemplateAudit, csv_path: str | Path) -> str:
    status = "READY_FOR_DATA_ACCESS_REVIEW" if audit.ready else "NOT_READY"
    lines = [
        "# Data access template audit",
        "",
        f"Status: {status}",
        f"Root: {audit.root.as_posix()}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"issue_count | {len(audit.issues)}",
        "",
        "## Issues",
        "",
    ]
    if audit.issues:
        lines.extend(["template | field | issue | value", "--- | --- | --- | ---"])
        for issue in audit.issues[:100]:
            lines.append(f"{issue.template} | {issue.field} | {issue.issue} | {issue.value}")
        if len(audit.issues) > 100:
            lines.append(f"... | ... | ... | {len(audit.issues) - 100} additional issues")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计检查 ERA5、MODIS 和 FLUXNET 的访问模板是否仍包含待确认字段。只有账号、产品版本、请求参数、下载日期、质量规则、政策限制和校验信息补齐后，数据访问证据才应进入完成状态。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_data_access_template_audit_command(
    root: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[DataAccessTemplateAudit, Path, Path]:
    audit = audit_data_access_templates(root)
    csv_output = write_data_access_template_audit_csv(audit, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_data_access_template_audit(audit, csv_output), encoding="utf-8")
    return audit, report_output, csv_output
