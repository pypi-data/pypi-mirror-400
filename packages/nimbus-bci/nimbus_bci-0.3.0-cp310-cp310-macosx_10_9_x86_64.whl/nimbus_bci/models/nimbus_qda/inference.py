from __future__ import annotations

import math
import numpy as np

from ...nimbus_io import NimbusModel


def nimbus_qda_predict_proba(
    model: NimbusModel,
    X: np.ndarray,
) -> np.ndarray:
    """Predict class probabilities under the QDA posterior predictive.

    Args:
        model: A model returned by `nimbus_qda_fit` or `nimbus_qda_update`.
        X: Feature matrix of shape (n_trials, n_features).

    Returns:
        Array of shape (n_trials, n_classes) with rows summing to 1.

    Raises:
        ValueError: If X is not 2D or the stored posterior is invalid.
    """
    Xn = np.asarray(X, dtype=np.float64)
    if Xn.ndim != 2:
        raise ValueError("X must be 2D: (n_trials, n_features)")

    n_classes = int(np.asarray(model.params["n_classes"], dtype=np.int64))
    log_priors = np.asarray(model.params["log_priors"], dtype=np.float64)

    mu = np.asarray(model.params["mu"], dtype=np.float64)
    kappa = np.asarray(model.params["kappa"], dtype=np.float64)
    nu = np.asarray(model.params["nu"], dtype=np.float64)
    psi = np.asarray(model.params["psi"], dtype=np.float64)

    n_features = int(Xn.shape[1])
    scores = np.empty((Xn.shape[0], n_classes), dtype=np.float64)
    for k in range(n_classes):
        df = float(nu[k]) - float(n_features) + 1.0
        if df <= 0.0:
            raise ValueError("invalid posterior df")
        scale = psi[k] * ((kappa[k] + 1.0) / (kappa[k] * df))
        L = np.linalg.cholesky(scale)
        xc = (Xn - mu[k]).T
        sol = np.linalg.solve(L, xc)
        quad = np.sum(sol * sol, axis=0)
        logdet = 2.0 * float(np.sum(np.log(np.diag(L))))
        a = 0.5 * (df + float(n_features))
        logc = math.lgamma(a) - math.lgamma(0.5 * df) - 0.5 * (
            float(n_features) * math.log(df * math.pi) + logdet
        )
        scores[:, k] = log_priors[k] + logc - a * np.log1p(quad / df)

    m = np.max(scores, axis=1, keepdims=True)
    z = scores - m
    e = np.exp(z)
    return e / np.sum(e, axis=1, keepdims=True)


def nimbus_qda_predict(
    model: NimbusModel,
    X: np.ndarray,
) -> np.ndarray:
    """Predict the most likely class label for each row of X.

    Args:
        model: A model returned by `nimbus_qda_fit` or `nimbus_qda_update`.
        X: Feature matrix of shape (n_trials, n_features).

    Returns:
        Integer labels of shape (n_trials,) in the model's label space.
    """
    probs = nimbus_qda_predict_proba(model, X)
    label_base = int(np.asarray(model.params["label_base"], dtype=np.int64))
    return np.argmax(probs, axis=1).astype(np.int64) + label_base


