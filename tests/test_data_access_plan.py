from pathlib import Path

from nature_climate_ai.config import load_study_config
from nature_climate_ai.data_access_plan import build_data_access_plan, run_data_access_plan_command


def test_build_data_access_plan_lists_public_sources() -> None:
    config = load_study_config("config/study.yaml")
    rows = build_data_access_plan(config)

    assert {row.source for row in rows} == {"era5", "modis", "fluxnet"}
    era5 = next(row for row in rows if row.source == "era5")
    assert "2m_temperature" in era5.requested_variables
    assert era5.target_years == "2000-2025"
    assert era5.access_status == "GEE_EXPORT_PRESENT_GRID_ALIGNMENT_BLOCKED"


def test_data_access_plan_command_writes_manifest_and_report(tmp_path: Path) -> None:
    manifest_path = tmp_path / "metadata" / "data_access_manifest.csv"
    report_path = tmp_path / "metadata" / "data_access_plan.md"

    manifest, report = run_data_access_plan_command(
        config_path="config/study.yaml",
        manifest_path=manifest_path,
        report_path=report_path,
    )

    assert manifest == manifest_path
    assert report == report_path
    manifest_text = manifest.read_text(encoding="utf-8")
    assert "source,provider,source_url" in manifest_text
    assert "DATA_ACCESS_REQUIRED" not in manifest_text
    report_text = report.read_text(encoding="utf-8")
    assert "Status: READY_FOR_DATA_DOWNLOAD" in report_text
    assert "中文" in report_text
