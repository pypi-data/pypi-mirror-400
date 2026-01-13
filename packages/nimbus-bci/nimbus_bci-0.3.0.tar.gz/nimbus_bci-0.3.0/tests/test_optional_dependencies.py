import importlib.util

import pytest


def _has_jax() -> bool:
    return importlib.util.find_spec("jax") is not None


def test_import_nimbus_bci_without_optional_deps():
    # Base import should work even if JAX (softmax extra) is not installed.
    import nimbus_bci  # noqa: F401


def test_softmax_missing_dep_error_message():
    # If JAX is missing, NimbusSoftmax and softmax functions should raise a clear error.
    import nimbus_bci

    if _has_jax():
        pytest.skip("JAX is installed; softmax-missing behavior not applicable.")

    with pytest.raises(ImportError, match=r"nimbus-bci\\[softmax\\]"):
        _ = nimbus_bci.NimbusSoftmax()

    with pytest.raises(ImportError, match=r"nimbus-bci\\[softmax\\]"):
        nimbus_bci.nimbus_softmax_fit(None, None, None, None, None, None, None, None, None, None)  # type: ignore[arg-type]


def test_dispatch_softmax_missing_dep_error_message():
    from nimbus_bci.nimbus_io import NimbusModel
    from nimbus_bci.inference.dispatch import get_predict_proba_fn

    if _has_jax():
        pytest.skip("JAX is installed; softmax-missing dispatch behavior not applicable.")

    model = NimbusModel(model_type="nimbus_softmax", params={})
    with pytest.raises(ImportError, match=r"nimbus-bci\\[softmax\\]"):
        _ = get_predict_proba_fn(model)


