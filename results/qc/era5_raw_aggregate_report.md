# ERA5 raw aggregation QC report

Status: COMPLETE_FOR_INPUT_DATA

Input directory: data/raw/era5
Output table: data/interim/era5_composite_climate.csv

metric | value
--- | ---
rows | 31
variables | soil_moisture,total_precipitation,surface_net_solar_radiation,2m_temperature,vapour_pressure_deficit
missing_configured_variables | none
spatial_stride | 50

## Method note

This command creates a pilot global area-weighted daily aggregate from local ERA5 NetCDF files. Temperature and vapour-pressure deficit are daily means; total precipitation and surface net solar radiation are daily sums. The output is a QC/pipeline input, not final manuscript evidence, because it is not yet aligned to MODIS pixels or composite windows.

## Manuscript-use warning

Do not use this table as a Nature/Science result. It is only an intermediate check that raw ERA5 files can be opened and converted into a tabular climate input. Missing configured variables must be resolved or explicitly excluded in a separate pilot analysis decision.

## 中文审阅说明

本报告把本地 ERA5 NetCDF 原始文件聚合为 pilot 级日尺度全球面积加权表。它只证明原始数据可以进入后续流程，不代表 MODIS 网格对齐、完整 ERA5-Land 变量、泄漏检查或论文结果已经完成。

## Spatial subsampling warning

This run used spatial_stride=50; only every 50th latitude/longitude cell was sampled before spatial aggregation. This is acceptable for pipeline smoke testing but not for final scientific inference.

## 空间抽样警告

本次运行使用 spatial_stride=50，即仅抽取每 50 个经纬度格点参与聚合。该结果只能用于流程烟测，不能作为最终科学推断。
