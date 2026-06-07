# Known risks and mitigation

## Scientific risks

| risk | mitigation |
| --- | --- |
| The model only rediscovers known drought, heat or VPD controls. | Compare against SPEI, soil moisture, VPD, temperature-only and precipitation-only baselines; require added value from compound interactions. |
| Predictive skill reflects seasonality or persistence rather than precursor discovery. | Include climatology and persistence baselines, temporal holdout, shuffled-lag placebo tests and calibration checks. |
| Spatial transfer fails. | Use leave-region-out and biome-stratified validation; report failure regions instead of hiding them. |
| MODIS-only stress labels are too weak. | Treat MODIS EVI/NDVI as the minimum signal and plan sensor/functional cross-validation with SIF, NIRv or FLUXNET where feasible. |
| Mechanism claims overreach correlation. | Separate predictive performance, mechanistic interpretation and hypothesis generation in the manuscript. |
| Public-data access or licensing blocks reproducibility. | Record provider access routes, checksums, policy constraints and substitute access paths before making data-availability claims. |

## Editorial risks

| risk | mitigation |
| --- | --- |
| Desk rejection because the result is an AI application rather than a discovery. | Lead with recurrent climate precursor pathways and ecological mechanism, not model architecture. |
| Reviewers ask why traditional indices are insufficient. | Pre-register strong baselines and no-compound-interaction ablations. |
| The global claim is too broad for the evidence. | Run a minimum publishable evidence slice first, then scale only if the signal is strong. |

## 中文审阅说明

最大的风险不是代码不完整，而是结果可能只是在重复已知干旱指标，或只在随机拆分里表现好。每个风险都必须有对应的验证或证伪测试；失败结果也应记录。
