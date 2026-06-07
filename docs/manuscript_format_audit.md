# Manuscript format audit

`manuscript-format-audit` checks the draft before the final submission gate. It is designed for Nature-first preparation, with a Science fallback mode for the compact alternative draft.

## Nature command

```powershell
python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/nature_article_draft.md --journal nature --output results/submission/manuscript_format_audit.md
```

## Science fallback command

```powershell
python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/science_research_article_draft.md --journal science --output results/submission/science_format_audit.md
```

## What it checks

- summary or abstract word count,
- main-text word count,
- methods word count,
- main display-item count,
- reference count,
- required declaration sections,
- unresolved `RESULT_REQUIRED`, `DATA_ACCESS_REQUIRED` and `AUTHOR_REQUIRED` placeholders.

## Current source constraints

Nature's current initial-submission guidance is flexible on format but describes a fully referenced summary paragraph of about 200 words, main text around 2,500 words with 4 display items for a 6-page Article, and up to about 4,300 words with 5-6 display items for an 8-page Article. The audit uses these Nature limits as the primary target.

## 中文说明

该审计只检查稿件形式风险，不检查科学结果是否成立。它可以帮助发现摘要过长、主文字数不合适、图表数量不合适、声明部分缺失、占位符未替换等问题。即使格式审计通过，论文仍必须等数据、证据注册表、统计验证和投稿门控全部通过后才能提交。
