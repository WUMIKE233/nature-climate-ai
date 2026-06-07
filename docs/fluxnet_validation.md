# FLUXNET ecosystem validation

## Purpose

This step evaluates whether predicted stress windows correspond to independent ecosystem-function anomalies at FLUXNET sites.

## Inputs

```text
data/processed/fluxnet_anomalies.csv
results/fluxnet/predicted_stress_windows.csv
```

Required FLUXNET anomaly columns:

- `site_id`
- `date`
- `gpp_anomaly`
- optional `le_anomaly`

Required predicted-window columns:

- `site_id`
- `start_date`
- `end_date`

## Command

```powershell
python -m nature_climate_ai.cli fluxnet-validation --fluxnet data/processed/fluxnet_anomalies.csv --windows results/fluxnet/predicted_stress_windows.csv --output results/fluxnet/site_anomaly_metrics.csv --report results/fluxnet/validation_summary.md
```

## Method

For each FLUXNET site, the command labels observations that fall inside predicted stress windows. It then compares GPP anomaly, and LE anomaly when available, inside versus outside predicted windows.

## Manuscript gate

Do not claim independent ecosystem validation until:

- FLUXNET data policy and required acknowledgements are documented,
- site-years and plant functional types are documented,
- predicted-window provenance is documented,
- uncertainty intervals are computed,
- and site representativeness limitations are reported.

## 中文说明

本步骤用于检验模型预测的胁迫窗口是否对应 FLUXNET 站点的生态功能异常。默认比较 predicted stress windows 内外的 GPP anomaly，并在存在 `le_anomaly` 时比较潜热异常。该结果不能单独作为 Nature 或 Science 主张；必须先完成 FLUXNET 数据政策审查、站点代表性说明和不确定性分析。
