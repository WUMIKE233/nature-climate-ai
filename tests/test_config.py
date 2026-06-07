from nature_climate_ai.config import load_study_config
from nature_climate_ai.data_catalog import sources_from_config
from nature_climate_ai.validation import validation_design_from_config


def test_study_config_has_expected_sources() -> None:
    config = load_study_config("config/study.yaml")
    sources = {source.key for source in sources_from_config(config)}
    assert sources == {"era5", "modis", "fluxnet"}


def test_validation_design_is_explicit() -> None:
    config = load_study_config("config/study.yaml")
    design = validation_design_from_config(config)
    assert design.temporal_holdout_years == (2021, 2025)
    assert "leave-one" in design.spatial_holdout
