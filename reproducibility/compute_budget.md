# Compute budget

Status: PLANNED_NOT_MEASURED

The current scaffold and tests run on CPU. Real global analysis will require recording the actual compute environment before any Nature/Science submission claim is finalized.

## Planned records

- CPU model, RAM and operating system.
- GPU model, count, memory and driver/CUDA stack if neural models are trained.
- Wall-clock time for data preprocessing, feature generation, model training, validation, robustness checks and figure generation.
- Peak memory/storage use and intermediate-data footprint.
- Any cloud, cluster or local workstation identifiers that can be shared publicly.

## Current local scaffold

- Tests and readiness commands run in the local Python environment recorded by `reproducibility/environment_report.md`.
- No manuscript result has been generated from GPU training yet.

## 中文审阅说明

本文件记录计算资源计划。当前只证明脚手架可以在本地环境运行，不代表真实全球分析已经完成；正式投稿前必须补充实际 CPU/GPU、运行时间、内存、存储和训练设置。
