# Submission-readiness audit

Audit date: 2026-06-05

## Current verdict

Status: **not submission-ready yet**.

Reason: the workspace now contains a Nature/Science manuscript package and reproducible analysis scaffold, but it does not yet contain validated scientific results. The submission gate correctly blocks submission because manuscript placeholders and pending evidence items remain.

## Completed preparation

- Nature-first manuscript draft exists: `manuscript/nature_article_draft.md`.
- Science alternative draft exists: `manuscript/science_research_article_draft.md`.
- Editorial strategy exists: `manuscript/editorial_strategy.md`.
- Literature positioning exists: `docs/literature_positioning.md`.
- Figure plan exists: `figures/figure_plan.md`.
- Figure asset-generation command exists and can generate the Fig. 1 workflow schematic plus a figure manifest without inventing result panels.
- Manuscript format-audit command exists and can check Nature/Science draft structure, word counts, display items, references and placeholders.
- Submission package-audit command exists and can check manuscript package files plus unresolved placeholders.
- Reference audit command exists and can track checked seed references, DOI metadata and targeted literature-review gaps.
- Author metadata audit command exists and can track names, affiliations, contributions, acknowledgements, funding, competing interests and submission approvals without inventing author information.
- Supplementary outline, cover letter, presubmission enquiry and checklist exist.
- Bilingual README files exist.
- Public data-source metadata templates exist for ERA5/ERA5-Land, MODIS and FLUXNET.
- Evidence registry exists: `evidence/registry.yaml`.
- Evidence artifact-audit command exists and can check required artifact presence plus unresolved placeholders.
- Placeholder evidence-map command exists and can link each manuscript placeholder to the evidence item or author input required before replacement.
- Data checksum-audit command exists and can generate SHA-256 checksum reports for downloaded public data or generated intermediate artifacts.
- Reproducibility audit command exists and records environment/package versions, the command manifest, environment specification, local lockfile, random-seed manifest and planned compute-budget record.
- Public release audit command exists and can check required release artifacts, git repository presence and common high-risk credential patterns before code availability claims are finalized.
- Synthetic pipeline smoke-test command exists and can run the scaffold end to end on artificial data without generating manuscript evidence.
- Readiness dashboard command exists and can summarize environment, smoke-test, data-access, evidence, figure, manuscript, reference and submission-gate status in one report.
- Nature claim strategy, editorial significance rationale, validation design, interpretability plan, robustness/falsification plan, data ethics/licensing plan, target-journal decision tree and minimum publishable evidence-slice plan exist.
- Submission gate exists and blocks unverified manuscripts.
- Data-access plan command exists and can generate a public-source manifest and bilingual access report before data download.
- Provider request-template command exists and can generate ERA5, MODIS and FLUXNET request scaffolds without credentials or downloads.
- Data-access template audit command exists and can detect unresolved ERA5, MODIS and FLUXNET request, product, quality, policy and site-selection fields.
- ERA5/MODIS/FLUXNET download infrastructure exists, including ERA5 and MODIS CLI entry points plus a safer ERA5 script that supports environment-based configuration and one-month dry runs.
- Confirmed author contact information has been added for 吴卓宪, Guangdong Neusoft Institute NUIT, wum2371@gmail.com; contribution, funding, competing-interest and final approval fields remain pending for manual confirmation.
- E00 data-QC command exists and has generated a local report at `results/qc/e00_data_qc_report.md`.
- ERA5 climate-feature command exists and can generate leakage-safe lagged climate precursor features from an aggregated ERA5/ERA5-Land table.
- MODIS quality-filtering command exists and can generate `data/interim/modis_quality_filtered.csv` from imported MODIS observations.
- MODIS anomaly-generation command exists and can generate `data/processed/modis_anomalies.csv` from a quality-filtered MODIS table.
- E01 event-catalogue command exists and can generate a readiness report when processed MODIS anomaly input is missing.
- Modeling dataset command exists and can assemble climate lag features with stress-event labels.
- Baseline evaluation command exists and can evaluate majority, prevalence, persistence, single-feature, climate-family and compound heat-drought comparators once a modeling dataset exists.
- Precursor-discovery command exists and can rank lagged climate features as candidate stress precursors once a modeling dataset exists.
- Temporal holdout validation command exists and can evaluate ranked candidates on configured holdout years.
- Spatial holdout validation command exists and can evaluate ranked candidates under leave-one-region-out validation.
- Predictive validation summary command exists and can summarize baseline, temporal-holdout and spatial-holdout metrics into one evidence artifact.
- Uncertainty audit command exists and can compute Wilson intervals from validation confusion-count metrics.
- Robustness and falsification commands exist for placebo validation, stress-threshold sensitivity, biome-stratified validation and sensor cross-validation.
- Pilot figure-generation command exists and can create three pilot PNG figures from real event, precursor and validation artifacts.
- Minimum evidence-slice gate command exists and checks whether pilot stress-event, precursor, validation, robustness and figure artifacts are ready before full manuscript expansion.
- FLUXNET validation command exists and can compare ecosystem-function anomalies inside versus outside predicted stress windows.

## Blocking evidence

The following must be completed before any Nature or Science submission:

- Data access and policy review for ERA5/ERA5-Land, MODIS and FLUXNET.
- Replacement of data-access placeholders in data metadata templates after real provider access is confirmed.
- MODIS quality-filtered vegetation-stress event catalogue.
- Climate-feature construction with leakage checks.
- Baseline and AI model comparisons.
- Temporal holdout validation.
- Spatial holdout validation.
- FLUXNET external validation.
- Main figure generation from result artifacts.
- Final manuscript text with all result, data-access and author placeholders replaced by verified information.

## Verification commands

```powershell
.\.venv\Scripts\python -m pytest -q --basetemp .test_tmp -p no:cacheprovider
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli manuscript-format-audit --manuscript manuscript/nature_article_draft.md --journal nature --output results/submission/manuscript_format_audit.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli submission-package-audit --root . --output manuscript/submission_package_audit.md --csv manuscript/submission_package_status.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli reference-audit --metadata manuscript/reference_metadata.yaml --output manuscript/reference_audit.md --status-csv manuscript/reference_status.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli author-metadata-audit --metadata manuscript/author_metadata.yaml --output manuscript/author_metadata_audit.md --csv manuscript/author_metadata_status.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli generate-figure-assets --config config/study.yaml --output-dir figures/generated --manifest figures/generated/figure_manifest.csv --report figures/generated/figure_generation_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli evidence-status --registry evidence/registry.yaml
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli evidence-artifact-audit --registry evidence/registry.yaml --root . --output evidence/artifact_audit.md --csv evidence/artifact_audit.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli placeholder-map --manuscript manuscript/nature_article_draft.md --output manuscript/placeholder_evidence_map.md --csv manuscript/placeholder_evidence_map.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli checksum-audit --root data --output data/checksums/data_checksum_audit.md --csv data/checksums/data_checksums.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli reproducibility-audit --output reproducibility/environment_report.md --command-manifest reproducibility/command_manifest.csv --environment-yml reproducibility/environment.yml --requirements-lock reproducibility/requirements-lock.txt --seed-manifest reproducibility/random_seed_manifest.yaml --compute-budget reproducibility/compute_budget.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli pipeline-smoke-test --output-dir outputs/smoke --report reproducibility/pipeline_smoke_report.md --manifest reproducibility/pipeline_smoke_manifest.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli data-access-plan --config config/study.yaml --manifest data/metadata/data_access_manifest.csv --report data/metadata/data_access_plan.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli provider-request-templates --config config/study.yaml --output-dir data/metadata/provider_requests --manifest data/metadata/provider_request_manifest.csv --report data/metadata/provider_request_templates.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli data-access-template-audit --root . --output data/metadata/data_access_template_audit.md --csv data/metadata/data_access_template_status.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli public-release-audit --root . --output reproducibility/public_release_audit.md --csv reproducibility/public_release_status.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli readiness-dashboard --root . --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml --config config/study.yaml --reference-metadata manuscript/reference_metadata.yaml --output reproducibility/readiness_dashboard.md --csv reproducibility/readiness_dashboard.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli submission-gate --manuscript manuscript/nature_article_draft.md --registry evidence/registry.yaml
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli e00-data-qc --output results/qc/e00_data_qc_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli era5-climate-features --input data/interim/era5_composite_climate.csv --output data/processed/climate_lag_features.csv --report results/qc/era5_climate_feature_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli modis-quality-filter --input data/raw/modis_observations.csv --output data/interim/modis_quality_filtered.csv --report results/qc/modis_quality_filter_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli modis-anomalies --input data/interim/modis_quality_filtered.csv --output data/processed/modis_anomalies.csv --report results/qc/modis_anomaly_qc_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli e01-event-catalogue --input data/processed/modis_anomalies.csv --output-dir results/stress_events
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli modeling-dataset --climate data/processed/climate_lag_features.csv --events results/stress_events/event_catalogue_summary.csv --anomalies data/processed/modis_anomalies.csv --output data/processed/modeling_dataset.csv --report results/qc/modeling_dataset_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli baseline-evaluation --input data/processed/modeling_dataset.csv --output results/validation/baseline_metrics.csv --report results/validation/baseline_comparison.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli precursor-discovery --input data/processed/modeling_dataset.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --report results/modeling/precursor_discovery_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli temporal-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/temporal_holdout_metrics.csv --report results/validation/temporal_holdout_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli spatial-holdout-validation --modeling data/processed/modeling_dataset.csv --candidates results/modeling/feature_attribution_table.csv --output results/validation/spatial_holdout_metrics.csv --report results/validation/spatial_holdout_report.md --region-col region
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli predictive-validation-summary --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/predictive_validation_summary.csv --report results/validation/predictive_validation_summary.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli uncertainty-audit --baseline results/validation/baseline_metrics.csv --temporal results/validation/temporal_holdout_metrics.csv --spatial results/validation/spatial_holdout_metrics.csv --output results/validation/uncertainty_intervals.csv --report results/validation/uncertainty_audit.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli placebo-validation --input data/processed/modeling_dataset.csv --output results/validation/placebo_metrics.csv --report results/validation/placebo_validation.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli threshold-sensitivity --input data/processed/modis_anomalies.csv --output results/validation/threshold_sensitivity.csv --report results/validation/threshold_sensitivity.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli biome-stratified-validation --modeling data/processed/modeling_dataset.csv --biome-col biome --output results/validation/biome_metrics.csv --report results/validation/biome_validation.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli sensor-cross-validation --modis data/processed/modis_anomalies.csv --external data/processed/external_vegetation_anomalies.csv --output results/validation/sensor_cross_validation.csv --report results/validation/sensor_cross_validation.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli generate-pilot-figures --events results/stress_events/event_catalogue_summary.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --predictive results/validation/predictive_validation_summary.csv --output-dir figures/generated --manifest figures/generated/pilot_figure_manifest.csv --report figures/generated/pilot_figure_generation_report.md
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli minimum-evidence-slice --root . --output results/pilot/minimum_evidence_slice_report.md --csv results/pilot/minimum_evidence_slice_status.csv
$env:PYTHONPATH='src'; python -m nature_climate_ai.cli fluxnet-validation --fluxnet data/processed/fluxnet_anomalies.csv --windows results/fluxnet/predicted_stress_windows.csv --output results/fluxnet/site_anomaly_metrics.csv --report results/fluxnet/validation_summary.md
```

Expected current result:

- Tests pass. Latest local verification with workspace temp directory: `141 passed`.
- Reference audit currently returns `NOT_READY` because targeted literature gaps remain.
- Author metadata audit currently returns `NOT_READY` because contributions, acknowledgements, funding, competing interests and submission approvals still require author input.
- Manuscript format audit currently returns `NOT_READY` because the draft still contains placeholders and is not yet in final Nature length/claim state.
- Submission package audit currently returns `NOT_READY` because manuscript package files still contain result, author and data-access placeholders.
- Figure asset generation currently creates Fig. 1 only; Fig. 2-4 remain blocked until result artifacts exist.
- Evidence complete count is `0/18`.
- Evidence artifact audit currently returns `NOT_READY` because required result artifacts are missing; current generated evidence files contain no unresolved placeholder tokens.
- Placeholder evidence map currently returns `NOT_READY` because the Nature draft still has unresolved placeholders, but each placeholder now has a linked evidence or author-input requirement.
- Data checksum audit currently returns `NOT_READY` because no downloaded public-data files or generated intermediate data artifacts exist yet.
- Reproducibility audit currently returns `READY` for the current local scaffold environment.
- Public release audit currently returns `READY_FOR_PUBLIC_RELEASE_REVIEW` for the local scaffold: git is initialized, required release artifacts exist and no high-risk credential patterns are detected. Formal public archive identifiers are still not finalized.
- Pipeline smoke test currently returns `COMPLETE_FOR_SYNTHETIC_DATA`; outputs are not manuscript evidence.
- Readiness dashboard currently returns `NOT_READY` and identifies the remaining blockers across pending data-access confirmations, missing result artifacts, figure assets, manuscript/package placeholders, references and final submission gate.
- Submission gate returns `NOT_READY`.
- Data-access plan currently returns `NOT_READY` because ERA5, MODIS and FLUXNET access placeholders remain.
- Provider request templates currently return `NOT_READY` because they require human account, request, product, policy and checksum confirmation before download.
- Data-access template audit currently returns `NOT_READY` because provider request, product, quality, policy and site-selection fields remain pending.
- ERA5 climate-feature generation currently returns a readiness report unless `data/interim/era5_composite_climate.csv` exists.
- MODIS quality filtering currently returns a readiness report unless `data/raw/modis_observations.csv` exists.
- MODIS anomaly generation currently returns a readiness report unless `data/interim/modis_quality_filtered.csv` exists.
- E01 currently returns a readiness report unless `data/processed/modis_anomalies.csv` exists.
- Modeling dataset assembly currently returns a readiness report unless climate features and stress-event catalogue artifacts exist.
- Baseline evaluation currently returns a readiness report unless `data/processed/modeling_dataset.csv` exists.
- Precursor discovery currently returns a readiness report unless `data/processed/modeling_dataset.csv` exists.
- Temporal holdout validation currently returns a readiness report unless modeling dataset and precursor candidate artifacts exist.
- Spatial holdout validation currently returns a readiness report unless modeling dataset and precursor candidate artifacts exist and requires a `region` column.
- Predictive validation summary currently returns a readiness report unless baseline, temporal-holdout and spatial-holdout metric artifacts exist.
- Uncertainty audit currently returns a readiness report unless baseline, temporal-holdout and spatial-holdout metric artifacts with confusion counts exist.
- Placebo validation currently returns a readiness report unless `data/processed/modeling_dataset.csv` exists.
- Threshold sensitivity currently returns a readiness report unless `data/processed/modis_anomalies.csv` exists.
- Biome-stratified validation currently returns a readiness report unless `data/processed/modeling_dataset.csv` exists with a `biome` column.
- Sensor cross-validation currently returns a readiness report unless MODIS and external vegetation-anomaly artifacts exist.
- Pilot figure generation currently returns a readiness report unless event-catalogue, lag-response and predictive-validation artifacts exist.
- Minimum evidence-slice gate currently returns `NOT_READY` until pilot stress-event, precursor, validation, robustness and three pilot-figure artifacts exist.
- FLUXNET validation currently returns a readiness report unless FLUXNET anomalies and predicted stress-window artifacts exist.
- Strategy documents currently require a minimum publishable evidence slice before expanding the manuscript into full Nature/Science claims.

## Next milestone

The next concrete milestone is to complete `E00_data_qc` and then run a minimum publishable evidence slice: confirm access to public data sources, build a small but rigorous stress-event catalogue, test candidate precursors against strong baselines, and generate pilot stress-event, precursor-pathway and predictive-validation figures. Only if that slice shows a robust signal should the project expand to full global analysis and Nature/Science final drafting.
