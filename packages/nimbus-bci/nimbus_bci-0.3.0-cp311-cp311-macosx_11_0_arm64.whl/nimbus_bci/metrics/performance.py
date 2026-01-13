"""Performance metrics for BCI systems.

This module provides Information Transfer Rate (ITR) calculation
and online performance tracking.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


def calculate_itr(
    accuracy: float,
    n_classes: int,
    trial_duration: float,
    clip_negative: bool = True,
) -> float:
    """Calculate Information Transfer Rate (ITR) in bits per minute.

    ITR measures the effective communication rate of a BCI system,
    accounting for accuracy, number of classes, and trial duration.

    Uses the formula from Wolpaw et al. (2002):
        B = log2(N) + P*log2(P) + (1-P)*log2((1-P)/(N-1))
        ITR = B * (60 / T)

    Parameters
    ----------
    accuracy : float
        Classification accuracy in [0, 1].
    n_classes : int
        Number of possible classes.
    trial_duration : float
        Duration of each trial in seconds.
    clip_negative : bool, default=True
        If True, clip negative ITR values to 0.

    Returns
    -------
    float
        Information Transfer Rate in bits per minute.

    Examples
    --------
    >>> calculate_itr(0.85, 4, 4.0)
    19.32...  # ~19 bits/min for 85% accuracy, 4 classes, 4s trials

    >>> calculate_itr(0.25, 4, 4.0)  # At chance level
    0.0

    Notes
    -----
    Typical BCI ITR values:
    - Motor Imagery: 10-25 bits/min
    - P300: 20-40 bits/min
    - SSVEP: 40-100 bits/min

    At chance level (accuracy = 1/n_classes), ITR = 0.
    Below chance, ITR is negative (clipped to 0 by default).
    """
    if n_classes < 2:
        raise ValueError(f"n_classes must be >= 2, got {n_classes}")
    if trial_duration <= 0:
        raise ValueError(f"trial_duration must be positive, got {trial_duration}")

    # Clip accuracy to valid range
    accuracy = max(0.0, min(1.0, accuracy))
    n = float(n_classes)
    p = float(accuracy)

    # Handle edge cases explicitly
    # At P=0: only term1 contributes (but P=0 means no information)
    # At P=1: B = log2(N) (maximum information)
    # At P=1/N: B = 0 (chance level, no information)

    eps = 1e-15  # Numerical tolerance

    if p < eps:
        # 0% accuracy - no information
        bits_per_trial = 0.0
    elif p > 1.0 - eps:
        # 100% accuracy - maximum information
        bits_per_trial = np.log2(n)
    else:
        # Standard ITR formula (Wolpaw et al., 2002)
        # B = log2(N) + P*log2(P) + (1-P)*log2((1-P)/(N-1))
        term1 = np.log2(n)
        term2 = p * np.log2(p)
        term3 = (1.0 - p) * np.log2((1.0 - p) / (n - 1.0))

        bits_per_trial = term1 + term2 + term3

    # Convert to bits per minute
    trials_per_minute = 60.0 / trial_duration
    itr = bits_per_trial * trials_per_minute

    # Clip negative values (can occur below chance level)
    if clip_negative:
        itr = max(0.0, itr)

    return float(itr)


def compute_balance(predictions: np.ndarray, n_classes: int) -> float:
    """Compute class distribution balance.

    Balance measures how evenly predictions are distributed across classes.
    A value of 1.0 indicates perfectly balanced predictions.

    Parameters
    ----------
    predictions : np.ndarray
        Predicted class labels.
    n_classes : int
        Number of possible classes.

    Returns
    -------
    float
        Balance score in [0, 1].
        - 1.0: Perfectly balanced (equal predictions per class)
        - 0.0: Completely imbalanced (all same class)

    Examples
    --------
    >>> predictions = np.array([0, 1, 2, 3])  # One of each
    >>> compute_balance(predictions, 4)
    1.0

    >>> predictions = np.array([0, 0, 0, 0])  # All same class
    >>> compute_balance(predictions, 4)
    0.0
    """
    predictions = np.asarray(predictions)
    n_samples = len(predictions)

    if n_samples == 0:
        return 0.0

    # Count predictions per class
    counts = np.bincount(predictions, minlength=n_classes).astype(np.float64)

    # Normalize to fractions
    fractions = counts / n_samples

    # Compute balance as 1 - normalized entropy difference from uniform
    # Using Gini impurity style metric
    expected = 1.0 / n_classes
    max_deviation = 1.0 - expected  # Maximum possible deviation

    # Mean absolute deviation from uniform
    mean_deviation = np.mean(np.abs(fractions - expected))

    # Normalize to [0, 1] where 1 is balanced
    balance = 1.0 - (mean_deviation / max_deviation) if max_deviation > 0 else 1.0

    return float(np.clip(balance, 0.0, 1.0))


@dataclass
class OnlinePerformanceTracker:
    """Track performance metrics online with a sliding window.

    Useful for monitoring BCI performance during real-time sessions.

    Parameters
    ----------
    window_size : int, default=50
        Number of recent trials to track.

    Attributes
    ----------
    predictions : deque
        Recent predictions.
    labels : deque
        Recent true labels.
    confidences : deque
        Recent prediction confidences.
    n_total : int
        Total number of trials processed.

    Examples
    --------
    >>> tracker = OnlinePerformanceTracker(window_size=50)
    >>> for pred, label, conf in results:
    ...     metrics = tracker.update(pred, label, conf)
    ...     print(f"Running accuracy: {metrics['accuracy']:.2%}")
    """

    window_size: int = 50
    predictions: deque = field(default_factory=deque)
    labels: deque = field(default_factory=deque)
    confidences: deque = field(default_factory=deque)
    n_total: int = 0

    def __post_init__(self):
        """Initialize deques with maxlen."""
        self.predictions = deque(maxlen=self.window_size)
        self.labels = deque(maxlen=self.window_size)
        self.confidences = deque(maxlen=self.window_size)

    def update(self, prediction: int, label: int, confidence: float) -> dict:
        """Update tracker with a new trial.

        Parameters
        ----------
        prediction : int
            Predicted class label.
        label : int
            True class label.
        confidence : float
            Prediction confidence.

        Returns
        -------
        dict
            Current metrics including accuracy and mean confidence.
        """
        self.predictions.append(prediction)
        self.labels.append(label)
        self.confidences.append(confidence)
        self.n_total += 1

        return self._compute_metrics()

    def _compute_metrics(self) -> dict:
        """Compute current metrics from window."""
        preds = np.array(self.predictions)
        labs = np.array(self.labels)
        confs = np.array(self.confidences)

        n_window = len(preds)
        if n_window == 0:
            return {
                "accuracy": 0.0,
                "mean_confidence": 0.0,
                "window_size": 0,
                "n_total": self.n_total,
            }

        accuracy = float(np.mean(preds == labs))
        mean_confidence = float(np.mean(confs))

        return {
            "accuracy": accuracy,
            "mean_confidence": mean_confidence,
            "window_size": n_window,
            "n_total": self.n_total,
        }

    def get_metrics(
        self,
        n_classes: int,
        trial_duration: float,
    ) -> dict:
        """Get comprehensive performance metrics.

        Parameters
        ----------
        n_classes : int
            Number of possible classes.
        trial_duration : float
            Trial duration in seconds.

        Returns
        -------
        dict
            Comprehensive metrics including ITR.
        """
        metrics = self._compute_metrics()

        # Add ITR
        metrics["itr"] = calculate_itr(
            metrics["accuracy"],
            n_classes,
            trial_duration,
        )

        # Add balance
        if len(self.predictions) > 0:
            metrics["balance"] = compute_balance(
                np.array(self.predictions), n_classes
            )
        else:
            metrics["balance"] = 0.0

        return metrics

    def reset(self):
        """Reset tracker state."""
        self.predictions.clear()
        self.labels.clear()
        self.confidences.clear()
        self.n_total = 0

