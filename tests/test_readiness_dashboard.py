from pathlib import Path

from nature_climate_ai.readiness_dashboard import build_readiness_dashboard, run_readiness_dashboard_command


def test_readiness_dashboard_summarizes_current_blockers() -> None:
    dashboard = build_readiness_dashboard(".")

    assert not dashboard.ready
    assert dashboard.blocker_count > 0
    statuses = {row.component: row.status for row in dashboard.rows}
    assert statuses["submission_gate"] == "NOT_READY"
    assert statuses["tests_and_environment"] == "READY"
    assert statuses["gee_grid_alignment"] == "NOT_READY"
    assert statuses["era5_download_status"] in {"BLOCKED_BY_LICENSE", "READY_FOR_QC", "FAILED", "NO_LOG", "NO_DOWNLOAD_ATTEMPTS"}
    assert statuses["figure_assets"] in {"PARTIAL_READY", "NOT_READY"}


def test_readiness_dashboard_command_writes_report_and_csv(tmp_path: Path) -> None:
    dashboard, report, csv_path = run_readiness_dashboard_command(
        output_path=tmp_path / "readiness_dashboard.md",
        csv_path=tmp_path / "readiness_dashboard.csv",
        root=".",
    )

    assert not dashboard.ready
    assert report.exists()
    assert csv_path.exists()
    report_text = report.read_text(encoding="utf-8")
    assert "Nature/Science readiness dashboard" in report_text
    assert "中文审阅说明" in report_text
    assert "submission_gate" in csv_path.read_text(encoding="utf-8")
    assert "era5_download_status" in csv_path.read_text(encoding="utf-8")
    assert "gee_grid_alignment" in csv_path.read_text(encoding="utf-8")
    assert "component,status,blockers,summary,evidence" in csv_path.read_text(encoding="utf-8")
