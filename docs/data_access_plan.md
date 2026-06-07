# Public data-access plan

`data-access-plan` generates a manifest and bilingual report for the public data sources used by the manuscript package. It is the first evidence step before data download, preprocessing or model training.

## Command

```powershell
python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md
```

## Outputs

- `data/metadata/data_access_manifest.csv`: machine-readable source, provider, access, target year and required-action table.
- `data/metadata/data_access_plan.md`: human-readable report with Chinese review note.

## Interpretation

The command normally reports `NOT_READY` at the start of the project because ERA5, MODIS and FLUXNET access placeholders are still unresolved. This is intentional. A `NOT_READY` access report prevents the manuscript from implying that data have already been obtained.

The report can support `e00_data_qc` only after provider accounts, data policies, request parameters, download dates and checksums are documented in the metadata files.

Run `data-access-template-audit` after editing metadata templates to verify that pending request, product, quality, policy and site-selection fields have actually been resolved:

```powershell
python -m nature_climate_ai.cli provider-request-templates --config config/study.yaml --output-dir data/metadata/provider_requests --manifest data/metadata/provider_request_manifest.csv --report data/metadata/provider_request_templates.md
python -m nature_climate_ai.cli data-access-template-audit --root . --output data/metadata/data_access_template_audit.md --csv data/metadata/data_access_template_status.csv
```

## 中文说明

该步骤用于生成公共数据访问计划和审计清单，帮助确认 ERA5/ERA5-Land、MODIS 和 FLUXNET 的账号、政策、变量、年份、下载路线和本地产物路径。它不是下载命令，也不是科学结果证据；只有访问记录和质量控制都完成后，相关结论才可以进入论文。
