from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.precursor_discovery import (
    discover_precursor_candidates,
    parse_lag_feature,
    run_precursor_discovery_command,
    validate_precursor_frame,
)


def _modeling_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18"],
            "pixel_id": ["p1", "p1", "p1", "p1"],
            "2m_temperature_anomaly_lag_16d": [0.1, 0.2, 1.0, 1.2],
            "soil_moisture_anomaly_lag_16d": [0.4, 0.3, 0.2, 0.1],
            "stress_event": [0, 0, 1, 1],
        }
    )


def test_parse_lag_feature_extracts_variable_and_lag() -> None:
    variable, lag_days = parse_lag_feature("2m_temperature_anomaly_lag_16d")
    assert variable == "2m_temperature"
    assert lag_days == 16


def test_parse_lag_feature_rejects_unsupported_columns() -> None:
    with pytest.raises(ValueError, match="Not a supported"):
        parse_lag_feature("pixel_id")


def test_discover_precursor_candidates_ranks_associated_features() -> None:
    result = discover_precursor_candidates(_modeling_frame())

    assert result.qc["feature_count"] == 2
    assert result.attribution.iloc[0]["feature"] == "2m_temperature_anomaly_lag_16d"
    assert {"variable", "lag_days", "correlation_with_label"}.issubset(result.attribution.columns)
    assert not result.lag_response.empty


def test_validate_precursor_frame_requires_lag_features() -> None:
    with pytest.raises(ValueError, match="lag-feature"):
        validate_precursor_frame(pd.DataFrame({"stress_event": [0, 1]}))


def test_precursor_command_writes_readiness_report_when_input_missing(tmp_path: Path) -> None:
    completed, report_path = run_precursor_discovery_command(
        input_path=tmp_path / "missing.csv",
        attribution_path=tmp_path / "modeling" / "feature_attribution_table.csv",
        lag_response_path=tmp_path / "modeling" / "lag_response_summary.csv",
        report_path=tmp_path / "modeling" / "precursor_discovery_report.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "modeling" / "feature_attribution_table.csv").exists()


def test_precursor_command_writes_candidate_tables_for_valid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "modeling_dataset.csv"
    _modeling_frame().to_csv(input_path, index=False)
    attribution_path = tmp_path / "modeling" / "feature_attribution_table.csv"
    lag_response_path = tmp_path / "modeling" / "lag_response_summary.csv"
    report_path = tmp_path / "modeling" / "precursor_discovery_report.md"

    completed, written_report = run_precursor_discovery_command(
        input_path=input_path,
        attribution_path=attribution_path,
        lag_response_path=lag_response_path,
        report_path=report_path,
    )

    assert completed
    assert written_report == report_path
    assert attribution_path.exists()
    assert lag_response_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
