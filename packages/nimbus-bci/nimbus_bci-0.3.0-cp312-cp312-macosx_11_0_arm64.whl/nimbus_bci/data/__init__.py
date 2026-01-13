"""Data contracts and validation for BCI data."""

from .contracts import BCIData, BCIMetadata
from .validation import validate_data, check_model_compatibility, labels_to_zero_indexed

__all__ = [
    "BCIData",
    "BCIMetadata",
    "validate_data",
    "check_model_compatibility",
    "labels_to_zero_indexed",
]

