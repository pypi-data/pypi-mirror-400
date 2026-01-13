"""Shared model dispatch utilities for inference.

This module centralizes the mapping from NimbusModel.model_type to the
corresponding predict_proba implementation, so batch and streaming
inference don't duplicate branching logic.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from ..nimbus_io import NimbusModel


PredictProbaFn = Callable[[np.ndarray], np.ndarray]
PredictProbaKwFn = Callable[[np.ndarray], np.ndarray]


def get_predict_proba_fn(model: NimbusModel) -> Callable[..., np.ndarray]:
    """Return a predict_proba function for the given model.

    The returned callable supports the common keyword arguments:
    - num_posterior_samples (used by softmax models)
    - rng_seed (used by softmax models)
    LDA/QDA/STS ignore these kwargs.
    """
    model_type = model.model_type

    if model_type == "nimbus_lda":
        from ..models.nimbus_lda import nimbus_lda_predict_proba

        def _predict_proba(X: np.ndarray, *, num_posterior_samples: int = 1, rng_seed: int = 0) -> np.ndarray:  # noqa: ARG001
            return nimbus_lda_predict_proba(model, X)

        return _predict_proba

    if model_type == "nimbus_qda":
        from ..models.nimbus_qda import nimbus_qda_predict_proba

        def _predict_proba(X: np.ndarray, *, num_posterior_samples: int = 1, rng_seed: int = 0) -> np.ndarray:  # noqa: ARG001
            return nimbus_qda_predict_proba(model, X)

        return _predict_proba

    if model_type == "nimbus_softmax":
        try:
            from ..models.nimbus_softmax import nimbus_softmax_predict_proba
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "nimbus_softmax models require the optional 'softmax' extra. "
                "Install with: pip install nimbus-bci[softmax]"
            ) from e

        def _predict_proba(X: np.ndarray, *, num_posterior_samples: int = 50, rng_seed: int = 0) -> np.ndarray:
            return nimbus_softmax_predict_proba(
                model,
                X,
                num_posterior_samples=int(num_posterior_samples),
                rng_seed=int(rng_seed),
            )

        return _predict_proba

    if model_type == "nimbus_sts":
        from ..models.nimbus_sts import nimbus_sts_predict_proba

        def _predict_proba(X: np.ndarray, *, num_posterior_samples: int = 1, rng_seed: int = 0) -> np.ndarray:  # noqa: ARG001
            return nimbus_sts_predict_proba(model, X, evolve_state=False)

        return _predict_proba

    raise ValueError(f"Unknown model type: {model_type}")


def predict_proba(
    model: NimbusModel,
    X: np.ndarray,
    *,
    num_posterior_samples: int = 50,
    rng_seed: int = 0,
) -> np.ndarray:
    """Predict class probabilities for any Nimbus model."""
    fn = get_predict_proba_fn(model)
    return fn(X, num_posterior_samples=num_posterior_samples, rng_seed=rng_seed)





