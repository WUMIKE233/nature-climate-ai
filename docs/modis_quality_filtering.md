# MODIS quality filtering

## Purpose

This step converts an imported MODIS observation table into `data/interim/modis_quality_filtered.csv`, the default input for MODIS anomaly generation.

## Input contract

Default input:

```text
data/raw/modis_observations.csv
```

Required columns:

- `date`: MODIS composite date.
- `pixel_id`: stable pixel, site or region identifier.
- `evi`: EVI value.
- `ndvi`: NDVI value.

Preferred quality column:

- `vi_quality`: integer MODIS VI Quality layer.

Alternative bad-flag columns:

- `cloud`
- `adjacent_cloud`
- `mixed_cloud`
- `snow_ice`
- `shadow`
- `high_aerosol`
- `low_vi_usefulness`
- `bad_view_angle`

If `vi_quality` exists, it is used. If it does not exist, available bad-flag columns are used. If no quality columns exist, the command will keep valid rows but the QC report will identify `quality_source` as `none`; such output is not acceptable manuscript evidence.

## Command

```powershell
python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
```

## Conservative VI Quality parsing

The default parser keeps records with:

- acceptable MODLAND QA,
- VI usefulness no worse than the configured threshold,
- low aerosol quantity,
- no adjacent cloud,
- no mixed cloud,
- no possible snow/ice,
- and no possible shadow.

The exact MODIS collection and bit interpretation must still be documented in `data/metadata/modis_quality_flags.md` before manuscript use.

## Downstream order

```powershell
python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
python -m nature_climate_ai.cli e01-event-catalogue --input data/processed/modis_anomalies.csv --output-dir results/stress_events
```

## 中文说明

本步骤把导入后的 MODIS 观测表转换成 `data/interim/modis_quality_filtered.csv`。优先使用 `vi_quality` 整数质量层解析 MOD13/MYD13 常见质量位；如果没有该字段，也可以用显式布尔坏标记列筛选。该工具不会下载 MODIS 数据，也不会替代对产品集合、质量位规则和空间/时间覆盖范围的人工审阅。
