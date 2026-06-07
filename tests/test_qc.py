from pathlib import Path

from nature_climate_ai.qc import render_e00_qc_report, scan_data_inventory, summarize_placeholders


RESERVED_TOKENS = ("DATA_ACCESS_REQUIRED", "AUTHOR_REQUIRED", "RESULT_REQUIRED")


def test_data_inventory_ignores_metadata_csv(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    metadata = data_root / "metadata"
    checksums = data_root / "checksums"
    raw = data_root / "raw"
    metadata.mkdir(parents=True)
    checksums.mkdir()
    raw.mkdir(parents=True)
    (metadata / "fluxnet_sites.csv").write_text("template\n", encoding="utf-8")
    (checksums / "data_checksums.csv").write_text("path,checksum\n", encoding="utf-8")
    (raw / "sample.nc").write_bytes(b"1234")

    inventory = scan_data_inventory(data_root)
    assert inventory.file_count == 1
    assert inventory.candidate_files[0].name == "sample.nc"


def test_placeholder_summary_counts_tokens(tmp_path: Path) -> None:
    path = tmp_path / "template.md"
    path.write_text("DATA_ACCESS_REQUIRED AUTHOR_REQUIRED RESULT_REQUIRED", encoding="utf-8")
    summary = summarize_placeholders([path])[0]
    assert summary.data_access_required == 1
    assert summary.author_required == 1
    assert summary.result_required == 1


def test_e00_qc_report_renders_current_not_ready_state() -> None:
    report = render_e00_qc_report("config/study.yaml", "evidence/registry.yaml")
    assert "Status: NOT_READY" in report
    assert "Public data-source readiness" in report
    assert "Complete evidence items: 0/" in report
    assert "DATA_ACCESS_REQUIRED" not in report


def test_public_data_metadata_templates_do_not_use_reserved_tokens_as_field_values() -> None:
    metadata_root = Path("data/metadata")
    texts = {
        path: path.read_text(encoding="utf-8")
        for path in metadata_root.iterdir()
        if path.is_file() and path.name not in {"data_access_manifest.csv", "data_access_plan.md"}
    }

    assert texts
    for path, text in texts.items():
        assert not any(token in text for token in RESERVED_TOKENS), path
