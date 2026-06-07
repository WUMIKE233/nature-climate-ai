# Synthetic pipeline smoke test

`pipeline-smoke-test` runs a small artificial end-to-end workflow through the scaffold. It exercises MODIS quality filtering, anomaly construction, event catalogue generation, ERA5 lag-feature construction, model-dataset assembly, baseline evaluation, precursor ranking, temporal/spatial validation, predictive summary and uncertainty intervals.

## Command

```powershell
python -m nature_climate_ai.cli pipeline-smoke-test --output-dir outputs/smoke --report reproducibility/pipeline_smoke_report.md --manifest reproducibility/pipeline_smoke_manifest.csv
```

## Outputs

- `reproducibility/pipeline_smoke_report.md`: smoke-test report.
- `reproducibility/pipeline_smoke_manifest.csv`: smoke artifact manifest.
- `outputs/smoke/`: synthetic input and intermediate artifacts.

## Rule

Smoke-test outputs are artificial. They may be used to verify that the workflow runs, but they must not be cited, plotted or promoted as manuscript evidence.

## 中文说明

该命令使用合成数据检查项目脚手架能否端到端运行。它不是科学实验，不代表真实 MODIS、ERA5 或 FLUXNET 结果，不能写入论文结论或图件。
