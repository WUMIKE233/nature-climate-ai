from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .claim_gate import inspect_manuscript
from .evidence import load_evidence_registry


@dataclass(frozen=True)
class SubmissionGateReport:
    manuscript: Path
    registry: Path
    ready: bool
    reasons: tuple[str, ...]


def evaluate_submission_gate(manuscript: str | Path, registry: str | Path) -> SubmissionGateReport:
    claim_report = inspect_manuscript(manuscript)
    evidence_report = load_evidence_registry(registry)

    reasons: list[str] = []
    if claim_report.result_placeholders:
        reasons.append(f"{claim_report.result_placeholders} RESULT_REQUIRED placeholders remain.")
    if claim_report.author_placeholders:
        reasons.append(f"{claim_report.author_placeholders} AUTHOR_REQUIRED placeholders remain.")
    if claim_report.data_placeholders:
        reasons.append(f"{claim_report.data_placeholders} DATA_ACCESS_REQUIRED placeholders remain.")

    incomplete = evidence_report.pending_claims
    if incomplete:
        reasons.append(f"{len(incomplete)} evidence items are not complete.")

    return SubmissionGateReport(
        manuscript=claim_report.path,
        registry=evidence_report.path,
        ready=not reasons,
        reasons=tuple(reasons),
    )


def render_submission_gate(report: SubmissionGateReport) -> str:
    status = "READY" if report.ready else "NOT_READY"
    lines = [
        f"Submission gate: {status}",
        f"Manuscript: {report.manuscript}",
        f"Evidence registry: {report.registry}",
    ]
    if report.reasons:
        lines.append("")
        lines.append("Blocking reasons:")
        lines.extend(f"- {reason}" for reason in report.reasons)
    return "\n".join(lines)
