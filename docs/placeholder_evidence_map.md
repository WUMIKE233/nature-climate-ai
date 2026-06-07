# Manuscript placeholder evidence map

`placeholder-map` links each unresolved manuscript placeholder to the evidence item or author input required before it can be replaced.

## Command

```powershell
python -m nature_climate_ai.cli placeholder-map --manuscript manuscript/nature_article_draft.md --output manuscript/placeholder_evidence_map.md --csv manuscript/placeholder_evidence_map.csv
```

## Outputs

- `manuscript/placeholder_evidence_map.md`: human-readable line-by-line map from placeholders to evidence/input requirements.
- `manuscript/placeholder_evidence_map.csv`: machine-readable table with line number, section, token, linked evidence IDs, requirement and context.

## Interpretation

The command currently returns `NOT_READY` because the draft intentionally still contains `RESULT_REQUIRED`, `AUTHOR_REQUIRED` and `DATA_ACCESS_REQUIRED` placeholders. This report does not replace any manuscript text; it identifies the exact evidence or author information needed before replacement.

## 中文审阅说明

该报告用于防止把计划中的分析提前写成论文结论。每个占位符都必须先对应到真实数据、验证结果、投稿材料或作者输入，之后才能人工替换。
