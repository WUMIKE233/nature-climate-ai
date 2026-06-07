# Reproducibility checklist

## Environment

- [ ] Reproducibility audit generated `reproducibility/environment_report.md`.
- [ ] Command manifest generated `reproducibility/command_manifest.csv`.
- [ ] Synthetic smoke workflow generated `reproducibility/pipeline_smoke_report.md`.
- [ ] Python version recorded.
- [ ] Package versions pinned or exported.
- [ ] GPU model, CUDA version and driver recorded if neural models are used.
- [ ] Random seeds recorded for stochastic models.

## Data

- [ ] Download commands or provider request parameters recorded.
- [ ] Data licences and use conditions reviewed.
- [ ] File checksums recorded with `checksum-audit` for local archives and generated intermediate artifacts where appropriate.
- [ ] Missingness diagnostics generated.
- [ ] Spatial and temporal alignment verified.

## Analysis

- [ ] Readiness commands have expected `NOT_READY` statuses until data and results exist.
- [ ] Synthetic smoke outputs are kept separate from manuscript evidence.
- [ ] All preprocessing steps are scripted.
- [ ] No manual spreadsheet edits are required for core results.
- [ ] Train/test split logic is versioned.
- [ ] Baseline models are run with the same splits as the AI model.
- [ ] Figures regenerate from saved analysis artifacts.

## Reporting

- [ ] Every result in the manuscript links to a result artifact.
- [ ] Every figure has a generation command.
- [ ] Every claim has either a citation or project evidence.
- [ ] Limitations and failure cases are explicitly reported.
