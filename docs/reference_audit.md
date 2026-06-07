# Reference audit

`reference-audit` checks the structured reference metadata used by the manuscript package. It records DOI metadata for the current seed references and keeps targeted literature-review gaps visible.

## Command

```powershell
python -m nature_climate_ai.cli reference-audit --metadata manuscript/reference_metadata.yaml --output manuscript/reference_audit.md --status-csv manuscript/reference_status.csv
```

## Outputs

- `manuscript/reference_metadata.yaml`: structured reference metadata and remaining literature gaps.
- `manuscript/reference_audit.md`: human-readable reference readiness report.
- `manuscript/reference_status.csv`: machine-readable reference status table.

## Current state

The four seed references for ERA5, MODIS vegetation indices, FLUXNET2015 and AI/process understanding have DOI metadata recorded. The audit remains `NOT_READY` because targeted review is still required for compound heat-drought extremes, ecological early warning, interpretable climate/ecology machine learning and global vegetation anomaly remote sensing.

## 中文说明

该审计用于防止参考文献在投稿前才暴露 DOI、年份、题名或主题覆盖缺口。当前核心种子文献已经结构化记录，但文献综述尚未完成，仍需要人工补充和核验近期相关研究。
