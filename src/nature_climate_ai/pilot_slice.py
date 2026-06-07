from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PilotArtifact:
    group: str
    artifact: str
    exists: bool
    role: str


@dataclass(frozen=True)
class PilotEvidenceSlice:
    artifacts: tuple[PilotArtifact, ...]

    @property
    def ready(self) -> bool:
        return all(item.exists for item in self.artifacts)

    @property
    def missing_count(self) -> int:
        return sum(not item.exists for item in self.artifacts)

    @property
    def complete_count(self) -> int:
        return sum(item.exists for item in self.artifacts)


DEFAULT_PILOT_ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    ("stress_event_definition", "results/stress_events/event_catalogue_summary.csv", "pilot stress-event catalogue"),
    ("stress_event_definition", "results/stress_events/quality_control_report.md", "stress-event QC report"),
    ("precursor_pathway", "results/modeling/feature_attribution_table.csv", "ranked precursor candidates"),
    ("precursor_pathway", "results/modeling/lag_response_summary.csv", "lag-response evidence"),
    ("predictive_validation", "results/validation/baseline_metrics.csv", "baseline comparator metrics"),
    ("predictive_validation", "results/validation/temporal_holdout_metrics.csv", "temporal holdout metrics"),
    ("predictive_validation", "results/validation/spatial_holdout_metrics.csv", "spatial holdout metrics"),
    ("predictive_validation", "results/validation/predictive_validation_summary.csv", "combined predictive validation summary"),
    ("robustness_falsification", "results/validation/placebo_metrics.csv", "placebo lag-shift test"),
    ("robustness_falsification", "results/validation/threshold_sensitivity.csv", "stress-threshold sensitivity"),
    ("robustness_falsification", "results/validation/biome_metrics.csv", "biome-stratified validation"),
    ("pilot_figures", "figures/generated/pilot_fig1_stress_event_map.png", "Pilot Fig. 1 stress-event map"),
    ("pilot_figures", "figures/generated/pilot_fig2_precursor_pathway.png", "Pilot Fig. 2 precursor pathway"),
    ("pilot_figures", "figures/generated/pilot_fig3_predictive_validation.png", "Pilot Fig. 3 predictive validation"),
)


def evaluate_minimum_evidence_slice(
    root: str | Path = ".",
    artifacts: tuple[tuple[str, str, str], ...] = DEFAULT_PILOT_ARTIFACTS,
) -> PilotEvidenceSlice:
    root_path = Path(root)
    rows = tuple(
        PilotArtifact(
            group=group,
            artifact=artifact,
            exists=(root_path / artifact).exists(),
            role=role,
        )
        for group, artifact, role in artifacts
    )
    return PilotEvidenceSlice(artifacts=rows)


def write_pilot_status_csv(slice_report: PilotEvidenceSlice, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["group", "artifact", "exists", "role"])
        writer.writeheader()
        for item in slice_report.artifacts:
            writer.writerow(item.__dict__)
    return output


def render_minimum_evidence_slice_report(slice_report: PilotEvidenceSlice, csv_path: str | Path) -> str:
    status = "READY_FOR_PILOT_REVIEW" if slice_report.ready else "NOT_READY"
    lines = [
        "# Minimum publishable evidence-slice gate",
        "",
        f"Status: {status}",
        f"Complete artifacts: {slice_report.complete_count}/{len(slice_report.artifacts)}",
        f"Missing artifacts: {slice_report.missing_count}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "group | exists | artifact | role",
        "--- | --- | --- | ---",
    ]
    for item in slice_report.artifacts:
        lines.append(f"{item.group} | {item.exists} | {item.artifact} | {item.role}")

    missing = [item for item in slice_report.artifacts if not item.exists]
    lines.extend(["", "## Decision rule", ""])
    if missing:
        lines.append("Do not expand the manuscript into full Nature/Science claims. Complete the missing pilot artifacts first.")
    else:
        lines.append("The minimum artifact set exists. Human scientific review must still verify signal strength before any manuscript claim is promoted.")

    lines.extend(
        [
            "",
            "## Stop rules",
            "",
            "- Stop or redesign if pilot results do not beat climatology, persistence and standard climate-index baselines.",
            "- Stop or downscope if precursor patterns collapse under temporal or spatial holdout.",
            "- Stop claim promotion if threshold, biome or sensor robustness checks fail.",
            "",
            "## 中文审阅说明",
            "",
            "该门控只检查最小可验证结果切片所需文件是否存在，不证明结果已经足够强。只有三张 pilot 图、基线对比、时空验证和稳健性检查都完成并通过人工科学审阅后，才应继续扩展到 Nature/Science 全稿。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_minimum_evidence_slice_command(
    root: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[PilotEvidenceSlice, Path, Path]:
    slice_report = evaluate_minimum_evidence_slice(root=root)
    csv_output = write_pilot_status_csv(slice_report, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_minimum_evidence_slice_report(slice_report, csv_output), encoding="utf-8")
    return slice_report, report_output, csv_output
