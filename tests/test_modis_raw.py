from pathlib import Path

from nature_climate_ai.modis_raw import expected_phase1_granules, run_modis_raw_inventory_command, scan_modis_raw_files


def test_scan_modis_raw_files_parses_hdf_file_name(tmp_path: Path) -> None:
    root = tmp_path / "modis"
    path = root / "MOD13Q1" / "2001" / "001" / "MOD13Q1.A2001001.h31v11.061.2020061201448.hdf"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\x0e\x03\x13\x01mock-hdf")

    frame = scan_modis_raw_files(root)

    assert len(frame) == 1
    assert frame.loc[0, "product"] == "MOD13Q1"
    assert frame.loc[0, "year"] == "2001"
    assert frame.loc[0, "doy"] == "001"
    assert frame.loc[0, "tile"] == "h31v11"
    assert frame.loc[0, "collection"] == "061"


def test_modis_raw_inventory_flags_html_payload(tmp_path: Path) -> None:
    root = tmp_path / "modis"
    path = root / "MYD13Q1.A2001001.h29v12.061.2020061201448.hdf"
    path.parent.mkdir(parents=True)
    path.write_text("<!DOCTYPE html><html></html>", encoding="utf-8")

    result = run_modis_raw_inventory_command(
        input_dir=root,
        output_csv=tmp_path / "metadata" / "modis_raw_inventory.csv",
        output_report=tmp_path / "metadata" / "modis_raw_inventory.md",
        start_year=2001,
        end_year=2001,
    )

    assert result.status == "NEEDS_REVIEW"
    assert result.suspicious_files == 1
    assert "Downloaded HTML" in result.rows.loc[0, "issue"]


def test_expected_phase1_granules_counts_products_tiles_and_16_day_slots() -> None:
    assert expected_phase1_granules(2001, 2001) == 23 * 2 * 4
