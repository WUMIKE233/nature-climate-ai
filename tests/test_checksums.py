from pathlib import Path

from nature_climate_ai.checksums import audit_data_checksums, compute_sha256, run_checksum_audit_command


def test_compute_sha256_records_file_digest(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")

    assert compute_sha256(path) == "ea14f99c47575613ab22111122c847728c61007f6bfd7b062d02fcb99df3feb0"


def test_checksum_audit_ignores_metadata_and_checksum_outputs(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    raw = data_root / "raw"
    metadata = data_root / "metadata"
    checksums = data_root / "checksums"
    raw.mkdir(parents=True)
    metadata.mkdir()
    checksums.mkdir()
    (raw / "era5_sample.nc").write_bytes(b"1234")
    (metadata / "template.csv").write_text("metadata\n", encoding="utf-8")
    (checksums / "data_checksums.csv").write_text("old\n", encoding="utf-8")

    audit = audit_data_checksums(data_root)

    assert audit.ready
    assert len(audit.rows) == 1
    assert audit.rows[0].path.endswith("era5_sample.nc")
    assert audit.rows[0].algorithm == "sha256"


def test_checksum_audit_command_writes_report_and_csv(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    raw = data_root / "raw"
    raw.mkdir(parents=True)
    (raw / "modis_sample.csv").write_text("pixel_id,evi\np1,0.3\n", encoding="utf-8")

    audit, report, csv_output = run_checksum_audit_command(
        root=data_root,
        output_path=tmp_path / "data_checksum_audit.md",
        csv_path=tmp_path / "data_checksums.csv",
    )

    assert audit.ready
    assert report.exists()
    assert csv_output.exists()
    assert "Data checksum audit" in report.read_text(encoding="utf-8")
    assert "modis_sample.csv" in csv_output.read_text(encoding="utf-8")


def test_checksum_audit_reports_not_ready_without_data(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()

    audit, report, csv_output = run_checksum_audit_command(
        root=data_root,
        output_path=tmp_path / "data_checksum_audit.md",
        csv_path=tmp_path / "data_checksums.csv",
    )

    assert not audit.ready
    assert "Status: NOT_READY" in report.read_text(encoding="utf-8")
    assert csv_output.read_text(encoding="utf-8").startswith("path,bytes,algorithm,checksum")
