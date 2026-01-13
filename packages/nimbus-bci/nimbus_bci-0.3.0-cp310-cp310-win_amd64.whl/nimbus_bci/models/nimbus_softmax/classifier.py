"""sklearn-compatible NimbusSoftmax classifier.

Bayesian multinomial logistic regression using Polya-Gamma variational inference.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.utils.validation import check_array

from ..base import NimbusClassifierMixin
from .learning import nimbus_softmax_fit, nimbus_softmax_update
from .inference import nimbus_softmax_predict_proba, nimbus_softmax_predict_samples


class NimbusSoftmax(NimbusClassifierMixin):
    """Bayesian Multinomial Logistic Regression classifier.

    A Bayesian softmax classifier using Polya-Gamma variational inference
    with a reference-class parameterization.

    This classifier is sklearn-compatible and works with pipelines, cross-validation,
    and hyperparameter tuning.

    Parameters
    ----------
    w_loc : float, default=0.0
        Prior mean for weight parameters.
    w_scale : float, default=1.0
        Prior scale for weight parameters (> 0).
    b_loc : float, default=0.0
        Prior mean for bias parameters.
    b_scale : float, default=1.0
        Prior scale for bias parameters (> 0).
    learning_rate : float, default=0.2
        Damping factor for variational updates (0, 1].
    num_steps : int, default=50
        Number of coordinate ascent variational inference sweeps.
    num_posterior_samples : int, default=50
        Number of posterior samples for prediction.
    rng_seed : int, default=0
        Random seed for reproducibility.

    Attributes
    ----------
    classes_ : np.ndarray of shape (n_classes,)
        Unique class labels discovered during fit.
    n_classes_ : int
        Number of classes.
    n_features_in_ : int
        Number of features seen during fit.
    model_ : NimbusModel
        The underlying fitted Nimbus model with posterior parameters.

    Examples
    --------
    >>> from nimbus_bci import NimbusSoftmax
    >>> clf = NimbusSoftmax(num_steps=100)
    >>> clf.fit(X_train, y_train)
    >>> probs = clf.predict_proba(X_test)
    >>> predictions = clf.predict(X_test)

    Using with sklearn pipelines:

    >>> from sklearn.pipeline import make_pipeline
    >>> from sklearn.preprocessing import StandardScaler
    >>> pipe = make_pipeline(StandardScaler(), NimbusSoftmax())
    >>> pipe.fit(X_train, y_train)

    See Also
    --------
    NimbusLDA : LDA with shared covariance (faster, closed-form).
    NimbusQDA : QDA with class-specific covariances.

    Notes
    -----
    This classifier uses Polya-Gamma augmentation for variational inference,
    providing a fully Bayesian treatment of logistic regression. It is more
    computationally expensive than LDA/GMM but can model non-Gaussian decision
    boundaries.

    The Bayesian formulation provides:
    - Uncertainty quantification via posterior sampling
    - Natural regularization via priors
    - Online learning via iterative updates
    """

    def __init__(
        self,
        w_loc: float = 0.0,
        w_scale: float = 1.0,
        b_loc: float = 0.0,
        b_scale: float = 1.0,
        learning_rate: float = 0.2,
        num_steps: int = 50,
        num_posterior_samples: int = 50,
        rng_seed: int = 0,
    ):
        self.w_loc = w_loc
        self.w_scale = w_scale
        self.b_loc = b_loc
        self.b_scale = b_scale
        self.learning_rate = learning_rate
        self.num_steps = num_steps
        self.num_posterior_samples = num_posterior_samples
        self.rng_seed = rng_seed

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NimbusSoftmax":
        """Fit the Bayesian Softmax model.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self : NimbusSoftmax
            Fitted estimator.
        """
        X, y = self._validate_fit_params(X, y)

        # Encode labels to 0-indexed
        y_encoded = self._encode_labels(y)

        self.model_ = nimbus_softmax_fit(
            X=X,
            y=y_encoded,
            n_classes=self.n_classes_,
            label_base=0,
            w_loc=self.w_loc,
            w_scale=self.w_scale,
            b_loc=self.b_loc,
            b_scale=self.b_scale,
            rng_seed=self.rng_seed,
            learning_rate=self.learning_rate,
            num_steps=self.num_steps,
        )

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return class probability estimates.

        Uses Monte Carlo sampling from the posterior for uncertainty estimation.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        np.ndarray of shape (n_samples, n_classes)
            Class probabilities. Each row sums to 1.
        """
        X = self._validate_predict_params(X)
        return nimbus_softmax_predict_proba(
            self.model_,
            X,
            num_posterior_samples=self.num_posterior_samples,
            rng_seed=self.rng_seed + 1,  # Different seed for prediction
        )

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Predicted class labels (in original label space).
        """
        proba = self.predict_proba(X)
        indices = np.argmax(proba, axis=1)
        return self.classes_[indices]

    def partial_fit(
        self, X: np.ndarray, y: np.ndarray, classes: Optional[np.ndarray] = None
    ) -> "NimbusSoftmax":
        """Incremental fit on a batch of samples.

        This method allows online learning by updating the model
        with new data without retraining from scratch.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        classes : array-like of shape (n_classes,), optional
            List of all possible classes. Required on first call,
            ignored on subsequent calls.

        Returns
        -------
        self : NimbusSoftmax
            Updated estimator.
        """
        if not hasattr(self, "model_"):
            # First call - perform full fit
            if classes is not None:
                self.classes_ = np.asarray(classes)
                self.n_classes_ = len(self.classes_)
                self._label_encoder = {c: i for i, c in enumerate(self.classes_)}
                self._label_decoder = {i: c for c, i in self._label_encoder.items()}
            return self.fit(X, y)

        # Subsequent calls - update existing model
        X = check_array(X, dtype=np.float64)
        y = np.asarray(y)

        if X.shape[1] != self.n_features_in_:
            raise ValueError(
                f"X has {X.shape[1]} features, but {self.__class__.__name__} "
                f"was fitted with {self.n_features_in_} features."
            )

        y_encoded = self._encode_labels(y)
        self.model_ = nimbus_softmax_update(self.model_, X, y_encoded)

        return self

    def predict_samples(
        self, X: np.ndarray, num_samples: Optional[int] = None, rng_seed: Optional[int] = None
    ) -> np.ndarray:
        """Draw label samples from the posterior predictive distribution.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.
        num_samples : int, optional
            Number of posterior samples. Defaults to num_posterior_samples.
        rng_seed : int, optional
            Random seed. Defaults to rng_seed + 2.

        Returns
        -------
        np.ndarray of shape (num_samples, n_samples)
            Sampled class labels for each posterior sample and input sample.
        """
        X = self._validate_predict_params(X)

        num_samples = num_samples or self.num_posterior_samples
        rng_seed = rng_seed or (self.rng_seed + 2)

        samples = nimbus_softmax_predict_samples(
            self.model_,
            X,
            num_posterior_samples=num_samples,
            rng_seed=rng_seed,
        )

        # Decode labels back to original space
        # samples shape: (num_samples, n_input_samples)
        return np.array([[self._label_decoder[int(s)] for s in row] for row in samples])

