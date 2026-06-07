from pathlib import Path
import zipfile

import pandas as pd

from nature_climate_ai.fluxnet_anomalies import preprocess_fluxnet_anomalies, run_fluxnet_anomaly_preprocess_command


HEADER = ["TIMESTAMP", "GPP_NT_VUT_REF", "LE_F_MDS", "TA_F", "SW_IN_F", "VPD_F"]


def _write_daily_archive(path: Path) -> str:
    daily_member = "AMF_US-X_FLUXNET_FLUXMET_DD_2000-2001_v1.3_r1.csv"
    rows = [
        "20000101,1,2,3,4,5",
        "20010101,3,4,5,6,7",
        "20000102,-9999,1,2,3,4",
        "20010102,5,3,4,5,6",
    ]
    text = ",".join(HEADER) + "\n" + "\n".join(rows) + "\n"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(daily_member, text)
    return daily_member


def test_preprocess_fluxnet_anomalies_from_readable_archive(tmp_path: Path) -> None:
    archive = tmp_path / "AMF_US-X_FLUXNET_2000-2001_v1.3_r1.zip"
    daily_member = _write_daily_archive(archive)
    audit = tmp_path / "audit.csv"
    pd.DataFrame(
        [
            {
                "archive": archive.as_posix(),
                "site_id": "US-X",
                "zip_status": "OK",
                "daily_member": daily_member,
                "missing_required_variables": "",
            }
        ]
    ).to_csv(audit, index=False)

    result = preprocess_fluxnet_anomalies(audit, min_climatology_samples=2)

    assert result.qc["sites_processed"] == 1
    assert {"gpp_anomaly", "le_anomaly", "ta_anomaly", "sw_in_anomaly", "vpd_anomaly"}.issubset(result.anomalies.columns)
    day_one = result.anomalies[result.anomalies["day_of_year"] == 1]
    assert day_one["gpp_anomaly"].dropna().tolist() == [-1.0, 1.0]


def test_fluxnet_anomaly_command_writes_outputs_for_truncated_daily_readable_archive(tmp_path: Path) -> None:
    archive = tmp_path / "AMF_US-X_FLUXNET_2000-2001_v1.3_r1.zip"
    daily_member = _write_daily_archive(archive)
    content = archive.read_bytes()
    archive.write_bytes(content[:-22])
    audit = tmp_path / "audit.csv"
    pd.DataFrame(
        [
            {
                "archive": archive.as_posix(),
                "site_id": "US-X",
                "zip_status": "TRUNCATED_BUT_DAILY_READABLE",
                "daily_member": daily_member,
                "missing_required_variables": "",
            }
        ]
    ).to_csv(audit, index=False)

    completed, report = run_fluxnet_anomaly_preprocess_command(
        audit_csv=audit,
        output_path=tmp_path / "processed" / "fluxnet_anomalies.csv",
        report_path=tmp_path / "results" / "fluxnet_anomaly_preprocess_report.md",
        min_climatology_samples=2,
    )

    assert completed
    assert (tmp_path / "processed" / "fluxnet_anomalies.csv").exists()
    assert "COMPLETE_FOR_READABLE_ARCHIVES" in report.read_text(encoding="utf-8")
