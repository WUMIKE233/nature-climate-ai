# Modeling dataset assembly

## Purpose

This step creates `data/processed/modeling_dataset.csv`, the supervised learning table used by baseline models and AI precursor-discovery experiments.

## Required inputs

```text
data/processed/climate_lag_features.csv
results/stress_events/event_catalogue_summary.csv
```

Optional input:

```text
data/processed/modis_anomalies.csv
```

## Command

```powershell
python -m nature_climate_ai.cli modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv --anomalies data/processed/modis_anomalies.csv --output data/processed/modeling_dataset.csv --report results/qc/modeling_dataset_report.md
```

## Label rule

For each `pixel_id,date` row in the climate lag-feature table:

- `stress_event = 1` if the target date falls within any event interval for that same `pixel_id`.
- `stress_event = 0` otherwise.

If `modis_anomalies.csv` exists, `evi_anomaly` and `ndvi_anomaly` are merged in as target-context columns. They should not be used as lagged predictors unless a later model step explicitly separates predictors from targets.

## Manuscript gate

Do not use the modeling dataset for manuscript claims until:

- ERA5 climate-feature evidence is complete,
- MODIS quality-filtering evidence is complete,
- the stress-event catalogue evidence is complete,
- class balance and spatial/temporal coverage are reviewed,
- and train/test split logic is documented.

## 中文说明

本步骤把 ERA5 lag 特征和 MODIS 植被胁迫事件目录合并成监督学习表 `data/processed/modeling_dataset.csv`。标签规则是：如果某个 `pixel_id,date` 落入同一像元的任意胁迫事件区间，则 `stress_event=1`，否则为 0。输入缺失时只生成 `NOT_READY` 报告，不会伪造训练数据。
