from __future__ import annotations

from typing import Literal

import numpy as np

from ...nimbus_io import NimbusModel


def nimbus_qda_fit(
    X: np.ndarray,
    y: np.ndarray,
    n_classes: int,
    label_base: Literal[0, 1],
    mu_loc: float,
    mu_scale: float,
    wishart_df: float,
    wishart_scale: np.ndarray,
    class_prior_alpha: float,
) -> NimbusModel:
    """Fit a Bayesian class-conditional Gaussian model with conjugate priors.

    This is a QDA-style classifier with a separate covariance per class.

    Args:
        X: Feature matrix of shape (n_trials, n_features).
        y: Integer labels of shape (n_trials,). Labels must be in
            {label_base, ..., label_base + n_classes - 1}.
        n_classes: Number of classes.
        label_base: 0 or 1, describing the minimum label value in y.
        mu_loc: Scalar prior mean location (broadcast to all features).
        mu_scale: Prior mean scale (>0).
        wishart_df: Wishart degrees of freedom (>= n_features).
        wishart_scale: Wishart scale matrix of shape (n_features, n_features).
        class_prior_alpha: Dirichlet smoothing for class prior (>=0).

    Returns:
        NimbusModel storing posterior parameters used by prediction.

    Raises:
        ValueError: If inputs have invalid shapes, label ranges, or hyperparameters.
    """
    Xn = np.asarray(X, dtype=np.float64)
    yn = np.asarray(y)
    if Xn.ndim != 2:
        raise ValueError("X must be 2D: (n_trials, n_features)")
    if yn.ndim != 1:
        raise ValueError("y must be 1D: (n_trials,)")
    if Xn.shape[0] != yn.shape[0]:
        raise ValueError("X and y must have same number of rows")
    if n_classes < 2:
        raise ValueError("n_classes must be >= 2")
    if label_base not in (0, 1):
        raise ValueError("label_base must be 0 or 1")
    if class_prior_alpha < 0.0:
        raise ValueError("class_prior_alpha must be >= 0")
    if mu_scale <= 0.0:
        raise ValueError("mu_scale must be > 0")

    y0 = yn.astype(np.int64) - int(label_base)
    if np.min(y0) < 0 or np.max(y0) >= n_classes:
        raise ValueError("y out of range for n_classes/label_base")

    counts = np.bincount(y0, minlength=n_classes).astype(np.float64)
    if np.any(counts == 0):
        raise ValueError("all classes must be present in y")
    priors = (counts + class_prior_alpha) / float(np.sum(counts) + n_classes * class_prior_alpha)

    n_features = int(Xn.shape[1])
    wishart_scale_n = np.asarray(wishart_scale, dtype=np.float64)
    if wishart_scale_n.shape != (n_features, n_features):
        raise ValueError("wishart_scale must be (n_features, n_features)")
    if wishart_df <= float(n_features - 1):
        raise ValueError("wishart_df must be >= n_features")

    mu0 = np.full((n_features,), float(mu_loc), dtype=np.float64)
    psi0 = wishart_scale_n
    kappa0 = (float(np.trace(psi0)) / float(n_features)) / float(mu_scale**2)

    mu = np.zeros((n_classes, n_features), dtype=np.float64)
    kappa = counts + kappa0
    nu = wishart_df + counts.astype(np.float64)
    psi = np.zeros((n_classes, n_features, n_features), dtype=np.float64)

    for k in range(n_classes):
        Xk = Xn[y0 == k]
        nk = float(Xk.shape[0])
        xbar = np.mean(Xk, axis=0)
        xc = Xk - xbar
        Sk = xc.T @ xc
        mu[k] = (kappa0 * mu0 + nk * xbar) / float(kappa[k])
        dmu = xbar - mu0
        psi[k] = psi0 + Sk + (kappa0 * nk / float(kappa[k])) * np.outer(dmu, dmu)

    return NimbusModel(
        model_type="nimbus_qda",
        params={
            "backend": np.array("conjugate", dtype=object),
            "n_classes": np.array(n_classes, dtype=np.int64),
            "label_base": np.array(int(label_base), dtype=np.int64),
            "class_counts": counts.astype(np.int64),
            "class_prior_alpha": np.array(float(class_prior_alpha), dtype=np.float64),
            "log_priors": np.log(priors).astype(np.float64),
            "mu_loc": np.array(mu_loc, dtype=np.float64),
            "mu_scale": np.array(mu_scale, dtype=np.float64),
            "wishart_df": np.array(wishart_df, dtype=np.float64),
            "wishart_scale": wishart_scale_n,
            "mu": mu,
            "kappa": kappa.astype(np.float64),
            "nu": nu.astype(np.float64),
            "psi": psi.astype(np.float64),
        },
    )


def nimbus_qda_update(model: NimbusModel, X: np.ndarray, y: np.ndarray) -> NimbusModel:
    """Update an existing QDA model with additional labeled observations.

    Args:
        model: A model returned by `nimbus_qda_fit` or `nimbus_qda_update`.
        X: Feature matrix of shape (n_trials, n_features).
        y: Integer labels of shape (n_trials,). Uses the model's `label_base`.

    Returns:
        Updated NimbusModel with refreshed posterior parameters. If new labels
        contain unseen classes, the model expands `n_classes`.

    Raises:
        ValueError: If X has incompatible shape or y is out of range.
    """
    Xn = np.asarray(X, dtype=np.float64)
    yn = np.asarray(y)
    if Xn.ndim != 2:
        raise ValueError("X must be 2D: (n_trials, n_features)")
    if yn.ndim != 1:
        raise ValueError("y must be 1D: (n_trials,)")
    if Xn.shape[0] != yn.shape[0]:
        raise ValueError("X and y must have same number of rows")

    label_base = int(np.asarray(model.params["label_base"], dtype=np.int64))
    y0 = yn.astype(np.int64) - label_base
    if np.min(y0) < 0:
        raise ValueError("y out of range for label_base")

    old_n_classes = int(np.asarray(model.params["n_classes"], dtype=np.int64))
    new_n_classes = int(max(old_n_classes, int(np.max(y0)) + 1))

    mu = np.asarray(model.params["mu"], dtype=np.float64)
    kappa = np.asarray(model.params["kappa"], dtype=np.float64)
    nu = np.asarray(model.params["nu"], dtype=np.float64)
    psi = np.asarray(model.params["psi"], dtype=np.float64)

    n_features = int(Xn.shape[1])
    if mu.shape[1] != n_features:
        raise ValueError("X has different number of features than model")

    class_counts = np.asarray(model.params["class_counts"], dtype=np.int64)
    class_prior_alpha = float(np.asarray(model.params["class_prior_alpha"], dtype=np.float64))

    mu_loc = float(np.asarray(model.params["mu_loc"], dtype=np.float64))
    mu_scale = float(np.asarray(model.params["mu_scale"], dtype=np.float64))
    wishart_df = float(np.asarray(model.params["wishart_df"], dtype=np.float64))
    wishart_scale_n = np.asarray(model.params["wishart_scale"], dtype=np.float64)
    psi_prior_base = wishart_scale_n
    kappa0 = (float(np.trace(psi_prior_base)) / float(n_features)) / float(mu_scale**2)
    mu_prior_base = np.full((n_features,), mu_loc, dtype=np.float64)

    if new_n_classes > old_n_classes:
        mu = np.concatenate([mu, np.tile(mu_prior_base[None, :], (new_n_classes - old_n_classes, 1))], axis=0)
        kappa = np.concatenate([kappa, np.full((new_n_classes - old_n_classes,), kappa0, dtype=np.float64)], axis=0)
        nu = np.concatenate([nu, np.full((new_n_classes - old_n_classes,), wishart_df, dtype=np.float64)], axis=0)
        psi = np.concatenate(
            [psi, np.tile(psi_prior_base[None, :, :], (new_n_classes - old_n_classes, 1, 1))], axis=0
        )
        class_counts = np.concatenate([class_counts, np.zeros((new_n_classes - old_n_classes,), dtype=np.int64)], axis=0)

    new_counts = np.bincount(y0, minlength=new_n_classes).astype(np.int64)
    class_counts = class_counts + new_counts

    mu_new = mu.copy()
    kappa_new = kappa.copy()
    nu_new = nu.copy()
    psi_new = psi.copy()

    for k in range(new_n_classes):
        nk = int(new_counts[k])
        if nk == 0:
            continue
        Xk = Xn[y0 == k]
        xbar = np.mean(Xk, axis=0)
        xc = Xk - xbar
        Sk = xc.T @ xc
        kappa_k = float(kappa[k] + nk)
        mu_new[k] = (kappa[k] * mu[k] + float(nk) * xbar) / kappa_k
        kappa_new[k] = kappa_k
        nu_new[k] = nu[k] + float(nk)
        dmu = xbar - mu[k]
        psi_new[k] = psi[k] + Sk + (kappa[k] * float(nk) / kappa_k) * np.outer(dmu, dmu)

    priors = (class_counts.astype(np.float64) + class_prior_alpha) / float(
        np.sum(class_counts) + new_n_classes * class_prior_alpha
    )

    return NimbusModel(
        model_type="nimbus_qda",
        params={
            **model.params,
            "n_classes": np.array(new_n_classes, dtype=np.int64),
            "class_counts": class_counts.astype(np.int64),
            "log_priors": np.log(priors).astype(np.float64),
            "mu": mu_new.astype(np.float64),
            "kappa": kappa_new.astype(np.float64),
            "nu": nu_new.astype(np.float64),
            "psi": psi_new.astype(np.float64),
        },
    )


