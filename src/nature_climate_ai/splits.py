from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TemporalSplit:
    train_years: tuple[int, ...]
    holdout_years: tuple[int, ...]


def build_temporal_split(years: list[int] | tuple[int, ...], holdout_range: tuple[int, int]) -> TemporalSplit:
    """Build a leakage-aware year split from configured study years."""
    start, end = holdout_range
    holdout = tuple(year for year in years if start <= year <= end)
    train = tuple(year for year in years if year < start or year > end)
    if not holdout:
        raise ValueError("Temporal holdout range does not overlap supplied years.")
    if not train:
        raise ValueError("Temporal split leaves no training years.")
    return TemporalSplit(train_years=train, holdout_years=holdout)


def label_year_split(dates: pd.Series, holdout_range: tuple[int, int]) -> pd.Series:
    years = pd.to_datetime(dates).dt.year
    start, end = holdout_range
    return pd.Series(
        ["holdout" if start <= year <= end else "train" for year in years],
        index=dates.index,
        dtype="string",
    )
