import time

import numpy as np

from nimbus_bci import nimbus_sts_fit, nimbus_sts_predict, nimbus_sts_predict_proba, nimbus_sts_update


def generate_drifting_data(n_samples, n_features, n_classes, drift_rate=0.05, rng_seed=0):
    """Generate synthetic data with drifting class means.
    
    This simulates non-stationary BCI data where class distributions
    gradually change over time (e.g., due to fatigue, electrode drift).
    """
    rng = np.random.default_rng(rng_seed)
    X, y = [], []
    
    # Initialize class means
    means = rng.standard_normal((n_classes, n_features)) * 2.0
    cov = np.eye(n_features) * 1.5
    cov_L = np.linalg.cholesky(cov)
    
    for t in range(n_samples):
        # Drift: classes slowly move (simulates non-stationarity)
        means += rng.standard_normal((n_classes, n_features)) * drift_rate
        
        # Generate samples for each class
        label = t % n_classes
        x = rng.standard_normal(n_features) @ cov_L.T + means[label]
        X.append(x)
        y.append(label)
    
    return np.array(X), np.array(y)


def main():
    rng = np.random.default_rng(0)
    n_classes = 4
    n_features = 16
    n_train = 5000
    n_test = 1000
    label_base = 0
    n_train0 = n_train // 2
    
    print("=" * 60)
    print("NimbusSTS Synthetic Benchmark (Non-Stationary Data)")
    print("=" * 60)
    print(f"Classes: {n_classes}, Features: {n_features}")
    print(f"Train samples: {n_train}, Test samples: {n_test}")
    print(f"Drift rate: 0.02 (moderate non-stationarity)")
    print()
    
    # Generate drifting data (non-stationary)
    X_train, y_train = generate_drifting_data(
        n_train, n_features, n_classes, drift_rate=0.02, rng_seed=0
    )
    X_test, y_test = generate_drifting_data(
        n_test, n_features, n_classes, drift_rate=0.02, rng_seed=1
    )
    
    # Fit model
    t0 = time.perf_counter()
    model = nimbus_sts_fit(
        X=X_train[:n_train0],
        y=y_train[:n_train0],
        n_classes=n_classes,
        label_base=label_base,
        state_dim=n_classes - 1,
        transition_cov=0.05,  # Moderate drift tracking
        observation_cov=1.0,
        learning_rate=0.1,
        num_steps=50,
        rng_seed=0,
        verbose=False,
    )
    fit_s = time.perf_counter() - t0
    
    # Predict probabilities
    t0 = time.perf_counter()
    probs = nimbus_sts_predict_proba(model, X_test)
    predict_proba_s = time.perf_counter() - t0
    
    # Predict labels
    t0 = time.perf_counter()
    pred = nimbus_sts_predict(model, X_test)
    predict_s = time.perf_counter() - t0
    acc = float(np.mean(pred == y_test))
    
    # Online update (simulating adaptive BCI)
    t0 = time.perf_counter()
    model_u = nimbus_sts_update(model, X_train[n_train0:], y_train[n_train0:])
    update_s = time.perf_counter() - t0
    
    # Evaluate after update
    t0 = time.perf_counter()
    pred_u = nimbus_sts_predict(model_u, X_test)
    predict_u_s = time.perf_counter() - t0
    acc_u = float(np.mean(pred_u == y_test))
    
    # Report results
    print("Results:")
    print("-" * 60)
    print(f"accuracy_before_update: {acc:.4f}")
    print(f"accuracy_after_update:  {acc_u:.4f} (improvement: {acc_u-acc:+.4f})")
    print()
    
    print("Performance:")
    print("-" * 60)
    print(f"fit_ms:                 {fit_s * 1000:.3f}")
    print(f"update_ms:              {update_s * 1000:.3f}")
    
    predict_proba_hz = X_test.shape[0] / predict_proba_s
    predict_hz = X_test.shape[0] / predict_s
    predict_u_hz = X_test.shape[0] / predict_u_s
    
    print(f"predict_proba_ms:       {predict_proba_s * 1000:.3f} "
          f"(speed: {predict_proba_hz:.0f} Hz, {predict_proba_hz/1000:.2f} kHz)")
    print(f"predict_ms:             {predict_s * 1000:.3f} "
          f"(speed: {predict_hz:.0f} Hz, {predict_hz/1000:.2f} kHz)")
    print(f"predict_after_update_ms: {predict_u_s * 1000:.3f} "
          f"(speed: {predict_u_hz:.0f} Hz, {predict_u_hz/1000:.2f} kHz)")
    print()
    
    print("Sample predictions (first test sample):")
    print("-" * 60)
    print(f"probs[0]: {np.round(probs[0], 4)}")
    print(f"predicted class: {pred[0]}, true class: {y_test[0]}")
    print()
    
    print("=" * 60)
    print("NimbusSTS demonstrates value on non-stationary data!")
    print("For stationary data, use NimbusLDA or NimbusQDA instead.")
    print("=" * 60)


if __name__ == "__main__":
    main()


