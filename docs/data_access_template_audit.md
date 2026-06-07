# Data access template audit

`data-access-template-audit` checks whether ERA5/ERA5-Land, MODIS and FLUXNET access templates still contain pending request, product, quality, policy or site-selection fields.

## Command

```powershell
python -m nature_climate_ai.cli data-access-template-audit --root . --output data/metadata/data_access_template_audit.md --csv data/metadata/data_access_template_status.csv
```

## Outputs

- `data/metadata/data_access_template_audit.md`: human-readable report of unresolved template fields.
- `data/metadata/data_access_template_status.csv`: machine-readable list of file, field, issue and value.

## Interpretation

The current expected status is `NOT_READY` because provider access, product versions, request payloads, download dates, quality rules, FLUXNET policy decisions and checksums still require human confirmation.

This audit does not download data and does not verify credentials. It prevents the project from treating planned access templates as completed data-access evidence.

## 中文审阅说明

本审计检查 ERA5、MODIS 和 FLUXNET 的访问模板是否仍有待确认字段。只有账号、产品版本、请求参数、下载日期、质量规则、政策限制、站点清单和校验信息补齐后，相关数据访问证据才应进入完成状态。
