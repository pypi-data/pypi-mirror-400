"""Tests for utility functions."""

import numpy as np
import pytest

from nimbus_bci.utils import (
    aggregate_temporal_features,
    NormalizationParams,
    estimate_normalization_params,
    apply_normalization,
    check_normalization_status,
    diagnose_preprocessing,
    compute_fisher_score,
    rank_features_by_discriminability,
)
from nimbus_bci.utils.feature_aggregation import get_recommended_aggregation
from nimbus_bci.data import BCIData, BCIMetadata


class TestFeatureAggregation:
    """Tests for feature aggregation utilities."""

    def test_mean_aggregation(self):
        """Test mean temporal aggregation."""
        features = np.ones((4, 100))  # 4 features, 100 samples
        features[0, :50] = 0  # First half = 0, second half = 1

        result = aggregate_temporal_features(features, "mean")

        assert result.shape == (4,)
        assert result[0] == 0.5

    def test_logvar_aggregation(self):
        """Test log-variance aggregation."""
        features = np.random.randn(4, 100)
        result = aggregate_temporal_features(features, "logvar")

        assert result.shape == (4,)
        # Variance of random data is close to 1, log(1) = 0
        assert np.all(np.abs(result) < 2)

    def test_last_aggregation(self):
        """Test last sample aggregation."""
        features = np.arange(8).reshape(2, 4).astype(float)
        result = aggregate_temporal_features(features, "last")

        assert result.shape == (2,)
        assert result[0] == 3  # Last element of first row
        assert result[1] == 7  # Last element of second row

    def test_invalid_method(self):
        """Test invalid aggregation method raises error."""
        features = np.random.randn(4, 100)
        with pytest.raises(ValueError, match="Unknown aggregation method"):
            aggregate_temporal_features(features, "invalid")

    def test_recommended_aggregation(self):
        """Test paradigm-specific recommendations."""
        # Feature type takes priority
        assert get_recommended_aggregation("motor_imagery", "csp") == "logvar"
        assert get_recommended_aggregation("p300", "erp_amplitude") == "mean"
        assert get_recommended_aggregation("motor_imagery", "bandpower") == "mean"
        # Raw features use paradigm-specific defaults
        assert get_recommended_aggregation("motor_imagery", "raw") == "var"
        assert get_recommended_aggregation("p300", "raw") == "mean"


class TestNormalization:
    """Tests for normalization utilities."""

    def test_zscore_normalization(self):
        """Test z-score normalization."""
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]], dtype=float)

        params = estimate_normalization_params(X, method="zscore")
        X_norm = apply_normalization(X, params)

        # Check normalized data has ~0 mean and ~1 std
        assert np.allclose(X_norm.mean(axis=0), 0, atol=1e-10)
        assert np.allclose(X_norm.std(axis=0), 1, atol=1e-10)

    def test_minmax_normalization(self):
        """Test min-max normalization."""
        X = np.array([[0, 0], [5, 10], [10, 20]], dtype=float)

        params = estimate_normalization_params(X, method="minmax")
        X_norm = apply_normalization(X, params)

        # Check normalized data is in [0, 1]
        assert np.all(X_norm >= 0)
        assert np.all(X_norm <= 1)

    def test_robust_normalization(self):
        """Test robust normalization with outliers."""
        X = np.array([[0, 0], [1, 1], [2, 2], [100, 100]], dtype=float)  # Last row is outlier

        params = estimate_normalization_params(X, method="robust")
        X_norm = apply_normalization(X, params)

        # Median-based normalization should be less affected by outlier
        assert np.abs(X_norm[1, 0]) < np.abs(X_norm[3, 0])

    def test_3d_input(self):
        """Test normalization with 3D input."""
        # Shape: (n_features, n_samples, n_trials)
        X = np.random.randn(4, 100, 10) * 5 + 10

        params = estimate_normalization_params(X, method="zscore")
        X_norm = apply_normalization(X, params)

        assert X_norm.shape == X.shape

    def test_check_normalization_status(self):
        """Test normalization status check."""
        # Unnormalized data
        X_raw = np.random.randn(100, 4) * 10 + 50
        status = check_normalization_status(X_raw)
        assert not status.appears_normalized
        assert len(status.recommendations) > 0

        # Normalized data
        X_norm = (X_raw - X_raw.mean(axis=0)) / X_raw.std(axis=0)
        status_norm = check_normalization_status(X_norm)
        assert status_norm.appears_normalized


class TestPreprocessingDiagnostics:
    """Tests for preprocessing diagnostics."""

    @pytest.fixture
    def valid_metadata(self):
        return BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=4,
            n_classes=2,
        )

    def test_good_data_high_score(self, valid_metadata):
        """Test that good data gets high quality score."""
        features = np.random.randn(4, 100, 50)
        features = (features - features.mean()) / features.std()  # Normalize
        labels = np.random.randint(0, 2, 50)
        data = BCIData(features, valid_metadata, labels)

        report = diagnose_preprocessing(data)

        assert report.is_valid()
        assert report.quality_score > 0.5

    def test_nan_data_fails(self, valid_metadata):
        """Test that NaN data fails diagnostics."""
        features = np.random.randn(4, 100, 10)
        features[0, 0, 0] = np.nan
        data = BCIData(features, valid_metadata)

        report = diagnose_preprocessing(data)

        assert not report.is_valid()
        assert any("NaN" in e for e in report.errors)


class TestFisherScore:
    """Tests for Fisher score computation."""

    def test_discriminative_features(self):
        """Test Fisher score identifies discriminative features."""
        np.random.seed(42)
        n_samples = 100
        n_features = 4

        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 2, n_samples)

        # Make first feature highly discriminative
        X[y == 0, 0] = 0
        X[y == 1, 0] = 5

        scores = compute_fisher_score(X, y)

        # First feature should have highest score
        assert np.argmax(scores) == 0

    def test_ranking(self):
        """Test feature ranking by discriminability."""
        np.random.seed(42)
        X = np.random.randn(100, 4)
        y = np.random.randint(0, 2, 100)

        # Make features discriminative in order
        for i in range(4):
            X[y == 1, i] += (4 - i)

        ranking = rank_features_by_discriminability(X, y)

        # First feature should be ranked first (most discriminative)
        assert ranking[0] == 0

