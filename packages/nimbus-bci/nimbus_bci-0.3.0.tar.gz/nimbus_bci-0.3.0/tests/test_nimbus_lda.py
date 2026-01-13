import numpy as np

from nimbus_bci import nimbus_lda_fit, nimbus_lda_predict, nimbus_lda_predict_proba, nimbus_lda_update


def test_nimbus_lda_fit_predict_shapes():
    rng = np.random.default_rng(0)
    n_classes = 3
    n_features = 5
    X = rng.standard_normal((60, n_features))
    y = np.repeat(np.arange(1, n_classes + 1), 20)

    model = nimbus_lda_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=1,
        mu_loc=0.0,
        mu_scale=3.0,
        wishart_df=float(n_features + 2),
        wishart_scale=np.eye(n_features),
        class_prior_alpha=1.0,
    )
    probs = nimbus_lda_predict_proba(model, X[:7])
    pred = nimbus_lda_predict(model, X[:7])

    assert probs.shape == (7, n_classes)
    assert pred.shape == (7,)
    assert np.allclose(np.sum(probs, axis=1), 1.0)
    assert np.all((pred >= 1) & (pred <= n_classes))


def test_nimbus_lda_update_can_expand_classes():
    rng = np.random.default_rng(0)
    n_features = 4

    X0 = rng.standard_normal((60, n_features))
    y0 = np.repeat(np.arange(0, 2), 30)
    model = nimbus_lda_fit(
        X=X0,
        y=y0,
        n_classes=2,
        label_base=0,
        mu_loc=0.0,
        mu_scale=3.0,
        wishart_df=float(n_features + 2),
        wishart_scale=np.eye(n_features),
        class_prior_alpha=1.0,
    )

    X1 = rng.standard_normal((30, n_features))
    y1 = np.repeat(np.array([2], dtype=int), 30)
    model2 = nimbus_lda_update(model, X1, y1)

    probs = nimbus_lda_predict_proba(model2, X1[:7])
    pred = nimbus_lda_predict(model2, X1[:7])
    assert probs.shape == (7, 3)
    assert np.all((pred >= 0) & (pred < 3))

