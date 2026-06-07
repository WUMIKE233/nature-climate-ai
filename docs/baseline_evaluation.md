# Baseline evaluation

## Purpose

This step evaluates simple baseline models on `data/processed/modeling_dataset.csv`. These baselines are required before any AI precursor-discovery model can be claimed to improve prediction.

## Input

```text
data/processed/modeling_dataset.csv
```

Required columns:

- `date`
- `stress_event`
- at least one lag-feature column containing `_lag_` and ending in `d`

## Command

```powershell
python -m nature_climate_ai.cli baseline-evaluation --input data/processed/modeling_dataset.csv --output results/validation/baseline_metrics.csv --report results/validation/baseline_comparison.md
```

## Baselines

The command evaluates:

- `majority_class`: constant prediction from training-set majority class.
- `training_prevalence`: constant prediction derived from training-set stress-event prevalence.
- `persistence_previous_event`: previous observed stress-event label within the same unit, with training-majority fallback.
- `threshold:<feature>`: one-feature median-threshold baseline for each lagged climate feature.
- `family_threshold:temperature_only`: median-threshold baseline using temperature lag features.
- `family_threshold:precipitation_only`: median-threshold baseline using precipitation lag features.
- `family_threshold:soil_moisture_only`: median-threshold baseline using soil-moisture lag features.
- `family_threshold:vpd_only`: median-threshold baseline using vapour-pressure-deficit lag features.
- `family_threshold:compound_heat_drought`: additive heat plus drought-family baseline for compound-stress comparison.

## Split

The command uses the temporal holdout years from `config/study.yaml`. Current default: `2021-2025`.

## Manuscript gate

Do not claim AI improvement until:

- baseline metrics exist,
- AI models use the same train/holdout split,
- uncertainty intervals are computed,
- and spatial holdout validation is also completed.

## 中文说明

本步骤对 `data/processed/modeling_dataset.csv` 运行基线模型，包括多数类、训练集事件率、上一期胁迫状态、单特征阈值、温度/降水/土壤水分/VPD 家族阈值，以及复合热旱基线。它只提供比较基准，不代表 AI 模型已经有改进。
