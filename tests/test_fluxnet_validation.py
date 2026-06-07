from pathlib import Path

import pandas as pd
import pytest

from nature_climate_ai.fluxnet_validation import (
    label_predicted_windows,
    run_fluxnet_validation_command,
    validate_fluxnet_ecosystem_response,
    validate_fluxnet_frame,
)


def _fluxnet_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "site_id": ["S1", "S1", "S1", "S2"],
            "date": ["2020-01-01", "2020-01-17", "2020-02-02", "2020-01-17"],
            "gpp_anomaly": [0.2, -1.0, -0.8, -0.4],
            "le_anomaly": [0.1, -0.5, -0.3, -0.2],
        }
    )


def _windows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "site_id": ["S1"],
            "start_date": ["2020-01-17"],
            "end_date": ["2020-02-02"],
        }
    )


def test_label_predicted_windows_marks_site_specific_windows() -> None:
    labels = label_predicted_windows(_fluxnet_frame(), _windows())
    assert labels.tolist() == [0, 1, 1, 0]


def test_validate_fluxnet_ecosystem_response_computes_site_differences() -> None:
    result = validate_fluxnet_ecosystem_response(_fluxnet_frame(), _windows())

    s1 = result.metrics[result.metrics["site_id"] == "S1"].iloc[0]
    assert result.qc["sites"] == 2
    assert result.qc["sites_with_predicted_windows"] == 1
    assert s1["inside_window_rows"] == 2
    assert s1["outside_window_rows"] == 1
    assert s1["gpp_inside_minus_outside"] == pytest.approx(-1.1)


def test_validate_fluxnet_frame_requires_gpp_anomaly() -> None:
    with pytest.raises(ValueError, match="missing required"):
        validate_fluxnet_frame(pd.DataFrame({"site_id": ["S1"], "date": ["2020-01-01"]}))


def test_fluxnet_command_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    completed, report_path = run_fluxnet_validation_command(
        fluxnet_path=tmp_path / "missing_fluxnet.csv",
        windows_path=tmp_path / "missing_windows.csv",
        output_path=tmp_path / "fluxnet" / "site_anomaly_metrics.csv",
        report_path=tmp_path / "fluxnet" / "validation_summary.md",
    )

    assert not completed
    assert "Status: NOT_READY" in report_path.read_text(encoding="utf-8")
    assert not (tmp_path / "fluxnet" / "site_anomaly_metrics.csv").exists()


def test_fluxnet_command_writes_metrics_for_valid_inputs(tmp_path: Path) -> None:
    fluxnet_path = tmp_path / "fluxnet_anomalies.csv"
    windows_path = tmp_path / "predicted_stress_windows.csv"
    output_path = tmp_path / "fluxnet" / "site_anomaly_metrics.csv"
    report_path = tmp_path / "fluxnet" / "validation_summary.md"
    _fluxnet_frame().to_csv(fluxnet_path, index=False)
    _windows().to_csv(windows_path, index=False)

    completed, written_report = run_fluxnet_validation_command(
        fluxnet_path=fluxnet_path,
        windows_path=windows_path,
        output_path=output_path,
        report_path=report_path,
    )

    assert completed
    assert written_report == report_path
    assert output_path.exists()
    assert "COMPLETE_FOR_INPUT_DATA" in report_path.read_text(encoding="utf-8")
    output = pd.read_csv(output_path)
    assert set(output["site_id"]) == {"S1", "S2"}
