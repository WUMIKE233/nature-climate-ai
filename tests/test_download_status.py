from pathlib import Path

from nature_climate_ai.download_status import read_download_log, render_download_status, run_download_status_command


def test_download_status_reports_missing_log(tmp_path: Path) -> None:
    report = read_download_log(tmp_path / "missing.csv")

    assert report.status == "NO_LOG"
    assert not report.ready_for_qc
    assert "NO_LOG" in render_download_status(report)


def test_download_status_detects_cds_licence_block(tmp_path: Path) -> None:
    log = tmp_path / "era5_download_log.csv"
    log.write_text(
        "\n".join(
            [
                "source,status,local_path,remote_id,size_bytes,sha256,timestamp,message",
                'era5,failed,data/raw/era5/era5_single_200001.nc,reanalysis-era5-single-levels/2000/01,0,,2026-06-05T12:00:00,"required licences not accepted"',
                'era5,failed,data/raw/era5/era5_land_200001.nc,reanalysis-era5-land/2000/01,0,,2026-06-05T12:00:01,"required licences not accepted"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    report, output = run_download_status_command(log, tmp_path / "era5_download_status.md")
    text = output.read_text(encoding="utf-8")

    assert report.status == "BLOCKED_BY_LICENSE"
    assert report.licence_blocked_count == 2
    assert "reanalysis-era5-single-levels" in text
    assert "manage-licences" in text
    assert "中文审阅说明" in text


def test_download_status_ready_for_qc_when_attempts_succeed(tmp_path: Path) -> None:
    log = tmp_path / "era5_download_log.csv"
    log.write_text(
        "\n".join(
            [
                "source,status,local_path,remote_id,size_bytes,sha256,timestamp,message",
                "era5,success,data/raw/era5/era5_single_200001.nc,reanalysis-era5-single-levels/2000/01,123,abc,2026-06-05T12:00:00,Downloaded",
                "era5,success,data/raw/era5/era5_land_200001.nc,reanalysis-era5-land/2000/01,456,def,2026-06-05T12:00:01,Downloaded",
                "",
            ]
        ),
        encoding="utf-8",
    )

    report = read_download_log(log)

    assert report.status == "READY_FOR_QC"
    assert report.ready_for_qc
    assert report.total_size_bytes == 579
