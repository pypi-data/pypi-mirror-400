"""sklearn-compatible NimbusSTS classifier.

Bayesian Structural Time Series classifier using Extended Kalman Filter.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.utils.validation import check_array

from ..base import NimbusClassifierMixin
from .learning import nimbus_sts_fit, nimbus_sts_update
from .inference import nimbus_sts_predict_proba


class NimbusSTS(NimbusClassifierMixin):
    """Bayesian Structural Time Series classifier.

    A classifier that combines feature-based classification with latent
    state dynamics using Extended Kalman Filter inference.

    Model Structure
    ---------------
    Latent dynamics: z_t = A @ z_{t-1} + w_t, where w_t ~ N(0, Q)
    Class logits: W @ x_t + H @ z_t + b
    Probabilities: softmax(logits)

    The latent state z captures temporal patterns (e.g., class prior drift)
    that persist across samples. During training, the EKF updates z using
    observed labels. During inference, use propagate_state() to advance
    the prior without labels.

    Parameters
    ----------
    state_dim : int or None, default=None
        Dimension of latent state. If None, set to n_classes - 1.
    w_loc : float, default=0.0
        Prior mean for feature weights.
    w_scale : float, default=1.0
        Prior scale for feature weights.
    transition_cov : float or None, default=None
        Process noise covariance (Q). Controls state drift speed.
        If None, auto-estimated from data.
        
        Typical values:
        - 0.001: Very slow drift (multi-day stability)
        - 0.01: Moderate drift (within-session adaptation)
        - 0.1: Fast drift (rapid environmental changes)
        
        Rule of thumb: Set to 1% of expected signal variance.
    observation_cov : float, default=1.0
        Observation noise covariance (R).
    transition_matrix : np.ndarray or None, default=None
        State transition matrix A of shape (state_dim, state_dim).
        If None, uses identity matrix (random walk dynamics).
    learning_rate : float, default=0.1
        Step size for parameter updates.
    num_steps : int, default=50
        Number of learning iterations.
    rng_seed : int, default=0
        Random seed for reproducibility.
    verbose : bool, default=False
        Print convergence diagnostics during training.

    Attributes
    ----------
    classes_ : np.ndarray of shape (n_classes,)
        Unique class labels discovered during fit.
    n_classes_ : int
        Number of classes.
    n_features_in_ : int
        Number of features seen during fit.
    model_ : NimbusModel
        The underlying fitted model with posterior parameters.

    Examples
    --------
    Basic usage with sklearn API:

    >>> from nimbus_bci import NimbusSTS
    >>> clf = NimbusSTS(transition_cov=0.05, num_steps=100)
    >>> clf.fit(X_train, y_train)
    >>> predictions = clf.predict(X_test)

    Using with sklearn pipelines:

    >>> from sklearn.pipeline import make_pipeline
    >>> from sklearn.preprocessing import StandardScaler
    >>> pipe = make_pipeline(StandardScaler(), NimbusSTS())
    >>> pipe.fit(X_train, y_train)

    Cross-validation:

    >>> from sklearn.model_selection import cross_val_score
    >>> scores = cross_val_score(NimbusSTS(), X, y, cv=5)
    >>> print(f"Accuracy: {scores.mean():.3f}")

    Online learning with delayed feedback (BCI paradigm):

    >>> clf = NimbusSTS()
    >>> clf.fit(X_calibration, y_calibration)
    >>> 
    >>> for x_trial, y_feedback in online_session:
    ...     clf.propagate_state()  # Advance time without label
    ...     pred = clf.predict(x_trial)
    ...     # ... user performs action ...
    ...     clf.partial_fit(x_trial, y_feedback)  # Update with true label

    State inspection and transfer across sessions:

    >>> # Day 1: Train and save state
    >>> clf.fit(X_day1, y_day1)
    >>> z_final, P_final = clf.get_latent_state()
    >>> 
    >>> # Day 2: Transfer state with increased uncertainty
    >>> clf_new = NimbusSTS()
    >>> clf_new.fit(X_day2_calib, y_day2_calib)
    >>> clf_new.set_latent_state(z_final * 0.5, P_final * 2.0)

    Notes
    -----
    - predict_proba() never mutates state (consistent with sklearn API)
    - propagate_state() explicitly advances the latent state prior
    - partial_fit() requires labels (performs EKF measurement update)
    - reset_state() returns to initial state from training

    See Also
    --------
    NimbusLDA : Static LDA (faster, for stationary data).
    NimbusQDA : Static QDA (class-specific covariances).
    NimbusSoftmax : Static softmax (non-Gaussian boundaries).
    """

    def __init__(
        self,
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
    ):
        self.state_dim = state_dim
        self.w_loc = w_loc
        self.w_scale = w_scale
        self.transition_cov = transition_cov
        self.observation_cov = observation_cov
        self.transition_matrix = transition_matrix
        self.learning_rate = learning_rate
        self.num_steps = num_steps
        self.rng_seed = rng_seed
        self.verbose = verbose

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NimbusSTS":
        X, y = self._validate_fit_params(X, y)
        y_encoded = self._encode_labels(y)

        self.model_ = nimbus_sts_fit(
            X=X,
            y=y_encoded,
            n_classes=self.n_classes_,
            label_base=0,
            state_dim=self.state_dim,
            w_loc=self.w_loc,
            w_scale=self.w_scale,
            transition_cov=self.transition_cov,
            observation_cov=self.observation_cov,
            transition_matrix=self.transition_matrix,
            learning_rate=self.learning_rate,
            num_steps=self.num_steps,
            rng_seed=self.rng_seed,
            verbose=self.verbose,
        )

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = self._validate_predict_params(X)
        # Treat rows as conditionally independent by default. For time-ordered
        # evaluation, call `propagate_state()` between samples (recommended) or
        # use the functional API with evolve_state=True.
        return nimbus_sts_predict_proba(self.model_, X, evolve_state=False)

    def predict(self, X: np.ndarray) -> np.ndarray:
        proba = self.predict_proba(X)
        indices = np.argmax(proba, axis=1)
        return self.classes_[indices]

    def partial_fit(
        self, X: np.ndarray, y: np.ndarray, classes: Optional[np.ndarray] = None
    ) -> "NimbusSTS":
        if not hasattr(self, "model_"):
            if classes is not None:
                self.classes_ = np.asarray(classes)
                self.n_classes_ = len(self.classes_)
                self._label_encoder = {c: i for i, c in enumerate(self.classes_)}
                self._label_decoder = {i: c for c, i in self._label_encoder.items()}
            return self.fit(X, y)

        X = check_array(X, dtype=np.float64)
        y = np.asarray(y)

        if X.shape[1] != self.n_features_in_:
            raise ValueError(
                f"X has {X.shape[1]} features, but {self.__class__.__name__} "
                f"was fitted with {self.n_features_in_} features."
            )

        y_encoded = self._encode_labels(y)
        self.model_ = nimbus_sts_update(
            self.model_, X, y_encoded, learning_rate=self.learning_rate
        )

        return self

    def propagate_state(self, n_steps: int = 1) -> "NimbusSTS":
        """Advance the latent state using prior dynamics only.

        Applies the state transition z_t = A @ z_{t-1} without any
        measurement update. Use this for streaming inference when
        labels are not yet available.

        Parameters
        ----------
        n_steps : int, default=1
            Number of time steps to propagate.

        Returns
        -------
        self : NimbusSTS
            Classifier with updated state.
        """
        if not hasattr(self, "model_"):
            raise ValueError("Model has not been fitted yet.")

        params = self.model_.params
        A = params["A"]
        Q = params["Q"]
        z_mean = params["z_mean"].copy()
        z_cov = params["z_cov"].copy()

        for _ in range(n_steps):
            z_mean = A @ z_mean
            z_cov = A @ z_cov @ A.T + Q

        new_params = params.copy()
        new_params["z_mean"] = z_mean
        new_params["z_cov"] = z_cov
        self.model_ = type(self.model_)(
            model_type=self.model_.model_type,
            params=new_params,
        )

        return self

    def reset_state(self) -> "NimbusSTS":
        """Reset the latent state to initial values from training.

        Returns
        -------
        self : NimbusSTS
            Classifier with reset state.
        """
        if not hasattr(self, "model_"):
            raise ValueError("Model has not been fitted yet.")

        params = self.model_.params
        new_params = params.copy()
        new_params["z_mean"] = params["z_mean_init"].copy()
        new_params["z_cov"] = params["z_cov_init"].copy()
        self.model_ = type(self.model_)(
            model_type=self.model_.model_type,
            params=new_params,
        )

        return self

    def get_latent_state(self) -> Optional[tuple[np.ndarray, np.ndarray]]:
        """Get the current latent state.

        Returns
        -------
        tuple of (z_mean, z_cov) or None
            z_mean : np.ndarray of shape (state_dim,)
                Current state mean.
            z_cov : np.ndarray of shape (state_dim, state_dim)
                Current state covariance.
            Returns None if model not fitted.
        """
        if not hasattr(self, "model_"):
            return None
        return self.model_.params["z_mean"].copy(), self.model_.params["z_cov"].copy()

    def set_latent_state(
        self, z_mean: np.ndarray, z_cov: Optional[np.ndarray] = None
    ) -> "NimbusSTS":
        """Set the latent state manually.

        Parameters
        ----------
        z_mean : np.ndarray of shape (state_dim,)
            New state mean.
        z_cov : np.ndarray of shape (state_dim, state_dim), optional
            New state covariance. If None, keeps current covariance.

        Returns
        -------
        self : NimbusSTS
            Classifier with updated state.
        """
        if not hasattr(self, "model_"):
            raise ValueError("Model has not been fitted yet.")

        params = self.model_.params
        state_dim = params["state_dim"]

        z_mean = np.asarray(z_mean, dtype=np.float64)
        if z_mean.shape != (state_dim,):
            raise ValueError(f"z_mean must have shape ({state_dim},)")

        new_params = params.copy()
        new_params["z_mean"] = z_mean

        if z_cov is not None:
            z_cov = np.asarray(z_cov, dtype=np.float64)
            if z_cov.shape != (state_dim, state_dim):
                raise ValueError(f"z_cov must have shape ({state_dim}, {state_dim})")
            new_params["z_cov"] = z_cov

        self.model_ = type(self.model_)(
            model_type=self.model_.model_type,
            params=new_params,
        )

        return self
