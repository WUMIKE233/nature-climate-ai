# Predictive validation summary

This step combines baseline, temporal-holdout and spatial-holdout metrics into one manuscript-facing validation table. It is a synthesis gate, not a substitute for uncertainty analysis or ecological validation.

## Required inputs

```text
results/validation/baseline_metrics.csv
results/validation/temporal_holdout_metrics.csv
results/validation/spatial_holdout_metrics.csv
```

Each input must contain:

- `model`
- `rows`
- `precision`
- `recall`
- `false_alarm_rate`
- `accuracy`

When a `split` column exists in baseline or temporal metrics, only rows with `split == holdout` are summarized.

## Command

```powershell
python -m nature_climate_ai.cli predictive-validation-summary --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/predictive_validation_summary.csv --report results/validation/predictive_validation_summary.md
```

If any required input is missing, the command writes a `NOT_READY` report and does not create the summary CSV.

## Manuscript rule

Use this artifact only to support a predictive-performance claim after:

- baseline, temporal and spatial validation artifacts all exist,
- uncertainty intervals have been estimated,
- matched baselines and standard climate indices have been compared,
- FLUXNET or other independent ecological evidence has been interpreted,
- and `predictive_validation` is marked complete in `evidence/registry.yaml`.

## 中文说明

该步骤把基线模型、时间留出验证和空间留出验证的指标汇总为一张可追溯表。它只能说明预测验证链条是否具备汇总条件，不能单独证明论文中的“AI 优于基线”结论。只有在不确定性、基线对比、空间/时间泛化和生态独立验证都完成后，相关结果才可以写入主稿。
