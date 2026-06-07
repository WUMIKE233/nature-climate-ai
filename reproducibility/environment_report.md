# Reproducibility environment audit

Status: READY_FOR_CURRENT_ENVIRONMENT

metric | value
--- | ---
python_version | 3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)]
platform | Windows-11-10.0.26220-SP0
executable | W:\Nature\.venv\Scripts\python.exe
command_manifest | reproducibility/command_manifest.csv
environment_yml | reproducibility/environment.yml
requirements_lock | reproducibility/requirements-lock.txt
seed_manifest | reproducibility/random_seed_manifest.yaml
compute_budget | reproducibility/compute_budget.md

## Package versions

package | version
--- | ---
cdsapi | 0.7.7
earthaccess | 0.18.0
nature-climate-ai | 0.1.0
netCDF4 | 1.7.4
numpy | 2.4.6
pandas | 3.0.3
pytest | 9.0.3
pyyaml | 6.0.3
xarray | 2026.4.0

## Missing packages

- None.

## Current-state warning

This environment can run the scaffold tests and readiness commands, but the manuscript remains non-submission-ready until data access, result artifacts, uncertainty analysis, figures and author metadata are complete.

## 中文审阅说明

本报告记录当前 Python 环境、核心包版本、复现命令清单、环境文件、锁定文件、随机种子和计算资源计划。它证明当前脚手架可运行，不代表真实数据、模型结果或论文结论已经完成。
