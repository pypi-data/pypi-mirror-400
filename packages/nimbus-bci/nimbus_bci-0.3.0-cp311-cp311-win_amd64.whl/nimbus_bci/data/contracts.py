"""Data contracts for BCI data structures.

This module defines the core data structures for representing
EEG/BCI data in a standardized format compatible with Nimbus models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal

import numpy as np


# Valid paradigm types
ParadigmType = Literal["motor_imagery", "p300", "ssvep", "erp", "custom"]

# Valid feature types
FeatureType = Literal["raw", "csp", "bandpower", "erp_amplitude", "custom"]

# Valid temporal aggregation methods
AggregationType = Literal["mean", "logvar", "last", "max", "median", "var", "std"]


@dataclass(frozen=True)
class BCIMetadata:
    """Metadata describing BCI recording and preprocessing.

    This immutable dataclass contains all metadata needed to properly
    interpret and process BCI features.

    Parameters
    ----------
    sampling_rate : float
        Original sampling rate in Hz (e.g., 250.0, 512.0).
    paradigm : str
        BCI paradigm type. One of:
        - "motor_imagery": Motor imagery (left/right hand, feet, tongue)
        - "p300": P300 event-related potential
        - "ssvep": Steady-state visual evoked potential
        - "erp": General event-related potential
        - "custom": Custom paradigm
    feature_type : str
        Type of extracted features. One of:
        - "raw": Raw EEG channels (no feature extraction)
        - "csp": Common Spatial Patterns features
        - "bandpower": Band power features
        - "erp_amplitude": ERP amplitude features
        - "custom": Custom feature type
    n_features : int
        Number of features (channels or extracted features).
    n_classes : int
        Number of classification classes.
    chunk_size : int or None, default=None
        Number of samples per chunk for streaming mode.
        If None, batch mode is assumed.
    temporal_aggregation : str, default="mean"
        Method for aggregating temporal dimension. One of:
        - "mean": Mean across time (default, general purpose)
        - "logvar": Log-variance (recommended for CSP features)
        - "last": Last time sample
        - "max": Maximum value across time
        - "median": Median across time
        - "var": Variance across time
        - "std": Standard deviation across time

    Examples
    --------
    >>> metadata = BCIMetadata(
    ...     sampling_rate=250.0,
    ...     paradigm="motor_imagery",
    ...     feature_type="csp",
    ...     n_features=16,
    ...     n_classes=4,
    ...     temporal_aggregation="logvar",
    ... )
    """

    sampling_rate: float
    paradigm: str
    feature_type: str
    n_features: int
    n_classes: int
    chunk_size: Optional[int] = None
    temporal_aggregation: str = "mean"

    def __post_init__(self):
        """Validate metadata values."""
        if self.sampling_rate <= 0:
            raise ValueError(f"sampling_rate must be positive, got {self.sampling_rate}")
        if self.n_features <= 0:
            raise ValueError(f"n_features must be positive, got {self.n_features}")
        if self.n_classes < 2:
            raise ValueError(f"n_classes must be >= 2, got {self.n_classes}")
        if self.chunk_size is not None and self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {self.chunk_size}")

        valid_paradigms = {"motor_imagery", "p300", "ssvep", "erp", "custom"}
        if self.paradigm not in valid_paradigms:
            raise ValueError(
                f"paradigm must be one of {valid_paradigms}, got '{self.paradigm}'"
            )

        valid_feature_types = {"raw", "csp", "bandpower", "erp_amplitude", "custom"}
        if self.feature_type not in valid_feature_types:
            raise ValueError(
                f"feature_type must be one of {valid_feature_types}, got '{self.feature_type}'"
            )

        valid_aggregations = {"mean", "logvar", "last", "max", "median", "var", "std"}
        if self.temporal_aggregation not in valid_aggregations:
            raise ValueError(
                f"temporal_aggregation must be one of {valid_aggregations}, "
                f"got '{self.temporal_aggregation}'"
            )

    @property
    def is_streaming(self) -> bool:
        """Check if metadata indicates streaming mode."""
        return self.chunk_size is not None

    def get_recommended_chunk_size(self) -> int:
        """Get recommended chunk size based on paradigm.

        Returns
        -------
        int
            Recommended number of samples per chunk.
        """
        # Recommendations based on literature and NimbusSDKCore
        chunk_durations = {
            "motor_imagery": 0.5,  # 500ms - ERD develops over time
            "p300": 0.3,  # 300ms - P300 peak at ~300-400ms
            "ssvep": 1.0,  # 1s - need time for steady-state
            "erp": 0.4,  # 400ms - depends on component
            "custom": 0.5,  # 500ms default
        }
        duration = chunk_durations.get(self.paradigm, 0.5)
        return int(self.sampling_rate * duration)


@dataclass
class BCIData:
    """Container for BCI features and metadata.

    This dataclass holds preprocessed BCI features along with
    metadata and optional labels for training.

    Parameters
    ----------
    features : np.ndarray
        Feature array with shape:
        - (n_features, n_samples, n_trials) for multiple trials
        - (n_features, n_samples) for a single trial
    metadata : BCIMetadata
        Metadata describing the data.
    labels : np.ndarray or None, default=None
        Class labels for each trial. Shape (n_trials,).
        Required for training, optional for inference.

    Attributes
    ----------
    n_trials : int
        Number of trials in the data.
    n_samples : int
        Number of time samples per trial.

    Examples
    --------
    >>> features = np.random.randn(16, 250, 100)  # 16 features, 250 samples, 100 trials
    >>> labels = np.random.randint(1, 5, size=100)  # 4 classes, 1-indexed
    >>> metadata = BCIMetadata(
    ...     sampling_rate=250.0,
    ...     paradigm="motor_imagery",
    ...     feature_type="csp",
    ...     n_features=16,
    ...     n_classes=4,
    ... )
    >>> data = BCIData(features, metadata, labels)
    >>> print(f"Trials: {data.n_trials}, Samples: {data.n_samples}")
    Trials: 100, Samples: 250
    """

    features: np.ndarray
    metadata: BCIMetadata
    labels: Optional[np.ndarray] = None

    def __post_init__(self):
        """Validate data consistency."""
        # Convert features to numpy array
        self.features = np.asarray(self.features, dtype=np.float64)

        # Validate feature dimensions
        if self.features.ndim not in (2, 3):
            raise ValueError(
                f"features must be 2D or 3D, got {self.features.ndim}D with shape {self.features.shape}"
            )

        # Check feature count matches metadata
        if self.features.shape[0] != self.metadata.n_features:
            raise ValueError(
                f"features has {self.features.shape[0]} features, "
                f"but metadata specifies {self.metadata.n_features}"
            )

        # Validate labels if provided
        if self.labels is not None:
            self.labels = np.asarray(self.labels)
            if self.labels.ndim != 1:
                raise ValueError(f"labels must be 1D, got {self.labels.ndim}D")

            expected_n_trials = self.features.shape[2] if self.features.ndim == 3 else 1
            if len(self.labels) != expected_n_trials:
                raise ValueError(
                    f"labels has {len(self.labels)} elements, "
                    f"but features has {expected_n_trials} trials"
                )

            # Check number of unique classes
            n_unique = len(np.unique(self.labels))
            if n_unique > self.metadata.n_classes:
                raise ValueError(
                    f"labels has {n_unique} unique classes, "
                    f"but metadata specifies {self.metadata.n_classes}"
                )

    @property
    def n_trials(self) -> int:
        """Number of trials in the data."""
        if self.features.ndim == 3:
            return self.features.shape[2]
        return 1

    @property
    def n_samples(self) -> int:
        """Number of time samples per trial."""
        return self.features.shape[1]

    def get_trial(self, idx: int) -> np.ndarray:
        """Get features for a specific trial.

        Parameters
        ----------
        idx : int
            Trial index.

        Returns
        -------
        np.ndarray
            Features of shape (n_features, n_samples).
        """
        if self.features.ndim == 2:
            if idx != 0:
                raise IndexError(f"Single trial data, index must be 0, got {idx}")
            return self.features
        return self.features[:, :, idx]

    def get_aggregated_features(self) -> np.ndarray:
        """Get temporally aggregated features.

        Aggregates the temporal dimension using the method specified
        in metadata.temporal_aggregation.

        Returns
        -------
        np.ndarray
            Aggregated features of shape (n_trials, n_features).
        """
        from ..utils.feature_aggregation import aggregate_temporal_features

        if self.features.ndim == 2:
            # Single trial
            agg = aggregate_temporal_features(self.features, self.metadata.temporal_aggregation)
            return agg.reshape(1, -1)

        # Multiple trials
        result = np.zeros((self.n_trials, self.metadata.n_features), dtype=np.float64)
        for i in range(self.n_trials):
            trial_features = self.features[:, :, i]
            result[i] = aggregate_temporal_features(
                trial_features, self.metadata.temporal_aggregation
            )
        return result

    def has_labels(self) -> bool:
        """Check if data has labels."""
        return self.labels is not None

    def check_nan(self) -> bool:
        """Check for NaN values in features.

        Returns
        -------
        bool
            True if no NaN values, False otherwise.
        """
        return not np.any(np.isnan(self.features))

    def check_inf(self) -> bool:
        """Check for infinite values in features.

        Returns
        -------
        bool
            True if no infinite values, False otherwise.
        """
        return not np.any(np.isinf(self.features))

