from .learning import nimbus_qda_fit, nimbus_qda_update
from .inference import nimbus_qda_predict, nimbus_qda_predict_proba
from .classifier import NimbusQDA

__all__ = [
    "nimbus_qda_fit",
    "nimbus_qda_update",
    "nimbus_qda_predict_proba",
    "nimbus_qda_predict",
    "NimbusQDA",
]


