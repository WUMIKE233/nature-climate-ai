# Validation uncertainty audit

`uncertainty-audit` computes initial Wilson score intervals for precision, recall, false-alarm rate and accuracy from saved baseline, temporal-holdout and spatial-holdout confusion-count metrics.

## Command

```powershell
python -m nature_climate_ai.cli uncertainty-audit --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/uncertainty_intervals.csv --report results/validation/uncertainty_audit.md
```

## Required metric columns

- `true_positive`
- `false_positive`
- `false_negative`
- `true_negative`

The baseline, temporal and spatial validation commands now write these counts alongside precision, recall, false-alarm rate and accuracy.

## Manuscript rule

Wilson intervals are an initial event-metric audit. They do not account for spatial autocorrelation, temporal autocorrelation or clustered sampling. Nature/Science claims still require block bootstrap or an equivalent dependence-aware uncertainty method before final promotion.

## 中文说明

该步骤根据验证指标中的混淆矩阵计数生成 Wilson 区间，用于初步检查 precision、recall、false-alarm rate 和 accuracy 的不确定性。它不是最终统计证明；论文正式结论仍需要考虑空间和时间相关性的 bootstrap 或同等方法。
