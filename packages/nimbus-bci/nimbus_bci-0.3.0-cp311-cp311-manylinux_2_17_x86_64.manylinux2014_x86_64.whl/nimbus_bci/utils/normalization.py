"""Normalization utilities for BCI features.

This module provides feature normalization methods critical for
cross-session BCI performance. EEG amplitude varies 50-200% across
sessions due to electrode impedance, skin conductance, and user state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


NormalizationMethod = Literal["zscore", "minmax", "robust"]


@dataclass(frozen=True)
class NormalizationParams:
    """Parameters for feature normalization.

    Store these parameters with your model to apply consistent
    normalization during inference.

    Attributes
    ----------
    method : str
        Normalization method ("zscore", "minmax", "robust").
    center : np.ndarray
        Centering values (mean, min, or median depending on method).
        Shape (n_features,).
    scale : np.ndarray
        Scaling values (std, range, or MAD depending on method).
        Shape (n_features,).
    """

    method: str
    center: np.ndarray
    scale: np.ndarray

    def __post_init__(self):
        """Validate parameters."""
        if len(self.center) != len(self.scale):
            raise ValueError(
                f"center and scale must have same length, "
                f"got {len(self.center)} and {len(self.scale)}"
            )

        valid_methods = {"zscore", "minmax", "robust"}
        if self.method not in valid_methods:
            raise ValueError(
                f"method must be one of {valid_methods}, got '{self.method}'"
            )


@dataclass
class NormalizationStatus:
    """Status report for feature normalization.

    Attributes
    ----------
    appears_normalized : bool
        Whether features appear to be already normalized.
    mean_abs_mean : float
        Mean of absolute feature means.
    mean_std : float
        Mean of feature standard deviations.
    recommendations : list of str
        Recommendations for normalization.
    """

    appears_normalized: bool
    mean_abs_mean: float
    mean_std: float
    recommendations: list


def estimate_normalization_params(
    features: np.ndarray,
    method: str = "zscore",
) -> NormalizationParams:
    """Estimate normalization parameters from training data.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix of shape (n_samples, n_features) or
        (n_features, n_samples, n_trials).
    method : str, default="zscore"
        Normalization method:
        - "zscore": Mean=0, Std=1 (recommended for most BCI)
        - "minmax": Scale to [0, 1] (for bounded features)
        - "robust": Uses median/MAD (resistant to artifacts)

    Returns
    -------
    NormalizationParams
        Parameters to use for normalization.

    Examples
    --------
    >>> # Training: estimate params
    >>> params = estimate_normalization_params(X_train, method="zscore")
    >>> X_train_norm = apply_normalization(X_train, params)

    >>> # Inference: use same params
    >>> X_test_norm = apply_normalization(X_test, params)

    Notes
    -----
    Always use training data to estimate parameters.
    Apply the SAME parameters to test/inference data.
    """
    features = np.asarray(features, dtype=np.float64)

    # Handle 3D input (n_features, n_samples, n_trials) -> (n_samples_total, n_features)
    if features.ndim == 3:
        n_features, n_samples, n_trials = features.shape
        # Reshape to (n_samples_total, n_features)
        features = features.transpose(2, 1, 0).reshape(-1, n_features)
    elif features.ndim == 2:
        # Assume (n_samples, n_features)
        pass
    else:
        raise ValueError(f"features must be 2D or 3D, got {features.ndim}D")

    method = method.lower()
    eps = 1e-10

    if method == "zscore":
        center = np.mean(features, axis=0)
        scale = np.std(features, axis=0)
        scale = np.where(scale < eps, 1.0, scale)  # Avoid division by zero

    elif method == "minmax":
        center = np.min(features, axis=0)
        feature_max = np.max(features, axis=0)
        scale = feature_max - center
        scale = np.where(scale < eps, 1.0, scale)

    elif method == "robust":
        # Robust: median and MAD (median absolute deviation)
        center = np.median(features, axis=0)
        mad = np.median(np.abs(features - center), axis=0)
        # Scale MAD to approximate std for normal distribution
        scale = mad * 1.4826
        scale = np.where(scale < eps, 1.0, scale)

    else:
        valid_methods = {"zscore", "minmax", "robust"}
        raise ValueError(
            f"method must be one of {valid_methods}, got '{method}'"
        )

    return NormalizationParams(
        method=method,
        center=center,
        scale=scale,
    )


def apply_normalization(
    features: np.ndarray,
    params: NormalizationParams,
) -> np.ndarray:
    """Apply normalization using pre-computed parameters.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix of shape (n_samples, n_features) or
        (n_features, n_samples, n_trials).
    params : NormalizationParams
        Parameters from estimate_normalization_params.

    Returns
    -------
    np.ndarray
        Normalized features with same shape as input.

    Examples
    --------
    >>> params = estimate_normalization_params(X_train)
    >>> X_train_norm = apply_normalization(X_train, params)
    >>> X_test_norm = apply_normalization(X_test, params)  # Same params!
    """
    features = np.asarray(features, dtype=np.float64)
    original_shape = features.shape

    # Handle 3D input
    if features.ndim == 3:
        n_features, n_samples, n_trials = features.shape
        # Reshape to (n_samples_total, n_features)
        features = features.transpose(2, 1, 0).reshape(-1, n_features)
        was_3d = True
    else:
        was_3d = False

    # Check feature count
    if features.shape[1] != len(params.center):
        raise ValueError(
            f"features has {features.shape[1]} features, "
            f"but params expects {len(params.center)}"
        )

    # Apply normalization
    normalized = (features - params.center) / params.scale

    # Restore original shape if needed
    if was_3d:
        n_features = original_shape[0]
        n_samples = original_shape[1]
        n_trials = original_shape[2]
        normalized = normalized.reshape(n_trials, n_samples, n_features)
        normalized = normalized.transpose(2, 1, 0)

    return normalized


def check_normalization_status(features: np.ndarray) -> NormalizationStatus:
    """Check if features appear to be normalized.

    Useful for diagnosing preprocessing issues.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix.

    Returns
    -------
    NormalizationStatus
        Status and recommendations.

    Examples
    --------
    >>> status = check_normalization_status(features)
    >>> if not status.appears_normalized:
    ...     for rec in status.recommendations:
    ...         print(f"  - {rec}")
    """
    features = np.asarray(features, dtype=np.float64)

    # Handle 3D input
    if features.ndim == 3:
        n_features = features.shape[0]
        features = features.transpose(2, 1, 0).reshape(-1, n_features)

    # Compute statistics
    feature_means = np.mean(features, axis=0)
    feature_stds = np.std(features, axis=0)

    mean_abs_mean = float(np.mean(np.abs(feature_means)))
    mean_std = float(np.mean(feature_stds))

    recommendations = []

    # Check if already normalized (approximately)
    is_centered = mean_abs_mean < 0.5
    is_scaled = 0.5 < mean_std < 2.0

    if not is_centered:
        recommendations.append(
            f"Features not centered (mean_abs_mean={mean_abs_mean:.2f}). "
            "Consider z-score normalization."
        )

    if mean_std < 0.1:
        recommendations.append(
            f"Features have very low variance (mean_std={mean_std:.4f}). "
            "Check for constant features or scaling issues."
        )
    elif mean_std > 10.0:
        recommendations.append(
            f"Features have high variance (mean_std={mean_std:.2f}). "
            "Consider normalization to improve numerical stability."
        )

    # Check for extreme values
    max_val = np.max(np.abs(features))
    if max_val > 1000:
        recommendations.append(
            f"Features contain extreme values (max={max_val:.2f}). "
            "Consider robust normalization or outlier removal."
        )

    appears_normalized = is_centered and is_scaled and len(recommendations) == 0

    return NormalizationStatus(
        appears_normalized=appears_normalized,
        mean_abs_mean=mean_abs_mean,
        mean_std=mean_std,
        recommendations=recommendations,
    )





