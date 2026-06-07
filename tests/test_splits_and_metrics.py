import numpy as np
import pandas as pd

from nature_climate_ai.metrics import binary_event_metrics
from nature_climate_ai.splits import build_temporal_split, label_year_split


def test_temporal_split_uses_configured_holdout() -> None:
    split = build_temporal_split(list(range(2001, 2026)), (2021, 2025))
    assert split.holdout_years == (2021, 2022, 2023, 2024, 2025)
    assert 2020 in split.train_years


def test_label_year_split_marks_holdout_dates() -> None:
    dates = pd.Series(pd.to_datetime(["2020-01-01", "2022-01-01"]))
    labels = label_year_split(dates, (2021, 2025))
    assert labels.tolist() == ["train", "holdout"]


def test_binary_event_metrics() -> None:
    metrics = binary_event_metrics(
        np.array([True, True, False, False]),
        np.array([True, False, True, False]),
    )
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.false_alarm_rate == 0.5
