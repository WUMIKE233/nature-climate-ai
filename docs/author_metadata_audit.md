# Author metadata audit

`author-metadata-audit` checks whether author names, affiliations, corresponding-author details, contributions, acknowledgements, funding, competing interests and submission approvals have been supplied.

## Command

```powershell
python -m nature_climate_ai.cli author-metadata-audit --metadata manuscript/author_metadata.yaml --output manuscript/author_metadata_audit.md --csv manuscript/author_metadata_status.csv
```

## Outputs

- `manuscript/author_metadata.yaml`: structured author-information template.
- `manuscript/author_metadata_audit.md`: human-readable readiness report.
- `manuscript/author_metadata_status.csv`: machine-readable list of missing or pending author fields.

## Interpretation

The current template intentionally uses `PENDING_AUTHOR_INPUT` rather than manuscript placeholder tokens. The audit returns `NOT_READY` until real author information and submission approvals are supplied by the author team.

## 中文审阅说明

本审计用于收集和检查作者、单位、贡献、致谢、资助、利益冲突和投稿确认信息。它不会替作者填写任何内容；正式投稿前必须由作者团队人工确认。
