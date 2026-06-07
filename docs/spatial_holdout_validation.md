# Spatial holdout validation

## Purpose

This step evaluates ranked precursor candidates under leave-one-region-out validation. It tests whether candidate precursor behavior transfers across spatial groups.

## Inputs

```text
data/processed/modeling_dataset.csv
results/modeling/feature_attribution_table.csv
```

Required modeling-dataset columns:

- `stress_event`
- `region` by default, or another column passed with `--region-col`
- candidate lag-feature columns

## Command

```powershell
python -m nature_climate_ai.cli spatial-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/spatial_holdout_metrics.csv --report results/validation/spatial_holdout_report.md --region-col region
```

## Method

For each region, the command:

- holds out that region,
- learns each selected candidate feature threshold from all other regions,
- evaluates the threshold on the held-out region,
- and reports precision, recall, false-alarm rate and accuracy.

## Manuscript gate

Do not claim spatial generalization until:

- region or biome definitions are documented,
- at least two regions are available,
- spatial holdout metrics are compared with baselines,
- uncertainty intervals are computed,
- and failure cases are reported.

## 中文说明

本步骤执行留一空间区域验证，用来检验候选气候前兆是否能跨区域迁移。默认空间列是 `region`，也可以用 `--region-col` 指定 `biome`、`continent` 等列。该结果只是空间迁移验证的一部分，不能单独作为 Nature 或 Science 主张。
