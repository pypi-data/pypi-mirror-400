from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from ...nimbus_io import NimbusModel
from ...nimbus_math import nimbus_softmax


def _logits_from_beta(
    X: jax.Array,
    beta_mean: jax.Array,
    non_ref_classes: np.ndarray,
    ref_class: int,
    n_classes: int,
) -> jax.Array:
    n = int(X.shape[0])
    ones = jnp.ones((n, 1), dtype=X.dtype)
    X_aug = jnp.concatenate([X, ones], axis=1)
    logits = jnp.zeros((n, int(n_classes)), dtype=X.dtype)
    eta = X_aug @ beta_mean.T
    logits = logits.at[:, non_ref_classes].set(eta)
    logits = logits.at[:, int(ref_class)].set(jnp.zeros((n,), dtype=X.dtype))
    return logits


def nimbus_softmax_predict_proba(
    model: NimbusModel,
    X: np.ndarray,
    num_posterior_samples: int,
    rng_seed: int,
) -> np.ndarray:
    """Predict class probabilities for Bayesian multinomial softmax regression."""
    Xn = np.asarray(X, dtype=np.float64)
    if Xn.ndim != 2:
        raise ValueError("X must be 2D: (n_trials, n_features)")
    if num_posterior_samples < 1:
        raise ValueError("num_posterior_samples must be >= 1")

    n_classes = int(np.asarray(model.params["n_classes"], dtype=np.int64))
    ref_class = int(np.asarray(model.params["ref_class"], dtype=np.int64))
    non_ref = np.asarray(model.params["non_ref_classes"], dtype=np.int64)

    beta_mean = jnp.asarray(model.params["beta_mean"])
    beta_cov_chol = jnp.asarray(model.params["beta_cov_chol"], dtype=beta_mean.dtype)

    Xj = jnp.asarray(Xn, dtype=beta_mean.dtype)

    if int(num_posterior_samples) == 1:
        logits = _logits_from_beta(Xj, beta_mean, non_ref, ref_class, n_classes)
        probs = nimbus_softmax(logits)
        return np.asarray(probs)

    n = int(Xj.shape[0])
    d_aug = int(beta_mean.shape[1])

    rng_key = jax.random.PRNGKey(int(rng_seed))
    eps = jax.random.normal(
        rng_key,
        shape=(int(num_posterior_samples), int(n_classes - 1), d_aug),
        dtype=beta_mean.dtype,
    )

    beta_s = beta_mean[None, :, :] + jnp.einsum("kij,skj->ski", beta_cov_chol, eps)

    ones = jnp.ones((n, 1), dtype=Xj.dtype)
    X_aug = jnp.concatenate([Xj, ones], axis=1)
    eta = jnp.einsum("nd,skd->skn", X_aug, beta_s)

    logits_s = jnp.zeros((int(num_posterior_samples), n, int(n_classes)), dtype=Xj.dtype)
    logits_s = logits_s.at[:, :, non_ref].set(jnp.transpose(eta, (0, 2, 1)))
    logits_s = logits_s.at[:, :, int(ref_class)].set(jnp.zeros((int(num_posterior_samples), n), dtype=Xj.dtype))

    probs_s = jax.vmap(nimbus_softmax)(logits_s)
    probs = jnp.mean(probs_s, axis=0)
    return np.asarray(probs)


def nimbus_softmax_predict(
    model: NimbusModel,
    X: np.ndarray,
    num_posterior_samples: int,
    rng_seed: int,
) -> np.ndarray:
    """Predict the most likely class label for each row of X."""
    probs = nimbus_softmax_predict_proba(model, X, num_posterior_samples, rng_seed)
    label_base = int(np.asarray(model.params["label_base"], dtype=np.int64))
    return np.argmax(probs, axis=1).astype(np.int64) + label_base


def nimbus_softmax_predict_samples(
    model: NimbusModel,
    X: np.ndarray,
    num_posterior_samples: int,
    rng_seed: int,
) -> np.ndarray:
    """Draw label samples from the posterior predictive distribution."""
    Xn = np.asarray(X, dtype=np.float64)
    if Xn.ndim != 2:
        raise ValueError("X must be 2D: (n_trials, n_features)")
    if num_posterior_samples < 1:
        raise ValueError("num_posterior_samples must be >= 1")

    n_classes = int(np.asarray(model.params["n_classes"], dtype=np.int64))
    ref_class = int(np.asarray(model.params["ref_class"], dtype=np.int64))
    non_ref = np.asarray(model.params["non_ref_classes"], dtype=np.int64)

    beta_mean = jnp.asarray(model.params["beta_mean"])
    beta_cov_chol = jnp.asarray(model.params["beta_cov_chol"], dtype=beta_mean.dtype)

    Xj = jnp.asarray(Xn, dtype=beta_mean.dtype)
    n = int(Xj.shape[0])
    d_aug = int(beta_mean.shape[1])

    rng_key = jax.random.PRNGKey(int(rng_seed))
    key_eps, key_cat = jax.random.split(rng_key, 2)

    eps = jax.random.normal(
        key_eps,
        shape=(int(num_posterior_samples), int(n_classes - 1), d_aug),
        dtype=beta_mean.dtype,
    )
    beta_s = beta_mean[None, :, :] + jnp.einsum("kij,skj->ski", beta_cov_chol, eps)

    ones = jnp.ones((n, 1), dtype=Xj.dtype)
    X_aug = jnp.concatenate([Xj, ones], axis=1)
    eta = jnp.einsum("nd,skd->skn", X_aug, beta_s)

    logits_s = jnp.zeros((int(num_posterior_samples), n, int(n_classes)), dtype=Xj.dtype)
    logits_s = logits_s.at[:, :, non_ref].set(jnp.transpose(eta, (0, 2, 1)))
    logits_s = logits_s.at[:, :, int(ref_class)].set(jnp.zeros((int(num_posterior_samples), n), dtype=Xj.dtype))

    probs = jax.vmap(nimbus_softmax)(logits_s)
    logp = jnp.log(probs + jnp.finfo(Xj.dtype).eps)

    keys = jax.random.split(key_cat, int(num_posterior_samples))
    y0 = jax.vmap(lambda kk, lp: jax.random.categorical(kk, lp, axis=-1))(keys, logp)

    label_base = int(np.asarray(model.params["label_base"], dtype=np.int64))
    return np.asarray(y0).astype(np.int64) + label_base
