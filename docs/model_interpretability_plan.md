# Model interpretability plan

## Purpose

The AI model must generate testable climate-ecology hypotheses, not just high prediction scores.

## Required interpretability outputs

- ranked lagged precursor variables by region and biome,
- lag-response curves for heat, precipitation, soil moisture and VPD,
- compound-interaction summaries for heat-drought states,
- maps of where each precursor pathway is strong or weak,
- failure-case summaries for regions or biomes where the signal does not transfer.

## Interpretation guardrails

- Use "candidate precursor" until temporal and spatial holdout pass.
- Use "mechanistic interpretation" only when attribution aligns with ecological water-stress theory and alternative explanations are tested.
- Avoid causal wording unless the analysis design supports it.
- Keep attribution methods secondary to the scientific pattern; do not make the paper an AI-methods paper by default.

## 中文审阅说明

可解释性不是为了展示 SHAP 或 attention，而是为了回答“为什么这些气候前兆会导致植被胁迫”。所有解释都必须能被生态水分胁迫机制理解，并接受基线、消融和失败案例检验。
