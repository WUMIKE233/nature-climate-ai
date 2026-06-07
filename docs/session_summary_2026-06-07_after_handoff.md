# Session summary after AI_HANDOFF review

更新时间：2026-06-07 20:30 CST

## 本轮目标

阅读 `docs/AI_HANDOFF.md`，接手另一位 AI 完成的数据准备工作，并继续推进 Nature/Science 论文项目的数据管道、验证产物和投稿 readiness。

## 已完成操作

1. 阅读交接文档与项目约束，确认当前主线数据来自 GEE 导出的 MODIS 与 ERA5 GeoTIFF/CSV，而不是 HDF/CDS 原始下载。
2. 跑通 MODIS 主线预处理：
   - `data/interim/modis_quality_filtered.csv`
   - `data/processed/modis_anomalies.csv`
   - `results/stress_events/event_catalogue_summary.csv`
3. 跑通 ERA5 主线预处理：
   - `data/processed/climate_lag_features.csv`
4. 修复真实数据规模下的建模集标签生成性能问题：
   - 将 `src/nature_climate_ai/modeling_dataset.py` 中逐事件循环改为按像元区间批量匹配。
   - 新增 `derive_grid_block_regions()`，从 GEE-style `pixel_id` 派生临时空间块 `region`。
   - `tests/test_modeling_dataset.py` 从 5 个测试增至 7 个测试，并通过。
5. 生成最新建模与验证产物：
   - `data/processed/modeling_dataset.csv`
   - `results/validation/baseline_metrics.csv`
   - `results/modeling/feature_attribution_table.csv`
   - `results/modeling/lag_response_summary.csv`
   - `results/validation/temporal_holdout_metrics.csv`
   - `results/validation/spatial_holdout_metrics.csv`
   - `results/validation/predictive_validation_summary.csv`
   - `results/validation/uncertainty_intervals.csv`
   - `results/validation/placebo_metrics.csv`
   - `results/validation/threshold_sensitivity.csv`
6. 新增并运行 GEE 网格对齐审计：
   - `scripts/audit_gee_grid_alignment.py`
   - `data/metadata/gee_grid_alignment_audit.csv`
   - `data/metadata/gee_grid_alignment_audit.md`
7. 更新 `config/study.yaml` 中 MODIS/ERA5 数据状态：
   - `GEE_EXPORT_PRESENT_GRID_ALIGNMENT_BLOCKED`
8. 刷新项目门控状态：
   - `data/metadata/data_access_plan.md`
   - `evidence/evidence_artifact_audit.md`
   - `results/pilot/minimum_evidence_slice_report.md`
   - `reproducibility/readiness_dashboard.md`
9. 继续推进共享网格修复：
   - 更新 `scripts/export_modis_gee.js`，加入显式共享 `SHARED_CRS`、`SHARED_TRANSFORM` 和 `EXPORT_REGION`。
   - 更新 `scripts/export_era5_gee.js`，使用同一套共享网格常量。
   - 增强 `scripts/audit_gee_grid_alignment.py`，支持 `--modis-glob` 与 `--era5-glob` 全批次审计。
   - 新增重导指南 `docs/gee_shared_grid_reexport_guide.md`。

## 关键发现：当前结果不能作为论文证据

GEE 网格对齐审计状态为 `FAIL_GRID_MISMATCH`。

当前参考文件显示：

- MODIS GEE reference: MODIS Sinusoidal, 255 x 121, pixel size about 27780 m.
- ERA5 GEE reference: EPSG:4326, 162 x 121, pixel size about 0.25 degree.

虽然两份 CSV 都使用 `pixel_id = p{row}c{col}`，但这些 row/col 来自不同 CRS、不同 transform、不同宽度的栅格。直接按 `pixel_id` 合并 MODIS 植被事件与 ERA5 气候特征不是有效的空间对齐，因此本轮生成的建模、候选前兆、baseline、temporal/spatial validation 产物只能视为软件管道试运行，不能进入 Nature/Science 稿件的结果证据。

## 当前数值状态

- MODIS anomaly rows: 10,508,318
- Stress-event catalogue rows: 144,269
- ERA5 lag-feature rows: 7,294,040
- Modeling dataset rows: 7,294,040
- Positive labels: 249,865
- Derived temporary grid regions: 20
- Top provisional candidate feature: `soil_moisture_anomaly_lag_16d`
- Readiness dashboard: `NOT_READY`
- Readiness blockers: 65

这些数值仅用于调试和管道性能评估，不用于论文主张。

## 下一步建议

优先修复空间网格：

1. 在 GEE 中重导 MODIS，使其与 ERA5 使用同一个 EPSG:4326、0.25 degree、同一 bounds、同一 transform。
2. 或者重导 ERA5 到 MODIS 使用的 Sinusoidal 网格，但这会增加 FLUXNET 站点经纬度映射复杂度。
3. 推荐方案：统一到 EPSG:4326 0.25 degree，经纬度边界采用 ERA5 GEE 导出的 bounds 或明确的研究区 bounds。
4. 重导后重新运行：
   - `scripts/audit_gee_grid_alignment.py`
   - MODIS quality/anomaly/event catalogue
   - ERA5 climate features
   - modeling dataset
   - baseline/precursor/temporal/spatial/uncertainty/robustness
5. FLUXNET 验证还缺 `results/fluxnet/predicted_stress_windows.csv`。该文件应在网格修复后，通过 FLUXNET 站点经纬度映射到统一网格，再从模型预测或验证窗口生成。

## 共享网格重导入口

已新增中英双语重导指南：

- `docs/gee_shared_grid_reexport_guide.md`

当前 GEE 脚本使用的共享网格常量为：

```javascript
var SHARED_CRS = "EPSG:4326";
var SHARED_TRANSFORM = [0.25, 0, 109.75, 0, -0.25, -10.00];
var EXPORT_REGION = ee.Geometry.Rectangle([109.75, -40.25, 150.25, -10.00], null, false);
```

这保留的是当前澳大利亚区域 footprint。若要支撑 Nature 主刊中“全球尺度”的表述，应在重导前先扩大 `EXPORT_REGION`，并保持 MODIS/ERA5 两个脚本完全一致。

## Verification

通过的命令：

```powershell
.\.venv\Scripts\python -m pytest tests\test_modeling_dataset.py tests\test_data_access_plan.py -q --basetemp .test_tmp -p no:cacheprovider
```

结果：9 passed。

后续补充验证：

```powershell
.\.venv\Scripts\python -m py_compile scripts\audit_gee_grid_alignment.py
.\.venv\Scripts\python scripts\audit_gee_grid_alignment.py --modis-glob "data/raw/modis_gee/modis_obs_*.tif" --era5-glob "data/raw/era5_gee/era5_16day_*.tif" --csv data/metadata/gee_grid_alignment_audit.csv --report data/metadata/gee_grid_alignment_audit.md
.\.venv\Scripts\python -m pytest tests\test_readiness_dashboard.py tests\test_modeling_dataset.py tests\test_data_access_plan.py -q --basetemp .test_tmp -p no:cacheprovider
```

结果：审计脚本语法通过；当前旧数据仍返回 `FAIL_GRID_MISMATCH`；相关测试 11 passed。

刷新 readiness/evidence 的命令均已运行；`readiness-dashboard` 与 evidence gates 返回 `NOT_READY`，符合当前科学阻断状态。
