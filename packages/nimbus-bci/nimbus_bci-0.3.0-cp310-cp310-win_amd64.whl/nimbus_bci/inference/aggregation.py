"""Chunk aggregation for streaming inference.

This module provides methods for combining chunk-level predictions
into trial-level predictions with various aggregation strategies.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def aggregate_chunks(
    predictions: list[int],
    confidences: list[float],
    n_classes: int,
    *,
    posteriors: Optional[list[np.ndarray]] = None,
    method: str = "weighted_vote",
) -> tuple[int, float, np.ndarray]:
    """Aggregate chunk predictions into a final trial prediction.

    Parameters
    ----------
    predictions : list of int
        Predicted class for each chunk.
    confidences : list of float
        Confidence for each chunk.
    n_classes : int
        Number of possible classes.
    posteriors : list of np.ndarray, optional
        Full posterior for each chunk. Required for some methods.
    method : str, default="weighted_vote"
        Aggregation method:
        - "weighted_vote": Confidence-weighted voting (default)
        - "max_confidence": Use chunk with highest confidence
        - "posterior_mean": Average posteriors across chunks (Bayesian)
        - "majority_vote": Simple majority voting

    Returns
    -------
    prediction : int
        Final predicted class.
    confidence : float
        Final confidence (= max of final posterior).
    posterior : np.ndarray
        Final posterior distribution.

    Examples
    --------
    >>> predictions = [0, 1, 1, 1]
    >>> confidences = [0.9, 0.8, 0.7, 0.6]
    >>> pred, conf, post = aggregate_chunks(predictions, confidences, 2)
    >>> print(f"Final: class {pred} with confidence {conf:.2f}")
    """
    predictions = list(predictions)
    confidences = list(confidences)
    n_chunks = len(predictions)

    if n_chunks == 0:
        raise ValueError("No chunks to aggregate")

    if n_chunks == 1:
        if posteriors is not None and len(posteriors) > 0:
            posterior = np.asarray(posteriors[0])
        else:
            posterior = np.zeros(n_classes)
            posterior[predictions[0]] = 1.0
        return predictions[0], confidences[0], posterior

    method = method.lower()

    if method == "weighted_vote":
        # Confidence-weighted voting
        votes = np.zeros(n_classes)
        for pred, conf in zip(predictions, confidences):
            votes[pred] += conf

        # Normalize to get posterior
        posterior = votes / (np.sum(votes) + 1e-10)
        final_pred = int(np.argmax(posterior))
        final_conf = float(posterior[final_pred])

    elif method == "max_confidence":
        # Use chunk with highest confidence
        max_idx = int(np.argmax(confidences))
        final_pred = predictions[max_idx]
        final_conf = confidences[max_idx]

        if posteriors is not None and len(posteriors) > max_idx:
            posterior = np.asarray(posteriors[max_idx])
        else:
            posterior = np.zeros(n_classes)
            posterior[final_pred] = final_conf
            # Distribute remaining probability
            remaining = 1.0 - final_conf
            for i in range(n_classes):
                if i != final_pred:
                    posterior[i] = remaining / (n_classes - 1)

    elif method == "posterior_mean":
        # Average posteriors (Bayesian approach)
        if posteriors is None or len(posteriors) == 0:
            raise ValueError("posterior_mean method requires posteriors")

        stacked = np.stack([np.asarray(p) for p in posteriors], axis=0)
        posterior = np.mean(stacked, axis=0)
        posterior = posterior / (np.sum(posterior) + 1e-10)  # Re-normalize

        final_pred = int(np.argmax(posterior))
        final_conf = float(posterior[final_pred])

    elif method == "majority_vote":
        # Simple majority voting
        votes = np.bincount(predictions, minlength=n_classes)
        final_pred = int(np.argmax(votes))

        # Posterior is proportion of votes
        posterior = votes.astype(np.float64) / n_chunks
        final_conf = float(posterior[final_pred])

    else:
        valid_methods = {"weighted_vote", "max_confidence", "posterior_mean", "majority_vote"}
        raise ValueError(
            f"Unknown aggregation method '{method}'. "
            f"Valid methods: {valid_methods}"
        )

    return final_pred, final_conf, posterior


def compute_temporal_weights(paradigm: str, n_chunks: int) -> np.ndarray:
    """Compute temporal importance weights for chunks.

    Different BCI paradigms have different temporal dynamics,
    so later or middle chunks may be more informative.

    Parameters
    ----------
    paradigm : str
        BCI paradigm ("motor_imagery", "p300", "ssvep", "erp").
    n_chunks : int
        Number of chunks in the trial.

    Returns
    -------
    np.ndarray
        Weights of shape (n_chunks,) that sum to n_chunks.

    Examples
    --------
    >>> weights = compute_temporal_weights("motor_imagery", 4)
    >>> print(weights)  # Later chunks weighted more
    [0.5  0.83 1.17 1.5]

    >>> weights = compute_temporal_weights("p300", 4)
    >>> print(weights)  # Middle chunks weighted more (P300 peak)
    """
    if n_chunks <= 0:
        raise ValueError(f"n_chunks must be positive, got {n_chunks}")

    if n_chunks == 1:
        return np.array([1.0])

    paradigm = paradigm.lower()

    if paradigm == "motor_imagery":
        # Motor Imagery: discriminative activity develops over time
        # Weight increases linearly from 0.5 to 1.5
        weights = np.linspace(0.5, 1.5, n_chunks)

    elif paradigm in ("p300", "erp"):
        # P300/ERP: peak response around 300-400ms post-stimulus
        # Gaussian centered at 40% of trial duration
        positions = np.linspace(0.0, 1.0, n_chunks)
        center = 0.4
        width = 0.25
        weights = np.exp(-((positions - center) ** 2) / (2 * width ** 2))
        weights = weights / np.mean(weights)  # Normalize to mean 1

    elif paradigm == "ssvep":
        # SSVEP: steady-state, relatively uniform
        # Slight reduction at start/end for transient effects
        weights = np.ones(n_chunks)
        if n_chunks > 2:
            weights[0] = 0.8
            weights[-1] = 0.8

    else:
        # Unknown paradigm: uniform weights
        weights = np.ones(n_chunks)

    # Ensure weights sum to n_chunks (preserves confidence scale)
    weights = weights * (n_chunks / np.sum(weights))

    return weights





