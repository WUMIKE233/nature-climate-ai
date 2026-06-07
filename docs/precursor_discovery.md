# Interpretable precursor discovery

## Purpose

This step ranks lagged climate features as candidate vegetation-stress precursors. It is the first interpretable discovery layer before more complex AI models, temporal/spatial holdout validation and FLUXNET validation.

## Input

```text
data/processed/modeling_dataset.csv
```

Required columns:

- `stress_event`
- at least one lag-feature column like `<variable>_anomaly_lag_<days>d`

## Command

```powershell
python -m nature_climate_ai.cli precursor-discovery --input data/processed/modeling_dataset.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --report results/modeling/precursor_discovery_report.md
```

## Outputs

- `feature_attribution_table.csv`: feature-level association summary, including stress-event mean differences and correlation with the stress label.
- `lag_response_summary.csv`: variable-by-lag summary of association strength.
- `precursor_discovery_report.md`: human-readable QC and manuscript-use warning.

## Manuscript gate

Do not convert any ranked feature into a Nature or Science discovery claim until:

- baseline metrics exist,
- the candidate survives temporal holdout,
- the candidate survives spatial holdout,
- uncertainty is quantified,
- and FLUXNET or another independent ecological validation source supports the mechanism.

## 中文说明

本步骤只是对 lagged climate features 做可解释候选前兆排序。它可以帮助发现哪些变量和提前量最值得后续验证，但不能单独作为 Nature 或 Science 主稿中的“新发现”。只有经过基线比较、时间留出、空间留出、不确定性分析和 FLUXNET 验证后，相关结果才可以替换主稿中的 `RESULT_REQUIRED`。
