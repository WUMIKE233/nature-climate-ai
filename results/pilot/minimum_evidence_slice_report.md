# Minimum publishable evidence-slice gate

Status: NOT_READY
Complete artifacts: 10/14
Missing artifacts: 4
CSV: results/pilot/minimum_evidence_slice_status.csv

group | exists | artifact | role
--- | --- | --- | ---
stress_event_definition | True | results/stress_events/event_catalogue_summary.csv | pilot stress-event catalogue
stress_event_definition | True | results/stress_events/quality_control_report.md | stress-event QC report
precursor_pathway | True | results/modeling/feature_attribution_table.csv | ranked precursor candidates
precursor_pathway | True | results/modeling/lag_response_summary.csv | lag-response evidence
predictive_validation | True | results/validation/baseline_metrics.csv | baseline comparator metrics
predictive_validation | True | results/validation/temporal_holdout_metrics.csv | temporal holdout metrics
predictive_validation | True | results/validation/spatial_holdout_metrics.csv | spatial holdout metrics
predictive_validation | True | results/validation/predictive_validation_summary.csv | combined predictive validation summary
robustness_falsification | True | results/validation/placebo_metrics.csv | placebo lag-shift test
robustness_falsification | True | results/validation/threshold_sensitivity.csv | stress-threshold sensitivity
robustness_falsification | False | results/validation/biome_metrics.csv | biome-stratified validation
pilot_figures | False | figures/generated/pilot_fig1_stress_event_map.png | Pilot Fig. 1 stress-event map
pilot_figures | False | figures/generated/pilot_fig2_precursor_pathway.png | Pilot Fig. 2 precursor pathway
pilot_figures | False | figures/generated/pilot_fig3_predictive_validation.png | Pilot Fig. 3 predictive validation

## Decision rule

Do not expand the manuscript into full Nature/Science claims. Complete the missing pilot artifacts first.

## Stop rules

- Stop or redesign if pilot results do not beat climatology, persistence and standard climate-index baselines.
- Stop or downscope if precursor patterns collapse under temporal or spatial holdout.
- Stop claim promotion if threshold, biome or sensor robustness checks fail.

## 中文审阅说明

该门控只检查最小可验证结果切片所需文件是否存在，不证明结果已经足够强。只有三张 pilot 图、基线对比、时空验证和稳健性检查都完成并通过人工科学审阅后，才应继续扩展到 Nature/Science 全稿。
