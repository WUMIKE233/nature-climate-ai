from pathlib import Path

from nature_climate_ai.data_access_templates import audit_data_access_templates, run_data_access_template_audit_command


def test_current_data_access_templates_are_ready() -> None:
    audit = audit_data_access_templates(".")

    assert audit.ready
    assert audit.issues == ()


def test_complete_data_access_templates_are_ready(tmp_path: Path) -> None:
    metadata = tmp_path / "data" / "metadata"
    metadata.mkdir(parents=True)
    (metadata / "era5_request_parameters.yaml").write_text(
        "access_status: confirmed\nhuman_owner_pending: false\ndataset_id: reanalysis-era5-single-levels\n",
        encoding="utf-8",
    )
    (metadata / "era5_access_log.md").write_text(
        "# ERA5 access log\n\n- CDS account confirmed: yes\n- Dataset IDs: reanalysis-era5-single-levels\n- Download date: 2026-06-05\n",
        encoding="utf-8",
    )
    (metadata / "modis_products.yaml").write_text(
        "access_status: confirmed\nproduct_collection: '061'\nproducts: [MOD13Q1, MYD13Q1]\n",
        encoding="utf-8",
    )
    (metadata / "modis_quality_flags.md").write_text(
        "# MODIS quality flags\n\n- Product collection: 061\n- Review date: 2026-06-05\n",
        encoding="utf-8",
    )
    (metadata / "fluxnet_sites.csv").write_text(
        "site_id,country,latitude,longitude,plant_functional_type,years_available,policy_status,notes\n"
        "US-Example,USA,40.0,-105.0,grassland,2010-2015,CONFIRMED,policy reviewed\n",
        encoding="utf-8",
    )
    (metadata / "fluxnet_policy_review.md").write_text(
        "# FLUXNET policy review\n\n- FLUXNET dataset/version: FLUXNET2015\n- Review date: 2026-06-05\n",
        encoding="utf-8",
    )

    audit = audit_data_access_templates(tmp_path)

    assert audit.ready


def test_data_access_template_audit_command_writes_outputs(tmp_path: Path) -> None:
    audit, report, csv_output = run_data_access_template_audit_command(
        root=".",
        output_path=tmp_path / "data_access_template_audit.md",
        csv_path=tmp_path / "data_access_template_status.csv",
    )

    assert audit.ready
    assert report.exists()
    assert csv_output.exists()
    assert "Data access template audit" in report.read_text(encoding="utf-8")
    assert "template,field,issue,value" in csv_output.read_text(encoding="utf-8")
