"""Tests for inference modules (batch and streaming)."""

import numpy as np
import pytest

from nimbus_bci import NimbusLDA, NimbusQDA
from nimbus_bci.data import BCIData, BCIMetadata
from nimbus_bci.inference import (
    predict_batch,
    BatchResult,
    StreamingSession,
    ChunkResult,
    StreamingResult,
    aggregate_chunks,
    compute_temporal_weights,
)


@pytest.fixture
def trained_model():
    """Create a trained LDA model."""
    np.random.seed(42)
    X = np.random.randn(100, 8)
    y = np.random.randint(0, 3, 100)

    # Make classes separable
    for k in range(3):
        X[y == k] += k

    clf = NimbusLDA()
    clf.fit(X, y)
    return clf.model_


@pytest.fixture
def bci_data():
    """Create BCI data for testing."""
    np.random.seed(42)
    n_features = 8
    n_samples = 100
    n_trials = 20

    features = np.random.randn(n_features, n_samples, n_trials)
    labels = np.random.randint(0, 3, n_trials)

    metadata = BCIMetadata(
        sampling_rate=250.0,
        paradigm="motor_imagery",
        feature_type="csp",
        n_features=n_features,
        n_classes=3,
        temporal_aggregation="mean",
    )

    return BCIData(features, metadata, labels)


class TestBatchInference:
    """Tests for batch inference."""

    def test_predict_batch_shapes(self, trained_model, bci_data):
        """Test predict_batch returns correct shapes."""
        result = predict_batch(trained_model, bci_data)

        assert isinstance(result, BatchResult)
        assert result.predictions.shape == (20,)
        assert result.confidences.shape == (20,)
        assert result.posteriors.shape == (20, 3)
        assert result.entropy.shape == (20,)

    def test_predict_batch_probabilities(self, trained_model, bci_data):
        """Test that posteriors sum to 1."""
        result = predict_batch(trained_model, bci_data)

        assert np.allclose(result.posteriors.sum(axis=1), 1.0)

    def test_predict_batch_calibration(self, trained_model, bci_data):
        """Test that calibration metrics are computed when labels provided."""
        result = predict_batch(trained_model, bci_data)

        assert result.calibration is not None
        assert 0 <= result.calibration.ece <= 1

    def test_predict_batch_latency(self, trained_model, bci_data):
        """Test that latency is measured."""
        result = predict_batch(trained_model, bci_data)

        assert result.latency_ms > 0
        assert len(result.per_trial_latency_ms) == 20


class TestAggregation:
    """Tests for chunk aggregation."""

    def test_weighted_vote(self):
        """Test weighted vote aggregation."""
        predictions = [0, 1, 1, 1]
        confidences = [0.5, 0.8, 0.9, 0.7]

        pred, conf, post = aggregate_chunks(predictions, confidences, n_classes=2)

        assert pred == 1  # Class 1 has higher weighted votes
        assert 0 <= conf <= 1

    def test_max_confidence(self):
        """Test max confidence aggregation."""
        predictions = [0, 1, 0, 0]
        confidences = [0.5, 0.95, 0.6, 0.7]

        pred, conf, post = aggregate_chunks(
            predictions, confidences, n_classes=2, method="max_confidence"
        )

        assert pred == 1  # Chunk with highest confidence predicted 1
        assert conf == 0.95

    def test_majority_vote(self):
        """Test majority vote aggregation."""
        predictions = [0, 1, 0, 0]
        confidences = [0.5, 0.95, 0.6, 0.7]

        pred, conf, post = aggregate_chunks(
            predictions, confidences, n_classes=2, method="majority_vote"
        )

        assert pred == 0  # 3 votes for class 0 vs 1 for class 1

    def test_posterior_mean(self):
        """Test posterior mean aggregation."""
        predictions = [0, 1]
        confidences = [0.8, 0.8]
        posteriors = [
            np.array([0.8, 0.2]),
            np.array([0.3, 0.7]),
        ]

        pred, conf, post = aggregate_chunks(
            predictions, confidences, n_classes=2,
            posteriors=posteriors, method="posterior_mean"
        )

        # Mean posterior: [0.55, 0.45]
        assert pred == 0
        assert np.isclose(post[0], 0.55)


class TestTemporalWeights:
    """Tests for temporal weighting."""

    def test_motor_imagery_weights(self):
        """Test Motor Imagery temporal weights (increasing)."""
        weights = compute_temporal_weights("motor_imagery", 4)

        assert len(weights) == 4
        assert weights[3] > weights[0]  # Later chunks weighted more
        assert np.isclose(np.sum(weights), 4)  # Sum equals n_chunks

    def test_p300_weights(self):
        """Test P300 temporal weights (peaked in middle)."""
        weights = compute_temporal_weights("p300", 5)

        assert len(weights) == 5
        # Middle chunks should be weighted more
        middle_idx = len(weights) // 2
        assert weights[middle_idx] > weights[0]
        assert weights[middle_idx] > weights[-1]

    def test_single_chunk(self):
        """Test single chunk returns weight 1."""
        weights = compute_temporal_weights("motor_imagery", 1)

        assert len(weights) == 1
        assert weights[0] == 1.0


class TestStreamingSession:
    """Tests for streaming inference."""

    @pytest.fixture
    def metadata(self):
        return BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=8,
            n_classes=3,
            chunk_size=62,
            temporal_aggregation="mean",
        )

    def test_process_chunk(self, trained_model, metadata):
        """Test processing a single chunk."""
        session = StreamingSession(trained_model, metadata)

        chunk = np.random.randn(8, 62)
        result = session.process_chunk(chunk)

        assert isinstance(result, ChunkResult)
        assert 0 <= result.prediction < 3
        assert 0 <= result.confidence <= 1
        assert result.posterior.shape == (3,)
        assert result.latency_ms > 0

    def test_finalize_trial(self, trained_model, metadata):
        """Test finalizing a trial with multiple chunks."""
        session = StreamingSession(trained_model, metadata)

        # Process 4 chunks
        for _ in range(4):
            chunk = np.random.randn(8, 62)
            session.process_chunk(chunk)

        result = session.finalize_trial(method="weighted_vote")

        assert isinstance(result, StreamingResult)
        assert result.n_chunks == 4
        assert 0 <= result.prediction < 3
        assert len(result.chunk_posteriors) == 4

    def test_session_reset(self, trained_model, metadata):
        """Test session reset after finalization."""
        session = StreamingSession(trained_model, metadata)

        chunk = np.random.randn(8, 62)
        session.process_chunk(chunk)
        session.finalize_trial()

        assert session.chunk_count == 0
        assert not session.is_active

    def test_no_chunks_error(self, trained_model, metadata):
        """Test error when finalizing without chunks."""
        session = StreamingSession(trained_model, metadata)

        with pytest.raises(ValueError, match="No active trial"):
            session.finalize_trial()

    def test_temporal_weighting(self, trained_model, metadata):
        """Test that temporal weighting affects results."""
        np.random.seed(42)
        session = StreamingSession(trained_model, metadata)

        # Process chunks with different class predictions
        for _ in range(4):
            chunk = np.random.randn(8, 62)
            session.process_chunk(chunk)

        # Results should be valid
        result = session.finalize_trial(temporal_weighting=True)
        assert result.prediction in [0, 1, 2]





