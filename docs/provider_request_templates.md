# Provider request templates

`provider-request-templates` generates structured request templates for ERA5/ERA5-Land, MODIS and FLUXNET from `config/study.yaml`.

## Command

```powershell
python -m nature_climate_ai.cli provider-request-templates --config config/study.yaml --output-dir data/metadata/provider_requests --manifest data/metadata/provider_request_manifest.csv --report data/metadata/provider_request_templates.md
```

## Outputs

- `data/metadata/provider_request_manifest.csv`: source, provider, template path, access status and next action.
- `data/metadata/provider_request_templates.md`: human-readable provider request report.
- `data/metadata/provider_requests/era5_request_template.yaml`: CDS-style ERA5/ERA5-Land request scaffold.
- `data/metadata/provider_requests/modis_request_template.yaml`: MODIS product, index, quality-filter and access-route scaffold.
- `data/metadata/provider_requests/fluxnet_request_template.yaml`: FLUXNET policy, site and variable access scaffold.

## Interpretation

The command does not download data, validate credentials or certify that access has been granted. Its expected current status is `NOT_READY` until human reviewers confirm accounts, request payloads, product versions, site lists, policy restrictions, download dates and checksums.

## 中文审阅说明

本命令把研究配置转换成 ERA5、MODIS 和 FLUXNET 的访问请求模板，方便后续人工确认账号、产品版本、请求参数、政策限制和下载记录。它不会下载数据，也不能作为论文结果证据。
