# E01 stress-event catalogue

## Purpose

`E01_event_catalogue` converts a quality-filtered vegetation-index anomaly table into a persistent vegetation-stress event catalogue.

This step supports the manuscript claim:

> A global catalogue of persistent vegetation-stress events has been derived from quality-filtered MODIS anomalies.

The claim remains pending until the input table covers the intended study domain and years.

## Input contract

Default input:

```text
data/processed/modis_anomalies.csv
```

Required columns:

- `date`: MODIS composite date.
- `pixel_id`: stable pixel, site or region identifier.
- `evi_anomaly`: quality-filtered EVI anomaly.

The table must already have MODIS quality filtering applied. Raw MODIS retrievals, unfiltered vegetation indices or mixed-resolution extracts are not valid manuscript evidence.

To generate the default input from a quality-filtered MODIS table, run `modis-anomalies` first:

```powershell
python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
```

## Command

```powershell
python -m nature_climate_ai.cli e01-event-catalogue --input data/processed/modis_anomalies.csv --output-dir results/stress_events
```

If the input is missing, the command writes:

```text
results/stress_events/e01_event_catalogue_readiness_report.md
```

If the input exists and validates, the command writes:

```text
results/stress_events/event_catalogue_summary.csv
results/stress_events/quality_control_report.md
```

## Manuscript gate

Do not replace the `RESULT_REQUIRED` text in the Nature or Science drafts until:

- `event_catalogue_summary.csv` exists,
- `quality_control_report.md` exists,
- the input domain and years match `config/study.yaml`,
- MODIS quality-filtering decisions are documented,
- and sensitivity checks for EVI versus NDVI and event threshold are planned or complete.

## 中文说明

`E01_event_catalogue` 的作用是把已经通过 MODIS 质量标记筛选的植被指数异常表转换成“持续性植被胁迫事件目录”。如果输入数据不存在，命令只会生成 NOT_READY 报告，不会伪造结果。只有当输入数据覆盖目标年份和空间范围，并且质量过滤规则已记录时，事件目录才可以作为论文证据。
