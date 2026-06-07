# Data Account and Download Checklist

Status: ACTION_REQUIRED

This checklist records the account-registration and dataset-download entry points needed for the Nature/Science climate-ecology manuscript. It is a data-access planning document only; it does not certify that the data have been downloaded, quality-controlled or approved for manuscript claims.

## Required datasets

dataset | account required | registration | download entry point | local target
--- | --- | --- | --- | ---
ERA5 hourly single levels | yes, Copernicus/CDS | https://cds.climate.copernicus.eu/ | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download | data/raw/era5/
ERA5-Land hourly | yes, Copernicus/CDS | https://cds.climate.copernicus.eu/ | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=download | data/raw/era5/
MODIS Terra vegetation indices | yes, NASA Earthdata | https://urs.earthdata.nasa.gov/ | https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13q1-061 | data/raw/modis/
MODIS Aqua vegetation indices | yes, NASA Earthdata | https://urs.earthdata.nasa.gov/ | https://www.earthdata.nasa.gov/data/catalog/lpcloud-myd13q1-061 | data/raw/modis/
FLUXNET ecosystem flux validation | yes, FLUXNET | https://fluxnet.org/ | https://fluxnet.org/download-data/ | data/raw/fluxnet/

## Strongly recommended auxiliary datasets

dataset | account required | registration | download entry point | manuscript role
--- | --- | --- | --- | ---
MODIS land cover MCD12Q1 | yes, NASA Earthdata | https://urs.earthdata.nasa.gov/ | https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd12q1-061 | biome/land-cover stratification and masking
SPEIbase | usually no | not required | https://spei.csic.es/database.html | drought-index baseline comparison
Koppen-Geiger climate zones | usually no | not required | https://repository.library.noaa.gov/view/noaa/24183 | climate-zone stratification
GLEAM | may require registration or request | https://www.gleam.eu/ | https://www.gleam.eu/ | evapotranspiration or soil-moisture robustness check

## Credential handling

- Do not commit usernames, passwords, API keys, `.netrc`, `.cdsapirc` or token files.
- CDS credentials should stay in user-level environment variables or the provider-standard `.cdsapirc`.
- NASA Earthdata credentials should be configured through Earthdata Login, `earthaccess` interactive login or a local `.netrc`.
- FLUXNET policy tier, site list, citation requirements and redistribution limits must be recorded in `data/metadata/fluxnet_policy_review.md` before any FLUXNET result is used in the manuscript.

## Current local data note

- ERA5 single-level user-supplied NetCDF files are readable in `data/raw/era5/cds_8c5868ad2f6b9db27f57ebaaeb460755/`.
- `data/raw/era5/era5_land_200001.nc` currently has a ZIP file signature and failed archive integrity testing; it should not be treated as valid soil-moisture evidence until re-downloaded or replaced by a readable NetCDF file.
- MODIS and FLUXNET raw data are not yet present locally.

## 中文清单

本清单记录 Nature/Science 气候-生态论文所需数据账号和下载入口，只用于数据访问计划，不代表数据已经完成下载、质量控制或可作为论文证据。

## 必需数据集

数据集 | 是否需要账号 | 注册地址 | 下载入口 | 本地目标目录
--- | --- | --- | --- | ---
ERA5 小时级 single levels | 需要，Copernicus/CDS | https://cds.climate.copernicus.eu/ | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download | data/raw/era5/
ERA5-Land 小时级 | 需要，Copernicus/CDS | https://cds.climate.copernicus.eu/ | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=download | data/raw/era5/
MODIS Terra 植被指数 | 需要，NASA Earthdata | https://urs.earthdata.nasa.gov/ | https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13q1-061 | data/raw/modis/
MODIS Aqua 植被指数 | 需要，NASA Earthdata | https://urs.earthdata.nasa.gov/ | https://www.earthdata.nasa.gov/data/catalog/lpcloud-myd13q1-061 | data/raw/modis/
FLUXNET 生态通量验证数据 | 需要，FLUXNET | https://fluxnet.org/ | https://fluxnet.org/download-data/ | data/raw/fluxnet/

## 强烈建议准备的辅助数据

数据集 | 是否需要账号 | 注册地址 | 下载入口 | 论文用途
--- | --- | --- | --- | ---
MODIS 土地覆盖 MCD12Q1 | 需要，NASA Earthdata | https://urs.earthdata.nasa.gov/ | https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd12q1-061 | 生物群区/土地覆盖分层与掩膜
SPEIbase | 通常不需要 | 不需要 | https://spei.csic.es/database.html | 干旱指数基线对照
Koppen-Geiger 气候分区 | 通常不需要 | 不需要 | https://repository.library.noaa.gov/view/noaa/24183 | 气候分区验证
GLEAM | 可能需要注册或申请 | https://www.gleam.eu/ | https://www.gleam.eu/ | 蒸散或土壤湿度鲁棒性检验

## 凭据处理要求

- 不要把用户名、密码、API key、`.netrc`、`.cdsapirc` 或 token 文件提交到仓库。
- CDS 凭据应保存在用户级环境变量或官方 `.cdsapirc` 中。
- NASA Earthdata 凭据建议通过 Earthdata Login、`earthaccess` 交互登录或本地 `.netrc` 配置。
- 使用 FLUXNET 前，必须在 `data/metadata/fluxnet_policy_review.md` 记录政策 tier、站点列表、引用要求和再分发限制。

## 当前本地数据状态

- `data/raw/era5/cds_8c5868ad2f6b9db27f57ebaaeb460755/` 中的 ERA5 single-level NetCDF 文件可读。
- `data/raw/era5/era5_land_200001.nc` 当前是 ZIP 文件头，并且归档完整性测试失败；在重新下载或替换为可读 NetCDF 前，不应作为土壤湿度证据。
- MODIS 和 FLUXNET 原始数据当前尚未在本地出现。
