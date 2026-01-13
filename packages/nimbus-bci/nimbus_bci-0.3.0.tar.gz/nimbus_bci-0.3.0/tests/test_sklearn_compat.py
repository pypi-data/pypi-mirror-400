"""Tests for sklearn-compatible classifier wrappers."""

import numpy as np
import pytest
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from nimbus_bci import NimbusLDA, NimbusQDA, NimbusSoftmax


@pytest.fixture
def synthetic_data():
    """Create synthetic classification data."""
    np.random.seed(42)
    n_samples = 100
    n_features = 4
    n_classes = 3

    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, n_classes, n_samples)

    # Shift classes to make them separable
    for k in range(n_classes):
        X[y == k] += k * 0.5

    return X, y


class TestNimbusLDA:
    """Tests for NimbusLDA sklearn wrapper."""

    def test_fit_predict_shapes(self, synthetic_data):
        """Test fit and predict return correct shapes."""
        X, y = synthetic_data
        clf = NimbusLDA()
        clf.fit(X, y)

        predictions = clf.predict(X)
        assert predictions.shape == (len(y),)

        proba = clf.predict_proba(X)
        assert proba.shape == (len(y), 3)
        assert np.allclose(proba.sum(axis=1), 1.0)

    def test_partial_fit(self, synthetic_data):
        """Test online learning with partial_fit."""
        X, y = synthetic_data
        clf = NimbusLDA()

        # First batch
        clf.partial_fit(X[:50], y[:50], classes=np.unique(y))

        # Second batch
        clf.partial_fit(X[50:], y[50:])

        predictions = clf.predict(X)
        assert predictions.shape == (len(y),)

    def test_get_params(self, synthetic_data):
        """Test sklearn get_params interface."""
        clf = NimbusLDA(mu_scale=5.0, class_prior_alpha=2.0)
        params = clf.get_params()

        assert params["mu_scale"] == 5.0
        assert params["class_prior_alpha"] == 2.0

    def test_set_params(self, synthetic_data):
        """Test sklearn set_params interface."""
        clf = NimbusLDA()
        clf.set_params(mu_scale=10.0)

        assert clf.mu_scale == 10.0

    def test_pipeline_integration(self, synthetic_data):
        """Test integration with sklearn Pipeline."""
        X, y = synthetic_data
        pipe = make_pipeline(StandardScaler(), NimbusLDA())
        pipe.fit(X, y)

        predictions = pipe.predict(X)
        assert predictions.shape == (len(y),)

    def test_cross_validation(self, synthetic_data):
        """Test compatibility with sklearn cross_val_score."""
        X, y = synthetic_data
        clf = NimbusLDA()

        scores = cross_val_score(clf, X, y, cv=3)
        assert len(scores) == 3
        assert all(0 <= s <= 1 for s in scores)

    def test_label_encoding(self):
        """Test handling of non-zero-indexed labels."""
        np.random.seed(42)
        X = np.random.randn(50, 4)
        y = np.array([10, 20, 30] * 16 + [10, 20])  # Labels 10, 20, 30

        clf = NimbusLDA()
        clf.fit(X, y)

        predictions = clf.predict(X)
        assert set(predictions).issubset({10, 20, 30})


class TestNimbusQDA:
    """Tests for NimbusQDA sklearn wrapper."""

    def test_fit_predict_shapes(self, synthetic_data):
        """Test fit and predict return correct shapes."""
        X, y = synthetic_data
        clf = NimbusQDA()
        clf.fit(X, y)

        predictions = clf.predict(X)
        assert predictions.shape == (len(y),)

        proba = clf.predict_proba(X)
        assert proba.shape == (len(y), 3)

    def test_get_class_covariances(self, synthetic_data):
        """Test getting class covariances."""
        X, y = synthetic_data
        clf = NimbusQDA()
        clf.fit(X, y)

        covs = clf.get_class_covariances()
        assert covs is not None
        assert covs.shape[0] == 3  # n_classes


class TestNimbusSoftmax:
    """Tests for NimbusSoftmax sklearn wrapper."""

    def test_fit_predict_shapes(self, synthetic_data):
        """Test fit and predict return correct shapes."""
        X, y = synthetic_data
        clf = NimbusSoftmax(num_steps=10)  # Fewer steps for speed
        clf.fit(X, y)

        predictions = clf.predict(X)
        assert predictions.shape == (len(y),)

        proba = clf.predict_proba(X)
        assert proba.shape == (len(y), 3)

    def test_predict_samples(self, synthetic_data):
        """Test posterior sampling."""
        X, y = synthetic_data
        clf = NimbusSoftmax(num_steps=10)
        clf.fit(X, y)

        samples = clf.predict_samples(X[:5], num_samples=10)
        assert samples.shape == (10, 5)





