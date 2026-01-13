from __future__ import annotations

from typing import Literal

import jax
import jax.numpy as jnp
import numpy as np

from ...nimbus_io import NimbusModel


def _jax_dtype_from_numpy(x: np.ndarray) -> jnp.dtype:
    if x.dtype == np.float64:
        return jnp.float64 if jax.config.jax_enable_x64 else jnp.float32
    if x.dtype == np.float32:
        return jnp.float32
    return jnp.float32


def _pg_expected_omega(c: jax.Array) -> jax.Array:
    dtype = c.dtype
    one = jnp.array(1, dtype=dtype)
    two = one + one
    half = one / two
    eps = jnp.finfo(dtype).eps
    c1 = jnp.maximum(c, eps)
    return half / c1 * jnp.tanh(half * c1)


def _pg_binary_update(
    Xa: jax.Array,
    z: jax.Array,
    offset: jax.Array,
    m0: jax.Array,
    prec0: jax.Array,
    m: jax.Array,
    S: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    dtype = Xa.dtype
    one = jnp.array(1, dtype=dtype)
    two = one + one
    half = one / two
    eps = jnp.finfo(dtype).eps

    psi_mean = Xa @ m - offset
    psi_var = jnp.sum((Xa @ S) * Xa, axis=1)
    c = jnp.sqrt(psi_mean * psi_mean + psi_var + eps)
    omega = _pg_expected_omega(c)

    prec = prec0 + Xa.T @ (Xa * omega[:, None])
    kappa = z - half
    b = prec0 @ m0 + Xa.T @ (kappa + omega * offset)

    L = jnp.linalg.cholesky(prec)
    m_new = jax.scipy.linalg.cho_solve((L, True), b)
    eye = jnp.eye(int(prec.shape[0]), dtype=dtype)
    S_new = jax.scipy.linalg.cho_solve((L, True), eye)
    return m_new, S_new


def _build_logits(
    X_aug: jax.Array,
    beta_mean: jax.Array,
    non_ref_classes: jax.Array,
    ref_class: int,
    n_classes: int,
) -> jax.Array:
    n = int(X_aug.shape[0])
    logits = jnp.zeros((n, int(n_classes)), dtype=X_aug.dtype)
    eta = X_aug @ beta_mean.T
    logits = logits.at[:, non_ref_classes].set(eta)
    logits = logits.at[:, int(ref_class)].set(jnp.zeros((n,), dtype=X_aug.dtype))
    return logits


def nimbus_softmax_fit(
    X: np.ndarray,
    y: np.ndarray,
    n_classes: int,
    label_base: Literal[0, 1],
    w_loc: float,
    w_scale: float,
    b_loc: float,
    b_scale: float,
    rng_seed: int,
    learning_rate: float,
    num_steps: int,
) -> NimbusModel:
    """Fit Bayesian multinomial softmax regression using Polya-Gamma VI.

    This uses a reference-class softmax model and iteratively updates each
    class's parameters using a coupled one-vs-rest Polya-Gamma update.

    Args:
        X: Feature matrix of shape (n_trials, n_features).
        y: Integer labels of shape (n_trials,). Labels must be in
            {label_base, ..., label_base + n_classes - 1}.
        n_classes: Number of classes.
        label_base: 0 or 1, describing the minimum label value in y.
        w_loc: Scalar prior mean for weights (broadcast per feature).
        w_scale: Prior weight scale (>0).
        b_loc: Scalar prior mean for bias.
        b_scale: Prior bias scale (>0).
        rng_seed: Seed reserved for future use.
        learning_rate: Damping factor in (0, 1].
        num_steps: Number of coordinate sweeps (>=1).

    Returns:
        NimbusModel containing a Gaussian posterior approximation per class.

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
    if w_scale <= 0.0:
        raise ValueError("w_scale must be > 0")
    if b_scale <= 0.0:
        raise ValueError("b_scale must be > 0")
    if not (0.0 < learning_rate <= 1.0):
        raise ValueError("learning_rate must be in (0, 1]")
    if num_steps < 1:
        raise ValueError("num_steps must be >= 1")

    y0 = yn.astype(np.int64) - int(label_base)
    if np.min(y0) < 0 or np.max(y0) >= n_classes:
        raise ValueError("y out of range for n_classes/label_base")

    counts = np.bincount(y0, minlength=n_classes).astype(np.int64)
    ref_class = int(np.argmax(counts))
    non_ref = np.array([k for k in range(n_classes) if k != ref_class], dtype=np.int64)
    non_ref_j = jnp.asarray(non_ref, dtype=jnp.int32)

    dtype = _jax_dtype_from_numpy(Xn)
    Xj = jnp.asarray(Xn, dtype=dtype)
    yj = jnp.asarray(y0, dtype=jnp.int32)
    n_features = int(Xj.shape[1])

    one = jnp.ones((Xj.shape[0], 1), dtype=Xj.dtype)
    X_aug = jnp.concatenate([Xj, one], axis=1)
    d_aug = int(X_aug.shape[1])

    m_prior = jnp.concatenate(
        [jnp.full((n_features,), float(w_loc), dtype=Xj.dtype), jnp.array([float(b_loc)], dtype=Xj.dtype)], axis=0
    )

    w_prec = jnp.array(1.0 / float(w_scale * w_scale), dtype=Xj.dtype)
    b_prec = jnp.array(1.0 / float(b_scale * b_scale), dtype=Xj.dtype)
    prec_diag = jnp.concatenate([jnp.full((n_features,), w_prec, dtype=Xj.dtype), jnp.array([b_prec], dtype=Xj.dtype)])
    prec0 = jnp.diag(prec_diag)

    L0 = jnp.linalg.cholesky(prec0)
    S0 = jax.scipy.linalg.cho_solve((L0, True), jnp.eye(d_aug, dtype=Xj.dtype))

    beta_mean = jnp.tile(m_prior[None, :], (int(n_classes - 1), 1))
    beta_cov = jnp.tile(S0[None, :, :], (int(n_classes - 1), 1, 1))

    alpha = jnp.array(float(learning_rate), dtype=Xj.dtype)
    one_s = jnp.array(1, dtype=Xj.dtype)
    ref0 = jnp.zeros((X_aug.shape[0], 1), dtype=Xj.dtype)

    def sweep(_, state):
        beta_mean, beta_cov = state

        def update_one(i, st):
            beta_mean, beta_cov = st
            eta = X_aug @ beta_mean.T
            logZ = jax.nn.logsumexp(jnp.concatenate([eta, ref0], axis=1), axis=1)
            eta_i = eta[:, i]
            p = jnp.exp(eta_i - logZ)
            eps = jnp.finfo(Xj.dtype).eps
            logZ_minus = logZ + jnp.log(jnp.maximum(one_s - p, eps))

            z = (yj == non_ref_j[i]).astype(Xj.dtype)

            m_i = beta_mean[i]
            S_i = beta_cov[i]
            m_new, S_new = _pg_binary_update(X_aug, z, logZ_minus, m_prior, prec0, m_i, S_i)

            m_i = (one_s - alpha) * m_i + alpha * m_new
            S_i = (one_s - alpha) * S_i + alpha * S_new

            beta_mean = beta_mean.at[i].set(m_i)
            beta_cov = beta_cov.at[i].set(S_i)
            return beta_mean, beta_cov

        beta_mean, beta_cov = jax.lax.fori_loop(0, int(n_classes - 1), update_one, (beta_mean, beta_cov))
        return beta_mean, beta_cov

    beta_mean, beta_cov = jax.lax.fori_loop(0, int(num_steps), sweep, (beta_mean, beta_cov))
    beta_cov_chol = jnp.linalg.cholesky(beta_cov)

    return NimbusModel(
        model_type="nimbus_softmax",
        params={
            "backend": np.array("pg_softmax_ref", dtype=object),
            "n_classes": np.array(n_classes, dtype=np.int64),
            "label_base": np.array(int(label_base), dtype=np.int64),
            "ref_class": np.array(int(ref_class), dtype=np.int64),
            "non_ref_classes": np.asarray(non_ref, dtype=np.int64),
            "beta_mean": np.asarray(beta_mean),
            "beta_cov_chol": np.asarray(beta_cov_chol),
            "w_loc": np.array(w_loc, dtype=np.float64),
            "w_scale": np.array(w_scale, dtype=np.float64),
            "b_loc": np.array(b_loc, dtype=np.float64),
            "b_scale": np.array(b_scale, dtype=np.float64),
            "rng_seed": np.array(int(rng_seed), dtype=np.int64),
            "learning_rate": np.array(float(learning_rate), dtype=np.float64),
            "num_steps": np.array(int(num_steps), dtype=np.int64),
            "class_counts": counts,
        },
    )


def nimbus_softmax_update(model: NimbusModel, X: np.ndarray, y: np.ndarray) -> NimbusModel:
    """Update a softmax model with additional labeled observations."""
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

    ref_class = int(np.asarray(model.params["ref_class"], dtype=np.int64))
    non_ref = np.asarray(model.params["non_ref_classes"], dtype=np.int64)

    w_loc = float(np.asarray(model.params["w_loc"], dtype=np.float64))
    w_scale = float(np.asarray(model.params["w_scale"], dtype=np.float64))
    b_loc = float(np.asarray(model.params["b_loc"], dtype=np.float64))
    b_scale = float(np.asarray(model.params["b_scale"], dtype=np.float64))
    alpha = float(np.asarray(model.params["learning_rate"], dtype=np.float64))
    num_steps = int(np.asarray(model.params["num_steps"], dtype=np.int64))
    if not (0.0 < alpha <= 1.0):
        raise ValueError("learning_rate must be in (0, 1]")
    if num_steps < 1:
        raise ValueError("num_steps must be >= 1")

    dtype = _jax_dtype_from_numpy(Xn)
    Xj = jnp.asarray(Xn, dtype=dtype)
    yj = jnp.asarray(y0, dtype=jnp.int32)
    n_features = int(Xj.shape[1])

    one = jnp.ones((Xj.shape[0], 1), dtype=Xj.dtype)
    X_aug = jnp.concatenate([Xj, one], axis=1)
    d_aug = int(X_aug.shape[1])

    beta_mean = jnp.asarray(model.params["beta_mean"], dtype=Xj.dtype)
    beta_cov_chol = jnp.asarray(model.params["beta_cov_chol"], dtype=Xj.dtype)

    class_counts = np.asarray(model.params["class_counts"], dtype=np.int64)
    if new_n_classes > old_n_classes:
        add_classes = [k for k in range(new_n_classes) if k != ref_class and k not in set(non_ref.tolist())]
        if add_classes:
            non_ref = np.concatenate([non_ref, np.asarray(add_classes, dtype=np.int64)], axis=0)

            m_prior = np.concatenate([np.full((n_features,), w_loc, dtype=np.float64), np.array([b_loc], dtype=np.float64)])
            w_prec = 1.0 / float(w_scale * w_scale)
            b_prec = 1.0 / float(b_scale * b_scale)
            prec_diag = np.concatenate([np.full((n_features,), w_prec, dtype=np.float64), np.array([b_prec], dtype=np.float64)])
            prec0_np = np.diag(prec_diag)
            L0 = np.linalg.cholesky(prec0_np)
            S0 = np.linalg.solve(L0.T, np.linalg.solve(L0, np.eye(d_aug, dtype=np.float64)))

            beta_mean = jnp.concatenate([beta_mean, jnp.tile(jnp.asarray(m_prior, dtype=Xj.dtype)[None, :], (len(add_classes), 1))], axis=0)
            beta_cov_chol = jnp.concatenate([beta_cov_chol, jnp.tile(jnp.asarray(np.linalg.cholesky(S0), dtype=Xj.dtype)[None, :, :], (len(add_classes), 1, 1))], axis=0)

        if new_n_classes > class_counts.shape[0]:
            class_counts = np.concatenate([class_counts, np.zeros((new_n_classes - class_counts.shape[0],), dtype=np.int64)], axis=0)

    new_counts = np.bincount(y0, minlength=new_n_classes).astype(np.int64)
    class_counts = class_counts + new_counts

    alpha_j = jnp.array(float(alpha), dtype=Xj.dtype)
    one_s = jnp.array(1, dtype=Xj.dtype)
    non_ref_j = jnp.asarray(non_ref, dtype=jnp.int32)
    ref0 = jnp.zeros((X_aug.shape[0], 1), dtype=Xj.dtype)

    def sweep(_, state):
        beta_mean, beta_cov_chol = state

        def update_one(i, st):
            beta_mean, beta_cov_chol = st
            eta = X_aug @ beta_mean.T
            logZ = jax.nn.logsumexp(jnp.concatenate([eta, ref0], axis=1), axis=1)
            eta_i = eta[:, i]
            p = jnp.exp(eta_i - logZ)
            eps = jnp.finfo(Xj.dtype).eps
            logZ_minus = logZ + jnp.log(jnp.maximum(one_s - p, eps))

            z = (yj == non_ref_j[i]).astype(Xj.dtype)

            m0 = beta_mean[i]
            Lcov = beta_cov_chol[i]
            S0 = Lcov @ Lcov.T
            prec0 = jax.scipy.linalg.cho_solve((Lcov, True), jnp.eye(d_aug, dtype=Xj.dtype))

            m_i = beta_mean[i]
            m_new, S_new = _pg_binary_update(X_aug, z, logZ_minus, m0, prec0, m_i, S0)

            m_i = (one_s - alpha_j) * m_i + alpha_j * m_new
            S_i = (one_s - alpha_j) * S0 + alpha_j * S_new

            beta_mean = beta_mean.at[i].set(m_i)
            beta_cov_chol = beta_cov_chol.at[i].set(jnp.linalg.cholesky(S_i))
            return beta_mean, beta_cov_chol

        beta_mean, beta_cov_chol = jax.lax.fori_loop(0, int(non_ref.shape[0]), update_one, (beta_mean, beta_cov_chol))
        return beta_mean, beta_cov_chol

    beta_mean_u, beta_cov_u = jax.lax.fori_loop(0, int(num_steps), sweep, (beta_mean, beta_cov_chol))

    return NimbusModel(
        model_type="nimbus_softmax",
        params={
            **model.params,
            "backend": np.array("pg_softmax_ref", dtype=object),
            "n_classes": np.array(new_n_classes, dtype=np.int64),
            "non_ref_classes": np.asarray(non_ref, dtype=np.int64),
            "beta_mean": np.asarray(beta_mean_u),
            "beta_cov_chol": np.asarray(beta_cov_u),
            "class_counts": class_counts.astype(np.int64),
        },
    )
