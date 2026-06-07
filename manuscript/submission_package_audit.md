# Submission package audit

Status: NOT_READY
Root: .
CSV: manuscript/submission_package_status.csv

metric | value
--- | ---
package_files | 24
missing_files | 0
placeholder_files | 6

## File status

file | exists | result_token_count | author_token_count | data_access_token_count | issue
--- | --- | ---: | ---: | ---: | ---
manuscript/nature_article_draft.md | True | 16 | 3 | 2 | contains_placeholders
manuscript/science_research_article_draft.md | True | 8 | 1 | 1 | contains_placeholders
manuscript/cover_letter.md | True | 1 | 1 | 0 | contains_placeholders
manuscript/presubmission_enquiry.md | True | 2 | 0 | 0 | contains_placeholders
manuscript/supplementary_information_outline.md | True | 0 | 0 | 0 | ok
manuscript/submission_checklist.md | True | 1 | 0 | 0 | contains_placeholders
manuscript/editorial_strategy.md | True | 0 | 0 | 0 | ok
manuscript/chinese_review_notes.md | True | 1 | 0 | 0 | contains_placeholders
manuscript/reference_seed_list.md | True | 0 | 0 | 0 | ok
manuscript/reference_metadata.yaml | True | 0 | 0 | 0 | ok
manuscript/author_metadata.yaml | True | 0 | 0 | 0 | ok
manuscript/author_metadata_audit.md | True | 0 | 0 | 0 | ok
manuscript/author_metadata_status.csv | True | 0 | 0 | 0 | ok
docs/nature_claim_strategy.md | True | 0 | 0 | 0 | ok
docs/editorial_significance_rationale.md | True | 0 | 0 | 0 | ok
docs/known_risks_and_mitigation.md | True | 0 | 0 | 0 | ok
docs/validation_design.md | True | 0 | 0 | 0 | ok
docs/model_interpretability_plan.md | True | 0 | 0 | 0 | ok
docs/robustness_and_falsification_plan.md | True | 0 | 0 | 0 | ok
docs/data_ethics_and_licensing.md | True | 0 | 0 | 0 | ok
docs/target_journal_decision_tree.md | True | 0 | 0 | 0 | ok
docs/minimum_publishable_evidence_slice.md | True | 0 | 0 | 0 | ok
docs/readiness_dashboard.md | True | 0 | 0 | 0 | ok
docs/submission_readiness_audit.md | True | 0 | 0 | 0 | ok

## Manuscript-use warning

A package file can exist and still be non-submission-ready if it contains unresolved result, author or data-access placeholders.

## 中文审阅说明

本审计检查投稿包文件是否齐全，以及是否仍含结果、作者或数据访问占位符。文件存在不等于可以投稿；占位符和证据缺口必须全部清理后才能进入最终提交审阅。
