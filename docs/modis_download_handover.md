# MODIS Phase 1 下载 — 对话交接文档

> 写给即将接手此对话的 AI。下面记录了本项目的背景、遇到的问题、已尝试的方案和最终结论。

## 项目背景

- **目标**：Nature/Science 级别的 AI 气候前兆发现论文
- **数据来源**：ERA5/ERA5-Land（已有 2000-01 烟测数据）、MODIS MOD13Q1/MYD13Q1、FLUXNET
- **Phase 1 策略**：仅下载覆盖澳大利亚 FLUXNET 站点的 MODIS 瓦片（h31v11, h29v12, h32v10, h32v12），约 50-100 GB，而非全球 12 TB
- **MODIS 产品**：MOD13Q1.061 (Terra)、MYD13Q1.061 (Aqua)，Collection 061
- **年份范围**：2001-2025

## 关键技术问题

### 1. 网络代理导致 SSL 失败（核心问题）

用户机器上有本地 HTTPS 代理 `http://127.0.0.1:7890`（疑似 Clash/V2Ray），对 NASA LAADS 服务器 (`ladsweb.modaps.eosdis.nasa.gov`) 和 Earthdata Login (`urs.earthdata.nasa.gov`) 造成一系列 SSL 问题：

| 客户端 | 问题 |
|--------|------|
| PowerShell `Invoke-WebRequest` | `基础连接已经关闭: 接收时发生错误` — TLS 版本不兼容 |
| `curl.exe` (Windows) | `schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS` — Schannel 凭据存储问题 |
| Python `urllib` | `SSL: UNEXPECTED_EOF_WHILE_READING` — 代理在 SSL 握手期间中断连接 |
| Python `requests` + 代理 | 同上，即使 `verify=False` 也无法解决 |
| `earthaccess` 库 OAuth 登录 | `TimeoutError: The handshake operation timed out` — OAuth 握手卡在 10 秒内 |

### 2. Earthdata 认证问题

- **Bearer token** 对 LAADS 目录列表有效（HTTP 200），但对文件下载无效（被重定向到 Earthdata Login 页面）
- **`earthaccess` 环境变量登录** 能完成认证，但 OAuth 回调需要访问 `urs.earthdata.nasa.gov`，代理下超时
- **用户需手动授权**：打开 `https://urs.earthdata.nasa.gov/approve_app?client_id=A6th7HB-3EBoO7iOCiCLlA` 并点击 Approve
- **用户 Earthdata 档案**：用户名 `wuzhuoxian`，缺失 `Organization` 字段时需要补充

### 3. MODIS 文件名匹配

Collection 061 的目录列表中存在文件（每 DOY 约 3432 个 HDF），但目标瓦片 (h31v11 等) 不一定在每个 DOY 都存在。正则匹配需用实际目录 HTML 中的文件名。

## 最终可行方案（已实现）

### 方案：Bear Token + no_proxy 直连

绕过代理是唯一可行路径。Python 的 `requests` 库配合 `no_proxy` 环境变量可以直连 NASA 服务器：

```python
os.environ["no_proxy"] = ".nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov,urs.earthdata.nasa.gov"
```

关键配置：
- **认证**：从 `W:\Nature\.edl_token` 读取 Bearer token（JWT 格式）
- **Session**：`requests.Session()` 管理 cookie/redirect 链
- **SSL**：`verify=False` + `urllib3.disable_warnings()` 禁用警告
- **重试**：最多 5 次，间隔递增 (10s-60s)
- **HTML 检测**：下载后检查前 1KB 是否为 `<!DOCTYPE`，防止假文件

### 脚本位置

- **最终版本**：`W:\Nature\scripts\download_modis_phase1.py`
- **旧版 PowerShell**：`W:\Nature\scripts\download_modis_phase1.ps1`（因代理问题废弃）
- **测试脚本**：`W:\Nature\scripts\_test_modis.py`（可删除）

### 运行方式

```powershell
cd W:\Nature
Remove-Item -Recurse -Force data\raw\modis -ErrorAction SilentlyContinue
.\.venv\Scripts\python scripts\download_modis_phase1.py --max-gb 100 --start-year 2001 --end-year 2025
```

输出目录：`W:\Nature\data\raw\modis/{MOD13Q1,MYD13Q1}/{year}/{doy}/`

### Earthdata Token

Token 文件：`W:\Nature\.edl_token`
- JWT Bearer token，由用户在 https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/#generate-token 生成
- 过期后需用户重新生成并覆盖此文件

## 当前状态

| 项目 | 状态 |
|------|------|
| ERA5-Land swvl1/swvl2 | ✓ 已解压并可读 (5.5 GB, 2000-01) |
| ERA5 single-level (t2m, d2m, ssr, tp) | ✓ 已解压并可读 (3.6 GB, 2000-01) |
| FLUXNET 站点数据 | 部分下载（AU-ASM, AU-Boy, AU-Cow），AU-Cpr 未完成 |
| MODIS Phase 1 下载 | **待执行** — 脚本已就绪，需用户在终端运行 |
| MODIS 全量 Phase 2 | Phase 1 成功后才启动 |

## 注意事项

1. **`AGENTS.md` 规定**：删除操作需人工审核，README 必须中英双语，包含中文的文件用 UTF-8 读取
2. **不要改动用户已有的文件**：除非明确要求，不要 revert 其他变更
3. **代理不要改**：`127.0.0.1:7890` 是用户的代理软件，可能为访问外网必须——不要关闭或修改，只在需要时用 `no_proxy` 绕过
4. **Windows 环境**：路径用 `W:\Nature\...`，Python 在 `.\.venv\Scripts\python`，PowerShell 5.x
5. **earthaccess 0.18.0 已安装**：如需使用，可用环境变量方式登录 (`EARTHDATA_USERNAME`/`EARTHDATA_PASSWORD`)，但 OAuth 握手在代理下可能超时

## 关键文件清单

| 文件 | 说明 |
|------|------|
| `scripts/download_modis_phase1.py` | MODIS 最终下载脚本 |
| `.edl_token` | NASA Earthdata Bearer token |
| `data/raw/era5/cds_33d64.../era5_land_200001_swvl.nc` | ERA5-Land 土壤水分 |
| `data/raw/era5/cds_8c58.../*.nc` | ERA5 单层数据 |
| `data/raw/modis/` | MODIS 下载目标目录 |
| `data/raw/fluxnet/` | FLUXNET 站点 zip |
| `data/metadata/modis_phased_strategy.md` | 分阶段下载策略文档 |
| `data/metadata/modis_products.yaml` | MODIS 产品配置 |
