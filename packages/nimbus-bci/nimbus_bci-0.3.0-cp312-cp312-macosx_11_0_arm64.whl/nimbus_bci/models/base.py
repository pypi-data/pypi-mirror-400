"""Base classes for Nimbus models.

This module provides the abstract base class for all Nimbus classifiers
with sklearn-compatible APIs.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Optional

import numpy as np

from ..compat.sklearn_compat import BaseNimbusClassifier
from ..nimbus_io import NimbusModel


class NimbusClassifierMixin(BaseNimbusClassifier):
    """Mixin providing common functionality for Nimbus classifiers.

    This extends BaseNimbusClassifier with model-specific utilities
    like extracting posterior parameters for diagnostics.
    """

    model_: NimbusModel

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "NimbusClassifierMixin":
        """Fit the model to training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self
            Fitted estimator.
        """
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return class probability estimates.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        np.ndarray of shape (n_samples, n_classes)
            Class probabilities.
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Predicted class labels.
        """
        pass

    @abstractmethod
    def partial_fit(
        self, X: np.ndarray, y: np.ndarray, classes: Optional[np.ndarray] = None
    ) -> "NimbusClassifierMixin":
        """Incremental fit on a batch of samples.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        classes : array-like of shape (n_classes,), optional
            Classes to expect (required for first call).

        Returns
        -------
        self
            Updated estimator.
        """
        pass

    def get_model(self) -> NimbusModel:
        """Get the underlying NimbusModel.

        Returns
        -------
        NimbusModel
            The fitted model.

        Raises
        ------
        ValueError
            If the model has not been fitted.
        """
        if not hasattr(self, "model_"):
            raise ValueError("Model has not been fitted yet.")
        return self.model_

    def get_class_means(self) -> Optional[np.ndarray]:
        """Get posterior class means if available.

        Returns
        -------
        np.ndarray or None
            Class means of shape (n_classes, n_features), or None if not available.
        """
        if not hasattr(self, "model_"):
            return None
        if "mu" in self.model_.params:
            return np.asarray(self.model_.params["mu"])
        return None

    def get_precision_matrix(self) -> Optional[np.ndarray]:
        """Get posterior precision matrix if available.

        Returns
        -------
        np.ndarray or None
            Precision matrix, or None if not available.
        """
        if not hasattr(self, "model_"):
            return None
        if "psi" in self.model_.params:
            # For LDA/GMM, psi is the scatter matrix; precision is related to inverse
            return np.asarray(self.model_.params["psi"])
        return None

