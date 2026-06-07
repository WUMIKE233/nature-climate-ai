# Data ethics and licensing

## Policy basis

Nature's current author guidance requires Data Availability and Code Availability statements, and notes that data supporting the findings may need deposition in appropriate public repositories with full access at publication. Science/AAAS also requires authors to state where supporting data, code or materials can be accessed.

Source links:

- Nature initial submission: https://www.nature.com/nature/for-authors/initial-submission
- Nature formatting guide: https://www.nature.com/nature/for-authors/formatting-guide
- Nature Portfolio reporting standards and availability policy: https://www.nature.com/nataging/editorial-policies/reporting-standards
- AAAS data availability: https://www.aaas.org/disciplines/scientific-community/science-communication/data-availability

## Project requirements

- Record public-data access routes for ERA5/ERA5-Land, MODIS and FLUXNET before analysis claims are promoted.
- Treat data-access records as part of the manuscript evidence chain; a result is not submission-ready until its supporting data route is documented.
- Keep credentials, API keys, private tokens and restricted data out of the repository.
- Store checksum manifests under `data/checksums/`; store request payloads, product versions and policy notes under `data/metadata/`.
- Prepare public-code release with command manifest, environment file, seed manifest and compute-budget note.
- If restricted FLUXNET data cannot be redistributed, document the access route and provide reproducible code that can be run after authorized access.

## Repository additions to prepare

```text
data/
  checksums/
  metadata/
  raw/
  interim/
  processed/
  README_data_access.md

reproducibility/
  environment.yml
  requirements-lock.txt
  random_seed_manifest.yaml
  compute_budget.md
  docker/
```

## 中文审阅说明

数据和代码可用性必须从现在开始设计，而不是投稿前补写。公开数据并不等于可以随意再分发；FLUXNET 等数据尤其需要记录政策、引用和访问路径。
