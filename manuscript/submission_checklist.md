# Nature submission checklist

## Scientific evidence

- [ ] All relevant evidence items in `evidence/registry.yaml` are marked complete with artifacts present.
- [ ] Evidence artifact audit has passed with no missing required artifacts and no unresolved placeholders in text artifacts.
- [ ] Vegetation-stress events are defined from quality-filtered MODIS records.
- [ ] No future climate or vegetation information leaks into lagged predictors.
- [ ] Temporal holdout results are reported.
- [ ] Spatial holdout results are reported.
- [ ] Predictive validation summary has been generated from baseline, temporal-holdout and spatial-holdout metrics.
- [ ] Baseline comparisons include climatology, simple statistical models and standard climate indices.
- [ ] Feature-attribution results are checked for stability.
- [ ] Statistical uncertainty is reported for main metrics.
- [ ] Uncertainty audit has generated intervals from saved validation confusion counts.
- [ ] FLUXNET validation is complete or the absence of site validation is explicitly acknowledged.
- [ ] Negative or non-generalizing results are reported where relevant.
- [ ] Minimum publishable evidence slice has produced pilot stress-event, precursor-pathway and predictive-validation figures before full Nature/Science expansion.
- [ ] Robustness and falsification tests cover placebo lags, threshold sensitivity, biome stratification and sensor or ecosystem-function cross-validation where data permit.
- [ ] Mechanistic interpretation is explicitly separated from predictive performance and hypothesis generation.

## Manuscript

- [ ] Main claim replaces `RESULT_REQUIRED` only after validation artifacts exist.
- [ ] Readiness dashboard has been generated and reviewed, and all components are `READY` except synthetic-only checks that are explicitly labelled.
- [ ] Manuscript format audit has passed for the selected target journal.
- [ ] Submission package audit has passed with no unresolved placeholders across package files.
- [ ] Title, summary and introduction match the actual result.
- [ ] Nature claim strategy and target-journal decision tree have been reviewed against the actual evidence strength.
- [ ] Editorial significance rationale explains why the result merits the selected target rather than a specialist journal.
- [ ] Main text is within the target Nature length range.
- [ ] Main display items are limited to 4-6 figures or tables unless the target changes.
- [ ] Every main figure is cited in the text.
- [ ] Figure manifest and figure-generation report have been generated.
- [ ] Figure legends are self-contained.
- [ ] Methods are complete enough for expert review.
- [ ] References are verified against source metadata and DOI records.
- [ ] Reference audit has passed and targeted literature gaps have been closed.
- [ ] Author metadata audit has passed with names, affiliations, contributions, acknowledgements, funding, competing interests and submission approvals complete.

## Data and code

- [ ] Copernicus access and ERA5/ERA5-Land request parameters are documented.
- [ ] Data-access manifest and access plan have been generated and reviewed before data download.
- [ ] ERA5/ERA5-Land climate lag features have generated `data/processed/climate_lag_features.csv` and a QC report.
- [ ] NASA MODIS product versions, quality flags and download routes are documented.
- [ ] MODIS quality filtering has generated `data/interim/modis_quality_filtered.csv` and a QC report.
- [ ] Model-ready dataset has generated `data/processed/modeling_dataset.csv` and a QC report.
- [ ] Baseline metrics and comparison report have been generated before AI model claims are drafted.
- [ ] Precursor-discovery candidates are generated and remain labelled as candidates until validation is complete.
- [ ] Temporal holdout metrics have been generated for ranked precursor candidates.
- [ ] Spatial holdout metrics have been generated for ranked precursor candidates using documented region or biome definitions.
- [ ] Predictive validation summary has generated `results/validation/predictive_validation_summary.csv` and a summary report.
- [ ] FLUXNET dataset/version, Tier policy, site-years and data-use conditions are documented.
- [ ] FLUXNET ecosystem validation has generated site anomaly metrics and a validation summary.
- [ ] Environment setup runs on a clean machine.
- [ ] Reproducibility environment report and command manifest have been generated.
- [ ] Synthetic smoke-test report has been generated and clearly excluded from manuscript evidence.
- [ ] Data preprocessing, model training, validation and figure commands are documented.
- [ ] Public repository or archival DOI is prepared if allowed.
- [ ] Public release audit has passed with no missing release artifacts, no high-risk credential patterns and a versioned repository commit available.
- [ ] Credentials, private tokens and restricted datasets are excluded from public code.
- [ ] Data ethics and licensing review records public access routes, restricted-data constraints, checksums and substitute access paths.

## Chinese internal review

- [ ] 中文审阅说明已更新，明确哪些结论已经有证据支持。
- [ ] README 保持中英双语。
- [ ] 若涉及删除文件、数据或记录，已经完成人工审核。
