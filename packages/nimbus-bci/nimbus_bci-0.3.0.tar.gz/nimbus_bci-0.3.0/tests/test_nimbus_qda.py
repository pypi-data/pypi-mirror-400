import numpy as np

from nimbus_bci import nimbus_qda_fit, nimbus_qda_predict, nimbus_qda_predict_proba, nimbus_qda_update


def test_nimbus_qda_fit_predict_shapes():
    rng = np.random.default_rng(1)
    n_classes = 4
    n_features = 6
    X = rng.standard_normal((80, n_features))
    y = np.repeat(np.arange(0, n_classes), 20)

    model = nimbus_qda_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=0,
        mu_loc=0.0,
        mu_scale=3.0,
        wishart_df=float(n_features + 2),
        wishart_scale=np.eye(n_features),
        class_prior_alpha=1.0,
    )
    probs = nimbus_qda_predict_proba(model, X[:9])
    pred = nimbus_qda_predict(model, X[:9])

    assert probs.shape == (9, n_classes)
    assert pred.shape == (9,)
    assert np.allclose(np.sum(probs, axis=1), 1.0)
    assert np.all((pred >= 0) & (pred < n_classes))


def test_qda_example_synthetic_cov_indexing_does_not_oob():
    rng = np.random.default_rng(0)
    n_classes = 10
    n_features = 5
    n_train = 200

    means = rng.standard_normal((n_classes, n_features))
    covs = np.stack([np.eye(n_features) * s for s in (0.8, 1.6, 2.4)], axis=0)
    y = rng.integers(0, n_classes, size=n_train)

    X = np.stack([rng.multivariate_normal(means[k], covs[k % covs.shape[0]]) for k in y], axis=0)
    assert X.shape == (n_train, n_features)


def test_nimbus_qda_update_can_expand_classes():
    rng = np.random.default_rng(0)
    n_features = 4

    X0 = rng.standard_normal((60, n_features))
    y0 = np.repeat(np.arange(0, 2), 30)
    model = nimbus_qda_fit(
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
    model2 = nimbus_qda_update(model, X1, y1)

    probs = nimbus_qda_predict_proba(model2, X1[:7])
    pred = nimbus_qda_predict(model2, X1[:7])
    assert probs.shape == (7, 3)
    assert np.all((pred >= 0) & (pred < 3))

