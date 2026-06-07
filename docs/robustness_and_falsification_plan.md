# Robustness and falsification plan

## Rationale

Top-journal reviewers will ask whether the model has discovered robust climate precursors or simply exploited seasonality, persistence, regional differences or a single vegetation index. This plan adds negative tests before final claim promotion.

## Planned analyses

```powershell
python -m nature_climate_ai.cli placebo-validation --input data/processed/modeling_dataset.csv --output results/validation/placebo_metrics.csv --report results/validation/placebo_validation.md
python -m nature_climate_ai.cli threshold-sensitivity --input data/processed/modis_anomalies.csv --output results/validation/threshold_sensitivity.csv --report results/validation/threshold_sensitivity.md
python -m nature_climate_ai.cli biome-stratified-validation --modeling data/processed/modeling_dataset.csv --biome-col biome --output results/validation/biome_metrics.csv --report results/validation/biome_validation.md
python -m nature_climate_ai.cli sensor-cross-validation --modis data/processed/modis_anomalies.csv --external data/processed/external_vegetation_anomalies.csv --output results/validation/sensor_cross_validation.csv --report results/validation/sensor_cross_validation.md
```

These commands are implemented readiness-aware modules in `src/nature_climate_ai/cli.py`. When required inputs are missing, they write `NOT_READY` reports instead of creating manuscript evidence.

## Questions answered

- Does the result survive different vegetation-stress thresholds?
- Does it disappear when climate-stress lag relationships are shuffled?
- Is the precursor pathway stable across biomes?
- Does the signal survive a different vegetation or ecosystem-function indicator?
- Is the model learning climate precursors rather than static regional identity?

## 中文审阅说明

稳健性和证伪测试不是附加装饰，而是决定结果能否从“预测相关”上升为“可信发现”的关键。若这些测试失败，应下调目标期刊或重写核心结论。
