import time

import numpy as np

from nimbus_bci import nimbus_softmax_fit, nimbus_softmax_predict, nimbus_softmax_predict_proba, nimbus_softmax_update


def main():
    rng = np.random.default_rng(0)
    n_classes = 10
    n_features = 20
    n_train = 100000
    n_test = 10000
    label_base = 1
    n_train0 = n_train // 2

    W_true = rng.standard_normal((n_classes, n_features)) * 0.8
    b_true = rng.standard_normal((n_classes,)) * 0.2

    X_train = rng.standard_normal((n_train, n_features))
    logits_train = X_train @ W_true.T + b_true
    p_train = np.exp(logits_train - np.max(logits_train, axis=1, keepdims=True))
    p_train = p_train / np.sum(p_train, axis=1, keepdims=True)
    y_train0 = np.array([rng.choice(n_classes, p=p_train[i]) for i in range(n_train)], dtype=int)
    y_train = y_train0 + label_base

    X_test = rng.standard_normal((n_test, n_features))
    logits_test = X_test @ W_true.T + b_true
    p_test = np.exp(logits_test - np.max(logits_test, axis=1, keepdims=True))
    p_test = p_test / np.sum(p_test, axis=1, keepdims=True)
    y_test0 = np.array([rng.choice(n_classes, p=p_test[i]) for i in range(n_test)], dtype=int)
    y_test = y_test0 + label_base

    t0 = time.perf_counter()
    model = nimbus_softmax_fit(
        X=X_train[:n_train0],
        y=y_train[:n_train0],
        n_classes=n_classes,
        label_base=label_base,
        w_loc=0.0,
        w_scale=1.0,
        b_loc=0.0,
        b_scale=1.0,
        rng_seed=0,
        learning_rate=0.2,
        num_steps=60,
    )
    fit_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    probs = nimbus_softmax_predict_proba(model, X_test, num_posterior_samples=50, rng_seed=1)
    predict_proba_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    pred = nimbus_softmax_predict(model, X_test, num_posterior_samples=50, rng_seed=2)
    predict_s = time.perf_counter() - t0
    acc = float(np.mean(pred == y_test))

    t0 = time.perf_counter()
    model_u = nimbus_softmax_update(model, X_train[n_train0:], y_train[n_train0:])
    update_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    pred_u = nimbus_softmax_predict(model_u, X_test, num_posterior_samples=50, rng_seed=2)
    predict_u_s = time.perf_counter() - t0
    acc_u = float(np.mean(pred_u == y_test))

    print("nimbus_softmax synthetic")
    print("accuracy_before_update:", round(acc, 4))
    print("accuracy_after_update:", round(acc_u, 4))
    print("fit_ms:", round(fit_s * 1000.0, 3))
    print("update_ms:", round(update_s * 1000.0, 3))
    predict_proba_hz = X_test.shape[0] / predict_proba_s
    predict_hz = X_test.shape[0] / predict_s
    print("predict_proba_ms:", round(predict_proba_s * 1000.0, 3), "speed_hz:", round(predict_proba_hz, 2), "speed_khz:", round(predict_proba_hz / 1000.0, 4))
    print("predict_ms:", round(predict_s * 1000.0, 3), "speed_hz:", round(predict_hz, 2), "speed_khz:", round(predict_hz / 1000.0, 4))
    predict_u_hz = X_test.shape[0] / predict_u_s
    print("predict_after_update_ms:", round(predict_u_s * 1000.0, 3), "speed_hz:", round(predict_u_hz, 2), "speed_khz:", round(predict_u_hz / 1000.0, 4))
    print("probs[0]:", np.round(probs[0], 4))
    print("probs[0]:", np.round(probs[0], 4))


if __name__ == "__main__":
    main()


