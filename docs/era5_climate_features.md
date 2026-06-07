# ERA5 climate lag features

## Purpose

This step converts an aggregated ERA5/ERA5-Land climate table into `data/processed/climate_lag_features.csv`, the climate-side model input for precursor discovery.

## Input contract

Default input:

```text
data/interim/era5_composite_climate.csv
```

Required columns:

- `date`: climate aggregation window date aligned to the MODIS compositing cadence.
- `pixel_id`: stable pixel, site or region identifier aligned with MODIS.
- `2m_temperature`
- `total_precipitation`
- `soil_moisture`
- `surface_net_solar_radiation`
- `vapour_pressure_deficit`

The input table must already be spatially aligned with MODIS and temporally aggregated from hourly ERA5/ERA5-Land data into the chosen MODIS-composite or lead-window representation. This command does not download ERA5, regrid NetCDF files or derive vapour-pressure deficit from humidity variables.

## Command

```powershell
python -m nature_climate_ai.cli era5-climate-features --input data/interim/era5_composite_climate.csv --output data/processed/climate_lag_features.csv --report results/qc/era5_climate_feature_report.md
```

## Method

For each `pixel_id` and day of year, the command computes climate-variable climatologies and anomalies. Each anomaly is then aligned to future target dates using the configured lead times in `config/study.yaml`.

Example: a `2m_temperature` anomaly on January 1 becomes `2m_temperature_anomaly_lag_16d` for the January 17 target date when the configured lead time is 16 days.

This avoids using target-date or future climate information to predict vegetation stress at that target date.

## Manuscript gate

Do not use generated climate lag features as manuscript evidence until:

- Copernicus request parameters and access dates are documented,
- hourly-to-composite aggregation windows are documented,
- spatial alignment with MODIS pixels or regions is verified,
- vapour-pressure deficit derivation is documented if computed locally,
- and leakage checks confirm that lead features do not use future information.

## 中文说明

本步骤把已经聚合并与 MODIS 空间单元对齐的 ERA5/ERA5-Land 气候表转换成 `data/processed/climate_lag_features.csv`。工具会按像元和年内日计算气候态与异常值，再按配置中的提前量生成前兆特征。它不负责下载 ERA5、重网格 NetCDF 或从湿度变量推导 VPD。
