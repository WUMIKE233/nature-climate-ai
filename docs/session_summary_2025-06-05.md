# 对话总结：项目进度分析与 ERA5 数据下载配置

> 日期：2025-06-05 | 项目：Nature Climate AI

---

## 1. 项目进度分析

对 `W:\Nature` 项目进行了全面审查：

### 当前状态
- **证据链完成度**：0 / 18 项
- **代码框架**：34 个 Python 模块，完整 CLI + 测试套件
- **测试结果**：80 passed / 1 failed / 58 errors（README 声称 139 passed，存在退化）
- **手稿**：Nature 主稿 + Science 备选稿均存在（含 22 个 `RESULT_REQUIRED` 占位符）
- **Git**：已初始化但无任何 commit
- **投稿就绪判断**：`NOT_READY`

### 阻塞项
- ERA5 / MODIS / FLUXNET 全部为 `DATA_ACCESS_REQUIRED`
- 36 个结果产物缺失
- 所有验证指标、图表 PNG、最终稿件均未生成

---

## 2. 数据下载基础设施建设

### 2.1 新增模块

**`src/nature_climate_ai/data_download.py`**
- ERA5 下载器（CDS API，月度 NetCDF，支持断点续传）
- MODIS 下载器（NASA Earthdata，MOD13Q1/MYD13Q1）
- FLUXNET 下载指引（手动下载）
- 统一的 `DownloadLogEntry` 日志格式

### 2.2 新增 CLI 命令

| 命令 | 用途 |
|---|---|
| `download-era5` | ERA5/ERA5-Land 下载（`--year-start`, `--year-end`, `--months`, `--dry-run`） |
| `download-modis` | MODIS 产品下载（`--tiles`, `--dry-run`） |
| `fluxnet-instructions` | FLUXNET 手动下载指引 |

### 2.3 依赖变更（`pyproject.toml`）

- 新增 `cdsapi>=0.7`（核心依赖）
- 将 `xarray>=2024.1` 移为核心依赖
- 新增 `earthaccess>=0.12`（科学可选依赖）
- 新增 `pre-commit>=3.6`（开发可选依赖）

---

## 3. CDS API 凭据配置

### 3.1 正确的 API Key 获取方式

**官方页面**：https://cds.climate.copernicus.eu/how-to-api  
（需先登录 Copernicus 账号）

登录后页面会显示两行代码：
```
url: https://cds.climate.copernicus.eu/api
key: <personal-access-token>
```

参考文档：https://confluence.ecmwf.int/display/CKB/How+to+install+and+use+CDS+API+on+Windows

### 3.2 凭据配置方式

**环境变量**（本项目使用）：
```powershell
$env:CDSAPI_URL = "https://cds.climate.copernicus.eu/api"
$env:CDSAPI_KEY = "<your-token>"
```

**持久化文件**（Windows）：
创建 `C:\Users\<用户名>\.cdsapirc`，内容同上两行。  
Windows 上点号文件需通过记事本"另存为"时加双引号创建。

---

## 4. 已知问题与解决

### 4.1 403 Forbidden — Licence 未接受
**现象**：API 调用返回 `required licences not accepted`  
**解决**：在浏览器中分别接受两个数据集的许可：

- https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#manage-licences
- https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=download#manage-licences

### 4.2 下载超时
**现象**：沙箱环境中 `shell_command` 有超时限制（5min → 20min），CDS 处理全月逐小时数据需要更长时间  
**解决**：生成独立下载脚本 `scripts/download_era5.py`，由用户在本地终端运行，无超时限制

---

## 5. 手动下载方案

### 文件位置
`W:\Nature\scripts\download_era5.py`

### 运行方式
```powershell
cd W:\Nature
.\.venv\Scripts\Activate.ps1
python scripts/download_era5.py
```

### 脚本特性
- 断点续传（已下载文件自动跳过）
- 进度实时显示 `[当前/总数]`
- 可配置年份范围（`START_YEAR` / `END_YEAR`）
- 可筛选月份（`SELECTED_MONTHS`，设为 `None` = 全部 12 个月）
- 输出目录：`data/raw/era5/`
- 文件命名：`era5_single_YYYYMM.nc` 和 `era5_land_YYYYMM.nc`
- 总计：26 年 × 12 月 × 2 数据集 = 624 个文件

### 建议策略
先测试 1 个月（`START_YEAR=2000, END_YEAR=2000, SELECTED_MONTHS=[1]`），确认流程通畅后再扩大。

---

## 6. 待办事项

- [ ] 用户手动运行 `scripts/download_era5.py` 下载 ERA5 全部年份
- [ ] 配置 NASA Earthdata 凭据（`~/.netrc`），运行 `download-modis`
- [ ] 访问 FLUXNET 网站接受数据政策，手动下载站点数据
- [ ] 修复测试回归（当前 58 errors）
- [ ] 创建首次 Git commit
- [ ] 运行 `e00-data-qc` 验证已下载数据

---

## 7. 关键文件变更清单

| 文件 | 操作 |
|---|---|
| `src/nature_climate_ai/data_download.py` | 新建 |
| `src/nature_climate_ai/cli.py` | 修改（新增 import + 3 个 handler + 3 个 subparser） |
| `pyproject.toml` | 修改（新增 cdsapi 等依赖） |
| `scripts/download_era5.py` | 新建 |
| `data/raw/era5/` | 新建目录 |
