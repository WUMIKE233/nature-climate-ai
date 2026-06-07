# Evidence artifact audit

`evidence-artifact-audit` checks every required artifact listed in `evidence/registry.yaml`. It reports whether each file exists and whether text artifacts still contain `DATA_ACCESS_REQUIRED`, `AUTHOR_REQUIRED` or `RESULT_REQUIRED`.

## Command

```powershell
python -m nature_climate_ai.cli evidence-artifact-audit --registry evidence/registry.yaml --root . --output evidence/artifact_audit.md --csv evidence/artifact_audit.csv
```

## Outputs

- `evidence/artifact_audit.md`: human-readable blocking artifact report.
- `evidence/artifact_audit.csv`: machine-readable artifact status table.

## Manuscript rule

An evidence item should not be marked `complete` until all required artifacts exist, text artifacts are free of unresolved placeholders, and a human reviewer has checked that the artifact actually supports the linked manuscript claim.

## 中文说明

该审计逐项检查证据注册表中的必需文件是否存在，以及文本型证据文件中是否还含有占位符。它不会自动把证据项改成完成状态；最终仍需要人工确认科学结果、数据政策和论文结论之间的对应关系。
