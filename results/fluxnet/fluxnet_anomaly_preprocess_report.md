# FLUXNET anomaly preprocessing report

Status: COMPLETE_FOR_READABLE_ARCHIVES

Raw archive audit: data/metadata/fluxnet_raw_archive_audit.csv

metric | value
--- | ---
audit_rows | 111
usable_archive_rows | 58
sites_processed | 58
failed_sites | 0
output_rows | 302052
min_climatology_samples | 2
date_min | 1991-01-01
date_max | 2025-12-31

## Method note

Daily FLUXMET variables were converted to site-level day-of-year anomalies using only archives whose daily FLUXMET member and required variables were readable. Missing FLUXNET values encoded as -9999 were treated as missing.

## Manuscript-use warning

This is a pilot preprocessing artifact for readable local FLUXNET archives. It does not prove ecosystem validation and does not include model-predicted stress windows.

## 中文审阅说明

本报告把可读 FLUXNET 日尺度 FLUXMET 文件转换为站点逐日异常。它只覆盖当前可读站点，不代表所有 111 个站点都可用，也不能直接作为论文生态验证结论。
