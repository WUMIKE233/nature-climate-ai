# Minimum publishable evidence slice

## Purpose

Before expanding into a full Nature/Science manuscript, run a small but rigorous pilot that can falsify the central premise quickly.

## Scope

- Select two or three representative ecological regions or biomes.
- Use ERA5-Land plus MODIS EVI/NDVI as the minimum public-data stack.
- Define vegetation-stress events with quality filtering, seasonal anomaly baselines and explicit exclusion logic.
- Build 4-12 week lagged climate features.
- Compare baselines and the AI/discovery model under temporal and spatial holdout.
- Produce three evidence figures before drafting final claims.

## Pilot figures

| figure | purpose |
| --- | --- |
| Pilot Fig. 1: stress-event map | Show that event definition is ecologically plausible and spatially coherent. |
| Pilot Fig. 2: precursor pathway or lag-response | Show whether candidate climate precursors exist before vegetation stress. |
| Pilot Fig. 3: predictive validation | Show whether the model generalizes and improves over baselines. |

## Gate command

```powershell
python -m nature_climate_ai.cli generate-pilot-figures --events results/stress_events/event_catalogue_summary.csv --attribution results/modeling/feature_attribution_table.csv --lag-response results/modeling/lag_response_summary.csv --predictive results/validation/predictive_validation_summary.csv --output-dir figures/generated --manifest figures/generated/pilot_figure_manifest.csv --report figures/generated/pilot_figure_generation_report.md
python -m nature_climate_ai.cli minimum-evidence-slice --root . --output results/pilot/minimum_evidence_slice_report.md --csv results/pilot/minimum_evidence_slice_status.csv
```

The figure command generates the three pilot PNGs only when the required input artifacts exist. The gate command then checks the required stress-event, precursor, predictive-validation, robustness and pilot-figure artifacts. If any are missing, it returns `NOT_READY` and does not promote manuscript claims.

## Stop rules

- If pilot results do not beat climatology, persistence and standard climate-index baselines, do not scale to full Nature/Science drafting.
- If the precursor pattern collapses under temporal or spatial holdout, report a negative result or redesign the study.
- If event definitions are unstable across thresholds or sensors, prioritize robustness work before manuscript expansion.

## 中文审阅说明

下一步不应先把 Nature 稿写满，而应先跑出最小可验证结果切片。只有当三张 pilot 图出现强信号，并且基线、时空验证、稳健性和证伪测试都通过后，才值得扩展到全球、FLUXNET、SIF、biome 分层和机制解释。
