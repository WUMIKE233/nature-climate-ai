# Session Summary — Shared-grid GEE re-export and pipeline rebuild / 共享网格GEE重导与管道重建

> 更新时间 / Updated: 2026-06-07 23:30 CST | AI: Codex (GPT-5)

---

## 目标 / Objective

修复 MODIS 与 ERA5 的 GEE 导出栅格不在同一像元网格上的科学阻断问题（`FAIL_GRID_MISMATCH`），并基于共享网格数据完整重跑 Nature 论文分析管道。

Fix the scientific blocker where MODIS and ERA5 GEE exports used different pixel grids, then rebuild the full Nature analysis pipeline on shared-grid data.

---

## 完成操作 / Completed Actions

### 1. GEE 重导 / GEE Re-export

| 数据集 | 脚本 | 年份范围 | 文件数 | 状态 |
|--------|------|----------|--------|------|
| MODIS | `scripts/export_modis_gee.js` | 2000–2025 | 26 GeoTIFF | ✅ |
| ERA5  | `scripts/export_era5_gee.js`  | 2000–2025 | 26 GeoTIFF | ✅ |

共享网格常数 / Shared-grid constants:

```javascript
SHARED_CRS      = "EPSG:4326"
SHARED_TRANSFORM = [0.25, 0, 109.75, 0, -0.25, -10.00]
EXPORT_REGION   = [109.75, -40.25, 150.25, -10.00]  // 澳大利亚 / Australia
```

### 2. 网格对齐审计 / Grid Audit

```powershell
.\.venv\Scripts\python scripts\audit_gee_grid_alignment.py `
  --modis-glob "data/raw/modis_gee_shared_grid/modis_obs_*.tif" `
  --era5-glob "data/raw/era5_gee_shared_grid/era5_16day_*.tif"
```

结果 / Result: **`PASS_SHARED_GRID`** ✅

### 3. 脚本修复 / Script Fixes

#### `scripts/convert_gee_tif.py`

问题: `BAND_PATTERN` 仅匹配旧格式 `0_2001_01_01_NDVI`，新共享网格 TIFF 使用 `N_20240101` 紧凑格式。
修复:
- 新增 `BAND_PATTERN_NEW = r"^([NEQ])_(\d{4})(\d{2})(\d{2})$"` 匹配新格式
- 保留 `BAND_PATTERN_OLD` 向后兼容
- 输出增加 `qa_ok` 列（预计算二进制质量标志），供下游质量过滤使用
- 改为单文件直写模式（`convert_all`），避免 merge 时的列数不一致问题
- 写入**全部**像素（不再预过滤），让 `modis-quality-filter` 做最终过滤

#### `scripts/convert_era5_gee.py`

问题: `BAND_PATTERN` 仅匹配旧格式 `Y2000_D001_T`，新共享网格 TIFF 使用 `T_001` 无年份前缀格式。
修复:
- 新增 `BAND_PATTERN_NEW = r"^([TSDURPV])_(\d{3})$"` 匹配新格式
- 年份从文件名提取（`era5_16day_2024.tif` → `2024`）
- 保留 `BAND_PATTERN_OLD` 向后兼容
- 改为单文件直写模式

#### `src/nature_climate_ai/modis_quality.py`

问题: `compute_quality_filtered_modis` 仅识别 `vi_quality` 整数 bitmask 或 boolean bad-flag 列（cloud/shadow 等），不识别新 CSV 中的二进制 `qa_ok` 列。
修复:
- 新增 `_flag_or_fallback_quality()` 辅助函数
- 自动识别 `qa_ok` 列作为预计算二进制质量标志（1=good），`fillna(0).eq(1)` 处理海洋/无数据像素
- `quality_source` 输出变为 `"qa_ok"`（之前为 `"none"`）

### 4. 管道重建 / Pipeline Rebuild

全部 15 个 CLI 步骤按顺序成功完成：

| # | 命令 | 耗时 | 关键输出 |
|---|------|------|----------|
| 1 | `convert_gee_tif.py` | 56s | `modis_observations.csv` (22.3M 行, 836 MB) |
| 2 | `convert_era5_gee.py` | 118s | `era5_composite_climate.csv` (11.7M 行, 798 MB) |
| 3 | `modis-quality-filter` | 41s | `modis_quality_filtered.csv` (11.6M 行) |
| 4 | `modis-anomalies` | 78s | `modis_anomalies.csv` (1.44M 行) |
| 5 | `e01-event-catalogue` | 69s | 事件目录生成 |
| 6 | `era5-climate-features` | 176s | `climate_lag_features.csv` |
| 7 | `modeling-dataset` | 191s | `modeling_dataset.csv` |
| 8 | `baseline-evaluation` | 52s | `baseline_metrics.csv` |
| 9 | `precursor-discovery` | 49s | `feature_attribution_table.csv` + `lag_response_summary.csv` |
| 10 | `temporal-holdout-validation` | 35s | `temporal_holdout_metrics.csv` |
| 11 | `spatial-holdout-validation` | 79s | `spatial_holdout_metrics.csv` |
| 12 | `predictive-validation-summary` | 2s | `predictive_validation_summary.csv` |
| 13 | `uncertainty-audit` | 2s | `uncertainty_intervals.csv` |
| 14 | `placebo-validation` | 34s | `placebo_metrics.csv` |
| 15 | `threshold-sensitivity` | 247s | `threshold_sensitivity.csv` |
| 16 | `readiness-dashboard` | 243s | `readiness_dashboard.md` 已刷新 |

### 5. Readiness 面板变化 / Dashboard Changes

| 组件 | 之前 | 之后 |
|------|------|------|
| `gee_grid_alignment` | `NOT_READY` | `COMPLETE_FOR_SHAREDGRID` |
| Total blockers | 66 | 65 |

剩余的 65 个阻塞项全部属于 manuscript writing、figure generation、evidence registry、FLUXNET 验证等非管道代码领域。

---

## 文件变更清单 / Changed Files

| 文件 | 变更类型 |
|------|----------|
| `scripts/convert_gee_tif.py` | **重写** — 支持新旧 band 格式，输出 qa_ok 列 |
| `scripts/convert_era5_gee.py` | **重写** — 支持新旧 band 格式，从文件名提取年份 |
| `src/nature_climate_ai/modis_quality.py` | **修改** — 新增 `_flag_or_fallback_quality()` 识别 qa_ok |
| `data/raw/modis_observations.csv` | **重新生成** — 共享网格数据 |
| `data/interim/era5_composite_climate.csv` | **重新生成** — 共享网格数据 |
| `data/interim/modis_quality_filtered.csv` | **重新生成** |
| `data/processed/modis_anomalies.csv` | **重新生成** |
| `data/processed/climate_lag_features.csv` | **重新生成** |
| `data/processed/modeling_dataset.csv` | **重新生成** |
| `results/stress_events/*` | **重新生成** |
| `results/modeling/*` | **重新生成** |
| `results/validation/*` | **重新生成** |
| `results/qc/*` | **重新生成** |
| `reproducibility/readiness_dashboard.md` | **已刷新** |
| `data/metadata/gee_grid_alignment_audit.*` | **已更新** — PASS_SHARED_GRID |

---

## 已知未完成 / Remaining

1. **FLUXNET 31 个无效站点** — ZIP 文件为假 HTML，需从 [FLUXNET 官网](https://fluxnet.org/data/fluxnet2015-dataset/) 手动重下
2. **`fluxnet-validation`** — 需在 FLUXNET 站点数据齐全后运行
3. **`biome-stratified-validation`** — 生物群系分层验证
4. **`sensor-cross-validation`** — 传感器交叉验证
5. **`generate-pilot-figures`** — 论文图表生成
6. **论文写作** — manuscript 主体内容替换证据占位符
7. **CDS ERA5 全量备用下载** — `scripts/download_era5_smart.py` 已就绪，按需在 Terminal 后台运行

---

## 未删除的旧文件 / Old Files Retained

原始 GEE 导出文件仍保留在以下目录，供回溯对比使用：

- `data/raw/modis_gee/` — 旧 MODIS 导出（未删除）
- `data/raw/era5_gee/` — 旧 ERA5 导出（未删除）

---

## 环境备注 / Environment Notes

- Python venv: `W:\Nature\.venv`
- 磁盘: W 盘 ~87 GB 可用，E 盘 ~291 GB 可用
- GEE Code Editor 已验证可用，Python API 未配通
- 所有数据当前为澳大利亚区域 footprint（109.75°E–150.25°E, 40.25°S–10°S），如要扩展到全球，需扩大 GEE 脚本中的 `EXPORT_REGION` 并重新导出

---

*Summary generated by Codex (GPT-5) on 2026-06-07*
