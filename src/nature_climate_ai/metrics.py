from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BinaryEventMetrics:
    precision: float
    recall: float
    false_alarm_rate: float
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int


def binary_event_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> BinaryEventMetrics:
    """Compute simple event metrics without requiring scikit-learn."""
    truth = np.asarray(y_true, dtype=bool)
    pred = np.asarray(y_pred, dtype=bool)
    if truth.shape != pred.shape:
        raise ValueError("y_true and y_pred must have the same shape.")

    true_positive = np.logical_and(truth, pred).sum()
    false_positive = np.logical_and(~truth, pred).sum()
    false_negative = np.logical_and(truth, ~pred).sum()
    true_negative = np.logical_and(~truth, ~pred).sum()

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    false_alarm_rate = false_positive / (false_positive + true_negative) if false_positive + true_negative else 0.0
    return BinaryEventMetrics(
        precision=float(precision),
        recall=float(recall),
        false_alarm_rate=float(false_alarm_rate),
        true_positive=int(true_positive),
        false_positive=int(false_positive),
        false_negative=int(false_negative),
        true_negative=int(true_negative),
    )
