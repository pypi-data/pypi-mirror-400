"""Tests for metrics modules."""

import numpy as np
import pytest

from nimbus_bci.metrics import (
    compute_entropy,
    compute_mahalanobis_distances,
    compute_outlier_scores,
    CalibrationMetrics,
    compute_calibration_metrics,
    calculate_itr,
    compute_balance,
    OnlinePerformanceTracker,
    assess_trial_quality,
)
from nimbus_bci.metrics.diagnostics import compute_entropy_batch


class TestEntropy:
    """Tests for entropy computation."""

    def test_uniform_distribution(self):
        """Test entropy of uniform distribution."""
        uniform = np.array([0.25, 0.25, 0.25, 0.25])
        entropy = compute_entropy(uniform)
        assert np.isclose(entropy, 2.0)  # log2(4) = 2 bits

    def test_certain_distribution(self):
        """Test entropy of certain distribution."""
        certain = np.array([1.0, 0.0, 0.0, 0.0])
        entropy = compute_entropy(certain)
        assert entropy < 0.01  # Near 0 bits

    def test_entropy_batch(self):
        """Test batch entropy computation."""
        posteriors = np.array([
            [0.9, 0.1],
            [0.5, 0.5],
            [0.1, 0.9],
        ])
        entropies = compute_entropy_batch(posteriors)
        assert entropies.shape == (3,)
        assert entropies[1] > entropies[0]  # Uniform has higher entropy


class TestMahalanobisDistances:
    """Tests for Mahalanobis distance computation."""

    def test_basic_computation(self):
        """Test basic Mahalanobis distance computation."""
        features = np.array([[0.0, 0.0], [10.0, 10.0]])
        class_means = [np.array([0.0, 0.0]), np.array([10.0, 10.0])]
        precisions = [np.eye(2), np.eye(2)]

        distances = compute_mahalanobis_distances(features, class_means, precisions)

        assert distances.shape == (2, 2)
        # First sample should be close to first class
        assert distances[0, 0] < distances[0, 1]
        # Second sample should be close to second class
        assert distances[1, 1] < distances[1, 0]

    def test_outlier_scores(self):
        """Test outlier score computation."""
        distances = np.array([
            [1.0, 5.0],
            [4.0, 3.0],
        ])
        scores = compute_outlier_scores(distances)

        assert scores.shape == (2,)
        assert np.allclose(scores, [1.0, 3.0])  # Minimum distance to any class


class TestCalibration:
    """Tests for calibration metrics."""

    def test_perfect_calibration(self):
        """Test calibration with perfectly calibrated predictions."""
        # If confidence matches accuracy, ECE should be low
        predictions = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        labels = np.array([0, 1, 0, 1, 0, 1, 0, 1])  # All correct
        confidences = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

        metrics = compute_calibration_metrics(predictions, confidences, labels)

        assert metrics.ece <= 0.01
        assert metrics.is_well_calibrated()

    def test_calibration_metrics_structure(self):
        """Test calibration metrics structure."""
        predictions = np.array([0, 1, 1, 0])
        confidences = np.array([0.9, 0.8, 0.7, 0.6])
        labels = np.array([0, 1, 0, 0])

        metrics = compute_calibration_metrics(predictions, confidences, labels)

        assert isinstance(metrics, CalibrationMetrics)
        assert 0 <= metrics.ece <= 1
        assert 0 <= metrics.mce <= 1
        assert len(metrics.bin_accuracies) == metrics.n_bins


class TestITR:
    """Tests for Information Transfer Rate."""

    def test_perfect_accuracy(self):
        """Test ITR with perfect accuracy."""
        itr = calculate_itr(1.0, 4, 4.0)
        # ITR should be log2(4) * 60/4 = 2 * 15 = 30 bits/min
        assert np.isclose(itr, 30.0)

    def test_chance_level(self):
        """Test ITR at chance level."""
        itr = calculate_itr(0.25, 4, 4.0)  # Chance level for 4 classes
        # At chance, ITR should be very close to 0 (may have tiny numerical error)
        assert itr < 0.01

    def test_below_chance(self):
        """Test ITR below chance is small or clipped."""
        itr = calculate_itr(0.1, 4, 4.0)  # Below chance
        # Below chance ITR should be small (formula allows small positive)
        assert itr < 5.0  # Much less than typical good performance

    def test_invalid_n_classes(self):
        """Test that invalid n_classes raises error."""
        with pytest.raises(ValueError):
            calculate_itr(0.8, 1, 4.0)

    def test_invalid_trial_duration(self):
        """Test that invalid trial_duration raises error."""
        with pytest.raises(ValueError):
            calculate_itr(0.8, 4, 0.0)


class TestBalance:
    """Tests for class balance computation."""

    def test_perfect_balance(self):
        """Test perfectly balanced predictions."""
        predictions = np.array([0, 1, 2, 3])
        balance = compute_balance(predictions, 4)
        assert balance == 1.0

    def test_completely_imbalanced(self):
        """Test completely imbalanced predictions."""
        predictions = np.array([0, 0, 0, 0])
        balance = compute_balance(predictions, 4)
        assert balance <= 0.5  # Completely imbalanced = 0.5 or lower


class TestOnlinePerformanceTracker:
    """Tests for OnlinePerformanceTracker."""

    def test_update_and_metrics(self):
        """Test updating tracker and getting metrics."""
        tracker = OnlinePerformanceTracker(window_size=10)

        for i in range(5):
            metrics = tracker.update(prediction=i % 2, label=i % 2, confidence=0.8)

        assert metrics["accuracy"] == 1.0
        assert metrics["mean_confidence"] == 0.8
        assert metrics["n_total"] == 5

    def test_window_size(self):
        """Test sliding window behavior."""
        tracker = OnlinePerformanceTracker(window_size=5)

        # Add 10 items, but window only keeps 5
        for i in range(10):
            tracker.update(prediction=0, label=0, confidence=0.8)

        metrics = tracker._compute_metrics()
        assert metrics["window_size"] == 5

    def test_reset(self):
        """Test reset functionality."""
        tracker = OnlinePerformanceTracker()
        tracker.update(0, 0, 0.8)
        tracker.reset()

        assert tracker.n_total == 0


class TestTrialQuality:
    """Tests for trial quality assessment."""

    def test_valid_trial(self):
        """Test valid trial passes quality check."""
        features = np.random.randn(16, 250)
        quality = assess_trial_quality(
            features,
            confidence=0.9,
            confidence_threshold=0.6,
        )

        assert quality.is_valid
        assert quality.rejection_reason is None

    def test_low_confidence_rejection(self):
        """Test low confidence causes rejection."""
        features = np.random.randn(16, 250)
        quality = assess_trial_quality(
            features,
            confidence=0.3,
            confidence_threshold=0.6,
        )

        assert not quality.is_valid
        assert quality.rejection_reason == "low_confidence"

    def test_nan_features_rejection(self):
        """Test NaN features cause rejection."""
        features = np.random.randn(16, 250)
        features[0, 0] = np.nan

        quality = assess_trial_quality(features, confidence=0.9)

        assert not quality.is_valid
        assert quality.rejection_reason == "features_contain_nan"

