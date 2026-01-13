"""Compatibility modules for external libraries."""

from .sklearn_compat import BaseNimbusClassifier

# Lazy import for MNE to avoid hard dependency
def from_mne_epochs(*args, **kwargs):
    """Convert MNE Epochs to BCIData (lazy import)."""
    from .mne_compat import from_mne_epochs as _from_mne_epochs
    return _from_mne_epochs(*args, **kwargs)


def to_mne_epochs(*args, **kwargs):
    """Convert BCIData to MNE Epochs (lazy import)."""
    from .mne_compat import to_mne_epochs as _to_mne_epochs
    return _to_mne_epochs(*args, **kwargs)


def extract_csp_features(*args, **kwargs):
    """Extract CSP features from MNE Epochs (lazy import)."""
    from .mne_compat import extract_csp_features as _extract_csp_features
    return _extract_csp_features(*args, **kwargs)


def extract_bandpower_features(*args, **kwargs):
    """Extract bandpower features from MNE Epochs (lazy import)."""
    from .mne_compat import extract_bandpower_features as _extract_bandpower
    return _extract_bandpower(*args, **kwargs)


def create_bci_pipeline(*args, **kwargs):
    """Create BCI pipeline (lazy import)."""
    from .mne_compat import create_bci_pipeline as _create_bci_pipeline
    return _create_bci_pipeline(*args, **kwargs)


__all__ = [
    "BaseNimbusClassifier",
    # MNE compatibility (lazy imports)
    "from_mne_epochs",
    "to_mne_epochs",
    "extract_csp_features",
    "extract_bandpower_features",
    "create_bci_pipeline",
]

