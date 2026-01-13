"""Learning functions for NimbusSTS classifier."""

from __future__ import annotations

from typing import Optional

import numpy as np
from ...nimbus_io import NimbusModel
from .inference import run_filter, softmax


def estimate_optimal_transition_cov(X: np.ndarray, y: np.ndarray) -> float:
    """Estimate appropriate Q based on data variability.
    
    Uses simple heuristic: Q ≈ 0.01 × var(features)
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Labels (unused but kept for API consistency).
    
    Returns:
        Estimated transition covariance.
    """
    feature_var = np.mean(np.var(X, axis=0))
    return 0.01 * feature_var


def nimbus_sts_fit(
    X: np.ndarray,
    y: np.ndarray,
    n_classes: int,
    label_base: int = 0,
    state_dim: Optional[int] = None,
    w_loc: float = 0.0,
    w_scale: float = 1.0,
    transition_cov: Optional[float] = None,
    observation_cov: float = 1.0,
    transition_matrix: Optional[np.ndarray] = None,
    learning_rate: float = 0.1,
    num_steps: int = 50,
    rng_seed: int = 0,
    verbose: bool = False,
    convergence_tol: float = 1e-4,
) -> NimbusModel:
    """Fit NimbusSTS classifier with Extended Kalman Filter.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Integer labels of shape (n_samples,).
        n_classes: Number of classes.
        label_base: Base label value (0 or 1).
        state_dim: Latent state dimension. If None, set to n_classes - 1.
        w_loc: Prior mean for feature weights.
        w_scale: Prior scale for feature weights.
        transition_cov: Process noise covariance (Q). If None, auto-estimated.
        observation_cov: Observation noise covariance (R).
        transition_matrix: State transition matrix A. If None, uses identity.
        learning_rate: Step size for parameter updates.
        num_steps: Number of learning iterations.
        rng_seed: Random seed for reproducibility.
        verbose: Print convergence diagnostics during training.
        convergence_tol: Stop early if log-likelihood change < tol.
    
    Returns:
        NimbusModel storing the fitted parameters.
    """
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.int64) - label_base
    
    n_samples, n_features = X.shape
    
    if state_dim is None:
        state_dim = n_classes - 1
    
    # Auto-estimate transition covariance if not provided
    if transition_cov is None:
        transition_cov = estimate_optimal_transition_cov(X, y)
        if verbose:
            print(f"Auto-selected transition_cov={transition_cov:.6f}")
    
    rng = np.random.default_rng(rng_seed)
    
    W = rng.normal(w_loc, w_scale * 0.1, size=(n_classes, n_features))
    H = rng.normal(0, 0.1, size=(n_classes, state_dim))
    b = np.zeros(n_classes)
    
    # Use provided transition matrix or default to identity
    if transition_matrix is None:
        A = np.eye(state_dim)
    else:
        A = np.asarray(transition_matrix, dtype=np.float64)
        if A.shape != (state_dim, state_dim):
            raise ValueError(
                f"transition_matrix must have shape ({state_dim}, {state_dim}), "
                f"got {A.shape}"
            )
    
    Q = np.eye(state_dim) * transition_cov
    R = np.eye(n_classes) * observation_cov
    
    z_mean_init = np.zeros(state_dim)
    z_cov_init = np.eye(state_dim)
    
    prev_log_lik = -np.inf
    
    for step in range(num_steps):
        z_means, z_covs = run_filter(X, y, z_mean_init, z_cov_init, A, Q, W, H, b, R)
        
        # Compute log-likelihood for convergence monitoring
        log_lik = 0.0
        for t in range(n_samples):
            logits = W @ X[t] + H @ z_means[t + 1] + b
            proba = softmax(logits)
            log_lik += np.log(proba[y[t]] + 1e-10)
        
        if verbose:
            print(f"Step {step+1}/{num_steps}: log_lik={log_lik:.4f}")
        
        # Check convergence
        if step > 0 and abs(log_lik - prev_log_lik) < convergence_tol:
            if verbose:
                print(f"Converged at step {step+1}")
            break
        
        prev_log_lik = log_lik
        
        grad_W = np.zeros_like(W)
        grad_H = np.zeros_like(H)
        grad_b = np.zeros_like(b)
        
        for t in range(n_samples):
            # `run_filter` returns z_means[0] as the initial state and z_means[t+1]
            # as the updated state after observing sample t. Use the aligned state.
            logits = W @ X[t] + H @ z_means[t + 1] + b
            proba = softmax(logits)
            
            y_onehot = np.zeros(n_classes)
            y_onehot[y[t]] = 1.0
            error = y_onehot - proba
            
            grad_W += np.outer(error, X[t])
            grad_H += np.outer(error, z_means[t + 1])
            grad_b += error
        
        grad_W /= n_samples
        grad_H /= n_samples
        grad_b /= n_samples
        
        W += learning_rate * grad_W
        H += learning_rate * grad_H
        b += learning_rate * grad_b
    
    z_means_final, z_covs_final = run_filter(
        X, y, z_mean_init, z_cov_init, A, Q, W, H, b, R
    )
    
    params = {
        "W": W,
        "H": H,
        "b": b,
        "A": A,
        "Q": Q,
        "R": R,
        "z_mean": z_means_final[n_samples],
        "z_cov": z_covs_final[n_samples],
        "z_mean_init": z_mean_init,
        "z_cov_init": z_cov_init,
        "state_dim": state_dim,
        "n_classes": n_classes,
        "n_features": n_features,
        "label_base": label_base,
    }
    
    return NimbusModel(model_type="nimbus_sts", params=params)


def nimbus_sts_update(
    model: NimbusModel,
    X: np.ndarray,
    y: np.ndarray,
    learning_rate: float = 0.1,
) -> NimbusModel:
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.int64)
    
    if X.ndim == 1:
        X = X.reshape(1, -1)
    if y.ndim == 0:
        y = y.reshape(1)
    
    params = model.params.copy()
    W = params["W"].copy()
    H = params["H"].copy()
    b = params["b"].copy()
    A = params["A"]
    Q = params["Q"]
    R = params["R"]
    z_mean = params["z_mean"].copy()
    z_cov = params["z_cov"].copy()
    n_classes = params["n_classes"]
    label_base = int(params.get("label_base", 0))
    y = y - label_base
    
    z_means, z_covs = run_filter(X, y, z_mean, z_cov, A, Q, W, H, b, R)
    
    n_samples = X.shape[0]
    for t in range(n_samples):
        logits = W @ X[t] + H @ z_means[t + 1] + b
        proba = softmax(logits)
        
        y_onehot = np.zeros(n_classes)
        y_onehot[y[t]] = 1.0
        error = y_onehot - proba
        
        W += learning_rate * np.outer(error, X[t])
        H += learning_rate * np.outer(error, z_means[t + 1])
        b += learning_rate * error
    
    params["W"] = W
    params["H"] = H
    params["b"] = b
    params["z_mean"] = z_means[n_samples]
    params["z_cov"] = z_covs[n_samples]
    
    return NimbusModel(model_type="nimbus_sts", params=params)

