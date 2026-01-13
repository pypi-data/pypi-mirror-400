"""Batch inference for BCI classification.

This module provides batch inference with rich diagnostic outputs
including entropy, calibration metrics, and outlier detection.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

import numpy as np

from ..metrics.diagnostics import compute_entropy_batch, compute_mahalanobis_distances, compute_outlier_scores
from ..metrics.calibration import CalibrationMetrics, compute_calibration_metrics
from ..metrics.performance import compute_balance
from .dispatch import predict_proba

if TYPE_CHECKING:
    from ..data.contracts import BCIData
    from ..nimbus_io import NimbusModel


@dataclass
class BatchResult:
    """Results from batch inference on multiple trials.

    Attributes
    ----------
    predictions : np.ndarray
        Predicted class labels of shape (n_trials,).
    confidences : np.ndarray
        Maximum posterior probability per trial of shape (n_trials,).
        confidences[i] = maximum(posteriors[i, :]) for each trial.
    posteriors : np.ndarray
        Full posterior distribution of shape (n_trials, n_classes).
        Rows sum to 1.
    entropy : np.ndarray
        Shannon entropy per trial in bits, shape (n_trials,).
        Lower = more confident.
    mean_entropy : float
        Average entropy across all trials.
    mahalanobis_distances : np.ndarray
        Distance to each class center of shape (n_trials, n_classes).
    outlier_scores : np.ndarray
        Minimum distance to any class of shape (n_trials,).
        Higher = more outlier-like.
    latency_ms : float
        Total inference time in milliseconds.
    per_trial_latency_ms : np.ndarray
        Inference time per trial in milliseconds.
    balance : float
        Class distribution balance in [0, 1]. 1 = perfectly balanced.
    calibration : CalibrationMetrics or None
        Calibration metrics if labels were provided, else None.
    """

    predictions: np.ndarray
    confidences: np.ndarray
    posteriors: np.ndarray
    entropy: np.ndarray
    mean_entropy: float
    mahalanobis_distances: np.ndarray
    outlier_scores: np.ndarray
    latency_ms: float
    per_trial_latency_ms: np.ndarray
    balance: float
    calibration: Optional[CalibrationMetrics] = None


def predict_batch(
    model: "NimbusModel",
    data: "BCIData",
    *,
    num_posterior_samples: int = 50,
    rng_seed: int = 0,
) -> BatchResult:
    """Perform batch inference on multiple trials.

    This function wraps the model's prediction with comprehensive
    diagnostics including entropy, outlier detection, and calibration.

    Parameters
    ----------
    model : NimbusModel
        Fitted Nimbus model.
    data : BCIData
        BCI data with features and metadata.
    num_posterior_samples : int, default=50
        Number of posterior samples for softmax models.
    rng_seed : int, default=0
        Random seed for softmax prediction.

    Returns
    -------
    BatchResult
        Results including predictions, confidences, and diagnostics.

    Examples
    --------
    >>> from nimbus_bci.inference import predict_batch
    >>> results = predict_batch(model, bci_data)
    >>> print(f"Accuracy: {np.mean(results.predictions == data.labels):.2%}")
    >>> print(f"Mean entropy: {results.mean_entropy:.2f} bits")
    """
    from ..data.validation import validate_data, check_model_compatibility, labels_to_zero_indexed

    # Validate data
    validate_data(data)
    check_model_compatibility(data, model)

    start_time = time.perf_counter()
    label_base = int(np.asarray(model.params.get("label_base", 0), dtype=np.int64))

    # Get aggregated features
    X = data.get_aggregated_features()  # (n_trials, n_features)
    n_trials = X.shape[0]
    n_classes = data.metadata.n_classes

    per_trial_latency_ms = np.zeros(n_trials)

    trial_start = time.perf_counter()
    posteriors = predict_proba(
        model,
        X,
        num_posterior_samples=num_posterior_samples,
        rng_seed=rng_seed,
    )
    per_trial_latency_ms[:] = (time.perf_counter() - trial_start) * 1000 / n_trials

    # Extract predictions and confidences
    predictions0 = np.argmax(posteriors, axis=1).astype(np.int64)
    predictions = predictions0 + label_base
    confidences = np.max(posteriors, axis=1)

    # Compute entropy
    entropy = compute_entropy_batch(posteriors)
    mean_entropy = float(np.mean(entropy))

    # Compute Mahalanobis distances and outlier scores
    mahalanobis_distances = np.zeros((n_trials, n_classes))
    outlier_scores = np.zeros(n_trials)

    if "mu" in model.params:
        # LDA/GMM models have class means
        class_means = [model.params["mu"][k] for k in range(n_classes)]

        if "psi" in model.params:
            psi = model.params["psi"]
            if psi.ndim == 2:
                # LDA: shared precision
                nu = float(model.params["nu"])
                n_features = psi.shape[0]
                # Approximate precision from posterior scatter
                precision = np.linalg.inv(psi / (nu - n_features - 1 + 1e-6))
                precision_matrices = [precision for _ in range(n_classes)]
            else:
                # GMM: per-class precision
                nu = model.params["nu"]
                n_features = psi.shape[1]
                precision_matrices = []
                for k in range(n_classes):
                    prec = np.linalg.inv(psi[k] / (nu[k] - n_features - 1 + 1e-6))
                    precision_matrices.append(prec)

            try:
                mahalanobis_distances = compute_mahalanobis_distances(
                    X, class_means, precision_matrices
                )
                outlier_scores = compute_outlier_scores(mahalanobis_distances)
            except np.linalg.LinAlgError:
                # Matrix inversion failed - leave as zeros
                pass

    # Compute balance
    balance = compute_balance(predictions0, n_classes)

    # Compute calibration if labels available
    calibration = None
    if data.labels is not None:
        labels = np.asarray(data.labels)
        if labels.size != n_trials:
            raise ValueError(
                f"labels has {labels.size} elements, but data has {n_trials} trials"
            )
        labels0 = labels_to_zero_indexed(labels, n_classes=n_classes, label_base=label_base)

        calibration = compute_calibration_metrics(
            predictions0, confidences, labels0
        )

    # Total latency
    latency_ms = (time.perf_counter() - start_time) * 1000

    return BatchResult(
        predictions=predictions,
        confidences=confidences,
        posteriors=posteriors,
        entropy=entropy,
        mean_entropy=mean_entropy,
        mahalanobis_distances=mahalanobis_distances,
        outlier_scores=outlier_scores,
        latency_ms=latency_ms,
        per_trial_latency_ms=per_trial_latency_ms,
        balance=balance,
        calibration=calibration,
    )





