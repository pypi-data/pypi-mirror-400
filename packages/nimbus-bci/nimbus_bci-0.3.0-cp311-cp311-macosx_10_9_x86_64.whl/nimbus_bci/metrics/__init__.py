"""Metrics and diagnostics for BCI inference."""

from .diagnostics import (
    compute_entropy,
    compute_mahalanobis_distances,
    compute_outlier_scores,
)
from .calibration import (
    CalibrationMetrics,
    compute_calibration_metrics,
)
from .performance import (
    calculate_itr,
    compute_balance,
    OnlinePerformanceTracker,
)
from .quality import (
    TrialQuality,
    assess_trial_quality,
    should_reject_trial,
)

__all__ = [
    # Diagnostics
    "compute_entropy",
    "compute_mahalanobis_distances",
    "compute_outlier_scores",
    # Calibration
    "CalibrationMetrics",
    "compute_calibration_metrics",
    # Performance
    "calculate_itr",
    "compute_balance",
    "OnlinePerformanceTracker",
    # Quality
    "TrialQuality",
    "assess_trial_quality",
    "should_reject_trial",
]

