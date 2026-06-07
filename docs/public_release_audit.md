# Public release audit

`public-release-audit` checks whether the repository is ready for public code release and archival DOI preparation.

## Command

```powershell
python -m nature_climate_ai.cli public-release-audit --root . --output reproducibility/public_release_audit.md --csv reproducibility/public_release_status.csv
```

## Outputs

- `reproducibility/public_release_audit.md`: human-readable public-release readiness report.
- `reproducibility/public_release_status.csv`: machine-readable issue table.

## Interpretation

The audit checks required reproducibility artifacts, confirms that a git repository exists for commit-hash reporting, and scans text files for common high-risk credential patterns. It intentionally ignores policy text such as "do not store tokens" unless a high-risk assigned value is present.

The current expected status is `NOT_READY` because this workspace is not yet a git repository and the manuscript still lacks real data/results and archival identifiers.

## 中文审阅说明

本审计用于公开代码发布前的最低检查：版本库、复现文件、数据访问说明、校验记录和常见凭据泄露模式。它不能替代人工安全审查，也不能自动生成 DOI。
