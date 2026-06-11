from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .author_metadata import audit_author_metadata
from .checksums import audit_data_checksums
from .config import load_study_config
from .data_access_plan import build_data_access_plan
from .data_access_templates import audit_data_access_templates
from .download_status import read_download_log
from .evidence import audit_evidence_artifacts, load_evidence_registry
from .manuscript_format import audit_manuscript_format
from .public_release import audit_public_release
from .references import audit_references, load_reference_metadata
from .reproducibility import audit_environment
from .submission_gate import evaluate_submission_gate
from .submission_package import audit_submission_package


READY_STATUSES = {"READY"}
SMOKE_READY_STATUSES = {"READY", "COMPLETE_FOR_SYNTHETIC_DATA"}

FIGURE_ASSETS = (
    "figures/generated/fig1_workflow.svg",
    "figures/generated/figure_manifest.csv",
    "figures/generated/figure_generation_report.md",
    "figures/generated/fig2_precursors.png",
    "figures/generated/fig3_validation.png",
    "figures/generated/fig4_fluxnet.png",
)


@dataclass(frozen=True)
class DashboardRow:
    component: str
    status: str
    blockers: int
    summary: str
    evidence: str


@dataclass(frozen=True)
class ReadinessDashboard:
    rows: tuple[DashboardRow, ...]

    @property
    def ready(self) -> bool:
        return all(
            row.status in SMOKE_READY_STATUSES if row.component == "pipeline_smoke" else row.status in READY_STATUSES
            for row in self.rows
        )

    @property
    def blocker_count(self) -> int:
        return sum(row.blockers for row in self.rows)

    def top_blockers(self, limit: int = 5) -> tuple[DashboardRow, ...]:
        return tuple(
            sorted(
                (row for row in self.rows if row.blockers > 0),
                key=lambda row: (-row.blockers, row.component),
            )[:limit]
        )

    def top_blocker_actions(self, limit: int = 5) -> tuple[str, ...]:
        return tuple(_action_hint(row) for row in self.top_blockers(limit=limit))


ACTION_HINTS = {
    "data_access": "confirm source access or record the blocking licence/account step",
    "data_access_templates": "complete the missing request templates before claiming data availability",
    "era5_download_status": "resolve CDS licence/download failures, then refresh checksum and QC reports",
    "gee_grid_alignment": "rerun the shared-grid audit after MODIS/ERA5 export updates",
    "evidence_registry": "complete or explicitly defer pending evidence claims",
    "evidence_artifacts": "generate missing artifacts and replace placeholder files with real outputs",
    "figure_assets": "generate result figures from validated analysis artifacts",
    "manuscript_format": "fix manuscript format issues before journal-specific export",
    "submission_package": "replace placeholders and regenerate the package audit",
    "references": "fill missing reference metadata and literature-gap notes",
    "author_metadata": "collect author approvals, funding, competing-interest and contribution fields",
    "public_release": "finish public-release checks before tagging or archiving",
    "submission_gate": "clear unresolved evidence and manuscript gate reasons before submission",
}


def _action_hint(row: DashboardRow) -> str:
    hint = ACTION_HINTS.get(row.component, "review this component's evidence and refresh its audit command")
    return f"{row.component}: {hint}"


def _relative(root: Path, path: str | Path) -> Path:
    raw = Path(path)
    return raw if raw.is_absolute() else root / raw


def _smoke_status(root: Path) -> tuple[str, int, str, str]:
    report = root / "reproducibility/pipeline_smoke_report.md"
    manifest = root / "reproducibility/pipeline_smoke_manifest.csv"
    if not report.exists() or not manifest.exists():
        return "NOT_READY", 1, "synthetic smoke-test report or manifest is missing", "pipeline_smoke_test"
    text = report.read_text(encoding="utf-8")
    if "COMPLETE_FOR_SYNTHETIC_DATA" in text:
        return (
            "COMPLETE_FOR_SYNTHETIC_DATA",
            0,
            "synthetic workflow completed; outputs are excluded from manuscript evidence",
            f"{report.as_posix()}; {manifest.as_posix()}",
        )
    return "NOT_READY", 1, "synthetic smoke-test report exists but lacks completion status", report.as_posix()


def _figure_status(root: Path) -> DashboardRow:
    missing = tuple(asset for asset in FIGURE_ASSETS if not (root / asset).exists())
    fig1_ready = not any(asset in missing for asset in FIGURE_ASSETS[:3])
    if not missing:
        status = "READY"
    elif fig1_ready:
        status = "PARTIAL_READY"
    else:
        status = "NOT_READY"
    summary = (
        "Fig. 1 workflow assets exist; result figures remain blocked by real analysis"
        if status == "PARTIAL_READY"
        else f"{len(FIGURE_ASSETS) - len(missing)}/{len(FIGURE_ASSETS)} planned figure assets exist"
    )
    return DashboardRow(
        component="figure_assets",
        status=status,
        blockers=len(missing),
        summary=summary,
        evidence="; ".join(FIGURE_ASSETS),
    )


def _era5_download_status(root: Path) -> DashboardRow:
    report = read_download_log(root / "data/metadata/era5_download_log.csv")
    if report.status == "READY_FOR_QC":
        blockers = 0
        summary = f"{report.success_count} ERA5/ERA5-Land downloads ready for checksum and QC"
    elif report.status == "BLOCKED_BY_LICENSE":
        blockers = report.licence_blocked_count
        summary = f"{report.licence_blocked_count} CDS licence-blocked ERA5/ERA5-Land attempts"
    elif report.status == "NO_LOG":
        blockers = 1
        summary = "ERA5 download log is missing"
    elif report.status == "NO_DOWNLOAD_ATTEMPTS":
        blockers = 1
        summary = "ERA5 download log exists but contains no attempts"
    else:
        blockers = max(report.failed_count, 1)
        summary = f"{report.failed_count} ERA5/ERA5-Land download attempts failed"
    return DashboardRow(
        component="era5_download_status",
        status=report.status,
        blockers=blockers,
        summary=summary,
        evidence="data/metadata/era5_download_log.csv; data/metadata/era5_download_status.md",
    )


def _gee_grid_alignment_status(root: Path) -> DashboardRow:
    report = root / "data/metadata/gee_grid_alignment_audit.md"
    csv_path = root / "data/metadata/gee_grid_alignment_audit.csv"
    evidence = f"{report.as_posix()}; {csv_path.as_posix()}"
    if not report.exists() or not csv_path.exists():
        return DashboardRow(
            component="gee_grid_alignment",
            status="NOT_READY",
            blockers=1,
            summary="GEE MODIS/ERA5 grid-alignment audit is missing",
            evidence=evidence,
        )

    text = report.read_text(encoding="utf-8")
    if "Status: PASS_SHARED_GRID" in text:
        return DashboardRow(
            component="gee_grid_alignment",
            status="READY",
            blockers=0,
            summary="MODIS and ERA5 GEE reference rasters share one pixel grid",
            evidence=evidence,
        )
    if "Status: FAIL_GRID_MISMATCH" in text:
        return DashboardRow(
            component="gee_grid_alignment",
            status="NOT_READY",
            blockers=1,
            summary="MODIS and ERA5 GEE reference rasters do not share one pixel grid",
            evidence=evidence,
        )
    return DashboardRow(
        component="gee_grid_alignment",
        status="NOT_READY",
        blockers=1,
        summary="GEE grid-alignment audit exists but lacks a recognized status",
        evidence=evidence,
    )


def _diagnostic_text(text: str) -> str:
    return (
        text.replace("RESULT_REQUIRED", "result")
        .replace("AUTHOR_REQUIRED", "author")
        .replace("DATA_ACCESS_REQUIRED", "data-access")
    )


def build_readiness_dashboard(
    root: str | Path = ".",
    manuscript: str | Path = "manuscript/nature_article_draft.md",
    registry: str | Path = "evidence/registry.yaml",
    config: str | Path = "config/study.yaml",
    reference_metadata: str | Path = "manuscript/reference_metadata.yaml",
) -> ReadinessDashboard:
    root_path = Path(root)
    manuscript_path = _relative(root_path, manuscript)
    registry_path = _relative(root_path, registry)
    config_path = _relative(root_path, config)
    reference_path = _relative(root_path, reference_metadata)

    evidence_report = load_evidence_registry(registry_path)
    artifact_audit = audit_evidence_artifacts(registry_path, root_path)
    gate = evaluate_submission_gate(manuscript_path, registry_path)
    format_report = audit_manuscript_format(manuscript_path, journal="nature")
    package_audit = audit_submission_package(root_path)
    author_audit = audit_author_metadata(root_path / "manuscript/author_metadata.yaml")
    public_release_audit = audit_public_release(root_path)
    reference_data = load_reference_metadata(reference_path)
    reference_report = audit_references(reference_data, reference_path)
    environment = audit_environment()
    study_config = load_study_config(config_path)
    access_rows = build_data_access_plan(study_config)
    access_blockers = sum(row.access_status in {"DATA_ACCESS_REQUIRED", "PENDING_ACCESS_CONFIRMATION"} for row in access_rows)
    access_template_audit = audit_data_access_templates(root_path)
    checksum_audit = audit_data_checksums(root_path / "data")
    smoke_status, smoke_blockers, smoke_summary, smoke_evidence = _smoke_status(root_path)

    rows = (
        DashboardRow(
            component="tests_and_environment",
            status="READY" if environment.ready else "NOT_READY",
            blockers=len(environment.missing_packages),
            summary=f"{len(environment.package_versions)} core packages recorded",
            evidence="reproducibility/environment_report.md; reproducibility/command_manifest.csv",
        ),
        DashboardRow(
            component="pipeline_smoke",
            status=smoke_status,
            blockers=smoke_blockers,
            summary=smoke_summary,
            evidence=smoke_evidence,
        ),
        DashboardRow(
            component="data_access",
            status="READY" if access_blockers == 0 else "NOT_READY",
            blockers=access_blockers,
            summary=f"{access_blockers} source access confirmations remain pending",
            evidence="data/metadata/data_access_manifest.csv; data/metadata/data_access_plan.md",
        ),
        DashboardRow(
            component="data_access_templates",
            status="READY" if access_template_audit.ready else "NOT_READY",
            blockers=len(access_template_audit.issues),
            summary=f"{len(access_template_audit.issues)} data-access template issues remain",
            evidence="data/metadata/data_access_template_audit.md; data/metadata/data_access_template_status.csv",
        ),
        _era5_download_status(root_path),
        _gee_grid_alignment_status(root_path),
        DashboardRow(
            component="data_checksums",
            status="READY" if checksum_audit.ready else "NOT_READY",
            blockers=0 if checksum_audit.ready else 1,
            summary=f"{len(checksum_audit.rows)} checksum rows recorded for local data files",
            evidence="data/checksums/data_checksum_audit.md; data/checksums/data_checksums.csv",
        ),
        DashboardRow(
            component="evidence_registry",
            status="READY" if evidence_report.complete_count == len(evidence_report.items) else "NOT_READY",
            blockers=len(evidence_report.pending_claims),
            summary=f"{evidence_report.complete_count}/{len(evidence_report.items)} evidence items complete",
            evidence=evidence_report.path.as_posix(),
        ),
        DashboardRow(
            component="evidence_artifacts",
            status="READY" if artifact_audit.ready else "NOT_READY",
            blockers=artifact_audit.missing_count + artifact_audit.placeholder_file_count,
            summary=f"{artifact_audit.missing_count} missing artifacts; {artifact_audit.placeholder_file_count} placeholder files",
            evidence="evidence/artifact_audit.md; evidence/artifact_audit.csv",
        ),
        _figure_status(root_path),
        DashboardRow(
            component="manuscript_format",
            status="READY" if format_report.status == "READY_FOR_FORMAT_REVIEW" else "NOT_READY",
            blockers=len(format_report.issues),
            summary=f"{format_report.main_text_words} main-text words; {format_report.display_items} display items",
            evidence=format_report.manuscript.as_posix(),
        ),
        DashboardRow(
            component="submission_package",
            status="READY" if package_audit.ready else "NOT_READY",
            blockers=package_audit.missing_count + package_audit.placeholder_file_count,
            summary=f"{package_audit.missing_count} missing files; {package_audit.placeholder_file_count} placeholder files",
            evidence="manuscript/submission_package_audit.md; manuscript/submission_package_status.csv",
        ),
        DashboardRow(
            component="references",
            status="READY" if reference_report.ready else "NOT_READY",
            blockers=len(reference_report.missing_required_fields) + len(reference_report.literature_gaps),
            summary=f"{reference_report.checked_references}/{reference_report.total_references} seed references checked; {len(reference_report.literature_gaps)} literature gaps",
            evidence=reference_report.metadata_path.as_posix(),
        ),
        DashboardRow(
            component="author_metadata",
            status="READY" if author_audit.ready else "NOT_READY",
            blockers=len(author_audit.issues),
            summary=f"{len(author_audit.issues)} author metadata issues remain",
            evidence="manuscript/author_metadata.yaml; manuscript/author_metadata_audit.md; manuscript/author_metadata_status.csv",
        ),
        DashboardRow(
            component="public_release",
            status="READY" if public_release_audit.ready else "NOT_READY",
            blockers=len(public_release_audit.issues),
            summary=f"{len(public_release_audit.issues)} public release issues remain",
            evidence="reproducibility/public_release_audit.md; reproducibility/public_release_status.csv",
        ),
        DashboardRow(
            component="submission_gate",
            status="READY" if gate.ready else "NOT_READY",
            blockers=len(gate.reasons),
            summary=_diagnostic_text("; ".join(gate.reasons)) if gate.reasons else "all submission gates passed",
            evidence=f"{gate.manuscript.as_posix()}; {gate.registry.as_posix()}",
        ),
    )
    return ReadinessDashboard(rows=rows)


def write_dashboard_csv(dashboard: ReadinessDashboard, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["component", "status", "blockers", "summary", "evidence"])
        writer.writeheader()
        for row in dashboard.rows:
            writer.writerow(row.__dict__)
    return output


def render_readiness_dashboard(dashboard: ReadinessDashboard, csv_path: str | Path) -> str:
    status = "READY_FOR_SUBMISSION" if dashboard.ready else "NOT_READY"
    lines = [
        "# Nature/Science readiness dashboard",
        "",
        f"Status: {status}",
        f"Total blockers: {dashboard.blocker_count}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "component | status | blockers | summary | evidence",
        "--- | --- | ---: | --- | ---",
    ]
    for row in dashboard.rows:
        lines.append(f"{row.component} | {row.status} | {row.blockers} | {row.summary} | {row.evidence}")
    top_blockers = dashboard.top_blockers()
    if top_blockers:
        lines.extend(
            [
                "",
                "## Top blockers",
                "",
            ]
        )
        for row in top_blockers:
            lines.append(f"- {row.component}: {row.blockers} blocker(s) - {row.summary}")
        lines.extend(
            [
                "",
                "## Top blocker actions",
                "",
            ]
        )
        for action in dashboard.top_blocker_actions():
            lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Next-action logic",
            "",
            "Prioritize gates in this order: data access, real data preprocessing, modeling/validation artifacts, uncertainty and figure outputs, manuscript placeholder replacement, final package export.",
            "",
            "## 中文审阅说明",
            "",
            "本面板汇总当前投稿包的主要门控状态。它不会自动完成任何证据项，也不会把合成数据当作论文结果；只用于快速定位下一步最重要的阻塞。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_readiness_dashboard_command(
    output_path: str | Path,
    csv_path: str | Path,
    root: str | Path = ".",
    manuscript: str | Path = "manuscript/nature_article_draft.md",
    registry: str | Path = "evidence/registry.yaml",
    config: str | Path = "config/study.yaml",
    reference_metadata: str | Path = "manuscript/reference_metadata.yaml",
) -> tuple[ReadinessDashboard, Path, Path]:
    dashboard = build_readiness_dashboard(
        root=root,
        manuscript=manuscript,
        registry=registry,
        config=config,
        reference_metadata=reference_metadata,
    )
    csv_output = write_dashboard_csv(dashboard, csv_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_readiness_dashboard(dashboard, csv_output), encoding="utf-8")
    return dashboard, output, csv_output
