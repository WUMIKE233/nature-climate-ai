from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


REQUIRED_RELEASE_ARTIFACTS = (
    "README.md",
    "pyproject.toml",
    ".gitignore",
    "docs/data_ethics_and_licensing.md",
    "docs/reproducibility_checklist.md",
    "reproducibility/environment.yml",
    "reproducibility/requirements-lock.txt",
    "reproducibility/command_manifest.csv",
    "reproducibility/random_seed_manifest.yaml",
    "reproducibility/compute_budget.md",
    "data/metadata/data_access_manifest.csv",
    "data/metadata/provider_request_manifest.csv",
    "data/checksums/data_checksum_audit.md",
    "manuscript/placeholder_evidence_map.md",
    "manuscript/author_metadata_audit.md",
)
IGNORED_PARTS = {
    ".git",
    ".venv",
    ".test_tmp",
    ".pytest_cache",
    "__pycache__",
    "outputs",
    "results",
    "figures",
    "raw",
    "interim",
    "processed",
}
TEXT_SUFFIXES = {".cfg", ".csv", ".env", ".ini", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "assigned_secret",
        re.compile(r"(?i)\b(api[_-]?key|password|secret|token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    ),
)


@dataclass(frozen=True)
class PublicReleaseIssue:
    category: str
    path: str
    issue: str
    detail: str


@dataclass(frozen=True)
class PublicReleaseAudit:
    root: Path
    issues: tuple[PublicReleaseIssue, ...]

    @property
    def ready(self) -> bool:
        return not self.issues


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def _iter_scannable_files(root: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or _is_ignored(path.relative_to(root)):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 1_000_000:
            files.append(path)
    return tuple(sorted(files))


def scan_for_secret_patterns(root: str | Path) -> tuple[PublicReleaseIssue, ...]:
    root_path = Path(root)
    issues: list[PublicReleaseIssue] = []
    for path in _iter_scannable_files(root_path):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(root_path).as_posix()
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                issues.append(PublicReleaseIssue("credential_scan", relative, name, "high-risk credential pattern matched"))
    return tuple(issues)


def audit_public_release(
    root: str | Path = ".",
    required_artifacts: tuple[str, ...] = REQUIRED_RELEASE_ARTIFACTS,
) -> PublicReleaseAudit:
    root_path = Path(root)
    issues: list[PublicReleaseIssue] = []

    if not (root_path / ".git").exists():
        issues.append(PublicReleaseIssue("repository", ".git", "missing_git_repository", "public release requires a versioned repository and commit hash"))

    for artifact in required_artifacts:
        if not (root_path / artifact).exists():
            issues.append(PublicReleaseIssue("required_artifact", artifact, "missing_artifact", "required public-release artifact is missing"))

    issues.extend(scan_for_secret_patterns(root_path))
    return PublicReleaseAudit(root=root_path, issues=tuple(issues))


def write_public_release_audit_csv(audit: PublicReleaseAudit, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "path", "issue", "detail"])
        writer.writeheader()
        for issue in audit.issues:
            writer.writerow(issue.__dict__)
    return output


def render_public_release_audit(audit: PublicReleaseAudit, csv_path: str | Path) -> str:
    status = "READY_FOR_PUBLIC_RELEASE_REVIEW" if audit.ready else "NOT_READY"
    lines = [
        "# Public release audit",
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
        lines.extend(["category | path | issue | detail", "--- | --- | --- | ---"])
        for issue in audit.issues[:100]:
            lines.append(f"{issue.category} | {issue.path} | {issue.issue} | {issue.detail}")
        if len(audit.issues) > 100:
            lines.append(f"... | ... | ... | {len(audit.issues) - 100} additional issues")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本审计检查公开代码发布前的最低条件：版本库、复现文件、数据访问说明、校验记录和常见凭据泄露模式。它不能替代人工安全审查，也不能生成 DOI；正式投稿前仍需确认公开仓库、归档 DOI 和数据政策合规性。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_public_release_audit_command(
    root: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[PublicReleaseAudit, Path, Path]:
    audit = audit_public_release(root)
    csv_output = write_public_release_audit_csv(audit, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_public_release_audit(audit, csv_output), encoding="utf-8")
    return audit, report_output, csv_output
