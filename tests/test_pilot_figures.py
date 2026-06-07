from pathlib import Path

import pandas as pd

from nature_climate_ai.pilot_figures import run_pilot_figure_generation_command


def test_pilot_figure_generation_writes_readiness_report_when_inputs_missing(tmp_path: Path) -> None:
    result = run_pilot_figure_generation_command(
        event_path=tmp_path / "missing_events.csv",
        attribution_path=tmp_path / "missing_attr.csv",
        lag_response_path=tmp_path / "missing_lag.csv",
        predictive_path=tmp_path / "missing_pred.csv",
        output_dir=tmp_path / "figures",
        manifest_path=tmp_path / "figures" / "pilot_figure_manifest.csv",
        report_path=tmp_path / "figures" / "pilot_figure_generation_report.md",
    )

    assert not result.completed_for_input
    assert result.report_path.exists()
    assert result.manifest_path.exists()
    assert "Status: NOT_READY" in result.report_path.read_text(encoding="utf-8")
    assert result.figure_paths == ()


def test_pilot_figure_generation_writes_pngs_for_input_artifacts(tmp_path: Path) -> None:
    events = tmp_path / "event_catalogue_summary.csv"
    attribution = tmp_path / "feature_attribution_table.csv"
    lag_response = tmp_path / "lag_response_summary.csv"
    predictive = tmp_path / "predictive_validation_summary.csv"
    pd.DataFrame({"pixel_id": ["p1", "p1", "p2"], "event_id": ["e1", "e2", "e3"]}).to_csv(events, index=False)
    pd.DataFrame({"feature": ["temp", "vpd"], "absolute_correlation": [0.3, 0.7]}).to_csv(attribution, index=False)
    pd.DataFrame({"feature": ["temp"], "mean_response": [0.4]}).to_csv(lag_response, index=False)
    pd.DataFrame({"model": ["baseline", "candidate"], "accuracy": [0.55, 0.68], "recall": [0.4, 0.6]}).to_csv(predictive, index=False)

    result = run_pilot_figure_generation_command(
        event_path=events,
        attribution_path=attribution,
        lag_response_path=lag_response,
        predictive_path=predictive,
        output_dir=tmp_path / "figures",
        manifest_path=tmp_path / "figures" / "pilot_figure_manifest.csv",
        report_path=tmp_path / "figures" / "pilot_figure_generation_report.md",
    )

    assert result.completed_for_input
    assert len(result.figure_paths) == 3
    for figure in result.figure_paths:
        assert figure.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert "COMPLETE_FOR_INPUT_DATA" in result.report_path.read_text(encoding="utf-8")
