# Synthetic pipeline smoke-test report

Status: COMPLETE_FOR_SYNTHETIC_DATA

This report verifies that the local scaffold can run an end-to-end synthetic workflow. The generated data are artificial and must not be used as manuscript evidence or scientific results.

- Smoke output directory: outputs/smoke
- Artifact manifest: reproducibility/pipeline_smoke_manifest.csv

## Generated artifacts

artifact | exists
--- | ---
outputs/smoke/raw/modis_observations.csv | True
outputs/smoke/interim/modis_quality_filtered.csv | True
outputs/smoke/processed/modis_anomalies.csv | True
outputs/smoke/stress_events/event_catalogue_summary.csv | True
outputs/smoke/interim/era5_composite_climate.csv | True
outputs/smoke/processed/climate_lag_features.csv | True
outputs/smoke/processed/modeling_dataset.csv | True
outputs/smoke/validation/baseline_metrics.csv | True
outputs/smoke/modeling/feature_attribution_table.csv | True
outputs/smoke/modeling/lag_response_summary.csv | True
outputs/smoke/validation/temporal_holdout_metrics.csv | True
outputs/smoke/validation/spatial_holdout_metrics.csv | True
outputs/smoke/validation/predictive_validation_summary.csv | True
outputs/smoke/validation/uncertainty_intervals.csv | True

## Manuscript-use warning

Do not cite, plot or promote smoke-test outputs in the Nature or Science manuscript. This workflow is an engineering reproducibility check only.

## 中文审阅说明

本报告只证明项目脚手架可以用合成数据端到端运行。合成数据和 smoke-test 输出不能作为论文结果、图件或科学结论。
