"""Nimbus BCI SDK: Bayesian classifiers for BCI applications.

This SDK provides sklearn-compatible Bayesian classifiers with
support for streaming inference, online learning, and rich diagnostics.

Examples
--------
Basic usage with sklearn-compatible API:

>>> from nimbus_bci import NimbusLDA
>>> clf = NimbusLDA()
>>> clf.fit(X_train, y_train)
>>> predictions = clf.predict(X_test)

Using with sklearn pipelines:

>>> from sklearn.pipeline import make_pipeline
>>> from sklearn.preprocessing import StandardScaler
>>> pipe = make_pipeline(StandardScaler(), NimbusLDA())
>>> pipe.fit(X_train, y_train)

Streaming inference:

>>> from nimbus_bci.inference import StreamingSession
>>> session = StreamingSession(model, metadata)
>>> for chunk in eeg_stream:
...     result = session.process_chunk(chunk)
>>> final = session.finalize_trial()
"""

# Core model I/O
from .nimbus_io import NimbusModel, nimbus_load, nimbus_save

# Functional API (backward compatible)
from .models.nimbus_lda import (
    nimbus_lda_fit,
    nimbus_lda_predict,
    nimbus_lda_predict_proba,
    nimbus_lda_update,
)
from .models.nimbus_qda import (
    nimbus_qda_fit,
    nimbus_qda_predict,
    nimbus_qda_predict_proba,
    nimbus_qda_update,
)
from .models.nimbus_sts import (
    nimbus_sts_fit,
    nimbus_sts_predict,
    nimbus_sts_predict_proba,
    nimbus_sts_update,
)

# Optional Softmax functional API (requires `pip install nimbus-bci[softmax]`)
try:
    from .models.nimbus_softmax import (  # noqa: WPS433
        nimbus_softmax_fit,
        nimbus_softmax_predict,
        nimbus_softmax_predict_proba,
        nimbus_softmax_predict_samples,
        nimbus_softmax_update,
    )
except Exception:  # pragma: no cover
    def _softmax_missing(*_args, **_kwargs):
        raise ImportError(
            "NimbusSoftmax requires the optional 'softmax' extra. "
            "Install with: pip install nimbus-bci[softmax]"
        )

    nimbus_softmax_fit = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_update = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_predict_proba = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_predict = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_predict_samples = _softmax_missing  # type: ignore[assignment]

# sklearn-compatible classifier classes (NimbusSoftmax is optional)
from .models import NimbusLDA, NimbusQDA, NimbusSoftmax, NimbusSTS

# Data contracts
from .data import BCIData, BCIMetadata, validate_data, check_model_compatibility

# Inference modules
from .inference import (
    predict_batch,
    BatchResult,
    StreamingSession,
    StreamingSessionSTS,
    ChunkResult,
    StreamingResult,
    aggregate_chunks,
    compute_temporal_weights,
)

# Metrics
from .metrics import (
    compute_entropy,
    compute_mahalanobis_distances,
    compute_outlier_scores,
    CalibrationMetrics,
    compute_calibration_metrics,
    calculate_itr,
    compute_balance,
    OnlinePerformanceTracker,
    TrialQuality,
    assess_trial_quality,
    should_reject_trial,
)

# Utilities
from .utils import (
    aggregate_temporal_features,
    NormalizationParams,
    NormalizationStatus,
    estimate_normalization_params,
    apply_normalization,
    check_normalization_status,
    PreprocessingReport,
    diagnose_preprocessing,
    compute_fisher_score,
    rank_features_by_discriminability,
)

# MNE compatibility (lazy imports to avoid hard dependency)
from .compat import (
    from_mne_epochs,
    to_mne_epochs,
    extract_csp_features,
    extract_bandpower_features,
    create_bci_pipeline,
)

from importlib.metadata import PackageNotFoundError, version as _dist_version

try:
    # Keep runtime version in sync with `pyproject.toml` without manual edits.
    __version__ = _dist_version("nimbus-bci")
except PackageNotFoundError:  # pragma: no cover
    # Source checkout without installed dist metadata (e.g., direct PYTHONPATH use).
    __version__ = "0.0.0"

__all__ = [
    # Version
    "__version__",
    # Core I/O
    "NimbusModel",
    "nimbus_save",
    "nimbus_load",
    # Functional API (backward compatible)
    "nimbus_lda_fit",
    "nimbus_lda_update",
    "nimbus_lda_predict_proba",
    "nimbus_lda_predict",
    "nimbus_qda_fit",
    "nimbus_qda_update",
    "nimbus_qda_predict_proba",
    "nimbus_qda_predict",
    "nimbus_softmax_fit",
    "nimbus_softmax_update",
    "nimbus_softmax_predict_proba",
    "nimbus_softmax_predict",
    "nimbus_softmax_predict_samples",
    "nimbus_sts_fit",
    "nimbus_sts_update",
    "nimbus_sts_predict_proba",
    "nimbus_sts_predict",
    # sklearn-compatible classifier classes
    "NimbusLDA",
    "NimbusQDA",
    "NimbusSoftmax",
    "NimbusSTS",
    # Data contracts
    "BCIData",
    "BCIMetadata",
    "validate_data",
    "check_model_compatibility",
    # Inference
    "predict_batch",
    "BatchResult",
    "StreamingSession",
    "StreamingSessionSTS",
    "ChunkResult",
    "StreamingResult",
    "aggregate_chunks",
    "compute_temporal_weights",
    # Metrics
    "compute_entropy",
    "compute_mahalanobis_distances",
    "compute_outlier_scores",
    "CalibrationMetrics",
    "compute_calibration_metrics",
    "calculate_itr",
    "compute_balance",
    "OnlinePerformanceTracker",
    "TrialQuality",
    "assess_trial_quality",
    "should_reject_trial",
    # Utilities
    "aggregate_temporal_features",
    "NormalizationParams",
    "NormalizationStatus",
    "estimate_normalization_params",
    "apply_normalization",
    "check_normalization_status",
    "PreprocessingReport",
    "diagnose_preprocessing",
    "compute_fisher_score",
    "rank_features_by_discriminability",
    # MNE compatibility
    "from_mne_epochs",
    "to_mne_epochs",
    "extract_csp_features",
    "extract_bandpower_features",
    "create_bci_pipeline",
]
