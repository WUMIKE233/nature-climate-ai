# Validation design

## Evidence levels

Validation must distinguish three levels:

- Prediction: which lagged climate variables predict vegetation stress at 2-12 week lead times?
- Mechanism: do the strongest precursors align with soil-moisture deficit, VPD increase, heat anomaly, precipitation deficit and compound stress physiology?
- Generalization: does the signal transfer across years, regions, biomes and sensor definitions?

## Required validation families

| family | purpose | current or planned artifact |
| --- | --- | --- |
| Temporal holdout | Test future-year generalization. | `results/validation/temporal_holdout_metrics.csv` |
| Spatial holdout | Test leave-region-out transfer. | `results/validation/spatial_holdout_metrics.csv` |
| Baseline comparison | Rule out climatology, persistence and known drought/heat indices. | `results/validation/baseline_metrics.csv` |
| Compound ablation | Test whether heat-drought interactions add value beyond single variables. | `results/validation/predictive_validation_summary.csv` |
| Uncertainty | Attach intervals to key metrics. | `results/validation/uncertainty_intervals.csv` |
| FLUXNET validation | Test ecosystem-function agreement at site scale. | `results/fluxnet/site_anomaly_metrics.csv` |
| Robustness and falsification | Stress-test thresholds, shuffled lags, biome transfer and sensor definitions. | `docs/robustness_and_falsification_plan.md` |

## Baseline minimum set

- climatology baseline,
- persistence baseline,
- SPEI or drought-index baseline,
- temperature-only model,
- precipitation-only model,
- soil-moisture-only model,
- VPD-only or atmospheric-demand baseline,
- logistic regression or linear model,
- random forest or gradient boosting,
- no-compound-interaction ablation.

## 中文审阅说明

验证不能只看一个准确率。必须证明模型不是利用季节性、上一期状态或地区差异在“投机”，并且要说明复合高温-干旱机制相对于单一变量是否真的有增益。
