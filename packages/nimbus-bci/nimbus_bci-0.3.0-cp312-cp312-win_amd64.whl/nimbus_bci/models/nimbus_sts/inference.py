"""Inference for NimbusSTS using Extended Kalman Filter."""

from __future__ import annotations

import numpy as np
from ...nimbus_io import NimbusModel


def softmax(logits: np.ndarray) -> np.ndarray:
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


def softmax_jacobian(proba: np.ndarray) -> np.ndarray:
    n = proba.shape[0]
    return np.diag(proba) - np.outer(proba, proba)


def kalman_predict(
    z_mean: np.ndarray,
    z_cov: np.ndarray,
    A: np.ndarray,
    Q: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    z_mean_pred = A @ z_mean
    z_cov_pred = A @ z_cov @ A.T + Q
    return z_mean_pred, z_cov_pred


def ekf_update(
    z_mean: np.ndarray,
    z_cov: np.ndarray,
    x: np.ndarray,
    y: int,
    W: np.ndarray,
    H: np.ndarray,
    b: np.ndarray,
    R: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n_classes = W.shape[0]
    logits = W @ x + H @ z_mean + b
    proba = softmax(logits)
    
    y_onehot = np.zeros(n_classes)
    y_onehot[y] = 1.0
    innovation = y_onehot - proba
    
    J = softmax_jacobian(proba)
    C = J @ H
    
    S = C @ z_cov @ C.T + R
    # Kalman gain: K = P C^T S^{-1}
    # Use solve for numerical stability rather than explicitly inverting S.
    K = z_cov @ C.T @ np.linalg.solve(S, np.eye(S.shape[0]))
    
    z_mean_new = z_mean + K @ innovation
    z_cov_new = (np.eye(len(z_mean)) - K @ C) @ z_cov
    
    return z_mean_new, z_cov_new


def run_filter(
    X: np.ndarray,
    y: np.ndarray,
    z_mean_init: np.ndarray,
    z_cov_init: np.ndarray,
    A: np.ndarray,
    Q: np.ndarray,
    W: np.ndarray,
    H: np.ndarray,
    b: np.ndarray,
    R: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n_samples = X.shape[0]
    state_dim = z_mean_init.shape[0]
    
    z_means = np.zeros((n_samples + 1, state_dim))
    z_covs = np.zeros((n_samples + 1, state_dim, state_dim))
    
    z_means[0] = z_mean_init
    z_covs[0] = z_cov_init
    
    for t in range(n_samples):
        z_pred, P_pred = kalman_predict(z_means[t], z_covs[t], A, Q)
        z_upd, P_upd = ekf_update(z_pred, P_pred, X[t], int(y[t]), W, H, b, R)
        z_means[t + 1] = z_upd
        z_covs[t + 1] = P_upd
    
    return z_means, z_covs


def nimbus_sts_predict_proba(
    model: NimbusModel, X: np.ndarray, *, evolve_state: bool = False
) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    
    params = model.params
    W = params["W"]
    H = params["H"]
    b = params["b"]
    z_mean = np.asarray(params["z_mean"], dtype=np.float64).copy()  # FIX: Add .copy() to prevent mutation
    A = params.get("A", None)
    
    n_samples = X.shape[0]
    n_classes = W.shape[0]
    proba = np.zeros((n_samples, n_classes))
    
    for i in range(n_samples):
        # In sklearn-style batch prediction, treat rows as conditionally independent
        # by default. For ordered time-series evaluation, set evolve_state=True.
        if evolve_state and A is not None:
            z_mean = A @ z_mean
        logits = W @ X[i] + H @ z_mean + b
        proba[i] = softmax(logits)
    
    return proba


def nimbus_sts_predict(model: NimbusModel, X: np.ndarray) -> np.ndarray:
    proba = nimbus_sts_predict_proba(model, X)
    return np.argmax(proba, axis=1)

