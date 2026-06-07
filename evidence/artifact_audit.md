# Evidence artifact audit

Status: NOT_READY
Registry: evidence/registry.yaml
Root: .
CSV: evidence/artifact_audit.csv

metric | value
--- | ---
artifact_rows | 113
missing_artifacts | 9
placeholder_files | 0

## Blocking artifacts

- robustness_falsification: results/validation/sensor_cross_validation.csv (missing, placeholders=0)
- ecosystem_validation: results/fluxnet/predicted_stress_windows.csv (missing, placeholders=0)
- ecosystem_validation: results/fluxnet/site_anomaly_metrics.csv (missing, placeholders=0)
- figure_package: figures/generated/fig2_precursors.png (missing, placeholders=0)
- figure_package: figures/generated/fig3_validation.png (missing, placeholders=0)
- figure_package: figures/generated/fig4_fluxnet.png (missing, placeholders=0)
- manuscript_finalization: manuscript/final/nature_article.docx (missing, placeholders=0)
- manuscript_finalization: manuscript/final/nature_article.pdf (missing, placeholders=0)
- manuscript_finalization: manuscript/final/submission_ready_checklist.md (missing, placeholders=0)

## 中文审阅说明

本审计逐项检查证据注册表中的必需文件是否存在，以及文本型证据文件中是否仍含 DATA_ACCESS_REQUIRED、AUTHOR_REQUIRED 或 RESULT_REQUIRED 占位符。它不自动把证据项标记为完成；最终仍需要人工确认科学结果和数据政策。
