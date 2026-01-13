"""Quality assessment for BCI trials.

This module provides functions for assessing trial quality
and deciding whether to accept or reject predictions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class TrialQuality:
    """Quality assessment result for a single trial.

    Attributes
    ----------
    is_valid : bool
        Whether the trial passes quality criteria.
    confidence : float
        Prediction confidence.
    rejection_reason : str or None
        Reason for rejection, or None if valid.
    entropy : float or None
        Prediction entropy in bits.
    outlier_score : float or None
        Mahalanobis-based outlier score.
    """

    is_valid: bool
    confidence: float
    rejection_reason: Optional[str] = None
    entropy: Optional[float] = None
    outlier_score: Optional[float] = None


def assess_trial_quality(
    features: np.ndarray,
    confidence: float,
    confidence_threshold: float = 0.6,
    outlier_threshold: float = 5.0,
    entropy: Optional[float] = None,
    outlier_score: Optional[float] = None,
    entropy_threshold: float = 1.5,
) -> TrialQuality:
    """Assess quality of a BCI trial prediction.

    Evaluates multiple quality criteria to determine if a prediction
    should be accepted or rejected.

    Parameters
    ----------
    features : np.ndarray
        Trial features (used for artifact detection).
    confidence : float
        Prediction confidence in [0, 1].
    confidence_threshold : float, default=0.6
        Minimum confidence for accepting prediction.
    outlier_threshold : float, default=5.0
        Maximum outlier score for accepting prediction.
    entropy : float or None, optional
        Prediction entropy in bits.
    outlier_score : float or None, optional
        Mahalanobis-based outlier score.
    entropy_threshold : float, default=1.5
        Maximum entropy for accepting prediction.

    Returns
    -------
    TrialQuality
        Quality assessment result.

    Examples
    --------
    >>> features = np.random.randn(16, 250)
    >>> quality = assess_trial_quality(features, confidence=0.85)
    >>> if quality.is_valid:
    ...     print("Trial accepted")
    ... else:
    ...     print(f"Rejected: {quality.rejection_reason}")
    """
    features = np.asarray(features)

    # Check for NaN/Inf in features
    if np.any(np.isnan(features)):
        return TrialQuality(
            is_valid=False,
            confidence=confidence,
            rejection_reason="features_contain_nan",
            entropy=entropy,
            outlier_score=outlier_score,
        )

    if np.any(np.isinf(features)):
        return TrialQuality(
            is_valid=False,
            confidence=confidence,
            rejection_reason="features_contain_inf",
            entropy=entropy,
            outlier_score=outlier_score,
        )

    # Check confidence
    if confidence < confidence_threshold:
        return TrialQuality(
            is_valid=False,
            confidence=confidence,
            rejection_reason="low_confidence",
            entropy=entropy,
            outlier_score=outlier_score,
        )

    # Check outlier score if provided
    if outlier_score is not None and outlier_score > outlier_threshold:
        return TrialQuality(
            is_valid=False,
            confidence=confidence,
            rejection_reason="outlier_detected",
            entropy=entropy,
            outlier_score=outlier_score,
        )

    # Check entropy if provided
    if entropy is not None and entropy > entropy_threshold:
        return TrialQuality(
            is_valid=False,
            confidence=confidence,
            rejection_reason="high_uncertainty",
            entropy=entropy,
            outlier_score=outlier_score,
        )

    # All checks passed
    return TrialQuality(
        is_valid=True,
        confidence=confidence,
        rejection_reason=None,
        entropy=entropy,
        outlier_score=outlier_score,
    )


def should_reject_trial(confidence: float, threshold: float = 0.7) -> bool:
    """Simple check for trial rejection based on confidence.

    Parameters
    ----------
    confidence : float
        Prediction confidence in [0, 1].
    threshold : float, default=0.7
        Minimum confidence for accepting prediction.

    Returns
    -------
    bool
        True if trial should be rejected (confidence below threshold).

    Examples
    --------
    >>> if should_reject_trial(0.65, threshold=0.7):
    ...     print("Low confidence - trial rejected")
    Low confidence - trial rejected
    """
    return confidence < threshold


def compute_quality_rate(
    confidences: np.ndarray,
    threshold: float = 0.7,
    entropies: Optional[np.ndarray] = None,
    entropy_threshold: float = 1.5,
    outlier_scores: Optional[np.ndarray] = None,
    outlier_threshold: float = 5.0,
) -> float:
    """Compute the fraction of trials that pass quality criteria.

    Parameters
    ----------
    confidences : np.ndarray
        Prediction confidences of shape (n_trials,).
    threshold : float, default=0.7
        Minimum confidence threshold.
    entropies : np.ndarray or None, optional
        Prediction entropies of shape (n_trials,).
    entropy_threshold : float, default=1.5
        Maximum entropy threshold.
    outlier_scores : np.ndarray or None, optional
        Outlier scores of shape (n_trials,).
    outlier_threshold : float, default=5.0
        Maximum outlier score threshold.

    Returns
    -------
    float
        Fraction of trials passing all criteria.

    Examples
    --------
    >>> confidences = np.array([0.9, 0.8, 0.6, 0.4])
    >>> compute_quality_rate(confidences, threshold=0.7)
    0.5  # 2 out of 4 trials pass
    """
    confidences = np.asarray(confidences)
    n_trials = len(confidences)

    if n_trials == 0:
        return 0.0

    # Start with confidence mask
    quality_mask = confidences >= threshold

    # Add entropy criterion if provided
    if entropies is not None:
        entropies = np.asarray(entropies)
        quality_mask &= entropies <= entropy_threshold

    # Add outlier criterion if provided
    if outlier_scores is not None:
        outlier_scores = np.asarray(outlier_scores)
        quality_mask &= outlier_scores <= outlier_threshold

    return float(np.mean(quality_mask))

