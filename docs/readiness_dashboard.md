# Readiness dashboard

The readiness dashboard is a single status view for the Nature/Science manuscript package. It calls the existing audit functions directly instead of parsing old report text, so each run reflects the current files and code.

Run it with:

```powershell
python -m nature_climate_ai.cli readiness-dashboard --root . --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml --config config/study.yaml --reference-metadata manuscript/reference_metadata.yaml --output reproducibility/readiness_dashboard.md --csv reproducibility/readiness_dashboard.csv
```

Current expected status is `NOT_READY`. That is correct until real public-data access, result artifacts, uncertainty analysis, figure panels, author metadata and final manuscript exports are complete.

## Status meanings

- `READY`: the component has no current blockers according to its audit.
- `COMPLETE_FOR_SYNTHETIC_DATA`: the synthetic pipeline smoke test ran, but it is not manuscript evidence.
- `PARTIAL_READY`: preparatory assets exist, but result-dependent assets are still missing.
- `NOT_READY`: one or more blocking items remain.

## 中文审阅说明

该 dashboard 只是投稿准备度总览，不会把证据项自动标记为完成，也不会把合成数据输出当作论文结果。若 dashboard 显示 `NOT_READY`，应优先处理数据访问、真实数据预处理、模型验证、图件生成、文稿占位符和最终投稿包导出。
