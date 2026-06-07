# GEE shared-grid re-export guide / GEE 共享网格重导指南

更新时间 / Updated: 2026-06-07

## Why this is required / 为什么必须重导

The current local GEE outputs do not share one pixel grid:

- MODIS GeoTIFFs are on a MODIS Sinusoidal grid.
- ERA5 GeoTIFFs are on an EPSG:4326 grid.

Because `pixel_id` is generated from raster row and column, the same string such as `p00030c00040` only means the same location if CRS, transform, width and height are identical. The current mismatch means MODIS vegetation events and ERA5 climate features cannot be joined as manuscript evidence.

当前本地 GEE 输出不在同一个像元网格上：

- MODIS GeoTIFF 使用 MODIS Sinusoidal 网格。
- ERA5 GeoTIFF 使用 EPSG:4326 网格。

因为 `pixel_id` 是由栅格行列号生成的，只有当 CRS、transform、宽度和高度完全一致时，`p00030c00040` 这样的字符串才代表同一地理位置。当前不一致，所以不能把现有 MODIS 植被事件与 ERA5 气候特征作为论文证据直接合并。

## Shared grid currently configured / 当前脚本配置的共享网格

Both scripts now use identical constants:

```javascript
var SHARED_CRS = "EPSG:4326";
var SHARED_TRANSFORM = [0.25, 0, 109.75, 0, -0.25, -10.00];
var EXPORT_REGION = ee.Geometry.Rectangle([109.75, -40.25, 150.25, -10.00], null, false);
```

This keeps the current Australia-focused footprint. For the full Nature-global target, expand `EXPORT_REGION` first and use the same expanded constants in both scripts before exporting.

这会保留当前以澳大利亚区域为主的导出范围。如果要真正支撑 Nature 主刊中的全球尺度表述，应先扩大 `EXPORT_REGION`，并在 MODIS 与 ERA5 两个脚本中保持完全相同的常量。

## Files to use / 使用文件

- MODIS script: `scripts/export_modis_gee.js`
- ERA5 script: `scripts/export_era5_gee.js`
- Grid audit: `scripts/audit_gee_grid_alignment.py`
- MODIS converter: `scripts/convert_gee_tif.py`
- ERA5 converter: `scripts/convert_era5_gee.py`

## Re-export steps / 重导步骤

1. Open [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Paste `scripts/export_modis_gee.js`.
3. Change `YEAR` for each year from 2001 to 2025 and submit the export tasks.
4. Paste `scripts/export_era5_gee.js`.
5. Change `YEAR` for each year from 2000 to 2025 and submit the export tasks.
6. Download the exported GeoTIFFs into temporary local folders first, for example:

```text
W:\Nature\data\raw\modis_gee_shared_grid\
W:\Nature\data\raw\era5_gee_shared_grid\
```

Do not delete the old files until the shared-grid audit passes and the replacement has been reviewed.

1. 打开 [Google Earth Engine Code Editor](https://code.earthengine.google.com/)。
2. 粘贴 `scripts/export_modis_gee.js`。
3. 将 `YEAR` 从 2001 到 2025 逐年修改并提交导出任务。
4. 粘贴 `scripts/export_era5_gee.js`。
5. 将 `YEAR` 从 2000 到 2025 逐年修改并提交导出任务。
6. 先把导出的 GeoTIFF 下载到临时目录，例如：

```text
W:\Nature\data\raw\modis_gee_shared_grid\
W:\Nature\data\raw\era5_gee_shared_grid\
```

在共享网格审计通过并人工确认前，不要删除旧文件。

## Required audit / 必须通过的审计

After downloading the new GeoTIFFs, run:

```powershell
cd W:\Nature
.\.venv\Scripts\python scripts\audit_gee_grid_alignment.py `
  --modis-glob "data/raw/modis_gee_shared_grid/modis_obs_*.tif" `
  --era5-glob "data/raw/era5_gee_shared_grid/era5_16day_*.tif" `
  --csv data/metadata/gee_grid_alignment_audit.csv `
  --report data/metadata/gee_grid_alignment_audit.md
```

The report must show:

```text
Status: PASS_SHARED_GRID
```

If it still shows `FAIL_GRID_MISMATCH`, do not run the manuscript evidence pipeline yet.

下载新 GeoTIFF 后运行上面的审计命令。报告必须显示 `Status: PASS_SHARED_GRID`。如果仍然显示 `FAIL_GRID_MISMATCH`，不要继续把结果用于论文证据。

## Rebuild pipeline after audit passes / 审计通过后的重跑命令

After the grid audit passes, convert the temporary shared-grid GeoTIFFs:

```powershell
cd W:\Nature
.\.venv\Scripts\python scripts\convert_gee_tif.py --dir data/raw/modis_gee_shared_grid --output data/raw/modis_observations.csv
.\.venv\Scripts\python scripts\convert_era5_gee.py --dir data/raw/era5_gee_shared_grid --output data/interim/era5_composite_climate.csv
```

Then rebuild the analysis artifacts:

```powershell
.\.venv\Scripts\python -m nature_climate_ai.cli modis-quality-filter
.\.venv\Scripts\python -m nature_climate_ai.cli modis-anomalies
.\.venv\Scripts\python -m nature_climate_ai.cli e01-event-catalogue
.\.venv\Scripts\python -m nature_climate_ai.cli era5-climate-features
.\.venv\Scripts\python -m nature_climate_ai.cli modeling-dataset
.\.venv\Scripts\python -m nature_climate_ai.cli baseline-evaluation
.\.venv\Scripts\python -m nature_climate_ai.cli precursor-discovery
.\.venv\Scripts\python -m nature_climate_ai.cli temporal-holdout-validation
.\.venv\Scripts\python -m nature_climate_ai.cli spatial-holdout-validation --region-col region
.\.venv\Scripts\python -m nature_climate_ai.cli predictive-validation-summary
.\.venv\Scripts\python -m nature_climate_ai.cli uncertainty-audit
.\.venv\Scripts\python -m nature_climate_ai.cli placebo-validation
.\.venv\Scripts\python -m nature_climate_ai.cli threshold-sensitivity
.\.venv\Scripts\python -m nature_climate_ai.cli readiness-dashboard
```

## Manuscript policy / 论文使用原则

Only promote results into the Nature/Science manuscript after:

- `gee_grid_alignment` is `READY`.
- MODIS and ERA5 preprocessing reports are regenerated from shared-grid data.
- Temporal holdout, spatial holdout, uncertainty and robustness checks are regenerated.
- FLUXNET predicted windows are built from the shared grid and validated.

只有在以下条件满足后，才可以把结果写入 Nature/Science 稿件：

- `gee_grid_alignment` 为 `READY`。
- MODIS 与 ERA5 预处理报告已基于共享网格数据重新生成。
- temporal holdout、spatial holdout、不确定性和稳健性检查已重新生成。
- FLUXNET predicted windows 已基于共享网格生成并完成验证。
