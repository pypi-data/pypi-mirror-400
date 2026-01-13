"""Feature aggregation utilities for temporal dimension reduction.

This module provides methods for aggregating temporal features
from BCI data into single feature vectors per trial.
"""

from __future__ import annotations

import numpy as np


def aggregate_temporal_features(
    features: np.ndarray,
    method: str = "mean",
    eps: float = 1e-10,
) -> np.ndarray:
    """Aggregate temporal dimension of features into a single vector.

    This function reduces (n_features, n_samples) to (n_features,) by
    aggregating across the time dimension using the specified method.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix of shape (n_features, n_samples).
    method : str, default="mean"
        Aggregation method. One of:
        - "mean": Mean across time (default, general purpose)
        - "logvar": Log-variance (recommended for CSP features in Motor Imagery)
        - "last": Last time sample
        - "max": Maximum value across time
        - "median": Median across time
        - "var": Variance across time
        - "std": Standard deviation across time
    eps : float, default=1e-10
        Small constant for numerical stability in log operations.

    Returns
    -------
    np.ndarray
        Aggregated features of shape (n_features,).

    Raises
    ------
    ValueError
        If method is not recognized or features has wrong shape.

    Examples
    --------
    >>> features = np.random.randn(16, 250)  # 16 CSP features, 250 samples
    >>> aggregated = aggregate_temporal_features(features, method="logvar")
    >>> aggregated.shape
    (16,)

    Notes
    -----
    For Motor Imagery with CSP features, "logvar" is strongly recommended
    as CSP discriminates based on variance in the spatial filters.

    For P300 with ERP features, "mean" or "max" may be more appropriate.

    For SSVEP, "mean" or frequency-specific aggregation is typical.
    """
    features = np.asarray(features, dtype=np.float64)

    if features.ndim != 2:
        raise ValueError(
            f"features must be 2D (n_features, n_samples), got {features.ndim}D"
        )

    n_features, n_samples = features.shape

    if n_samples == 0:
        raise ValueError("features has 0 samples")

    method = method.lower()

    if method == "mean":
        return np.mean(features, axis=1)

    elif method == "logvar":
        # Log-variance: log(var + eps)
        # Critical for CSP features in Motor Imagery
        var = np.var(features, axis=1)
        return np.log(var + eps)

    elif method == "var":
        return np.var(features, axis=1)

    elif method == "std":
        return np.std(features, axis=1)

    elif method == "last":
        return features[:, -1]

    elif method == "max":
        return np.max(features, axis=1)

    elif method == "median":
        return np.median(features, axis=1)

    else:
        valid_methods = {"mean", "logvar", "var", "std", "last", "max", "median"}
        raise ValueError(
            f"Unknown aggregation method '{method}'. "
            f"Valid methods: {valid_methods}"
        )


def get_recommended_aggregation(paradigm: str, feature_type: str) -> str:
    """Get recommended temporal aggregation method for a paradigm/feature combination.

    The recommendation prioritizes feature_type over paradigm, since the
    optimal aggregation depends on what the features represent.

    Parameters
    ----------
    paradigm : str
        BCI paradigm ("motor_imagery", "p300", "ssvep", "erp").
    feature_type : str
        Feature type ("csp", "bandpower", "raw", "erp_amplitude").

    Returns
    -------
    str
        Recommended aggregation method.

    Examples
    --------
    >>> get_recommended_aggregation("motor_imagery", "csp")
    'logvar'

    >>> get_recommended_aggregation("p300", "erp_amplitude")
    'mean'

    >>> get_recommended_aggregation("motor_imagery", "raw")
    'var'  # Not logvar - raw channels need variance, not log-variance
    """
    # Feature type takes priority - this determines what the values represent
    feature_recommendations = {
        "csp": "logvar",  # CSP filters - log-variance is mathematically correct
        "bandpower": "mean",  # Already power values - just average
        "erp_amplitude": "mean",  # ERP amplitudes - average across time
    }

    if feature_type in feature_recommendations:
        return feature_recommendations[feature_type]

    # For raw/custom features, use paradigm-specific defaults
    paradigm_recommendations = {
        "motor_imagery": "var",  # ERD/ERS based on variance changes
        "p300": "mean",  # Average ERP amplitude
        "ssvep": "mean",  # Average power at target frequency
        "erp": "mean",  # Average ERP amplitude
        "custom": "mean",  # Safe default
    }

    return paradigm_recommendations.get(paradigm, "mean")


def validate_aggregation_choice(
    paradigm: str,
    feature_type: str,
    aggregation: str,
) -> bool:
    """Validate that aggregation method is appropriate for the data.

    Parameters
    ----------
    paradigm : str
        BCI paradigm.
    feature_type : str
        Feature type.
    aggregation : str
        Chosen aggregation method.

    Returns
    -------
    bool
        True if valid (always returns True, but may print warnings).

    Warnings
    --------
    Prints warning if CSP features are not using logvar aggregation.
    """
    import warnings

    # Warn if CSP features are not using logvar
    if feature_type == "csp" and aggregation != "logvar":
        warnings.warn(
            f"CSP features typically use 'logvar' aggregation, but '{aggregation}' "
            "was specified. This may reduce classification accuracy. "
            "Consider using 'logvar' for Motor Imagery CSP features.",
            UserWarning,
            stacklevel=2,
        )

    return True

