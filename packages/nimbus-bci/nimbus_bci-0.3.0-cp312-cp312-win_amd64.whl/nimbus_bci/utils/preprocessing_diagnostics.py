"""Preprocessing diagnostics for BCI data.

This module provides tools for diagnosing preprocessing quality
and identifying potential issues before model training.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..data.contracts import BCIData


@dataclass
class PreprocessingReport:
    """Report from preprocessing diagnostics.

    Attributes
    ----------
    quality_score : float
        Overall quality score in [0, 1]. Higher is better.
    errors : list of str
        Critical issues that must be fixed.
    warnings : list of str
        Issues that may affect performance.
    recommendations : list of str
        Suggestions for improvement.
    statistics : dict
        Detailed statistics about the data.
    """

    quality_score: float
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    statistics: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if data passes minimum quality requirements."""
        return len(self.errors) == 0

    def print_report(self):
        """Print a human-readable report."""
        print(f"Preprocessing Quality Score: {self.quality_score:.1%}")
        print()

        if self.errors:
            print("ERRORS (must fix):")
            for err in self.errors:
                print(f"  ❌ {err}")
            print()

        if self.warnings:
            print("WARNINGS (may affect performance):")
            for warn in self.warnings:
                print(f"  ⚠️  {warn}")
            print()

        if self.recommendations:
            print("RECOMMENDATIONS:")
            for rec in self.recommendations:
                print(f"  💡 {rec}")


def diagnose_preprocessing(data: "BCIData") -> PreprocessingReport:
    """Run comprehensive diagnostics on BCI data.

    Checks for common preprocessing issues that can affect
    classification performance.

    Parameters
    ----------
    data : BCIData
        Data to diagnose.

    Returns
    -------
    PreprocessingReport
        Diagnostic report with errors, warnings, and recommendations.

    Examples
    --------
    >>> from nimbus_bci.data import BCIData, BCIMetadata
    >>> report = diagnose_preprocessing(bci_data)
    >>> if not report.is_valid():
    ...     report.print_report()
    ...     raise ValueError("Data quality issues detected")
    """
    errors = []
    warnings = []
    recommendations = []
    statistics = {}

    features = data.features
    n_features = data.metadata.n_features

    # Flatten for statistics
    if features.ndim == 3:
        n_samples_total = features.shape[1] * features.shape[2]
        features_flat = features.transpose(2, 1, 0).reshape(-1, n_features)
    else:
        n_samples_total = features.shape[1]
        features_flat = features.T

    # Check for NaN values
    nan_count = np.sum(np.isnan(features))
    if nan_count > 0:
        errors.append(f"Data contains {nan_count} NaN values")
    statistics["nan_count"] = int(nan_count)

    # Check for infinite values
    inf_count = np.sum(np.isinf(features))
    if inf_count > 0:
        errors.append(f"Data contains {inf_count} infinite values")
    statistics["inf_count"] = int(inf_count)

    # Check for constant features
    feature_stds = np.std(features_flat, axis=0)
    zero_var_count = np.sum(feature_stds == 0)
    if zero_var_count > 0:
        errors.append(f"{zero_var_count} features have zero variance (constant)")
    statistics["zero_variance_features"] = int(zero_var_count)

    # Check for low variance features
    low_var_threshold = 1e-6
    low_var_count = np.sum(feature_stds < low_var_threshold)
    if low_var_count > zero_var_count:
        warnings.append(
            f"{low_var_count - zero_var_count} features have very low variance"
        )
    statistics["low_variance_features"] = int(low_var_count)

    # Check for extreme values
    feature_means = np.mean(features_flat, axis=0)
    max_abs_value = np.max(np.abs(features_flat))
    statistics["max_abs_value"] = float(max_abs_value)
    statistics["mean_abs_mean"] = float(np.mean(np.abs(feature_means)))
    statistics["mean_std"] = float(np.mean(feature_stds))

    if max_abs_value > 1e6:
        errors.append(f"Extreme values detected (max={max_abs_value:.2e})")
    elif max_abs_value > 1000:
        warnings.append(
            f"Large values detected (max={max_abs_value:.2f}). Consider normalization."
        )

    # Check normalization status
    mean_abs_mean = statistics["mean_abs_mean"]
    mean_std = statistics["mean_std"]

    if mean_abs_mean > 10:
        recommendations.append(
            "Features are not centered. Consider z-score normalization."
        )
    if mean_std > 10 or mean_std < 0.1:
        recommendations.append(
            f"Features have unusual variance (mean_std={mean_std:.2f}). "
            "Consider normalization."
        )

    # Check class balance (if labels provided)
    if data.labels is not None:
        unique, counts = np.unique(data.labels, return_counts=True)
        statistics["class_counts"] = dict(zip(unique.tolist(), counts.tolist()))

        if len(unique) < data.metadata.n_classes:
            warnings.append(
                f"Only {len(unique)} of {data.metadata.n_classes} classes present in labels"
            )

        max_ratio = counts.max() / counts.min()
        if max_ratio > 5:
            warnings.append(
                f"Severe class imbalance detected (ratio={max_ratio:.1f}:1)"
            )
        elif max_ratio > 2:
            recommendations.append(
                f"Moderate class imbalance (ratio={max_ratio:.1f}:1). "
                "Consider data augmentation or class weighting."
            )

    # Check paradigm-specific recommendations
    if data.metadata.paradigm == "motor_imagery":
        if data.metadata.feature_type == "csp":
            if data.metadata.temporal_aggregation != "logvar":
                recommendations.append(
                    "For CSP features in Motor Imagery, use 'logvar' temporal aggregation."
                )
        if n_features < 8:
            recommendations.append(
                f"Low feature count ({n_features}) for Motor Imagery. "
                "Consider 8-16 CSP components."
            )

    # Calculate quality score
    score = 1.0
    score -= 0.3 * min(1.0, len(errors) / 3)  # Up to 30% penalty for errors
    score -= 0.2 * min(1.0, len(warnings) / 5)  # Up to 20% penalty for warnings
    score -= 0.1 * min(1.0, len(recommendations) / 5)  # Up to 10% for recommendations

    # Penalize for abnormal statistics
    if mean_abs_mean > 1:
        score -= 0.1 * min(1.0, mean_abs_mean / 10)
    if mean_std < 0.5 or mean_std > 5:
        score -= 0.1

    score = max(0.0, min(1.0, score))

    return PreprocessingReport(
        quality_score=score,
        errors=errors,
        warnings=warnings,
        recommendations=recommendations,
        statistics=statistics,
    )


def compute_fisher_score(
    features: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    """Compute Fisher score for each feature.

    Fisher score measures class discriminability. Higher scores
    indicate features that better separate classes.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix of shape (n_samples, n_features).
    labels : np.ndarray
        Class labels of shape (n_samples,).

    Returns
    -------
    np.ndarray
        Fisher scores of shape (n_features,).

    Examples
    --------
    >>> scores = compute_fisher_score(X, y)
    >>> top_features = np.argsort(scores)[::-1][:10]  # Top 10 features
    """
    features = np.asarray(features, dtype=np.float64)
    labels = np.asarray(labels)

    n_samples, n_features = features.shape
    classes = np.unique(labels)
    n_classes = len(classes)

    # Global mean
    global_mean = np.mean(features, axis=0)

    # Compute between-class and within-class scatter
    between_class = np.zeros(n_features)
    within_class = np.zeros(n_features)

    for c in classes:
        mask = labels == c
        class_features = features[mask]
        n_c = len(class_features)

        if n_c == 0:
            continue

        class_mean = np.mean(class_features, axis=0)
        class_var = np.var(class_features, axis=0)

        # Between-class scatter (weighted by class size)
        between_class += n_c * (class_mean - global_mean) ** 2

        # Within-class scatter
        within_class += n_c * class_var

    # Fisher score = between-class / within-class
    eps = 1e-10
    fisher_scores = between_class / (within_class + eps)

    return fisher_scores


def rank_features_by_discriminability(
    features: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    """Rank features by their discriminative power.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix of shape (n_samples, n_features).
    labels : np.ndarray
        Class labels of shape (n_samples,).

    Returns
    -------
    np.ndarray
        Feature indices sorted by discriminability (best first).

    Examples
    --------
    >>> ranking = rank_features_by_discriminability(X, y)
    >>> print(f"Best feature: {ranking[0]}")
    >>> print(f"Worst feature: {ranking[-1]}")
    """
    scores = compute_fisher_score(features, labels)
    return np.argsort(scores)[::-1]





