"""Diagnostic metrics for BCI inference.

This module provides entropy-based uncertainty quantification
and Mahalanobis distance-based outlier detection.
"""

from __future__ import annotations

import numpy as np


def compute_entropy(posterior: np.ndarray, eps: float = 1e-10) -> float:
    """Compute Shannon entropy of a probability distribution.

    Entropy measures prediction uncertainty in bits. Lower entropy
    indicates more confident predictions.

    Parameters
    ----------
    posterior : np.ndarray
        Probability distribution (must sum to 1).
        Shape (n_classes,) for single trial or (n_trials, n_classes).
    eps : float, default=1e-10
        Small constant for numerical stability.

    Returns
    -------
    float
        Shannon entropy in bits.
        - 0 bits = completely certain (one class has probability 1)
        - log2(n_classes) = maximum uncertainty (uniform distribution)

    Examples
    --------
    >>> posterior = np.array([0.9, 0.05, 0.05])
    >>> compute_entropy(posterior)
    0.569...  # Low entropy = high confidence

    >>> uniform = np.array([0.25, 0.25, 0.25, 0.25])
    >>> compute_entropy(uniform)
    2.0  # Maximum entropy for 4 classes
    """
    posterior = np.asarray(posterior, dtype=np.float64)

    if posterior.ndim == 1:
        # Single distribution
        p = np.clip(posterior, eps, 1.0)
        return float(-np.sum(p * np.log2(p)))
    else:
        # Multiple distributions - return mean
        p = np.clip(posterior, eps, 1.0)
        entropies = -np.sum(p * np.log2(p), axis=-1)
        return float(np.mean(entropies))


def compute_entropy_batch(posteriors: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """Compute Shannon entropy for each row of a posterior matrix.

    Parameters
    ----------
    posteriors : np.ndarray
        Posterior matrix of shape (n_samples, n_classes).
    eps : float, default=1e-10
        Small constant for numerical stability.

    Returns
    -------
    np.ndarray
        Entropy values of shape (n_samples,).
    """
    posteriors = np.asarray(posteriors, dtype=np.float64)
    p = np.clip(posteriors, eps, 1.0)
    return -np.sum(p * np.log2(p), axis=1)


def compute_mahalanobis_distances(
    features: np.ndarray,
    class_means: list[np.ndarray],
    precision_matrices: list[np.ndarray],
) -> np.ndarray:
    """Compute Mahalanobis distance from each sample to each class center.

    Mahalanobis distance accounts for class-specific covariance structure,
    making it more principled than Euclidean distance for outlier detection.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix of shape (n_samples, n_features).
    class_means : list of np.ndarray
        Mean vector for each class, each of shape (n_features,).
    precision_matrices : list of np.ndarray
        Precision matrix (inverse covariance) for each class,
        each of shape (n_features, n_features).

    Returns
    -------
    np.ndarray
        Distance matrix of shape (n_samples, n_classes).
        Entry [i, k] is the Mahalanobis distance from sample i to class k.

    Examples
    --------
    >>> features = np.array([[1.0, 2.0], [3.0, 4.0]])
    >>> means = [np.array([0.0, 0.0]), np.array([3.0, 3.0])]
    >>> precisions = [np.eye(2), np.eye(2)]
    >>> distances = compute_mahalanobis_distances(features, means, precisions)
    >>> distances.shape
    (2, 2)

    Notes
    -----
    For LDA models with shared covariance, pass the same precision matrix
    for all classes.

    Interpretation of distances:
    - < 3.0: Normal (within ~3 standard deviations)
    - 3.0-5.0: Potential outlier
    - > 5.0: Likely outlier
    """
    features = np.asarray(features, dtype=np.float64)
    n_samples = features.shape[0]
    n_classes = len(class_means)

    distances = np.zeros((n_samples, n_classes), dtype=np.float64)

    for k in range(n_classes):
        mu = class_means[k]
        prec = precision_matrices[k]

        # Center features
        centered = features - mu  # (n_samples, n_features)

        # Compute quadratic form: x^T @ Precision @ x
        # = sum_j (centered @ prec)_j * centered_j
        transformed = centered @ prec  # (n_samples, n_features)
        quad_form = np.sum(transformed * centered, axis=1)  # (n_samples,)

        # Mahalanobis distance is sqrt of quadratic form
        distances[:, k] = np.sqrt(np.maximum(quad_form, 0.0))

    return distances


def compute_outlier_scores(mahalanobis_distances: np.ndarray) -> np.ndarray:
    """Compute outlier scores from Mahalanobis distances.

    The outlier score is the minimum distance to any class center.
    Higher scores indicate the sample is far from all known classes.

    Parameters
    ----------
    mahalanobis_distances : np.ndarray
        Distance matrix of shape (n_samples, n_classes).

    Returns
    -------
    np.ndarray
        Outlier scores of shape (n_samples,).

    Examples
    --------
    >>> distances = np.array([[1.0, 5.0], [4.0, 3.5]])
    >>> compute_outlier_scores(distances)
    array([1.0, 3.5])  # Minimum distance to any class

    Notes
    -----
    Interpretation:
    - < 3.0: Sample is close to at least one class center
    - 3.0-5.0: Sample is moderately far from all classes
    - > 5.0: Sample is far from all classes (likely outlier)
    """
    return np.min(mahalanobis_distances, axis=1)

