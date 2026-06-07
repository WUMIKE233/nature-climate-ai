from __future__ import annotations

import csv
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

from .config import load_study_config


@dataclass(frozen=True)
class FigureSpec:
    number: str
    title: str
    evidence_required: str
    output_path: str
    status: str


DEFAULT_FIGURES = (
    FigureSpec("Fig. 1", "Global study design and data/model pipeline", "data coverage and workflow outputs", "figures/generated/fig1_workflow.svg", "schematic_ready"),
    FigureSpec("Fig. 2", "Discovered climate precursor patterns and regions", "validated attribution maps", "figures/generated/fig2_precursors.png", "result_required"),
    FigureSpec("Fig. 3", "Prediction and attribution validation versus baselines", "holdout metrics and uncertainty", "figures/generated/fig3_validation.png", "result_required"),
    FigureSpec("Fig. 4", "Ecosystem validation and mechanism interpretation", "FLUXNET site-level agreement", "figures/generated/fig4_fluxnet.png", "result_required"),
    FigureSpec("Extended Data Fig. 1", "Robustness to event definitions", "threshold sensitivity analysis", "figures/generated/extended_data_fig1_sensitivity.png", "result_required"),
    FigureSpec("Extended Data Fig. 2", "Transfer across biomes or continents", "spatial holdout analysis", "figures/generated/extended_data_fig2_transfer.png", "result_required"),
)


def render_figure_plan() -> str:
    lines = ["number | title | evidence required | output | status", "--- | --- | --- | --- | ---"]
    for spec in DEFAULT_FIGURES:
        lines.append(f"{spec.number} | {spec.title} | {spec.evidence_required} | {spec.output_path} | {spec.status}")
    return "\n".join(lines)


def _box(x: int, y: int, width: int, height: int, title: str, subtitle: str, fill: str) -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="#1f2937" stroke-width="1.5"/>',
            f'<text x="{x + 16}" y="{y + 28}" font-size="18" font-weight="700" fill="#111827">{escape(title)}</text>',
            f'<text x="{x + 16}" y="{y + 54}" font-size="13" fill="#374151">{escape(subtitle)}</text>',
        ]
    )


def _arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#334155" stroke-width="2.2" marker-end="url(#arrow)"/>'


def render_fig1_workflow_svg(config: dict[str, Any]) -> str:
    project = config["project"]
    data_sources = config["data_sources"]
    temporal = config["temporal_domain"]
    lead_times = ", ".join(str(value) for value in temporal.get("lead_time_days", []))
    source_line = " + ".join(source.upper() for source in data_sources)
    title = project["working_title"]

    boxes = [
        _box(40, 115, 250, 92, "Public data", source_line, "#dbeafe"),
        _box(350, 115, 250, 92, "Quality control", "MODIS flags + access audit", "#dcfce7"),
        _box(660, 115, 250, 92, "Stress events", "EVI/NDVI anomalies", "#fef3c7"),
        _box(40, 285, 250, 92, "Climate lags", f"ERA5 lead windows: {lead_times} d", "#e0e7ff"),
        _box(350, 285, 250, 92, "AI discovery", "interpretable precursor ranking", "#fae8ff"),
        _box(660, 285, 250, 92, "Validation", "temporal + spatial + FLUXNET", "#fee2e2"),
        _box(350, 455, 250, 92, "Manuscript gate", "claims promoted only after evidence", "#f3f4f6"),
    ]
    arrows = [
        _arrow(290, 161, 350, 161),
        _arrow(600, 161, 660, 161),
        _arrow(165, 207, 165, 285),
        _arrow(290, 331, 350, 331),
        _arrow(600, 331, 660, 331),
        _arrow(785, 377, 600, 501),
        _arrow(475, 377, 475, 455),
    ]
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600" viewBox="0 0 960 600">',
            "<defs>",
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#334155"/>',
            "</marker>",
            "</defs>",
            '<rect width="960" height="600" fill="#ffffff"/>',
            f'<text x="40" y="48" font-size="24" font-weight="800" fill="#111827">{escape(title)}</text>',
            '<text x="40" y="76" font-size="14" fill="#475569">Fig. 1 schematic: workflow only; result panels remain evidence-gated.</text>',
            *boxes,
            *arrows,
            '<text x="40" y="575" font-size="12" fill="#64748b">Generated from config/study.yaml. No scientific result is implied by this schematic.</text>',
            "</svg>",
        ]
    )


def write_figure_manifest(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["number", "title", "evidence_required", "output_path", "status"],
        )
        writer.writeheader()
        for spec in DEFAULT_FIGURES:
            writer.writerow(spec.__dict__)
    return output


def render_figure_generation_report(generated: Path, manifest: Path) -> str:
    return "\n".join(
        [
            "# Figure generation report",
            "",
            "Status: PARTIAL_READY",
            "",
            f"- Generated schematic: {generated.as_posix()}",
            f"- Figure manifest: {manifest.as_posix()}",
            "",
            "Fig. 1 is a non-result workflow schematic generated from the study configuration. Figures 2-4 remain result-dependent because they need validated attribution, prediction and FLUXNET evidence.",
            "",
            "## 中文审阅说明",
            "",
            "本报告只说明 Fig. 1 研究流程示意图已经可生成。Fig. 2-4 仍需要真实数据分析、验证结果和不确定性评估，不能提前绘制或写入结论。",
        ]
    ) + "\n"


def run_figure_asset_generation_command(
    config_path: str | Path,
    output_dir: str | Path,
    manifest_path: str | Path,
    report_path: str | Path,
) -> tuple[Path, Path, Path]:
    config = load_study_config(config_path)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    fig1 = output_root / "fig1_workflow.svg"
    fig1.write_text(render_fig1_workflow_svg(config), encoding="utf-8")
    manifest = write_figure_manifest(manifest_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_figure_generation_report(fig1, manifest), encoding="utf-8")
    return fig1, manifest, report
