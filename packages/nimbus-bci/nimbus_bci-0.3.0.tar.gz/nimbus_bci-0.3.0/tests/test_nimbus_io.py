import numpy as np

from nimbus_bci.nimbus_io import NimbusModel, nimbus_load, nimbus_save


def test_nimbus_io_roundtrip(tmp_path):
    model = NimbusModel(
        model_type="nimbus_lda",
        params={
            "means": np.zeros((2, 3)),
            "label_base": np.array(1, dtype=np.int64),
            "svi_params": {"a": np.array([1.0, 2.0])},
        },
    )
    p = tmp_path / "model.npz"
    nimbus_save(model, str(p))
    loaded = nimbus_load(str(p))
    assert loaded.model_type == "nimbus_lda"
    assert loaded.params["means"].shape == (2, 3)
    assert int(loaded.params["label_base"]) == 1
    assert np.allclose(loaded.params["svi_params"]["a"], np.array([1.0, 2.0]))


