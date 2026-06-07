from pathlib import Path

from nature_climate_ai.config import load_study_config
from nature_climate_ai.figures import (
    render_fig1_workflow_svg,
    render_figure_plan,
    run_figure_asset_generation_command,
)


def test_figure_plan_includes_outputs_and_statuses() -> None:
    plan = render_figure_plan()

    assert "figures/generated/fig1_workflow.svg" in plan
    assert "result_required" in plan


def test_fig1_workflow_svg_is_schematic_only() -> None:
    svg = render_fig1_workflow_svg(load_study_config("config/study.yaml"))

    assert svg.startswith("<svg")
    assert "workflow only" in svg
    assert "No scientific result is implied" in svg
    assert "RESULT_REQUIRED" not in svg


def test_generate_figure_assets_writes_schematic_manifest_and_report(tmp_path: Path) -> None:
    fig1, manifest, report = run_figure_asset_generation_command(
        config_path="config/study.yaml",
        output_dir=tmp_path / "figures",
        manifest_path=tmp_path / "figures" / "figure_manifest.csv",
        report_path=tmp_path / "figures" / "figure_generation_report.md",
    )

    assert fig1.exists()
    assert manifest.exists()
    assert report.exists()
    assert "Fig. 1 schematic" in fig1.read_text(encoding="utf-8")
    assert "fig2_precursors.png" in manifest.read_text(encoding="utf-8")
    assert "Fig. 2-4" in report.read_text(encoding="utf-8")
