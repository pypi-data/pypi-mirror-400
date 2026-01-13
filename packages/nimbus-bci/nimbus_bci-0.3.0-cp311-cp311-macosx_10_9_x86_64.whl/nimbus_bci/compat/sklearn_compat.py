"""sklearn compatibility utilities for Nimbus classifiers.

This module provides base classes and utilities for sklearn-compatible
Nimbus classifiers, enabling integration with sklearn pipelines,
cross-validation, and hyperparameter tuning.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


class BaseNimbusClassifier(BaseEstimator, ClassifierMixin):
    """Base class for sklearn-compatible Nimbus classifiers.

    This class provides the common interface and utilities for all
    Nimbus classifiers to work seamlessly with sklearn's ecosystem.

    Subclasses must implement:
        - fit(X, y) -> self
        - predict_proba(X) -> np.ndarray
        - predict(X) -> np.ndarray

    Attributes
    ----------
    classes_ : np.ndarray
        Unique class labels discovered during fit.
    n_classes_ : int
        Number of classes.
    n_features_in_ : int
        Number of features seen during fit.
    model_ : NimbusModel
        The underlying fitted Nimbus model.
    """

    # Sklearn estimator tags
    _estimator_type = "classifier"

    def _validate_fit_params(
        self, X: np.ndarray, y: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Validate and prepare data for fitting.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        X : np.ndarray
            Validated feature array.
        y : np.ndarray
            Validated target array.
        """
        X, y = check_X_y(X, y, dtype=np.float64)
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        self.n_features_in_ = X.shape[1]

        # Create label encoder for mapping to 0-indexed labels
        self._label_encoder = {c: i for i, c in enumerate(self.classes_)}
        self._label_decoder = {i: c for c, i in self._label_encoder.items()}

        return X, y

    def _validate_predict_params(self, X: np.ndarray) -> np.ndarray:
        """Validate data for prediction.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        X : np.ndarray
            Validated feature array.
        """
        check_is_fitted(self, ["model_", "classes_", "n_features_in_"])
        X = check_array(X, dtype=np.float64)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(
                f"X has {X.shape[1]} features, but {self.__class__.__name__} "
                f"was fitted with {self.n_features_in_} features."
            )
        return X

    def _encode_labels(self, y: np.ndarray) -> np.ndarray:
        """Encode labels to 0-indexed integers.

        Parameters
        ----------
        y : np.ndarray
            Original labels.

        Returns
        -------
        np.ndarray
            0-indexed integer labels.
        """
        return np.array([self._label_encoder[yi] for yi in y], dtype=np.int64)

    def _decode_labels(self, y_encoded: np.ndarray) -> np.ndarray:
        """Decode 0-indexed labels back to original labels.

        Parameters
        ----------
        y_encoded : np.ndarray
            0-indexed integer labels.

        Returns
        -------
        np.ndarray
            Original labels.
        """
        return np.array([self._label_decoder[int(yi)] for yi in y_encoded])

    def _more_tags(self) -> dict[str, Any]:
        """Return sklearn estimator tags.

        Returns
        -------
        dict
            Estimator tags for sklearn compatibility.
        """
        return {
            "requires_y": True,
            "poor_score": False,
            "_xfail_checks": {
                # Our models handle multiclass natively
                "check_classifiers_train": "Nimbus uses Bayesian inference",
            },
        }

    def score(self, X: np.ndarray, y: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> float:
        """Return mean accuracy on the given test data and labels.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test samples.
        y : array-like of shape (n_samples,)
            True labels.
        sample_weight : array-like of shape (n_samples,), optional
            Sample weights.

        Returns
        -------
        float
            Mean accuracy.
        """
        from sklearn.metrics import accuracy_score
        return accuracy_score(y, self.predict(X), sample_weight=sample_weight)

