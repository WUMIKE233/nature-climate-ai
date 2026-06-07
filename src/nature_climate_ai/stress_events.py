from __future__ import annotations

import numpy as np
import pandas as pd


def percentile_stress_events(
    values: pd.Series,
    percentile: float = 10,
    minimum_duration: int = 2,
) -> pd.Series:
    """Flag low-vegetation anomaly events without assuming a scientific result.

    The input should already be quality-filtered and anomaly-normalized for a
    single pixel, site, or region. Consecutive runs shorter than
    ``minimum_duration`` are removed.
    """
    if values.empty:
        return pd.Series(dtype=bool, index=values.index)
    if not 0 < percentile < 100:
        raise ValueError("percentile must be between 0 and 100.")
    if minimum_duration < 1:
        raise ValueError("minimum_duration must be at least 1.")

    threshold = np.nanpercentile(values.to_numpy(dtype=float), percentile)
    raw = values <= threshold
    groups = (raw != raw.shift(fill_value=False)).cumsum()
    lengths = raw.groupby(groups).transform("sum")
    return raw & (lengths >= minimum_duration)
