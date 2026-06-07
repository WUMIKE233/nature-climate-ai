# Nature/Science readiness dashboard

Status: NOT_READY
Total blockers: 40
CSV: reproducibility/readiness_dashboard.csv

component | status | blockers | summary | evidence
--- | --- | ---: | --- | ---
tests_and_environment | READY | 0 | 9 core packages recorded | reproducibility/environment_report.md; reproducibility/command_manifest.csv
pipeline_smoke | COMPLETE_FOR_SYNTHETIC_DATA | 0 | synthetic workflow completed; outputs are excluded from manuscript evidence | reproducibility/pipeline_smoke_report.md; reproducibility/pipeline_smoke_manifest.csv
data_access | READY | 0 | 0 source access confirmations remain pending | data/metadata/data_access_manifest.csv; data/metadata/data_access_plan.md
data_access_templates | READY | 0 | 0 data-access template issues remain | data/metadata/data_access_template_audit.md; data/metadata/data_access_template_status.csv
era5_download_status | READY_FOR_QC | 0 | 3 ERA5/ERA5-Land downloads ready for checksum and QC | data/metadata/era5_download_log.csv; data/metadata/era5_download_status.md
gee_grid_alignment | READY | 0 | MODIS and ERA5 GEE reference rasters share one pixel grid | data/metadata/gee_grid_alignment_audit.md; data/metadata/gee_grid_alignment_audit.csv
data_checksums | READY | 0 | 1719 checksum rows recorded for local data files | data/checksums/data_checksum_audit.md; data/checksums/data_checksums.csv
evidence_registry | NOT_READY | 18 | 0/18 evidence items complete | evidence/registry.yaml
evidence_artifacts | NOT_READY | 9 | 9 missing artifacts; 0 placeholder files | evidence/artifact_audit.md; evidence/artifact_audit.csv
figure_assets | PARTIAL_READY | 3 | Fig. 1 workflow assets exist; result figures remain blocked by real analysis | figures/generated/fig1_workflow.svg; figures/generated/figure_manifest.csv; figures/generated/figure_generation_report.md; figures/generated/fig2_precursors.png; figures/generated/fig3_validation.png; figures/generated/fig4_fluxnet.png
manuscript_format | NOT_READY | 4 | 1822 main-text words; 0 display items | manuscript/nature_article_draft.md
submission_package | NOT_READY | 5 | 0 missing files; 5 placeholder files | manuscript/submission_package_audit.md; manuscript/submission_package_status.csv
references | READY | 0 | 15/15 seed references checked; 0 literature gaps | manuscript/reference_metadata.yaml
author_metadata | READY | 0 | 0 author metadata issues remain | manuscript/author_metadata.yaml; manuscript/author_metadata_audit.md; manuscript/author_metadata_status.csv
public_release | READY | 0 | 0 public release issues remain | reproducibility/public_release_audit.md; reproducibility/public_release_status.csv
submission_gate | NOT_READY | 1 | 18 evidence items are not complete. | manuscript/nature_article_draft.md; evidence/registry.yaml

## Next-action logic

Prioritize gates in this order: data access, real data preprocessing, modeling/validation artifacts, uncertainty and figure outputs, manuscript placeholder replacement, final package export.

## 中文审阅说明

本面板汇总当前投稿包的主要门控状态。它不会自动完成任何证据项，也不会把合成数据当作论文结果；只用于快速定位下一步最重要的阻塞。
