# Reproducibility audit

`reproducibility-audit` records the local Python environment, core package versions, command manifest, environment file, lightweight lockfile, random-seed manifest and planned compute-budget record needed to rerun the scaffold and readiness gates.

## Command

```powershell
python -m nature_climate_ai.cli reproducibility-audit --output reproducibility/environment_report.md --command-manifest reproducibility/command_manifest.csv --environment-yml reproducibility/environment.yml --requirements-lock reproducibility/requirements-lock.txt --seed-manifest reproducibility/random_seed_manifest.yaml --compute-budget reproducibility/compute_budget.md
```

## Outputs

- `reproducibility/environment_report.md`: Python version, platform, executable, package versions and links to reproducibility support files.
- `reproducibility/command_manifest.csv`: key commands and their expected current readiness status.
- `reproducibility/environment.yml`: conda-style environment specification for the scaffold.
- `reproducibility/requirements-lock.txt`: local package-version snapshot for the current environment.
- `reproducibility/random_seed_manifest.yaml`: planned fixed seeds for stochastic analysis stages.
- `reproducibility/compute_budget.md`: compute-resource plan to be filled with measured CPU/GPU, time, memory and storage use after real analysis.

## Interpretation

This audit can be `READY` even when the manuscript is not submission-ready. It only confirms that the local scaffold environment is runnable. Data access, result artifacts, manuscript placeholders and evidence completion remain separate gates.

## 中文说明

该审计记录当前运行环境和复现命令清单，用于支撑后续 code availability 和可复现性说明。它不代表数据已经获取、模型结果已经产生或论文已经可以投稿。
