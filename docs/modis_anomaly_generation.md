# MODIS anomaly generation

## Purpose

This step converts a quality-filtered MODIS vegetation-index table into `data/processed/modis_anomalies.csv`, the default input for `E01_event_catalogue`.

## Input contract

Default input:

```text
data/interim/modis_quality_filtered.csv
```

Required columns:

- `date`: MODIS composite date.
- `pixel_id`: stable pixel, site or region identifier.
- `evi`: quality-filtered EVI value.
- `ndvi`: quality-filtered NDVI value.

Optional column:

- `quality_ok`: boolean flag. If present, only truthy rows are used.

The input must already reflect MODIS quality-flag decisions. This command computes anomalies; it does not parse raw MODIS HDF quality bits.

To generate the default input from an imported MODIS observation table, run `modis-quality-filter` first:

```powershell
python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
```

## Command

```powershell
python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
```

If the input is missing, the command writes only:

```text
results/qc/modis_anomaly_qc_report.md
```

with `Status: NOT_READY`.

If the input exists and validates, it writes:

```text
data/processed/modis_anomalies.csv
results/qc/modis_anomaly_qc_report.md
```

## Method

For each `pixel_id` and day of year, the command computes mean EVI and NDVI climatologies, then subtracts those climatologies from each observation. Rows with fewer than the configured minimum climatology samples are dropped.

Default minimum climatology samples: `2`.

## Manuscript gate

Do not treat generated anomalies as manuscript evidence until:

- MODIS product collection and quality flags are documented,
- the input table covers the intended years and spatial domain,
- anomaly climatologies are computed without leaking held-out evaluation data where required,
- and sensitivity checks for EVI versus NDVI are planned.

## 中文说明

本步骤把已经完成 MODIS 质量筛选的植被指数表转换成 `data/processed/modis_anomalies.csv`。它只负责按像元和年内日计算 EVI/NDVI 气候态与异常值，不负责解析原始 MODIS HDF 质量位。输入缺失时只生成 `NOT_READY` 报告，不会伪造 anomaly 数据。
