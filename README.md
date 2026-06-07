[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14882001.svg)](https://doi.org/10.5281/zenodo.14882001)

# nature-climate-ai: Interpretable Climate Precursor Discovery for Vegetation Stress across Australia

## English

This workspace contains a complete, reproducible research package for discovering climate precursors of satellite-observed vegetation stress across Australia. Target journal: *Remote Sensing* (MDPI), Phase 1 regional-scale SCI paper.

**Phase 1: Regional-scale ecological remote sensing research — MODIS (MOD13Q1/MYD13Q1) + ERA5-Land on unified 0.25° grid, 2000–2025, Australia.**

The package is intentionally evidence-gated. Draft manuscript claims use `RESULT_REQUIRED` placeholders until the analysis pipeline produces validated results.

### Project layout

- `manuscript/`: Nature-style article draft, Science fallback draft, cover letter, presubmission enquiry, supplementary outline and submission checklist.
- `docs/`: research workflow, reproducibility notes, data-source notes and Chinese review guidance.
- `docs/nature_claim_strategy.md`, `docs/validation_design.md`, `docs/robustness_and_falsification_plan.md` and related strategy files: editorial positioning, validation thresholds and pilot-analysis decision rules.
- `figures/`: figure plan and generated figure outputs.
- `config/study.yaml`: study design defaults, public data sources, validation splits and modelling choices.
- `src/nature_climate_ai/`: reproducible analysis scaffold for data cataloguing, preprocessing, stress-event definition, modelling, validation and figure asset planning.
- `tests/`: lightweight checks that protect the scaffold from silent drift.

### Minimum workflow

1. Register accounts and access where required by public providers:
   - Copernicus Climate Data Store for ERA5/ERA5-Land.
   - NASA Earthdata or LAADS/LP DAAC access for MODIS MOD13/MYD13 products.
   - FLUXNET access following the applicable FLUXNET2015 or current FLUXNET data policy.
2. Create the Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev,science]"
```

For a safe one-month ERA5 dry run before a real download:

```powershell
$env:ERA5_DRY_RUN="1"
$env:ERA5_START_YEAR="2000"
$env:ERA5_END_YEAR="2000"
$env:ERA5_MONTHS="1"
python scripts/download_era5.py
```

For log-based progress while a real ERA5 download runs in the background:

```powershell
.\scripts\start_era5_download_with_log.ps1 -YearStart 2000 -YearEnd 2000 -Months "1"
Get-Content -Path "<stdout log printed by the script>" -Wait
```

The downloader prints each ERA5/ERA5-Land request, success, failure and skipped file to stdout. If CDS returns a licence error, accept the dataset licences in the Copernicus Climate Data Store before retrying.

To turn the ERA5 download log into a reviewable status report:

```powershell
python -m nature_climate_ai.cli download-status --log data/metadata/era5_download_log.csv --output data/metadata/era5_download_status.md
```

To request only the missing ERA5-Land soil-water variables for a small smoke test:

```powershell
python -m nature_climate_ai.cli download-era5 --year-start 2000 --year-end 2000 --months 1 --only land
```

3. Inspect and run the planned analysis:

```powershell
python -m nature_climate_ai.cli describe-study --config config/study.yaml
python -m nature_climate_ai.cli check-claims --manuscript manuscript/nature_article_draft.md
python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/nature_article_draft.md --journal nature --output results/submission/manuscript_format_audit.md
python -m nature_climate_ai.cli submission-package-audit --root . --output manuscript/submission_package_audit.md --csv manuscript/submission_package_status.csv
python -m nature_climate_ai.cli reference-audit --metadata manuscript/reference_metadata.yaml --output manuscript/reference_audit.md --status-csv manuscript/reference_status.csv
python -m nature_climate_ai.cli author-metadata-audit --metadata manuscript/author_metadata.yaml --output manuscript/author_metadata_audit.md --csv manuscript/author_metadata_status.csv
python -m nature_climate_ai.cli generate-figure-assets --config config/study.yaml --output-dir figures/generated --manifest figures/generated/figure_manifest.csv --report figures/generated/figure_generation_report.md
python -m nature_climate_ai.cli evidence-status --registry evidence/registry.yaml
python -m nature_climate_ai.cli evidence-artifact-audit --registry evidence/registry.yaml --root . --output evidence/artifact_audit.md --csv evidence/artifact_audit.csv
python -m nature_climate_ai.cli placeholder-map --manuscript manuscript/nature_article_draft.md --output manuscript/placeholder_evidence_map.md --csv manuscript/placeholder_evidence_map.csv
python -m nature_climate_ai.cli checksum-audit --root data --output data/checksums/data_checksum_audit.md --csv data/checksums/data_checksums.csv
python -m nature_climate_ai.cli reproducibility-audit --output reproducibility/environment_report.md --command-manifest reproducibility/command_manifest.csv --environment-yml reproducibility/environment.yml --requirements-lock reproducibility/requirements-lock.txt --seed-manifest reproducibility/random_seed_manifest.yaml --compute-budget reproducibility/compute_budget.md
python -m nature_climate_ai.cli pipeline-smoke-test --output-dir outputs/smoke --report reproducibility/pipeline_smoke_report.md --manifest reproducibility/pipeline_smoke_manifest.csv
python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md
python -m nature_climate_ai.cli provider-request-templates --config config/study.yaml --output-dir data/metadata/provider_requests --manifest data/metadata/provider_request_manifest.csv --report data/metadata/provider_request_templates.md
python -m nature_climate_ai.cli data-access-template-audit --root . --output data/metadata/data_access_template_audit.md --csv data/metadata/data_access_template_status.csv
python -m nature_climate_ai.cli public-release-audit --root . --output reproducibility/public_release_audit.md --csv reproducibility/public_release_status.csv
python -m nature_climate_ai.cli readiness-dashboard --root . --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml --config config/study.yaml --reference-metadata manuscript/reference_metadata.yaml --output reproducibility/readiness_dashboard.md --csv reproducibility/readiness_dashboard.csv
python -m nature_climate_ai.cli submission-gate --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml
python -m nature_climate_ai.cli e00-data-qc --output results/qc/e00_data_qc_report.md
python -m nature_climate_ai.cli era5-climate-features --input data/interim/era5_composite_climate.csv --output data/processed/climate_lag_features.csv --report results/qc/era5_climate_feature_report.md
python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
python -m nature_climate_ai.cli e01-event-catalogue --input data/processed/modis_anomalies.csv --output-dir results/stress_events
python -m nature_climate_ai.cli modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv --anomalies data/processed/modis_anomalies.csv --output data/processed/modeling_dataset.csv --report results/qc/modeling_dataset_report.md
python -m nature_climate_ai.cli baseline-evaluation --input data/processed/modeling_dataset.csv --output results/validation/baseline_metrics.csv --report results/validation/baseline_comparison.md
python -m nature_climate_ai.cli precursor-discovery --input data/processed/modeling_dataset.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --report results/modeling/precursor_discovery_report.md
python -m nature_climate_ai.cli temporal-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/temporal_holdout_metrics.csv --report results/validation/temporal_holdout_report.md
python -m nature_climate_ai.cli spatial-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/spatial_holdout_metrics.csv --report results/validation/spatial_holdout_report.md --region-col region
python -m nature_climate_ai.cli predictive-validation-summary --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/predictive_validation_summary.csv --report results/validation/predictive_validation_summary.md
python -m nature_climate_ai.cli uncertainty-audit --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/uncertainty_intervals.csv --report results/validation/uncertainty_audit.md
python -m nature_climate_ai.cli placebo-validation --input data/processed/modeling_dataset.csv --output results/validation/placebo_metrics.csv --report results/validation/placebo_validation.md
python -m nature_climate_ai.cli threshold-sensitivity --input data/processed/modis_anomalies.csv --output results/validation/threshold_sensitivity.csv --report results/validation/threshold_sensitivity.md
python -m nature_climate_ai.cli biome-stratified-validation --modeling data/processed/modeling_dataset.csv --biome-col biome --output results/validation/biome_metrics.csv --report results/validation/biome_validation.md
python -m nature_climate_ai.cli sensor-cross-validation --modis data/processed/modis_anomalies.csv --external data/processed/external_vegetation_anomalies.csv --output results/validation/sensor_cross_validation.csv --report results/validation/sensor_cross_validation.md
python -m nature_climate_ai.cli generate-pilot-figures --events results/stress_events/event_catalogue_summary.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --predictive results/validation/predictive_validation_summary.csv --output-dir figures/generated --manifest figures/generated/pilot_figure_manifest.csv --report figures/generated/pilot_figure_generation_report.md
python -m nature_climate_ai.cli minimum-evidence-slice --root . --output results/pilot/minimum_evidence_slice_report.md --csv results/pilot/minimum_evidence_slice_status.csv
python -m nature_climate_ai.cli fluxnet-validation --fluxnet data/processed/fluxnet_anomalies.csv --windows results/fluxnet/predicted_stress_windows.csv --output results/fluxnet/site_anomaly_metrics.csv --report results/fluxnet/validation_summary.md
```

4. Replace placeholders only after evidence exists:
   - `RESULT_REQUIRED`: requires computed and validated result.
   - `AUTHOR_REQUIRED`: requires author or institution input.
   - `DATA_ACCESS_REQUIRED`: requires account, licence or data-access confirmation.

### Current status

**v1.0-rs: Ready for submission to *Remote Sensing* (MDPI)**. Full shared-grid pipeline completed (PASS_SHARED_GRID). Six publication-quality figures generated with Cartopy. Manuscript v3-revised with F1-based skill scores. MDPI DOCX and double-spaced review DOCX generated. Cover letter prepared. GitHub tag `v1.0-rs` published. Zenodo DOI: 10.5281/zenodo.14882001.

### Submission maturity

Phase 1 complete and submission-ready. All placeholders cleared. Manuscript, figures, cover letter, and submission checklist are available in `manuscript/`. Submit via [MDPI Susy](https://susy.mdpi.com) → Remote Sensing → Article.

## 中文

本工作区包含一套完整的可复现研究包，用于发现澳大利亚卫星植被胁迫的气候前兆。投稿目标期刊：*Remote Sensing* (MDPI)，第一阶段定位为区域尺度 SCI 论文。、Science 作为备选定位的气候/生态 AI 研究投稿包，当前工作假设为：

****第一阶段：区域尺度生态遥感研究 — MODIS + ERA5-Land，统一 0.25° 网格，2000–2025 年，澳大利亚。****

本项目采用“证据门控”原则。主稿中的科学结论在数据分析和验证完成前保留 `RESULT_REQUIRED` 占位符，避免把尚未产生的结果写成事实。

### 项目结构

- `manuscript/`：Nature 风格主稿、Science 备选稿、投稿信、预投稿询问信、补充材料大纲和投稿检查清单。
- `docs/`：研究流程、可复现说明、数据源说明和中文审阅说明。
- `docs/nature_claim_strategy.md`、`docs/validation_design.md`、`docs/robustness_and_falsification_plan.md` 等：正刊定位、验证门槛、稳健性/证伪测试和 pilot 分析决策规则。
- `figures/`：图件方案和后续生成的图件输出。
- `config/study.yaml`：研究设计默认值、公共数据源、验证拆分和建模选择。
- `src/nature_climate_ai/`：用于数据目录、预处理、胁迫事件定义、建模、验证和图件规划的可复现分析框架。
- `tests/`：用于防止项目框架静默漂移的轻量测试。

### 最小工作流

1. 按公共数据源要求注册或确认访问权限：
   - Copernicus Climate Data Store：ERA5/ERA5-Land。
   - NASA Earthdata、LAADS 或 LP DAAC：MODIS MOD13/MYD13 植被指数产品。
   - FLUXNET：按适用的 FLUXNET2015 或当前 FLUXNET 数据政策获取站点数据。
2. 创建 Python 环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev,science]"
```

在正式下载 ERA5 之前，可先运行 1 个月的安全 dry run：

```powershell
$env:ERA5_DRY_RUN="1"
$env:ERA5_START_YEAR="2000"
$env:ERA5_END_YEAR="2000"
$env:ERA5_MONTHS="1"
python scripts/download_era5.py
```

如果需要在真实下载时实时看进度，可以让下载在后台运行并查看日志：

```powershell
.\scripts\start_era5_download_with_log.ps1 -YearStart 2000 -YearEnd 2000 -Months "1"
Get-Content -Path "<脚本输出的 stdout log 路径>" -Wait
```

下载器会把每个 ERA5/ERA5-Land 请求、成功、失败和跳过文件写入 stdout。如果 CDS 返回许可证错误，需要先在 Copernicus Climate Data Store 接受对应数据集许可后再重试。

如需把 ERA5 下载日志转成可审阅状态报告：

```powershell
python -m nature_climate_ai.cli download-status --log data/metadata/era5_download_log.csv --output data/metadata/era5_download_status.md
```

如需只补缺失的 ERA5-Land 土壤水分变量，可先做 2000 年 1 月的小样本：

```powershell
python -m nature_climate_ai.cli download-era5 --year-start 2000 --year-end 2000 --months 1 --only land
```

3. 查看并运行计划中的分析：

```powershell
python -m nature_climate_ai.cli describe-study --config config/study.yaml
python -m nature_climate_ai.cli check-claims --manuscript manuscript/nature_article_draft.md
python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/nature_article_draft.md --journal nature --output results/submission/manuscript_format_audit.md
python -m nature_climate_ai.cli submission-package-audit --root . --output manuscript/submission_package_audit.md --csv manuscript/submission_package_status.csv
python -m nature_climate_ai.cli reference-audit --metadata manuscript/reference_metadata.yaml --output manuscript/reference_audit.md --status-csv manuscript/reference_status.csv
python -m nature_climate_ai.cli author-metadata-audit --metadata manuscript/author_metadata.yaml --output manuscript/author_metadata_audit.md --csv manuscript/author_metadata_status.csv
python -m nature_climate_ai.cli generate-figure-assets --config config/study.yaml --output-dir figures/generated --manifest figures/generated/figure_manifest.csv --report figures/generated/figure_generation_report.md
python -m nature_climate_ai.cli evidence-status --registry evidence/registry.yaml
python -m nature_climate_ai.cli evidence-artifact-audit --registry evidence/registry.yaml --root . --output evidence/artifact_audit.md --csv evidence/artifact_audit.csv
python -m nature_climate_ai.cli placeholder-map --manuscript manuscript/nature_article_draft.md --output manuscript/placeholder_evidence_map.md --csv manuscript/placeholder_evidence_map.csv
python -m nature_climate_ai.cli checksum-audit --root data --output data/checksums/data_checksum_audit.md --csv data/checksums/data_checksums.csv
python -m nature_climate_ai.cli reproducibility-audit --output reproducibility/environment_report.md --command-manifest reproducibility/command_manifest.csv --environment-yml reproducibility/environment.yml --requirements-lock reproducibility/requirements-lock.txt --seed-manifest reproducibility/random_seed_manifest.yaml --compute-budget reproducibility/compute_budget.md
python -m nature_climate_ai.cli pipeline-smoke-test --output-dir outputs/smoke --report reproducibility/pipeline_smoke_report.md --manifest reproducibility/pipeline_smoke_manifest.csv
python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md
python -m nature_climate_ai.cli provider-request-templates --config config/study.yaml --output-dir data/metadata/provider_requests --manifest data/metadata/provider_request_manifest.csv --report data/metadata/provider_request_templates.md
python -m nature_climate_ai.cli data-access-template-audit --root . --output data/metadata/data_access_template_audit.md --csv data/metadata/data_access_template_status.csv
python -m nature_climate_ai.cli public-release-audit --root . --output reproducibility/public_release_audit.md --csv reproducibility/public_release_status.csv
python -m nature_climate_ai.cli readiness-dashboard --root . --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml --config config/study.yaml --reference-metadata manuscript/reference_metadata.yaml --output reproducibility/readiness_dashboard.md --csv reproducibility/readiness_dashboard.csv
python -m nature_climate_ai.cli submission-gate --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml
python -m nature_climate_ai.cli e00-data-qc --output results/qc/e00_data_qc_report.md
python -m nature_climate_ai.cli era5-climate-features --input data/interim/era5_composite_climate.csv --output data/processed/climate_lag_features.csv --report results/qc/era5_climate_feature_report.md
python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
python -m nature_climate_ai.cli e01-event-catalogue --input data/processed/modis_anomalies.csv --output-dir results/stress_events
python -m nature_climate_ai.cli modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv --anomalies data/processed/modis_anomalies.csv --output data/processed/modeling_dataset.csv --report results/qc/modeling_dataset_report.md
python -m nature_climate_ai.cli baseline-evaluation --input data/processed/modeling_dataset.csv --output results/validation/baseline_metrics.csv --report results/validation/baseline_comparison.md
python -m nature_climate_ai.cli precursor-discovery --input data/processed/modeling_dataset.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --report results/modeling/precursor_discovery_report.md
python -m nature_climate_ai.cli temporal-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/temporal_holdout_metrics.csv --report results/validation/temporal_holdout_report.md
python -m nature_climate_ai.cli spatial-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/spatial_holdout_metrics.csv --report results/validation/spatial_holdout_report.md --region-col region
python -m nature_climate_ai.cli predictive-validation-summary --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/predictive_validation_summary.csv --report results/validation/predictive_validation_summary.md
python -m nature_climate_ai.cli uncertainty-audit --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/uncertainty_intervals.csv --report results/validation/uncertainty_audit.md
python -m nature_climate_ai.cli placebo-validation --input data/processed/modeling_dataset.csv --output results/validation/placebo_metrics.csv --report results/validation/placebo_validation.md
python -m nature_climate_ai.cli threshold-sensitivity --input data/processed/modis_anomalies.csv --output results/validation/threshold_sensitivity.csv --report results/validation/threshold_sensitivity.md
python -m nature_climate_ai.cli biome-stratified-validation --modeling data/processed/modeling_dataset.csv --biome-col biome --output results/validation/biome_metrics.csv --report results/validation/biome_validation.md
python -m nature_climate_ai.cli sensor-cross-validation --modis data/processed/modis_anomalies.csv --external data/processed/external_vegetation_anomalies.csv --output results/validation/sensor_cross_validation.csv --report results/validation/sensor_cross_validation.md
python -m nature_climate_ai.cli generate-pilot-figures --events results/stress_events/event_catalogue_summary.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --predictive results/validation/predictive_validation_summary.csv --output-dir figures/generated --manifest figures/generated/pilot_figure_manifest.csv --report figures/generated/pilot_figure_generation_report.md
python -m nature_climate_ai.cli minimum-evidence-slice --root . --output results/pilot/minimum_evidence_slice_report.md --csv results/pilot/minimum_evidence_slice_status.csv
python -m nature_climate_ai.cli fluxnet-validation --fluxnet data/processed/fluxnet_anomalies.csv --windows results/fluxnet/predicted_stress_windows.csv --output results/fluxnet/site_anomaly_metrics.csv --report results/fluxnet/validation_summary.md
```

4. 只有在证据产生后才替换占位符：
   - `RESULT_REQUIRED`：需要已经计算并验证的结果。
   - `AUTHOR_REQUIRED`：需要作者、机构或贡献信息。
   - `DATA_ACCESS_REQUIRED`：需要账号、许可或数据访问确认。

### 当前状态

**v1.0-rs：已准备投稿至 *Remote Sensing* (MDPI)**。共享网格管道全部完成 (PASS_SHARED_GRID)。6 张论文图表使用 Cartopy 生成。稿件 v3-revised 使用 F1-based skill scores。已生成 MDPI DOCX 和双倍行距审阅 DOCX。投稿信已准备就绪。GitHub tag `v1.0-rs` 已发布。Zenodo DOI: 10.5281/zenodo.14882001。

### 当前投稿成熟度

第一阶段已完成，具备投稿条件。所有占位符已清除。稿件、图表、投稿信、投稿检查清单均位于 `manuscript/`。通过 [MDPI Susy](https://susy.mdpi.com) → Remote Sensing → Article 提交。
