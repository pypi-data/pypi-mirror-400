"""sklearn-compatible NimbusLDA classifier.

Bayesian Linear Discriminant Analysis with shared covariance (pooled).
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.utils.validation import check_array

from ..base import NimbusClassifierMixin
from .learning import nimbus_lda_fit, nimbus_lda_update
from .inference import nimbus_lda_predict_proba


class NimbusLDA(NimbusClassifierMixin):
    """Bayesian Linear Discriminant Analysis classifier.

    A Bayesian LDA classifier with shared covariance (pooled) across all classes,
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
        Wishart degrees of freedom for precision matrix prior.
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
    >>> from nimbus_bci import NimbusLDA
    >>> clf = NimbusLDA(mu_scale=5.0)
    >>> clf.fit(X_train, y_train)
    >>> probs = clf.predict_proba(X_test)
    >>> predictions = clf.predict(X_test)

    Using with sklearn pipelines:

    >>> from sklearn.pipeline import make_pipeline
    >>> from sklearn.preprocessing import StandardScaler
    >>> pipe = make_pipeline(StandardScaler(), NimbusLDA())
    >>> pipe.fit(X_train, y_train)

    Cross-validation:

    >>> from sklearn.model_selection import cross_val_score
    >>> scores = cross_val_score(NimbusLDA(), X, y, cv=5)
    >>> print(f"Accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")

    Hyperparameter tuning:

    >>> from sklearn.model_selection import GridSearchCV
    >>> param_grid = {'mu_scale': [1.0, 3.0, 5.0], 'class_prior_alpha': [0.5, 1.0]}
    >>> grid = GridSearchCV(NimbusLDA(), param_grid, cv=5)
    >>> grid.fit(X, y)

    Online learning:

    >>> clf = NimbusLDA()
    >>> clf.partial_fit(X_batch1, y_batch1, classes=[0, 1, 2])
    >>> clf.partial_fit(X_batch2, y_batch2)  # Incremental update

    See Also
    --------
    NimbusQDA : QDA with class-specific covariances.
    NimbusSoftmax : Bayesian multinomial logistic regression.

    Notes
    -----
    LDA assumes all classes share the same covariance structure. This is
    appropriate when class distributions have similar shapes but different
    means. For heterogeneous covariances, use NimbusQDA instead.

    The Bayesian formulation provides:
    - Natural regularization via priors
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

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NimbusLDA":
        """Fit the Bayesian LDA model.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self : NimbusLDA
            Fitted estimator.
        """
        X, y = self._validate_fit_params(X, y)

        # Determine wishart_df
        wishart_df = self.wishart_df
        if wishart_df is None:
            wishart_df = float(X.shape[1] + 2)

        # Encode labels to 0-indexed
        y_encoded = self._encode_labels(y)

        self.model_ = nimbus_lda_fit(
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
        return nimbus_lda_predict_proba(self.model_, X)

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
    ) -> "NimbusLDA":
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
        self : NimbusLDA
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
        self.model_ = nimbus_lda_update(self.model_, X, y_encoded)

        return self

