from pathlib import Path

from nature_climate_ai.config import load_study_config
from nature_climate_ai.provider_requests import build_provider_request_templates, run_provider_request_templates_command


def test_provider_request_templates_include_public_sources() -> None:
    config = load_study_config("config/study.yaml")
    templates = build_provider_request_templates(config)

    assert set(templates) == {"era5", "modis", "fluxnet"}
    assert "2m_temperature" in templates["era5"]["cds_request_template"]["variable"]
    assert "2m_dewpoint_temperature" in templates["era5"]["cds_request_template"]["variable"]
    assert templates["modis"]["products"] == ["MOD13Q1", "MYD13Q1"]
    assert "GPP_NT_VUT_REF" in templates["fluxnet"]["variables"]


def test_provider_request_templates_command_writes_manifest_report_and_templates(tmp_path: Path) -> None:
    artifacts, manifest, report = run_provider_request_templates_command(
        config_path="config/study.yaml",
        output_dir=tmp_path / "provider_requests",
        manifest_path=tmp_path / "provider_request_manifest.csv",
        report_path=tmp_path / "provider_request_templates.md",
    )

    assert len(artifacts) == 3
    assert manifest.exists()
    assert report.exists()
    assert (tmp_path / "provider_requests" / "era5_request_template.yaml").exists()
    assert (tmp_path / "provider_requests" / "modis_request_template.yaml").exists()
    assert (tmp_path / "provider_requests" / "fluxnet_request_template.yaml").exists()
    assert "provider" in manifest.read_text(encoding="utf-8")
    assert "Provider request templates" in report.read_text(encoding="utf-8")


def test_provider_request_templates_do_not_emit_reserved_manuscript_tokens(tmp_path: Path) -> None:
    run_provider_request_templates_command(
        config_path="config/study.yaml",
        output_dir=tmp_path / "provider_requests",
        manifest_path=tmp_path / "provider_request_manifest.csv",
        report_path=tmp_path / "provider_request_templates.md",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in tmp_path.rglob("*") if path.is_file())

    assert "RESULT_REQUIRED" not in combined
    assert "AUTHOR_REQUIRED" not in combined
    assert "DATA_ACCESS_REQUIRED" not in combined
    assert "credential" in combined.lower()
