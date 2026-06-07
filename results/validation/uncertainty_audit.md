# Validation uncertainty audit

Status: COMPLETE_FOR_INPUT_DATA

This report computes Wilson score intervals from saved confusion-count metrics. It does not replace block bootstrap, spatial autocorrelation checks or final manuscript uncertainty analysis.

- Baseline metrics: results/validation/baseline_metrics.csv
- Temporal holdout metrics: results/validation/temporal_holdout_metrics.csv
- Spatial holdout metrics: results/validation/spatial_holdout_metrics.csv

metric | value
--- | ---
baseline_rows | 56
temporal_rows | 20
spatial_rows | 200
interval_rows | 952
confidence_method | Wilson score interval, z=1.96

## Manuscript-use warning

Use these intervals as an initial event-metric uncertainty audit only. Nature/Science-level claims still require resampling that respects spatial and temporal dependence.

## 中文审阅说明

本报告根据混淆矩阵计数生成 Wilson 区间，只能作为预测指标不确定性的初步审计。最终论文仍需要考虑空间和时间相关性的 bootstrap 或同等方法。
