from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PENDING_VALUE = "PENDING_AUTHOR_INPUT"
REQUIRED_TOP_LEVEL_FIELDS = (
    "status",
    "corresponding_author",
    "authors",
    "contributions",
    "acknowledgements",
    "funding",
    "competing_interests",
    "data_policy_confirmed_by",
    "submission_approval",
)


@dataclass(frozen=True)
class AuthorMetadataIssue:
    field: str
    issue: str
    value: str


@dataclass(frozen=True)
class AuthorMetadataAudit:
    metadata_path: Path
    issues: tuple[AuthorMetadataIssue, ...]

    @property
    def ready(self) -> bool:
        return not self.issues


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return yaml.safe_dump(value, allow_unicode=True, sort_keys=True).strip().replace("\n", " ")
    return str(value)


def _contains_pending(value: Any) -> bool:
    if value is None or value == "":
        return True
    if isinstance(value, str):
        return value.strip() == PENDING_VALUE
    if isinstance(value, dict):
        return any(_contains_pending(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return not value or any(_contains_pending(item) for item in value)
    return False


def _walk_pending(value: Any, prefix: str) -> list[AuthorMetadataIssue]:
    issues: list[AuthorMetadataIssue] = []
    if isinstance(value, dict):
        if not value:
            issues.append(AuthorMetadataIssue(prefix, "empty_mapping", ""))
        for key, item in value.items():
            issues.extend(_walk_pending(item, f"{prefix}.{key}"))
        return issues
    if isinstance(value, list):
        if not value:
            return [AuthorMetadataIssue(prefix, "empty_list", "")]
        for index, item in enumerate(value):
            issues.extend(_walk_pending(item, f"{prefix}[{index}]"))
        return issues
    if _contains_pending(value):
        issue = "pending_author_input" if value == PENDING_VALUE else "empty_value"
        issues.append(AuthorMetadataIssue(prefix, issue, _format_value(value)))
    return issues


def load_author_metadata(path: str | Path) -> dict[str, Any]:
    metadata_path = Path(path)
    data = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Author metadata must be a YAML mapping.")
    return data


def audit_author_metadata(path: str | Path) -> AuthorMetadataAudit:
    metadata_path = Path(path)
    if not metadata_path.exists():
        return AuthorMetadataAudit(
            metadata_path=metadata_path,
            issues=(AuthorMetadataIssue("author_metadata", "missing_file", metadata_path.as_posix()),),
        )

    data = load_author_metadata(metadata_path)
    issues: list[AuthorMetadataIssue] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in data:
            issues.append(AuthorMetadataIssue(field, "missing_field", ""))
            continue
        issues.extend(_walk_pending(data[field], field))
    return AuthorMetadataAudit(metadata_path=metadata_path, issues=tuple(issues))


def write_author_metadata_status_csv(audit: AuthorMetadataAudit, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field", "issue", "value"])
        writer.writeheader()
        for issue in audit.issues:
            writer.writerow(issue.__dict__)
    return output


def render_author_metadata_audit(audit: AuthorMetadataAudit, csv_path: str | Path) -> str:
    status = "READY_FOR_AUTHOR_REVIEW" if audit.ready else "NOT_READY"
    lines = [
        "# Author metadata audit",
        "",
        f"Status: {status}",
        f"Metadata: {audit.metadata_path.as_posix()}",
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
        lines.extend(["field | issue | value", "--- | --- | ---"])
        for issue in audit.issues:
            lines.append(f"{issue.field} | {issue.issue} | {issue.value}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计检查作者、单位、贡献、致谢、资助、利益冲突和投稿确认信息是否已经由作者人工补齐。它不会替作者填写任何信息，也不能替代最终作者确认。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_author_metadata_audit_command(
    metadata_path: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[AuthorMetadataAudit, Path, Path]:
    audit = audit_author_metadata(metadata_path)
    csv_output = write_author_metadata_status_csv(audit, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_author_metadata_audit(audit, csv_output), encoding="utf-8")
    return audit, report_output, csv_output
