# Submission package audit

`submission-package-audit` checks the manuscript package files that accompany a Nature-first or Science-fallback submission.

## Command

```powershell
python -m nature_climate_ai.cli submission-package-audit --root . --output manuscript/submission_package_audit.md --csv manuscript/submission_package_status.csv
```

## What it checks

- Nature draft.
- Science fallback draft.
- Cover letter.
- Presubmission enquiry.
- Supplementary information outline.
- Submission checklist.
- Editorial strategy.
- Chinese review notes.
- Reference seed list and structured reference metadata.
- Submission readiness audit.

The audit counts unresolved `RESULT_REQUIRED`, `AUTHOR_REQUIRED` and `DATA_ACCESS_REQUIRED` placeholders in each file.

## 中文说明

该审计检查投稿包文件是否齐全，以及每个文件中是否还含有结果、作者或数据访问占位符。它不会判断科学结果是否成立，只用于防止投稿材料在最终阶段漏文件或漏改占位符。
