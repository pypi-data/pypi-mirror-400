import time

import numpy as np

from nimbus_bci import nimbus_lda_fit, nimbus_lda_predict, nimbus_lda_predict_proba, nimbus_lda_update


def main():
    rng = np.random.default_rng(0)
    n_classes = 10
    n_features = 20
    n_train = 100000
    n_test = 10000
    label_base = 1
    n_train0 = n_train // 2

    means = rng.standard_normal((n_classes, n_features)) * 2.0
    cov = np.eye(n_features) * 1.5
    cov_L = np.linalg.cholesky(cov)

    y_train0 = rng.integers(0, n_classes, size=n_train)
    X_train = rng.standard_normal((n_train, n_features)) @ cov_L.T + means[y_train0]
    y_train = y_train0 + label_base

    y_test0 = rng.integers(0, n_classes, size=n_test)
    X_test = rng.standard_normal((n_test, n_features)) @ cov_L.T + means[y_test0]
    y_test = y_test0 + label_base

    t0 = time.perf_counter()
    model = nimbus_lda_fit(
        X=X_train[:n_train0],
        y=y_train[:n_train0],
        n_classes=n_classes,
        label_base=label_base,
        mu_loc=0.0,
        mu_scale=3.0,
        wishart_df=float(n_features + 2),
        wishart_scale=np.eye(n_features),
        class_prior_alpha=1.0,
    )
    fit_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    probs = nimbus_lda_predict_proba(model, X_test)
    predict_proba_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    pred = nimbus_lda_predict(model, X_test)
    predict_s = time.perf_counter() - t0
    acc = float(np.mean(pred == y_test))

    t0 = time.perf_counter()
    model_u = nimbus_lda_update(model, X_train[n_train0:], y_train[n_train0:])
    update_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    pred_u = nimbus_lda_predict(model_u, X_test)
    predict_u_s = time.perf_counter() - t0
    acc_u = float(np.mean(pred_u == y_test))

    print("nimbus_lda synthetic")
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


if __name__ == "__main__":
    main()


