# Figure generation

`generate-figure-assets` creates the first manuscript figure asset that can be prepared before scientific results exist: a workflow schematic for Fig. 1. It also writes a manifest that keeps result-dependent figures labelled as pending.

## Command

```powershell
python -m nature_climate_ai.cli generate-figure-assets --config config/study.yaml --output-dir figures/generated --manifest figures/generated/figure_manifest.csv --report figures/generated/figure_generation_report.md
```

## Outputs

- `figures/generated/fig1_workflow.svg`: non-result workflow schematic generated from `config/study.yaml`.
- `figures/generated/figure_manifest.csv`: planned figure outputs and evidence status.
- `figures/generated/figure_generation_report.md`: readiness report.

## Rule

Fig. 1 may be used as a study-design schematic, but it cannot carry event counts, maps or performance claims until data coverage and analysis outputs exist. Fig. 2-4 must remain `RESULT_REQUIRED` until precursor-discovery, validation and FLUXNET artifacts are complete.

## 中文说明

该命令只生成 Fig. 1 的研究流程示意图和图件清单，不生成发现图、性能图或生态验证图。Fig. 2-4 必须等真实数据分析和验证完成后再生成，不能提前画出不存在的科学结果。
