"""Nimbus BCI classifiers - functional and sklearn-compatible APIs."""

# NOTE: NimbusSoftmax depends on optional JAX. We import it lazily so users
# can install and use LDA/QDA/STS without the softmax extra.

# Functional API (existing)
from .nimbus_lda import nimbus_lda_fit, nimbus_lda_predict, nimbus_lda_predict_proba, nimbus_lda_update
from .nimbus_qda import nimbus_qda_fit, nimbus_qda_predict, nimbus_qda_predict_proba, nimbus_qda_update
from .nimbus_sts import (
    nimbus_sts_fit,
    nimbus_sts_predict,
    nimbus_sts_predict_proba,
    nimbus_sts_update,
)

# sklearn-compatible classes (new)
from .nimbus_lda import NimbusLDA
from .nimbus_qda import NimbusQDA
from .nimbus_sts import NimbusSTS

# Optional softmax exports (requires `pip install nimbus-bci[softmax]`)
try:
    from .nimbus_softmax import (  # noqa: WPS433
        nimbus_softmax_fit,
        nimbus_softmax_predict,
        nimbus_softmax_predict_proba,
        nimbus_softmax_predict_samples,
        nimbus_softmax_update,
        NimbusSoftmax,
    )
except Exception:  # pragma: no cover
    class NimbusSoftmax:  # type: ignore[no-redef]
        """Stub NimbusSoftmax when optional JAX dependency is not installed.

        Install with: pip install nimbus-bci[softmax]
        """

        def __init__(self, *args, **kwargs):  # noqa: D401, ANN001
            raise ImportError(
                "NimbusSoftmax requires the optional 'softmax' extra. "
                "Install with: pip install nimbus-bci[softmax]"
            )

    def _softmax_missing(*_args, **_kwargs):  # type: ignore[no-redef]
        raise ImportError(
            "NimbusSoftmax requires the optional 'softmax' extra. "
            "Install with: pip install nimbus-bci[softmax]"
        )

    nimbus_softmax_fit = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_update = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_predict_proba = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_predict = _softmax_missing  # type: ignore[assignment]
    nimbus_softmax_predict_samples = _softmax_missing  # type: ignore[assignment]

# Base class for custom models
from .base import NimbusClassifierMixin

__all__ = [
    # Functional API
    "nimbus_lda_fit",
    "nimbus_lda_update",
    "nimbus_lda_predict_proba",
    "nimbus_lda_predict",
    "nimbus_qda_fit",
    "nimbus_qda_update",
    "nimbus_qda_predict_proba",
    "nimbus_qda_predict",
    "nimbus_softmax_fit",
    "nimbus_softmax_update",
    "nimbus_softmax_predict_proba",
    "nimbus_softmax_predict",
    "nimbus_softmax_predict_samples",
    "nimbus_sts_fit",
    "nimbus_sts_update",
    "nimbus_sts_predict_proba",
    "nimbus_sts_predict",
    # sklearn-compatible classes
    "NimbusLDA",
    "NimbusQDA",
    "NimbusSoftmax",
    "NimbusSTS",
    "NimbusClassifierMixin",
]


