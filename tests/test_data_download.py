from pathlib import Path

from nature_climate_ai.data_download import run_era5_download_command


def test_era5_dry_run_counts_selected_months(tmp_path: Path, capsys, monkeypatch) -> None:
    config = tmp_path / "study.yaml"
    config.write_text(
        "\n".join(
            [
                "project: {}",
                "data_sources: {}",
                "stress_event_definition: {}",
                "modeling: {}",
                "validation: {}",
                "temporal_domain:",
                "  era5_years: [2000, 2000]",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("CDSAPI_URL", raising=False)
    monkeypatch.delenv("CDSAPI_KEY", raising=False)

    run_era5_download_command(
        config_path=config,
        output_dir=tmp_path / "raw",
        log_path=tmp_path / "era5_download_log.csv",
        year_start=2000,
        year_end=2000,
        months=[1, 2],
        dry_run=True,
    )

    output = capsys.readouterr().out
    assert "Total CDS API requests: 4" in output
    assert "Dataset selection: both" in output
    assert "Months: 1,2" in output
    assert "CDS API credentials NOT FOUND - set up ~/.cdsapirc first" in output


def test_era5_dry_run_counts_land_only_request(tmp_path: Path, capsys, monkeypatch) -> None:
    config = tmp_path / "study.yaml"
    config.write_text(
        "\n".join(
            [
                "project: {}",
                "data_sources: {}",
                "stress_event_definition: {}",
                "modeling: {}",
                "validation: {}",
                "temporal_domain:",
                "  era5_years: [2000, 2000]",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("CDSAPI_URL", raising=False)
    monkeypatch.delenv("CDSAPI_KEY", raising=False)

    run_era5_download_command(
        config_path=config,
        output_dir=tmp_path / "raw",
        log_path=tmp_path / "era5_download_log.csv",
        year_start=2000,
        year_end=2000,
        months=[1, 2],
        dry_run=True,
        dataset_selection="land",
    )

    output = capsys.readouterr().out
    assert "Total CDS API requests: 2" in output
    assert "Dataset selection: land" in output
