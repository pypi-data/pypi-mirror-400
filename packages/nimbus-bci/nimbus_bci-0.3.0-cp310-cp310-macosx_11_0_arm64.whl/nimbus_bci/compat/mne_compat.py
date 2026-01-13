"""MNE-Python compatibility utilities.

MNE is an optional dependency. Install with:
    pip install nimbus-bci[mne]

This module provides functions to convert between MNE's data structures
and Nimbus SDK's BCIData format.
"""

from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..data.contracts import BCIData, BCIMetadata


def _check_mne_installed():
    """Check if MNE-Python is installed and return the module."""
    try:
        import mne
        return mne
    except ImportError as e:
        raise ImportError(
            "MNE-Python is required for this function. "
            "Install with: pip install mne"
        ) from e


def from_mne_epochs(
    epochs,  # mne.Epochs
    paradigm: str = "motor_imagery",
    feature_type: str = "raw",
    labels: Optional[np.ndarray] = None,
    temporal_aggregation: str = "mean",
) -> "BCIData":
    """Convert MNE Epochs to BCIData.

    Parameters
    ----------
    epochs : mne.Epochs
        MNE Epochs object.
    paradigm : str, default="motor_imagery"
        BCI paradigm ("motor_imagery", "p300", "ssvep", "erp", "custom").
    feature_type : str, default="raw"
        Feature type ("raw", "csp", "bandpower", "erp_amplitude", "custom").
    labels : array-like, optional
        Override labels (default: use epochs.events[:, 2]).
    temporal_aggregation : str, default="mean"
        Method for aggregating temporal dimension.

    Returns
    -------
    BCIData
        Data ready for Nimbus models.

    Examples
    --------
    >>> import mne
    >>> from nimbus_bci.compat import from_mne_epochs
    >>> epochs = mne.Epochs(raw, events, tmin=0, tmax=4)
    >>> bci_data = from_mne_epochs(epochs, paradigm="motor_imagery")
    >>> print(f"Trials: {bci_data.n_trials}, Features: {bci_data.metadata.n_features}")
    """
    from ..data.contracts import BCIData, BCIMetadata

    mne = _check_mne_installed()

    # Extract data: (n_epochs, n_channels, n_times)
    data = epochs.get_data()

    # Convert to Nimbus format: (n_features, n_samples, n_trials)
    # MNE: (n_epochs, n_channels, n_times)
    # Nimbus: (n_features, n_samples, n_trials)
    # So we transpose (0, 1, 2) -> (1, 2, 0)
    features = np.transpose(data, (1, 2, 0))

    # Extract labels
    if labels is None:
        labels = epochs.events[:, 2]
    labels = np.asarray(labels)

    # Get unique classes
    unique_labels = np.unique(labels)
    n_classes = len(unique_labels)

    # Convert to 0-indexed class IDs (robust to arbitrary MNE event codes)
    label_map = {old: new for new, old in enumerate(sorted(unique_labels))}
    labels = np.asarray([label_map[l] for l in labels], dtype=np.int64)

    metadata = BCIMetadata(
        sampling_rate=float(epochs.info['sfreq']),
        paradigm=paradigm,
        feature_type=feature_type,
        n_features=data.shape[1],  # n_channels
        n_classes=n_classes,
        chunk_size=None,
        temporal_aggregation=temporal_aggregation,
    )

    return BCIData(features=features, metadata=metadata, labels=labels)


def to_mne_epochs(
    data: Union["BCIData", np.ndarray],
    info,  # mne.Info
    events: Optional[np.ndarray] = None,
    tmin: float = 0.0,
):
    """Convert BCIData or predictions back to MNE Epochs.

    Useful for visualization with MNE's plotting functions.

    Parameters
    ----------
    data : BCIData or np.ndarray
        BCIData object or raw feature array.
        If array, shape should be (n_features, n_samples, n_trials).
    info : mne.Info
        MNE Info object with channel information.
    events : np.ndarray, optional
        Events array. If None and data has labels, creates events from labels.
    tmin : float, default=0.0
        Start time of epochs.

    Returns
    -------
    mne.EpochsArray
        MNE Epochs object.

    Examples
    --------
    >>> from nimbus_bci.compat import from_mne_epochs, to_mne_epochs
    >>> bci_data = from_mne_epochs(original_epochs)
    >>> # ... process data ...
    >>> new_epochs = to_mne_epochs(bci_data, original_epochs.info)
    """
    from ..data.contracts import BCIData

    mne = _check_mne_installed()

    if isinstance(data, BCIData):
        # (n_features, n_samples, n_trials) -> (n_epochs, n_channels, n_times)
        arr = np.transpose(data.features, (2, 0, 1))

        if events is None and data.labels is not None:
            n_trials = data.n_trials
            sfreq = data.metadata.sampling_rate
            events = np.column_stack([
                np.arange(n_trials) * int(data.n_samples),  # Sample indices
                np.zeros(n_trials, dtype=int),  # Previous event
                data.labels,  # Event ID
            ]).astype(int)
    else:
        # Raw array: (n_features, n_samples, n_trials)
        arr = np.transpose(data, (2, 0, 1))

    return mne.EpochsArray(arr, info, events=events, tmin=tmin)


def extract_csp_features(
    epochs,  # mne.Epochs
    n_components: int = 8,
):
    """Extract CSP features from MNE Epochs.

    Common Spatial Patterns (CSP) is a popular feature extraction
    method for Motor Imagery BCI.

    Parameters
    ----------
    epochs : mne.Epochs
        MNE Epochs object.
    n_components : int, default=8
        Number of CSP components per class pair.
        Total features = 2 * n_components.

    Returns
    -------
    features : np.ndarray of shape (n_epochs, 2 * n_components)
        CSP features (log-variance of spatial filters).
    csp : mne.decoding.CSP
        Fitted CSP transformer for use on new data.

    Examples
    --------
    >>> from nimbus_bci.compat import extract_csp_features
    >>> # Extract CSP features
    >>> features, csp = extract_csp_features(epochs_train, n_components=8)
    >>>
    >>> # Apply to test data
    >>> features_test = csp.transform(epochs_test.get_data())
    """
    mne = _check_mne_installed()

    try:
        from mne.decoding import CSP
    except ImportError as e:
        raise ImportError(
            "mne.decoding.CSP is required for CSP feature extraction. "
            "Make sure you have a recent version of MNE installed."
        ) from e

    X = epochs.get_data()
    y = epochs.events[:, 2]

    csp = CSP(n_components=n_components, log=True)
    features = csp.fit_transform(X, y)

    return features, csp


def extract_bandpower_features(
    epochs,  # mne.Epochs
    bands: Optional[dict] = None,
    log_transform: bool = True,
):
    """Extract band power features from MNE Epochs.

    Computes power in specified frequency bands for each channel.
    Uses Welch's method for robust power spectral density estimation.

    Parameters
    ----------
    epochs : mne.Epochs
        MNE Epochs object.
    bands : dict, optional
        Frequency bands as {name: (fmin, fmax)}.
        Default: Standard EEG bands (delta, theta, alpha, beta, gamma).
    log_transform : bool, default=True
        Apply log10 transform to band powers. Recommended for classification
        as EEG power is log-normally distributed.

    Returns
    -------
    features : np.ndarray of shape (n_epochs, n_channels * n_bands)
        Band power features (log-transformed if log_transform=True).
    band_names : list of str
        Names of the bands.

    Examples
    --------
    >>> from nimbus_bci.compat import extract_bandpower_features
    >>> features, band_names = extract_bandpower_features(epochs)
    >>> print(f"Shape: {features.shape}, Bands: {band_names}")

    Notes
    -----
    For Motor Imagery, mu (8-12 Hz) and beta (13-30 Hz) are most relevant.
    For relaxation/meditation BCIs, alpha (8-13 Hz) is typically used.
    """
    mne = _check_mne_installed()
    try:
        from scipy import signal
    except ImportError as e:
        raise ImportError(
            "scipy is required for bandpower feature extraction. "
            "Install with: pip install nimbus-bci[all] (or pip install scipy)"
        ) from e

    if bands is None:
        bands = {
            "delta": (1, 4),
            "theta": (4, 8),
            "alpha": (8, 13),
            "beta": (13, 30),
            "gamma": (30, 100),
        }

    X = epochs.get_data()  # (n_epochs, n_channels, n_times)
    sfreq = epochs.info['sfreq']
    n_epochs, n_channels, n_times = X.shape

    # Compute PSD once for all bands (efficiency improvement)
    nperseg = min(n_times, int(sfreq * 2))  # 2-second windows or max available
    freqs, psd = signal.welch(X, fs=sfreq, nperseg=nperseg, axis=2)

    all_features = []
    band_names = list(bands.keys())

    for band_name, (fmin, fmax) in bands.items():
        # Find frequency indices for this band
        freq_mask = (freqs >= fmin) & (freqs <= fmax)

        if not np.any(freq_mask):
            # Band outside frequency resolution - skip with warning
            import warnings
            warnings.warn(
                f"Band '{band_name}' ({fmin}-{fmax} Hz) has no frequency bins. "
                f"Increase epoch length or adjust band limits.",
                UserWarning,
            )
            # Use zeros for this band
            band_power = np.zeros((n_epochs, n_channels))
        else:
            # Average power in band
            band_power = psd[:, :, freq_mask].mean(axis=2)  # (n_epochs, n_channels)

        all_features.append(band_power)

    # Concatenate all bands: (n_epochs, n_channels * n_bands)
    features = np.concatenate(all_features, axis=1)

    # Log-transform for more Gaussian distribution
    if log_transform:
        eps = 1e-10  # Avoid log(0)
        features = np.log10(features + eps)

    return features, band_names


def create_bci_pipeline(
    model_class,
    preprocessor: str = "standard",
    feature_extraction: Optional[str] = None,
    n_csp_components: int = 8,
    **model_kwargs,
):
    """Create a complete BCI pipeline with MNE-compatible preprocessing.

    Parameters
    ----------
    model_class : class
        Nimbus classifier class (NimbusLDA, NimbusQDA, NimbusSoftmax).
    preprocessor : str, default="standard"
        Preprocessing method ("standard", "robust", None).
    feature_extraction : str, optional
        Feature extraction method ("csp", None).
    n_csp_components : int, default=8
        Number of CSP components (if using CSP).
    **model_kwargs
        Additional arguments for the model.

    Returns
    -------
    sklearn.pipeline.Pipeline
        Complete BCI classification pipeline.

    Examples
    --------
    >>> from nimbus_bci import NimbusLDA
    >>> from nimbus_bci.compat import create_bci_pipeline
    >>> pipe = create_bci_pipeline(NimbusLDA, feature_extraction="csp")
    >>> pipe.fit(X_train, y_train)
    """
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler, RobustScaler

    steps = []

    # Feature extraction
    if feature_extraction == "csp":
        mne = _check_mne_installed()
        from mne.decoding import CSP
        steps.append(CSP(n_components=n_csp_components, log=True))

    # Preprocessing
    if preprocessor == "standard":
        steps.append(StandardScaler())
    elif preprocessor == "robust":
        steps.append(RobustScaler())

    # Classifier
    steps.append(model_class(**model_kwargs))

    return make_pipeline(*steps)

