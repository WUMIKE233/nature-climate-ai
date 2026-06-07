from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .claim_gate import AUTHOR_TOKEN, DATA_TOKEN, RESULT_TOKEN


PACKAGE_FILES = (
    "manuscript/nature_article_draft.md",
    "manuscript/science_research_article_draft.md",
    "manuscript/cover_letter.md",
    "manuscript/presubmission_enquiry.md",
    "manuscript/supplementary_information_outline.md",
    "manuscript/submission_checklist.md",
    "manuscript/editorial_strategy.md",
    "manuscript/chinese_review_notes.md",
    "manuscript/reference_seed_list.md",
    "manuscript/reference_metadata.yaml",
    "manuscript/author_metadata.yaml",
    "manuscript/author_metadata_audit.md",
    "manuscript/author_metadata_status.csv",
    "docs/nature_claim_strategy.md",
    "docs/editorial_significance_rationale.md",
    "docs/known_risks_and_mitigation.md",
    "docs/validation_design.md",
    "docs/model_interpretability_plan.md",
    "docs/robustness_and_falsification_plan.md",
    "docs/data_ethics_and_licensing.md",
    "docs/target_journal_decision_tree.md",
    "docs/minimum_publishable_evidence_slice.md",
    "docs/readiness_dashboard.md",
    "docs/submission_readiness_audit.md",
)


@dataclass(frozen=True)
class PackageFileStatus:
    path: str
    exists: bool
    result_required: int
    author_required: int
    data_access_required: int
    issue: str

    @property
    def placeholder_total(self) -> int:
        return self.result_required + self.author_required + self.data_access_required


@dataclass(frozen=True)
class SubmissionPackageAudit:
    root: Path
    files: tuple[PackageFileStatus, ...]

    @property
    def missing_count(self) -> int:
        return sum(not item.exists for item in self.files)

    @property
    def placeholder_file_count(self) -> int:
        return sum(item.placeholder_total > 0 for item in self.files)

    @property
    def ready(self) -> bool:
        return self.missing_count == 0 and self.placeholder_file_count == 0


def _file_status(root: Path, relative_path: str) -> PackageFileStatus:
    path = root / relative_path
    if not path.exists():
        return PackageFileStatus(
            path=relative_path,
            exists=False,
            result_required=0,
            author_required=0,
            data_access_required=0,
            issue="missing",
        )
    text = path.read_text(encoding="utf-8")
    result = text.count(RESULT_TOKEN)
    author = text.count(AUTHOR_TOKEN)
    data = text.count(DATA_TOKEN)
    issue = "contains_placeholders" if result + author + data else "ok"
    return PackageFileStatus(
        path=relative_path,
        exists=True,
        result_required=result,
        author_required=author,
        data_access_required=data,
        issue=issue,
    )


def audit_submission_package(root: str | Path = ".", files: tuple[str, ...] = PACKAGE_FILES) -> SubmissionPackageAudit:
    root_path = Path(root)
    return SubmissionPackageAudit(
        root=root_path,
        files=tuple(_file_status(root_path, path) for path in files),
    )


def write_submission_package_status_csv(audit: SubmissionPackageAudit, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["path", "exists", "result_required", "author_required", "data_access_required", "issue"]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in audit.files:
            writer.writerow(item.__dict__)
    return output


def render_submission_package_audit(audit: SubmissionPackageAudit, csv_path: str | Path) -> str:
    status = "READY_FOR_FINAL_SUBMISSION_REVIEW" if audit.ready else "NOT_READY"
    lines = [
        "# Submission package audit",
        "",
        f"Status: {status}",
        f"Root: {audit.root.as_posix()}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"package_files | {len(audit.files)}",
        f"missing_files | {audit.missing_count}",
        f"placeholder_files | {audit.placeholder_file_count}",
        "",
        "## File status",
        "",
        "file | exists | result_token_count | author_token_count | data_access_token_count | issue",
        "--- | --- | ---: | ---: | ---: | ---",
    ]
    for item in audit.files:
        lines.append(
            f"{item.path} | {item.exists} | {item.result_required} | "
            f"{item.author_required} | {item.data_access_required} | {item.issue}"
        )
    lines.extend(
        [
            "",
            "## Manuscript-use warning",
            "",
            "A package file can exist and still be non-submission-ready if it contains unresolved result, author or data-access placeholders.",
            "",
            "## 中文审阅说明",
            "",
            "本审计检查投稿包文件是否齐全，以及是否仍含结果、作者或数据访问占位符。文件存在不等于可以投稿；占位符和证据缺口必须全部清理后才能进入最终提交审阅。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_submission_package_audit_command(
    root: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[SubmissionPackageAudit, Path, Path]:
    audit = audit_submission_package(root)
    csv_output = write_submission_package_status_csv(audit, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_submission_package_audit(audit, csv_output), encoding="utf-8")
    return audit, report_output, csv_output
