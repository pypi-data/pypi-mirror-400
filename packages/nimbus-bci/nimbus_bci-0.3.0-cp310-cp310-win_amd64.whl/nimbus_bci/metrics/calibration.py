"""Calibration metrics for classifier confidence.

This module provides Expected Calibration Error (ECE) and
Maximum Calibration Error (MCE) for assessing confidence calibration.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CalibrationMetrics:
    """Calibration metrics for classifier confidence.

    Measures alignment between predicted confidence and actual accuracy.
    A well-calibrated classifier should have confidence close to accuracy.

    Attributes
    ----------
    ece : float
        Expected Calibration Error. Weighted average of calibration
        error across bins. Target: < 0.10 for well-calibrated models.
    mce : float
        Maximum Calibration Error. Worst-case calibration error
        across all bins.
    n_bins : int
        Number of bins used for calibration computation.
    bin_accuracies : np.ndarray
        Accuracy in each confidence bin.
    bin_confidences : np.ndarray
        Mean confidence in each confidence bin.
    bin_counts : np.ndarray
        Number of samples in each bin.
    """

    ece: float
    mce: float
    n_bins: int
    bin_accuracies: np.ndarray
    bin_confidences: np.ndarray
    bin_counts: np.ndarray

    def is_well_calibrated(self, threshold: float = 0.10) -> bool:
        """Check if model is well-calibrated.

        Parameters
        ----------
        threshold : float, default=0.10
            ECE threshold for well-calibrated model.

        Returns
        -------
        bool
            True if ECE < threshold.
        """
        return self.ece < threshold


def compute_calibration_metrics(
    predictions: np.ndarray,
    confidences: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 10,
) -> CalibrationMetrics:
    """Compute calibration metrics (ECE and MCE).

    Expected Calibration Error (ECE) measures the average difference
    between confidence and accuracy, weighted by bin size.

    Maximum Calibration Error (MCE) is the largest calibration error
    in any bin.

    Parameters
    ----------
    predictions : np.ndarray
        Predicted class labels of shape (n_samples,).
    confidences : np.ndarray
        Prediction confidences of shape (n_samples,).
        Should be in [0, 1].
    labels : np.ndarray
        True class labels of shape (n_samples,).
    n_bins : int, default=10
        Number of bins for confidence bucketing.

    Returns
    -------
    CalibrationMetrics
        Calibration metrics including ECE and MCE.

    Examples
    --------
    >>> predictions = np.array([0, 1, 1, 0])
    >>> confidences = np.array([0.9, 0.8, 0.7, 0.6])
    >>> labels = np.array([0, 1, 0, 0])
    >>> metrics = compute_calibration_metrics(predictions, confidences, labels)
    >>> print(f"ECE: {metrics.ece:.3f}")
    ECE: 0.175

    Notes
    -----
    Interpretation:
    - ECE < 0.05: Excellent calibration
    - ECE < 0.10: Good calibration
    - ECE < 0.15: Acceptable calibration
    - ECE >= 0.15: Poor calibration, consider recalibration
    """
    predictions = np.asarray(predictions)
    confidences = np.asarray(confidences, dtype=np.float64)
    labels = np.asarray(labels)

    n_samples = len(predictions)
    if n_samples == 0:
        return CalibrationMetrics(
            ece=0.0,
            mce=0.0,
            n_bins=n_bins,
            bin_accuracies=np.zeros(n_bins),
            bin_confidences=np.zeros(n_bins),
            bin_counts=np.zeros(n_bins, dtype=np.int64),
        )

    # Create bins
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_accuracies = np.zeros(n_bins)
    bin_confidences = np.zeros(n_bins)
    bin_counts = np.zeros(n_bins, dtype=np.int64)

    for i in range(n_bins):
        lower = bin_boundaries[i]
        upper = bin_boundaries[i + 1]

        # Include upper boundary for last bin
        if i == n_bins - 1:
            mask = (confidences >= lower) & (confidences <= upper)
        else:
            mask = (confidences >= lower) & (confidences < upper)

        bin_counts[i] = np.sum(mask)

        if bin_counts[i] > 0:
            bin_accuracies[i] = np.mean(predictions[mask] == labels[mask])
            bin_confidences[i] = np.mean(confidences[mask])

    # Compute ECE (weighted average of calibration errors)
    weights = bin_counts / n_samples
    calibration_errors = np.abs(bin_accuracies - bin_confidences)
    ece = float(np.sum(weights * calibration_errors))

    # Compute MCE (maximum calibration error across non-empty bins)
    non_empty = bin_counts > 0
    if np.any(non_empty):
        mce = float(np.max(calibration_errors[non_empty]))
    else:
        mce = 0.0

    return CalibrationMetrics(
        ece=ece,
        mce=mce,
        n_bins=n_bins,
        bin_accuracies=bin_accuracies,
        bin_confidences=bin_confidences,
        bin_counts=bin_counts,
    )

