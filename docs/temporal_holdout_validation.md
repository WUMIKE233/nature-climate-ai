# Temporal holdout validation

## Purpose

This step evaluates ranked precursor candidates on the configured temporal holdout. It is one part of predictive validation, not the full validation package.

## Inputs

```text
data/processed/modeling_dataset.csv
results/modeling/feature_attribution_table.csv
```

## Command

```powershell
python -m nature_climate_ai.cli temporal-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/temporal_holdout_metrics.csv --report results/validation/temporal_holdout_report.md
```

## Method

The command selects the top ranked candidate features, learns a median threshold on the training years, and evaluates the same threshold on the configured holdout years.

Current holdout years are read from `config/study.yaml`: `2021-2025`.

## Outputs

- `temporal_holdout_metrics.csv`: train and holdout metrics for candidate-threshold models.
- `temporal_holdout_report.md`: QC report and manuscript-use warning.

## Manuscript gate

Do not claim predictive improvement until:

- baseline metrics are available,
- candidate thresholds are evaluated on the same temporal holdout,
- spatial holdout validation is complete,
- uncertainty intervals are computed,
- and the result is compared against standard climate indices.

## 中文说明

本步骤用配置中的时间留出年份检验候选气候前兆特征。它只验证候选特征在时间留出上的表现，不等同于完整预测验证；完整主张还需要空间留出、不确定性、基线对比和独立生态验证。
