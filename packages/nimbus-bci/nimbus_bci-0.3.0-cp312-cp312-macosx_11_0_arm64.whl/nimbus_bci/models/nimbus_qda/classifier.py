"""sklearn-compatible NimbusQDA classifier.

Bayesian Gaussian model with class-specific covariances (QDA).
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.utils.validation import check_array

from ..base import NimbusClassifierMixin
from .learning import nimbus_qda_fit, nimbus_qda_update
from .inference import nimbus_qda_predict_proba


class NimbusQDA(NimbusClassifierMixin):
    """Bayesian Quadratic Discriminant Analysis (QDA) classifier.

    A Bayesian QDA-style classifier with class-specific covariances,
    using conjugate Normal-Inverse-Wishart priors for closed-form posterior updates.

    This classifier is sklearn-compatible and works with pipelines, cross-validation,
    and hyperparameter tuning.

    Parameters
    ----------
    mu_loc : float, default=0.0
        Prior mean location for class means. Broadcast to all features.
    mu_scale : float, default=3.0
        Prior scale for class means (> 0). Controls prior uncertainty.
    wishart_df : float or None, default=None
        Wishart degrees of freedom for precision matrix priors.
        If None, set to n_features + 2 (minimum for valid prior).
    class_prior_alpha : float, default=1.0
        Dirichlet smoothing parameter for class priors (>= 0).
        Higher values lead to more uniform class priors.

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
    >>> from nimbus_bci import NimbusQDA
    >>> clf = NimbusQDA(mu_scale=5.0)
    >>> clf.fit(X_train, y_train)
    >>> probs = clf.predict_proba(X_test)
    >>> predictions = clf.predict(X_test)

    Using with sklearn pipelines:

    >>> from sklearn.pipeline import make_pipeline
    >>> from sklearn.preprocessing import StandardScaler
    >>> pipe = make_pipeline(StandardScaler(), NimbusQDA())
    >>> pipe.fit(X_train, y_train)

    See Also
    --------
    NimbusLDA : LDA with shared covariance (more efficient, less flexible).
    NimbusSoftmax : Bayesian multinomial logistic regression.

    Notes
    -----
    QDA allows each class to have its own covariance structure. This is more
    flexible than LDA but requires more parameters to estimate.
    Use when class distributions have different shapes.

    The Bayesian formulation provides:
    - Natural regularization via priors (critical for high-dimensional data)
    - Uncertainty quantification in predictions
    - Online learning via conjugate updates
    """

    def __init__(
        self,
        mu_loc: float = 0.0,
        mu_scale: float = 3.0,
        wishart_df: Optional[float] = None,
        class_prior_alpha: float = 1.0,
    ):
        self.mu_loc = mu_loc
        self.mu_scale = mu_scale
        self.wishart_df = wishart_df
        self.class_prior_alpha = class_prior_alpha

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NimbusQDA":
        """Fit the Bayesian QDA model.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self : NimbusQDA
            Fitted estimator.
        """
        X, y = self._validate_fit_params(X, y)

        # Determine wishart_df
        wishart_df = self.wishart_df
        if wishart_df is None:
            wishart_df = float(X.shape[1] + 2)

        # Encode labels to 0-indexed
        y_encoded = self._encode_labels(y)

        self.model_ = nimbus_qda_fit(
            X=X,
            y=y_encoded,
            n_classes=self.n_classes_,
            label_base=0,
            mu_loc=self.mu_loc,
            mu_scale=self.mu_scale,
            wishart_df=wishart_df,
            wishart_scale=np.eye(X.shape[1]),
            class_prior_alpha=self.class_prior_alpha,
        )

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return class probability estimates.

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
        return nimbus_qda_predict_proba(self.model_, X)

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
    ) -> "NimbusQDA":
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
        self : NimbusQDA
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
        self.model_ = nimbus_qda_update(self.model_, X, y_encoded)

        return self

    def get_class_covariances(self) -> Optional[np.ndarray]:
        """Get posterior covariance matrices for each class.

        Returns
        -------
        np.ndarray or None
            Covariance matrices of shape (n_classes, n_features, n_features),
            or None if not available.
        """
        if not hasattr(self, "model_"):
            return None
        if "psi" in self.model_.params:
            return np.asarray(self.model_.params["psi"])
        return None

