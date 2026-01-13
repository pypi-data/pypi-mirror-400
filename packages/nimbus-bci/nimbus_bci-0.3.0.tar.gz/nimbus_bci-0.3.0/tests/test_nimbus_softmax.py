import numpy as np

from nimbus_bci import (
    nimbus_softmax_fit,
    nimbus_softmax_predict,
    nimbus_softmax_predict_proba,
    nimbus_softmax_predict_samples,
    nimbus_softmax_update,
)


def test_nimbus_softmax_fit_predict_shapes():
    rng = np.random.default_rng(2)
    n_classes = 3
    X = rng.standard_normal((90, 4))
    y = np.repeat(np.arange(1, n_classes + 1), 30)

    model = nimbus_softmax_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=1,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.05,
        num_steps=30,
    )
    probs = nimbus_softmax_predict_proba(model, X[:11], num_posterior_samples=20, rng_seed=1)
    pred = nimbus_softmax_predict(model, X[:11], num_posterior_samples=20, rng_seed=2)

    assert probs.shape == (11, n_classes)
    assert pred.shape == (11,)
    assert np.allclose(np.sum(probs, axis=1), 1.0)
    assert np.all((pred >= 1) & (pred <= n_classes))


def test_nimbus_softmax_predict_proba_uses_seed_when_sampling():
    rng = np.random.default_rng(10)
    n_classes = 4
    X = rng.standard_normal((120, 5))
    y = np.repeat(np.arange(1, n_classes + 1), 30)

    model = nimbus_softmax_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=1,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.05,
        num_steps=20,
    )

    p1 = nimbus_softmax_predict_proba(model, X[:13], num_posterior_samples=25, rng_seed=1)
    p2 = nimbus_softmax_predict_proba(model, X[:13], num_posterior_samples=25, rng_seed=2)
    assert p1.shape == (13, n_classes)
    assert p2.shape == (13, n_classes)
    assert not np.allclose(p1, p2)


def test_nimbus_softmax_predict_proba_sampling_differs_from_mean():
    rng = np.random.default_rng(11)
    n_classes = 3
    X = rng.standard_normal((90, 4))
    y = np.repeat(np.arange(1, n_classes + 1), 30)

    model = nimbus_softmax_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=1,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.05,
        num_steps=15,
    )

    p_mean = nimbus_softmax_predict_proba(model, X[:17], num_posterior_samples=1, rng_seed=0)
    p_mc = nimbus_softmax_predict_proba(model, X[:17], num_posterior_samples=40, rng_seed=0)
    assert p_mean.shape == (17, n_classes)
    assert p_mc.shape == (17, n_classes)
    assert not np.allclose(p_mean, p_mc)


def test_nimbus_softmax_predict_samples_shapes_and_range():
    rng = np.random.default_rng(3)
    n_classes = 3
    X = rng.standard_normal((90, 4))
    y = np.repeat(np.arange(1, n_classes + 1), 30)

    model = nimbus_softmax_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=1,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.05,
        num_steps=15,
    )
    y_s = nimbus_softmax_predict_samples(model, X[:11], num_posterior_samples=7, rng_seed=1)
    assert y_s.shape == (7, 11)
    assert np.all((y_s >= 1) & (y_s <= n_classes))


def test_nimbus_softmax_update_can_expand_classes():
    rng = np.random.default_rng(4)
    X0 = rng.standard_normal((90, 4))
    y0 = np.repeat(np.arange(1, 3), 45)

    model = nimbus_softmax_fit(
        X=X0,
        y=y0,
        n_classes=2,
        label_base=1,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.05,
        num_steps=10,
    )

    X1 = rng.standard_normal((30, 4))
    y1 = np.repeat(np.array([3], dtype=int), 30)
    model2 = nimbus_softmax_update(model, X1, y1)

    probs = nimbus_softmax_predict_proba(model2, X1[:11], num_posterior_samples=5, rng_seed=1)
    pred = nimbus_softmax_predict(model2, X1[:11], num_posterior_samples=5, rng_seed=2)
    y_s = nimbus_softmax_predict_samples(model2, X1[:11], num_posterior_samples=5, rng_seed=3)

    assert probs.shape == (11, 3)
    assert pred.shape == (11,)
    assert y_s.shape == (5, 11)
    assert np.all((pred >= 1) & (pred <= 3))
    assert np.all((y_s >= 1) & (y_s <= 3))


def test_nimbus_softmax_learns_softmax_synthetic_better_than_chance():
    rng = np.random.default_rng(0)
    n_classes = 4
    n_features = 4
    n_train = 800
    n_test = 400
    label_base = 1

    W_true = rng.standard_normal((n_classes, n_features)) * 1.2
    b_true = rng.standard_normal((n_classes,)) * 0.2

    X_train = rng.standard_normal((n_train, n_features))
    logits = X_train @ W_true.T + b_true
    p = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    p = p / np.sum(p, axis=1, keepdims=True)
    y0 = np.array([rng.choice(n_classes, p=p[i]) for i in range(n_train)], dtype=int)
    y = y0 + label_base

    X_test = rng.standard_normal((n_test, n_features))
    logits_t = X_test @ W_true.T + b_true
    p_t = np.exp(logits_t - np.max(logits_t, axis=1, keepdims=True))
    p_t = p_t / np.sum(p_t, axis=1, keepdims=True)
    y0_t = np.array([rng.choice(n_classes, p=p_t[i]) for i in range(n_test)], dtype=int)
    y_t = y0_t + label_base

    model = nimbus_softmax_fit(
        X=X_train,
        y=y,
        n_classes=n_classes,
        label_base=label_base,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.2,
        num_steps=25,
    )

    pred = nimbus_softmax_predict(model, X_test, num_posterior_samples=1, rng_seed=1)
    acc = float(np.mean(pred == y_t))
    assert acc > 0.35

