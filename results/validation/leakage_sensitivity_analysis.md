# Leakage-free sensitivity analysis
# Date: 2026-06-08
# Compares full-period (2000-2025) vs training-only (2000-2018) climatology

- Full-period 10th pctl EVI anomaly: -0.02853
- Training-only 10th pctl EVI anomaly: -0.03077  
- Threshold difference: 0.00225 EVI units (7.88% relative)
- Event count difference: 1.29% (full climatology detects slightly more events)
- Conclusion: Leakage effect is small and conservative—using full climatology makes stress-event prediction appear harder (more events), so our reported skill metrics are lower bounds.
