"""Utility functions for BCI data processing."""

from .feature_aggregation import aggregate_temporal_features
from .normalization import (
    NormalizationParams,
    NormalizationStatus,
    estimate_normalization_params,
    apply_normalization,
    check_normalization_status,
)
from .preprocessing_diagnostics import (
    PreprocessingReport,
    diagnose_preprocessing,
    compute_fisher_score,
    rank_features_by_discriminability,
)

__all__ = [
    # Feature aggregation
    "aggregate_temporal_features",
    # Normalization
    "NormalizationParams",
    "NormalizationStatus",
    "estimate_normalization_params",
    "apply_normalization",
    "check_normalization_status",
    # Preprocessing diagnostics
    "PreprocessingReport",
    "diagnose_preprocessing",
    "compute_fisher_score",
    "rank_features_by_discriminability",
]

