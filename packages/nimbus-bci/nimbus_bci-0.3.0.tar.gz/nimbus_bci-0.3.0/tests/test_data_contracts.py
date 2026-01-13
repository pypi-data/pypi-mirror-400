"""Tests for data contracts (BCIData, BCIMetadata)."""

import numpy as np
import pytest

from nimbus_bci.data import BCIData, BCIMetadata, validate_data, check_model_compatibility


class TestBCIMetadata:
    """Tests for BCIMetadata dataclass."""

    def test_valid_metadata(self):
        """Test creating valid metadata."""
        metadata = BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=16,
            n_classes=4,
        )
        assert metadata.sampling_rate == 250.0
        assert metadata.n_features == 16

    def test_invalid_sampling_rate(self):
        """Test that negative sampling rate raises error."""
        with pytest.raises(ValueError, match="sampling_rate must be positive"):
            BCIMetadata(
                sampling_rate=-100.0,
                paradigm="motor_imagery",
                feature_type="csp",
                n_features=16,
                n_classes=4,
            )

    def test_invalid_paradigm(self):
        """Test that invalid paradigm raises error."""
        with pytest.raises(ValueError, match="paradigm must be one of"):
            BCIMetadata(
                sampling_rate=250.0,
                paradigm="invalid_paradigm",
                feature_type="csp",
                n_features=16,
                n_classes=4,
            )

    def test_invalid_n_classes(self):
        """Test that n_classes < 2 raises error."""
        with pytest.raises(ValueError, match="n_classes must be >= 2"):
            BCIMetadata(
                sampling_rate=250.0,
                paradigm="motor_imagery",
                feature_type="csp",
                n_features=16,
                n_classes=1,
            )

    def test_is_streaming(self):
        """Test streaming mode detection."""
        batch_meta = BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=16,
            n_classes=4,
        )
        assert batch_meta.is_streaming is False

        streaming_meta = BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=16,
            n_classes=4,
            chunk_size=125,
        )
        assert streaming_meta.is_streaming is True

    def test_recommended_chunk_size(self):
        """Test paradigm-specific chunk size recommendations."""
        mi_meta = BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=16,
            n_classes=4,
        )
        assert mi_meta.get_recommended_chunk_size() == 125  # 500ms at 250Hz


class TestBCIData:
    """Tests for BCIData dataclass."""

    @pytest.fixture
    def valid_metadata(self):
        return BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=16,
            n_classes=4,
        )

    def test_valid_3d_data(self, valid_metadata):
        """Test creating valid 3D data."""
        features = np.random.randn(16, 250, 100)
        labels = np.random.randint(0, 4, 100)

        data = BCIData(features, valid_metadata, labels)

        assert data.n_trials == 100
        assert data.n_samples == 250
        assert data.has_labels()

    def test_valid_2d_data(self, valid_metadata):
        """Test creating valid 2D data (single trial)."""
        features = np.random.randn(16, 250)

        data = BCIData(features, valid_metadata)

        assert data.n_trials == 1
        assert data.n_samples == 250
        assert not data.has_labels()

    def test_feature_mismatch(self, valid_metadata):
        """Test that feature count mismatch raises error."""
        features = np.random.randn(8, 250, 100)  # Wrong n_features

        with pytest.raises(ValueError, match="features has 8 features"):
            BCIData(features, valid_metadata)

    def test_label_count_mismatch(self, valid_metadata):
        """Test that label count mismatch raises error."""
        features = np.random.randn(16, 250, 100)
        labels = np.random.randint(0, 4, 50)  # Wrong length

        with pytest.raises(ValueError, match="labels has 50 elements"):
            BCIData(features, valid_metadata, labels)

    def test_get_trial(self, valid_metadata):
        """Test getting individual trials."""
        features = np.random.randn(16, 250, 100)
        data = BCIData(features, valid_metadata)

        trial = data.get_trial(0)
        assert trial.shape == (16, 250)

    def test_check_nan(self, valid_metadata):
        """Test NaN detection."""
        features = np.random.randn(16, 250, 10)
        data = BCIData(features, valid_metadata)
        assert data.check_nan() is True

        features[0, 0, 0] = np.nan
        data_nan = BCIData(features, valid_metadata)
        assert data_nan.check_nan() is False


class TestValidateData:
    """Tests for validate_data function."""

    @pytest.fixture
    def valid_metadata(self):
        return BCIMetadata(
            sampling_rate=250.0,
            paradigm="motor_imagery",
            feature_type="csp",
            n_features=4,
            n_classes=2,
        )

    def test_valid_data_passes(self, valid_metadata):
        """Test that valid data passes validation."""
        features = np.random.randn(4, 100, 50)
        labels = np.random.randint(0, 2, 50)
        data = BCIData(features, valid_metadata, labels)

        assert validate_data(data) is True

    def test_nan_values_fail(self, valid_metadata):
        """Test that NaN values fail validation."""
        features = np.random.randn(4, 100, 10)
        features[0, 0, 0] = np.nan
        data = BCIData(features, valid_metadata)

        with pytest.raises(ValueError, match="NaN values"):
            validate_data(data)

    def test_require_labels(self, valid_metadata):
        """Test require_labels parameter."""
        features = np.random.randn(4, 100, 10)
        data = BCIData(features, valid_metadata)  # No labels

        with pytest.raises(ValueError, match="Labels are required"):
            validate_data(data, require_labels=True)

    def test_zero_variance_features(self, valid_metadata):
        """Test that constant features fail validation."""
        features = np.random.randn(4, 100, 10)
        features[0, :, :] = 1.0  # Constant feature
        data = BCIData(features, valid_metadata)

        with pytest.raises(ValueError, match="zero variance"):
            validate_data(data)





