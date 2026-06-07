from pathlib import Path
import zipfile

import pandas as pd

from nature_climate_ai.fluxnet_raw import audit_fluxnet_archive, audit_fluxnet_raw_archives


def _write_fluxnet_zip(path: Path, header: list[str]) -> None:
    csv_text = ",".join(header) + "\n20200101,1,2,3,4,5\n"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("AMF_US-X_FLUXNET_FLUXMET_DD_2000-2001_v1.3_r1.csv", csv_text)


def test_audit_fluxnet_archive_detects_required_daily_variables(tmp_path: Path) -> None:
    archive = tmp_path / "AMF_US-X_FLUXNET_2000-2001_v1.3_r1.zip"
    _write_fluxnet_zip(
        archive,
        ["TIMESTAMP", "GPP_NT_VUT_REF", "LE_F_MDS", "TA_F", "SW_IN_F", "VPD_F"],
    )

    row = audit_fluxnet_archive(archive)

    assert row["zip_status"] == "OK"
    assert row["missing_required_variables"] == ""
    assert "FLUXMET_DD" in str(row["daily_member"])


def test_fluxnet_raw_audit_writes_report_for_missing_variable(tmp_path: Path) -> None:
    archive = tmp_path / "AMF_US-X_FLUXNET_2000-2001_v1.3_r1.zip"
    _write_fluxnet_zip(archive, ["TIMESTAMP", "GPP_NT_VUT_REF"])

    result = audit_fluxnet_raw_archives(
        input_dir=tmp_path,
        output_csv=tmp_path / "metadata" / "fluxnet_raw_archive_audit.csv",
        output_report=tmp_path / "metadata" / "fluxnet_raw_archive_audit.md",
    )

    assert result.status == "PARTIAL_VARIABLE_COVERAGE"
    assert result.output_csv.exists()
    rows = pd.read_csv(result.output_csv)
    assert rows.loc[0, "zip_status"] == "OK"
    assert "LE_F_MDS" in rows.loc[0, "missing_required_variables"]
    assert "Missing required daily variables" in result.output_report.read_text(encoding="utf-8")


def test_audit_fluxnet_archive_reads_daily_header_from_truncated_zip(tmp_path: Path) -> None:
    archive = tmp_path / "AMF_US-X_FLUXNET_2000-2001_v1.3_r1.zip"
    _write_fluxnet_zip(
        archive,
        ["TIMESTAMP", "GPP_NT_VUT_REF", "LE_F_MDS", "TA_F", "SW_IN_F", "VPD_F"],
    )
    content = archive.read_bytes()
    archive.write_bytes(content[:-22])

    row = audit_fluxnet_archive(archive)

    assert row["zip_status"] == "TRUNCATED_BUT_DAILY_READABLE"
    assert row["missing_required_variables"] == ""
