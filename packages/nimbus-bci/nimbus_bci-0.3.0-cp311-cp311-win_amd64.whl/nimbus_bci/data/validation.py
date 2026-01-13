"""Data validation utilities for BCI data.

This module provides functions to validate BCIData and check
compatibility with Nimbus models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .contracts import BCIData, BCIMetadata

if TYPE_CHECKING:
    from ..nimbus_io import NimbusModel


def labels_to_zero_indexed(
    labels: np.ndarray,
    *,
    n_classes: int,
    label_base: int,
) -> np.ndarray:
    """Convert labels to 0-indexed class IDs for metrics/aggregation.

    Accepts labels that are already 0-indexed ([0..K-1]) or labels that are in the
    model label space ([label_base..label_base+K-1]).
    """
    labs = np.asarray(labels)
    if labs.ndim != 1:
        raise ValueError(f"labels must be 1D, got {labs.ndim}D")

    if labs.size == 0:
        return labs.astype(np.int64)

    min_lab = int(np.min(labs))
    max_lab = int(np.max(labs))
    k = int(n_classes)
    lb = int(label_base)

    if 0 <= min_lab and max_lab < k:
        return labs.astype(np.int64)

    if lb <= min_lab and max_lab < (lb + k):
        return (labs.astype(np.int64) - lb).astype(np.int64)

    raise ValueError(
        "labels are not compatible with label space. "
        f"Expected labels in [0, {k - 1}] or [{lb}, {lb + k - 1}], "
        f"got min={min_lab}, max={max_lab}."
    )


def validate_data(data: BCIData, require_labels: bool = False) -> bool:
    """Validate BCIData for use with Nimbus models.

    Parameters
    ----------
    data : BCIData
        Data to validate.
    require_labels : bool, default=False
        If True, require labels to be present.

    Returns
    -------
    bool
        True if validation passes.

    Raises
    ------
    ValueError
        If validation fails with a descriptive message.
    """
    # Check for NaN values
    if not data.check_nan():
        nan_count = np.sum(np.isnan(data.features))
        raise ValueError(
            f"features contains {nan_count} NaN values. "
            "Please check preprocessing pipeline."
        )

    # Check for infinite values
    if not data.check_inf():
        inf_count = np.sum(np.isinf(data.features))
        raise ValueError(
            f"features contains {inf_count} infinite values. "
            "Please check preprocessing pipeline."
        )

    # Check labels if required
    if require_labels and not data.has_labels():
        raise ValueError(
            "Labels are required for training. "
            "Please provide labels in BCIData."
        )

    # Validate labels if labels exist
    if data.labels is not None:
        labels = np.asarray(data.labels)
        if labels.ndim != 1:
            raise ValueError(f"labels must be 1D, got {labels.ndim}D")

        # Allow integer labels (including floats like 1.0).
        if not np.issubdtype(labels.dtype, np.integer):
            rounded = np.rint(labels)
            if not np.allclose(labels, rounded):
                raise ValueError("labels must be integer-valued")
            labels = rounded.astype(np.int64)

        min_label = int(np.min(labels))
        max_label = int(np.max(labels))
        if min_label < 0:
            raise ValueError(f"Labels must be non-negative, got min label {min_label}")

        n_classes = int(data.metadata.n_classes)
        # For BCIData we allow arbitrary non-negative integer codes (common with MNE event IDs),
        # as long as the number of unique classes does not exceed metadata.n_classes.
        n_unique = int(np.unique(labels).size)
        if n_unique > n_classes:
            raise ValueError(
                f"labels has {n_unique} unique classes, but metadata specifies n_classes={n_classes}."
            )

    # Check for sufficient samples
    if data.n_samples < 2:
        raise ValueError(
            f"At least 2 time samples required, got {data.n_samples}"
        )

    # Check feature variance (detect constant features)
    if data.features.ndim == 3:
        feature_var = np.var(data.features, axis=(1, 2))
    else:
        feature_var = np.var(data.features, axis=1)

    zero_var_features = np.sum(feature_var == 0)
    if zero_var_features > 0:
        raise ValueError(
            f"{zero_var_features} features have zero variance (constant). "
            "Please remove or check preprocessing."
        )

    return True


def check_model_compatibility(data: BCIData, model: "NimbusModel") -> bool:
    """Check if BCIData is compatible with a fitted model.

    Parameters
    ----------
    data : BCIData
        Data to check.
    model : NimbusModel
        Fitted model to check against.

    Returns
    -------
    bool
        True if compatible.

    Raises
    ------
    ValueError
        If incompatible with a descriptive message.
    """
    # Extract model parameters
    model_n_features = None
    model_n_classes = None

    if "n_classes" in model.params:
        model_n_classes = int(model.params["n_classes"])
    if "mu" in model.params:
        model_n_features = model.params["mu"].shape[1]
    elif "beta_mean" in model.params:
        # Softmax model: beta_mean shape is (n_classes-1, n_features+1)
        model_n_features = model.params["beta_mean"].shape[1] - 1  # -1 for bias
    elif "W" in model.params:
        # STS model: W shape is (n_classes, n_features)
        model_n_features = model.params["W"].shape[1]

    # Check feature count
    if model_n_features is not None and data.metadata.n_features != model_n_features:
        raise ValueError(
            f"Data has {data.metadata.n_features} features, "
            f"but model expects {model_n_features}"
        )

    # Check class count
    if model_n_classes is not None and data.metadata.n_classes != model_n_classes:
        raise ValueError(
            f"Data has {data.metadata.n_classes} classes, "
            f"but model has {model_n_classes}"
        )

    return True


def validate_chunk(chunk: np.ndarray, metadata: "BCIMetadata") -> bool:
    """Validate a single chunk for streaming inference.

    Parameters
    ----------
    chunk : np.ndarray
        Chunk features of shape (n_features, n_samples).
    metadata : BCIMetadata
        Metadata describing expected format.

    Returns
    -------
    bool
        True if validation passes.

    Raises
    ------
    ValueError
        If validation fails.
    """
    if chunk.ndim != 2:
        raise ValueError(
            f"Chunk must be 2D (n_features, n_samples), got {chunk.ndim}D"
        )

    if chunk.shape[0] != metadata.n_features:
        raise ValueError(
            f"Chunk has {chunk.shape[0]} features, "
            f"expected {metadata.n_features}"
        )

    if metadata.chunk_size is not None and chunk.shape[1] != metadata.chunk_size:
        raise ValueError(
            f"Chunk has {chunk.shape[1]} samples, expected {metadata.chunk_size} "
            f"(metadata.chunk_size)."
        )

    if np.any(np.isnan(chunk)):
        raise ValueError("Chunk contains NaN values")

    if np.any(np.isinf(chunk)):
        raise ValueError("Chunk contains infinite values")

    return True

