from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class NimbusModel:
    model_type: str
    params: dict[str, Any]


def nimbus_save(model: NimbusModel, path: str) -> str:
    payload: dict[str, Any] = {"model_type": np.array(model.model_type)}
    for k, v in model.params.items():
        if isinstance(v, np.ndarray):
            payload[k] = v
        else:
            payload[k] = np.array(v, dtype=object)
    np.savez(path, **payload)
    return path


def nimbus_load(path: str) -> NimbusModel:
    data = np.load(path, allow_pickle=True)
    model_type = str(data["model_type"])
    params: dict[str, Any] = {}
    for k in data.files:
        if k == "model_type":
            continue
        v = data[k]
        if isinstance(v, np.ndarray) and v.dtype == object and v.shape == ():
            params[k] = v.item()
        else:
            params[k] = v
    return NimbusModel(model_type=model_type, params=params)


def nimbus_params(model: NimbusModel) -> Mapping[str, Any]:
    return model.params


