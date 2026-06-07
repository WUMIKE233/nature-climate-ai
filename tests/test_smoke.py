from pathlib import Path

import pandas as pd

from nature_climate_ai.smoke import run_pipeline_smoke_test_command


def test_pipeline_smoke_test_generates_end_to_end_artifacts(tmp_path: Path) -> None:
    result = run_pipeline_smoke_test_command(
        output_dir=tmp_path / "smoke",
        report_path=tmp_path / "pipeline_smoke_report.md",
        manifest_path=tmp_path / "pipeline_smoke_manifest.csv",
    )

    assert result.report_path.exists()
    assert result.manifest_path.exists()
    assert all(path.exists() for path in result.artifacts)
    report = result.report_path.read_text(encoding="utf-8")
    assert "COMPLETE_FOR_SYNTHETIC_DATA" in report
    assert "不能作为论文结果" in report
    modeling = pd.read_csv(tmp_path / "smoke" / "processed" / "modeling_dataset.csv")
    assert {"stress_event", "region"}.issubset(modeling.columns)
    uncertainty = pd.read_csv(tmp_path / "smoke" / "validation" / "uncertainty_intervals.csv")
    assert not uncertainty.empty
