# AI Handoff — Nature Climate AI 项目交接文档

> 最后更新：2026-06-07 18:20 CST | 本轮 AI：Codex (GPT-5)

---

## 项目概览 / Project Overview

**目标期刊**：Nature | **工作标题**：AI-guided discovery of climate precursors for global vegetation stress

**研究问题**：利用可解释 ML 发现全球植被胁迫（EVI/NDVI 异常）的气候前兆信号（温度、降水、土壤湿度、VPD、辐射），铅期 16/32/48/64 天。全球 0.25° 网格，FLUXNET 站点独立验证。

**核心管道**：MODIS 植被异常 + ERA5 气候特征 → 建模数据集 → 前兆发现 → 时空验证 → 论文

---

## 数据集状态 / Dataset Status

### ✅ MODIS 植被指数 (2001-2025)

| 文件 | 行数 | 大小 | 来源 |
|------|------|------|------|
| `data/raw/modis_observations.csv` | 10,521,996 | 389 MB | GEE export → `convert_gee_tif.py` |
| `data/raw/modis_gee/modis_obs_20*.tif` | 25 个 GeoTIFF | ~220 MB | GEE `export_modis_gee.js` |

- GEE 脚本：`scripts/export_modis_gee.js`（在 Code Editor 粘贴运行）
- 质量过滤：`SummaryQA` bitmask（modland≤1, viUse≤11, 无云/气溶胶/雪/阴影）
- 分辨率：0.25° (scale: 27780m), EPSG:4326, 255×121 像素
- **HDF 原始存档不重要**——管道只用 GEE CSV，HDF 仅用于 `modis-raw-inventory` 审计

### ✅ ERA5 气候再分析 (2000-2025)

| 文件 | 行数 | 大小 | 来源 |
|------|------|------|------|
| `data/interim/era5_composite_climate.csv` | 11,721,996 | 788 MB | GEE export → `convert_era5_gee.py` |
| `data/raw/era5_gee/era5_16day_20*.tif` | 26 个 GeoTIFF | 218 MB | GEE `export_era5_gee.js` |

- **本轮关键决策**：ERA5 按 **16 天复合**（匹配 MODIS MOD13Q1 周期），而非日尺度
- 23 个复合窗口/年（DoY 1, 17, 33, …, 353），每年 161 波段（7 变量 × 23 窗口）
- 窗口中心日 = DoY_start + 7，保证铅期对齐（16/32/48/64 = n × 16 天）
- 变量：2m_temperature, total_precipitation, soil_moisture（swvl1+2 均值）, surface_net_solar_radiation, vapour_pressure_deficit（从 T+Td 计算）
- 19,602 陆地像素，海洋像素为 NaN（ERA5-Land 特性）
- 波段命名：`Y{year}_D{DoY}_{var}`（如 `Y2000_D001_T`）
- **CDS 备用下载**脚本已写好：`scripts/download_era5_smart.py`（4 时段/天，输出到 `E:\Nature_ERA5`）

### 🟡 FLUXNET 站点验证

| 项 | 数值 |
|----|------|
| ZIP 数量 | 111（`data/raw/fluxnet/`，6.5 GB） |
| 有效站点 | 80，含全部 5 必需变量 |
| 无效 | 31 个假 HTML 文件（ICOS/AsiaFlux/欧洲站点） |

- 审计文件：`data/metadata/fluxnet_raw_archive_audit.csv`
- 无效站点需从 [FLUXNET 官网](https://fluxnet.org/data/fluxnet2015-dataset/) 手动重下
- 重试清单：`data/metadata/fluxnet_retry_manifest.csv`（但链接已过期 404）

---

## 关键脚本 / Key Scripts

| 脚本 | 用途 | 运行方式 |
|------|------|----------|
| `scripts/export_modis_gee.js` | GEE 导出 MODIS NDVI/EVI 16 天复合 | GEE Code Editor 粘贴运行 |
| `scripts/export_era5_gee.js` | GEE 导出 ERA5-Land 16 天复合（**本轮新增**） | GEE Code Editor 粘贴运行，每年改 YEAR |
| `scripts/convert_gee_tif.py` | MODIS GeoTIFF → CSV | `.\.venv\Scripts\python scripts/convert_gee_tif.py` |
| `scripts/convert_era5_gee.py` | ERA5 GeoTIFF → CSV（**本轮新增**） | `.\.venv\Scripts\python scripts/convert_era5_gee.py` |
| `scripts/download_era5_smart.py` | CDS 备用下载（**本轮新增**） | 需 Terminal 后台运行 |
| `scripts/download_era5.py` | CDS 原始下载脚本（24 小时/天） | 不推荐（文件太大） |
| `scripts/download_modis_phase1.py` | MODIS HDF 直下（Bear token） | 不推荐（GEE 已覆盖） |

---

## 管道命令 / Pipeline Commands

全部通过 venv + CLI 运行：

```powershell
cd W:\Nature
.\.venv\Scripts\python -m nature_climate_ai <command>
```

关键命令链：

```powershell
# MODIS 处理
nature_climate_ai modis-quality-filter
nature_climate_ai modis-anomalies

# ERA5 处理（GEE CSV 直接输入，跳过 era5-raw-aggregate）
nature_climate_ai era5-climate-features --input data/interim/era5_composite_climate.csv

# 建模
nature_climate_ai modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv

# 前兆发现
nature_climate_ai precursor-discovery

# 验证
nature_climate_ai temporal-holdout-validation
nature_climate_ai spatial-holdout-validation
nature_climate_ai fluxnet-validation
```

**注意**：`era5-raw-aggregate` 是为 CDS NetCDF 设计的，GEE CSV 路径跳过了它——因为 GEE 导出已经是 16 天复合格式，直接进入 `era5-climate-features`。

---

## 环境 / Environment

| 项 | 值 |
|----|-----|
| Python | `W:\Nature\.venv` |
| 关键包 | `rasterio`, `pandas`, `numpy`, `xarray`, `cdsapi`, `pyyaml`, `scikit-learn`, `earthaccess` |
| 包管理器 | pip + `pyproject.toml`（`[project.scripts] nature-climate-ai = "nature_climate_ai.cli:main"`） |
| GEE API | 凭据存在 `~/.config/earthengine/credentials`，但 `ee.Initialize()` 缺 Cloud Project 参数，**Code Editor 可用** |
| CDS API | Key: `70f66e5d-a057-45a8-8a90-a5f47b23d2b1`，URL: `https://cds.climate.copernicus.eu/api`，通过环境变量注入 |
| EDL Token | `W:\Nature\.edl_token`（676 bytes JWT），用于 NASA Earthdata |
| Node.js | 已安装（GEE CLI 等工具） |

---

## 磁盘空间 / Disk Space

| 盘 | 可用 | 用途 |
|----|------|------|
| W: | ~87 GB | 项目主目录，已用 866 GB |
| E: | ~291 GB | ERA5 CDS 备用下载目标 |

---

## 已知未完成 / Remaining Work

1. **FLUXNET 31 个无效站点**：需手动从官网重下，放入 `data/raw/fluxnet/`
2. **CDS ERA5 全量下载**：如需要 CDS 原始数据做验证，在 Terminal 后台跑：
   ```powershell
   cd W:\Nature
   $env:CDSAPI_URL="https://cds.climate.copernicus.eu/api"
   $env:CDSAPI_KEY="70f66e5d-a057-45a8-8a90-a5f47b23d2b1"
   $env:ERA5_OUTPUT_DIR="E:/Nature_ERA5"
   $env:ERA5_START_YEAR="2000"; $env:ERA5_END_YEAR="2025"
   .\.venv\Scripts\python scripts/download_era5_smart.py
   ```
   预计 ~180 GB（4 时段/天，单层含土壤湿度），支持断点续传。
3. **GEE Python API 认证**：`ee.Initialize(project='<your-cloud-project>')`，当前缺 Cloud Project。认证后可批量提交 GEE 导出任务。
4. **管道试跑**：建议先跑 `modis-quality-filter` → `modis-anomalies` → `era5-climate-features` 验证 MODIS + ERA5 CSV 都能正常进入管道。

---

## 设计决策 / Design Decisions

1. **MODIS 走 GEE 而非 HDF 直下**：HDF 文件 134 GB 仅用于回溯审计，核心分析全走 GEE 导出 CSV
2. **ERA5 16 天复合（非日尺度）**：因 lead_time_days 全是 16 的倍数，16 天复合天然对齐 MODIS，且文件量从 2,555→161 波段/年（96% 缩小）
3. **ERA5-Land 而非 ERA5 single-levels**：GEE 的 ERA5-Land 含全部所需变量（t2m, d2m, tp, ssr, swvl1, swvl2），0.1° 原生分辨率重采样到 0.25°
4. **VPD 在 GEE 中计算**：使用 Magnus 公式从窗口平均 t2m + d2m 计算，避免下载额外变量
5. **双轨策略（GEE 主线 + CDS 备线）**：GEE 快且省空间做主力，CDS 下载脚本做原始数据备查

---

## 文件索引 / File Index

```
W:\Nature\
├── data/
│   ├── raw/
│   │   ├── modis_observations.csv          # ← 核心：MODIS 25年全部数据
│   │   ├── modis_gee/                      # 25个 GeoTIFF (~220 MB)
│   │   ├── era5_gee/                       # 26个 GeoTIFF (~218 MB) ← 本轮新增
│   │   ├── fluxnet/                        # 111 ZIPs (6.5 GB)
│   │   └── era5/                           # CDS 测试数据 (8.5 GB, 仅 2000-01)
│   ├── interim/
│   │   └── era5_composite_climate.csv      # ← 核心：ERA5 26年全部数据 ← 本轮新增
│   └── metadata/
│       └── fluxnet_raw_archive_audit.csv   # FLUXNET 审计
├── scripts/
│   ├── export_era5_gee.js                  # ← 本轮新增：GEE ERA5 16天导出
│   ├── export_modis_gee.js                 # GEE MODIS 导出
│   ├── convert_era5_gee.py                 # ← 本轮新增：ERA5 TIF→CSV
│   ├── convert_gee_tif.py                  # MODIS TIF→CSV
│   ├── download_era5_smart.py              # ← 本轮新增：CDS 智能下载
│   └── download_era5.py                    # CDS 原版下载
├── config/
│   └── study.yaml                          # 项目配置
└── src/nature_climate_ai/
    └── *.py                                # 管道模块（cli.py 为入口）
```

---

## AI 交接备注 / Notes for Next AI

- 用户用中文沟通，偏好中英双语文档
- 项目使用 Codex/Codex 桌面版，sandbox 有时间限制——长时间下载需指导用户在 Terminal 运行
- GEE Code Editor 已验证可用（用户之前成功导出 MODIS 和 ERA5），但 Python API 未完全配通
- 用户的 Google Drive 有 `Nature_MODIS_Export` 和 `Nature_ERA5_Export` 两个文件夹
- W 盘 87 GB 可用，大型文件建议放 E 盘（291 GB）
- 删除命令需人工审核（AGENTS.md 要求）
- `.cdsapirc` 无法创建（sandbox 限制），CDS 认证将通过环境变量

---

*Handoff generated by Codex (GPT-5) on 2026-06-07*
