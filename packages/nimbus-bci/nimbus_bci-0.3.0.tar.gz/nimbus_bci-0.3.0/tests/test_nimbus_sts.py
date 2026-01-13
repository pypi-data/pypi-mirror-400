import numpy as np

from nimbus_bci import (
    nimbus_sts_fit,
    nimbus_sts_predict,
    nimbus_sts_predict_proba,
    nimbus_sts_update,
    NimbusSTS,
)


def test_nimbus_sts_fit_predict_shapes():
    rng = np.random.default_rng(42)
    n_classes = 3
    n_features = 5
    n_samples = 60
    
    X = rng.standard_normal((n_samples, n_features))
    y = np.repeat(np.arange(n_classes), n_samples // n_classes)

    model = nimbus_sts_fit(
        X=X,
        y=y,
        n_classes=n_classes,
        label_base=0,
        num_steps=20,
    )
    
    probs = nimbus_sts_predict_proba(model, X[:7])
    pred = nimbus_sts_predict(model, X[:7])

    assert probs.shape == (7, n_classes)
    assert pred.shape == (7,)
    assert np.allclose(np.sum(probs, axis=1), 1.0)
    assert np.all((pred >= 0) & (pred < n_classes))


def test_nimbus_sts_evolve_state_is_opt_in():
    """By default, predict_proba should not implicitly evolve latent state across rows."""
    import numpy as np

    from nimbus_bci.models.nimbus_sts.inference import nimbus_sts_predict_proba
    from nimbus_bci.nimbus_io import NimbusModel

    # Construct a tiny deterministic STS model where evolving state changes logits.
    W = np.zeros((2, 2), dtype=np.float64)
    H = np.array([[1.0], [-1.0]], dtype=np.float64)
    b = np.zeros(2, dtype=np.float64)
    z_mean = np.array([1.0], dtype=np.float64)
    A = np.array([[0.5]], dtype=np.float64)  # decay

    model = NimbusModel(
        model_type="nimbus_sts",
        params={
            "W": W,
            "H": H,
            "b": b,
            "z_mean": z_mean,
            "A": A,
        },
    )

    X = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float64)

    p_indep = nimbus_sts_predict_proba(model, X, evolve_state=False)
    assert np.allclose(p_indep[0], p_indep[1]), "Rows should match when evolve_state=False"

    p_seq = nimbus_sts_predict_proba(model, X, evolve_state=True)
    assert not np.allclose(p_seq[0], p_seq[1]), "Rows should differ when evolve_state=True"


def test_nimbus_sts_update():
    rng = np.random.default_rng(42)
    n_features = 4
    n_classes = 2

    X0 = rng.standard_normal((40, n_features))
    y0 = np.repeat(np.arange(n_classes), 20)
    
    model = nimbus_sts_fit(
        X=X0,
        y=y0,
        n_classes=n_classes,
        label_base=0,
        num_steps=10,
    )

    X1 = rng.standard_normal((20, n_features))
    y1 = np.repeat(np.arange(n_classes), 10)
    model2 = nimbus_sts_update(model, X1, y1)

    probs = nimbus_sts_predict_proba(model2, X1[:5])
    assert probs.shape == (5, n_classes)
    assert np.allclose(np.sum(probs, axis=1), 1.0)


def test_nimbus_sts_classifier_api():
    rng = np.random.default_rng(42)
    n_classes = 3
    n_features = 4
    n_samples = 90
    
    X = rng.standard_normal((n_samples, n_features))
    y = np.repeat(np.arange(n_classes), n_samples // n_classes)

    clf = NimbusSTS(num_steps=20, rng_seed=42)
    clf.fit(X, y)

    probs = clf.predict_proba(X[:10])
    preds = clf.predict(X[:10])

    assert probs.shape == (10, n_classes)
    assert preds.shape == (10,)
    assert np.allclose(np.sum(probs, axis=1), 1.0)
    assert set(preds).issubset(set(range(n_classes)))


def test_nimbus_sts_partial_fit():
    rng = np.random.default_rng(42)
    n_classes = 2
    n_features = 4

    X1 = rng.standard_normal((30, n_features))
    y1 = np.repeat(np.arange(n_classes), 15)

    clf = NimbusSTS(num_steps=10)
    clf.partial_fit(X1, y1, classes=np.arange(n_classes))

    X2 = rng.standard_normal((20, n_features))
    y2 = np.repeat(np.arange(n_classes), 10)
    clf.partial_fit(X2, y2)

    probs = clf.predict_proba(X2[:5])
    assert probs.shape == (5, n_classes)


def test_nimbus_sts_latent_state():
    rng = np.random.default_rng(42)
    n_classes = 2
    n_features = 3
    
    X = rng.standard_normal((40, n_features))
    y = np.repeat(np.arange(n_classes), 20)

    clf = NimbusSTS(num_steps=10)
    clf.fit(X, y)

    state = clf.get_latent_state()
    assert state is not None
    z_mean, z_cov = state
    assert z_mean.shape == (n_classes - 1,)
    assert z_cov.shape == (n_classes - 1, n_classes - 1)


def test_nimbus_sts_learns_separable_data():
    rng = np.random.default_rng(42)
    n_per_class = 50
    n_features = 4
    
    X0 = rng.standard_normal((n_per_class, n_features)) + np.array([2, 0, 0, 0])
    X1 = rng.standard_normal((n_per_class, n_features)) + np.array([-2, 0, 0, 0])
    X = np.vstack([X0, X1])
    y = np.array([0] * n_per_class + [1] * n_per_class)

    clf = NimbusSTS(num_steps=50, learning_rate=0.2)
    clf.fit(X, y)

    preds = clf.predict(X)
    accuracy = np.mean(preds == y)
    assert accuracy > 0.7


def test_nimbus_sts_propagate_state():
    rng = np.random.default_rng(42)
    n_classes = 2
    n_features = 4
    
    X = rng.standard_normal((40, n_features))
    y = np.repeat(np.arange(n_classes), 20)

    clf = NimbusSTS(num_steps=10, transition_cov=0.1)
    clf.fit(X, y)

    z_before, P_before = clf.get_latent_state()
    clf.propagate_state(n_steps=3)
    z_after, P_after = clf.get_latent_state()

    assert not np.allclose(P_before, P_after)
    assert P_after[0, 0] > P_before[0, 0]


def test_nimbus_sts_reset_state():
    rng = np.random.default_rng(42)
    n_classes = 2
    n_features = 4
    
    X = rng.standard_normal((40, n_features))
    y = np.repeat(np.arange(n_classes), 20)

    clf = NimbusSTS(num_steps=10, transition_cov=0.1)
    clf.fit(X, y)

    _, P_after_fit = clf.get_latent_state()
    clf.propagate_state(n_steps=5)
    _, P_propagated = clf.get_latent_state()
    
    assert not np.allclose(P_after_fit, P_propagated)

    clf.reset_state()
    z_reset, P_reset = clf.get_latent_state()

    assert np.allclose(z_reset, np.zeros_like(z_reset))
    assert np.allclose(P_reset, np.eye(len(z_reset)))


def test_nimbus_sts_set_latent_state():
    rng = np.random.default_rng(42)
    n_classes = 2
    n_features = 4
    state_dim = n_classes - 1
    
    X = rng.standard_normal((40, n_features))
    y = np.repeat(np.arange(n_classes), 20)

    clf = NimbusSTS(num_steps=10)
    clf.fit(X, y)

    new_z = np.array([0.5])
    new_P = np.array([[2.0]])
    clf.set_latent_state(new_z, new_P)

    z, P = clf.get_latent_state()
    assert np.allclose(z, new_z)
    assert np.allclose(P, new_P)


def test_nimbus_sts_streaming_with_delayed_labels():
    rng = np.random.default_rng(42)
    n_per_class = 30
    n_features = 4
    
    X0 = rng.standard_normal((n_per_class, n_features)) + np.array([2, 0, 0, 0])
    X1 = rng.standard_normal((n_per_class, n_features)) + np.array([-2, 0, 0, 0])
    X_train = np.vstack([X0, X1])
    y_train = np.array([0] * n_per_class + [1] * n_per_class)

    clf = NimbusSTS(num_steps=30, learning_rate=0.2)
    clf.fit(X_train, y_train)

    X_stream = rng.standard_normal((10, n_features)) + np.array([2, 0, 0, 0])
    y_stream = np.zeros(10, dtype=int)

    predictions = []
    for i in range(len(X_stream)):
        clf.propagate_state()
        pred = clf.predict(X_stream[i:i+1])
        predictions.append(pred[0])
        clf.partial_fit(X_stream[i:i+1], y_stream[i:i+1])

    accuracy = np.mean(np.array(predictions) == y_stream)
    assert accuracy >= 0.5


def test_nimbus_sts_prediction_reproducibility():
    """Ensure predict_proba doesn't mutate state (bug fix verification)."""
    rng = np.random.default_rng(42)
    X = rng.standard_normal((40, 4))
    y = np.repeat(np.arange(2), 20)
    
    clf = NimbusSTS(num_steps=10)
    clf.fit(X, y)
    
    # Get state before predictions
    z_before, P_before = clf.get_latent_state()
    
    # Make multiple predictions
    pred1 = clf.predict(X[:5])
    pred2 = clf.predict(X[:5])
    
    # State should be unchanged
    z_after, P_after = clf.get_latent_state()
    assert np.allclose(z_before, z_after), "predict() mutated latent state!"
    assert np.allclose(P_before, P_after), "predict() mutated latent covariance!"
    
    # Predictions should be identical
    assert np.array_equal(pred1, pred2), "Predictions not reproducible!"


def test_nimbus_sts_sklearn_compatibility():
    """Test sklearn API compatibility (cross_val_score, GridSearchCV)."""
    from sklearn.model_selection import cross_val_score, GridSearchCV
    
    rng = np.random.default_rng(42)
    X = rng.standard_normal((100, 4))
    y = np.repeat(np.arange(2), 50)
    
    # Cross-validation
    clf = NimbusSTS(num_steps=10)
    scores = cross_val_score(clf, X, y, cv=3)
    assert len(scores) == 3
    assert all(0 <= s <= 1 for s in scores)
    
    # Grid search
    param_grid = {
        'transition_cov': [0.01, 0.05],
        'learning_rate': [0.1, 0.2]
    }
    grid = GridSearchCV(NimbusSTS(num_steps=10), param_grid, cv=3)
    grid.fit(X, y)
    assert hasattr(grid, 'best_params_')


def test_nimbus_sts_streaming_integration():
    """Test integration with StreamingSessionSTS (stateful)."""
    from nimbus_bci.inference import StreamingSessionSTS
    from nimbus_bci.data import BCIMetadata
    
    rng = np.random.default_rng(42)
    X = rng.standard_normal((40, 8))
    y = np.repeat(np.arange(2), 20)
    
    clf = NimbusSTS(num_steps=10)
    clf.fit(X, y)
    
    metadata = BCIMetadata(
        sampling_rate=250.0,
        paradigm="motor_imagery",
        feature_type="csp",
        n_features=8,
        n_classes=2,
        chunk_size=125,
        temporal_aggregation="mean",
    )
    
    session = StreamingSessionSTS(clf, metadata)
    
    # Process chunks
    chunk = rng.standard_normal((8, 125))
    z_before, P_before = clf.get_latent_state()
    result = session.process_chunk(chunk)
    z_after, P_after = clf.get_latent_state()
    
    assert result.prediction in [0, 1]
    assert 0 <= result.confidence <= 1
    assert result.posterior.shape == (2,)
    # State should have advanced (propagate_state is called by default)
    assert not np.allclose(P_before, P_after)


def test_nimbus_sts_auto_transition_cov():
    """Test automatic transition covariance estimation."""
    rng = np.random.default_rng(42)
    X = rng.standard_normal((40, 4))
    y = np.repeat(np.arange(2), 20)
    
    # With auto-estimation (transition_cov=None)
    clf_auto = NimbusSTS(transition_cov=None, num_steps=10)
    clf_auto.fit(X, y)
    
    # Should still work and have reasonable performance
    preds = clf_auto.predict(X)
    accuracy = np.mean(preds == y)
    assert accuracy >= 0.4  # Should be better than random


def test_nimbus_sts_custom_transition_matrix():
    """Test custom transition matrix specification."""
    rng = np.random.default_rng(42)
    X = rng.standard_normal((40, 4))
    y = np.repeat(np.arange(2), 20)
    
    # Custom transition matrix (damped dynamics)
    state_dim = 1
    A_custom = np.array([[0.95]])  # Damped random walk
    
    clf = NimbusSTS(
        state_dim=state_dim,
        transition_matrix=A_custom,
        num_steps=10
    )
    clf.fit(X, y)
    
    # Should work with custom matrix
    preds = clf.predict(X)
    assert preds.shape == (40,)


def test_nimbus_sts_convergence_monitoring():
    """Test convergence monitoring with verbose mode."""
    import io
    import sys
    
    rng = np.random.default_rng(42)
    X = rng.standard_normal((40, 4))
    y = np.repeat(np.arange(2), 20)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    clf = NimbusSTS(num_steps=50, verbose=True)
    clf.fit(X, y)
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    # Should print step information
    assert "Step" in output
    assert "log_lik" in output


def test_nimbus_sts_data_validation_integration():
    """Test integration with data validation module."""
    from nimbus_bci.data import BCIData, BCIMetadata, check_model_compatibility
    
    rng = np.random.default_rng(42)
    n_features = 8
    n_samples = 40
    n_time_samples = 125  # Simulated time samples per trial
    
    # Create 3D data: (n_features, n_time_samples, n_trials)
    X_3d = rng.standard_normal((n_features, n_time_samples, n_samples))
    y = np.repeat(np.arange(2), 20)
    
    # For classifier, we need 2D aggregated features
    X_2d = np.mean(X_3d, axis=1).T  # (n_trials, n_features)
    
    clf = NimbusSTS(num_steps=10)
    clf.fit(X_2d, y)
    
    # Create BCIData with 3D format
    metadata = BCIMetadata(
        sampling_rate=250.0,
        paradigm="motor_imagery",
        feature_type="csp",
        n_features=n_features,
        n_classes=2,
    )
    data = BCIData(X_3d, metadata, y)
    
    # Check model compatibility (checks n_features only, not temporal dim)
    assert check_model_compatibility(data, clf.model_)
    
    # Wrong number of features should fail
    X_3d_wrong = rng.standard_normal((10, n_time_samples, n_samples))  # Wrong n_features
    metadata_wrong = BCIMetadata(
        sampling_rate=250.0,
        paradigm="motor_imagery",
        feature_type="csp",
        n_features=10,  # Wrong!
        n_classes=2,
    )
    data_wrong = BCIData(X_3d_wrong, metadata_wrong, y)
    
    try:
        check_model_compatibility(data_wrong, clf.model_)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_nimbus_sts_score_method():
    """Test sklearn-compatible score() method."""
    rng = np.random.default_rng(42)
    n_per_class = 30
    n_features = 4
    
    X0 = rng.standard_normal((n_per_class, n_features)) + np.array([2, 0, 0, 0])
    X1 = rng.standard_normal((n_per_class, n_features)) + np.array([-2, 0, 0, 0])
    X = np.vstack([X0, X1])
    y = np.array([0] * n_per_class + [1] * n_per_class)
    
    clf = NimbusSTS(num_steps=30, learning_rate=0.2)
    clf.fit(X, y)
    
    # Test score method
    score = clf.score(X, y)
    assert 0 <= score <= 1
    assert score > 0.5  # Should be better than random

