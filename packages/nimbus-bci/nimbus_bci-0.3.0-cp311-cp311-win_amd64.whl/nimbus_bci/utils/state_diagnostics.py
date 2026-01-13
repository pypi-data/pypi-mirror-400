"""State diagnostics and visualization utilities for NimbusSTS.

This module provides tools for visualizing and analyzing the latent state
evolution in NimbusSTS models, useful for debugging and understanding temporal
dynamics in BCI applications.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np

if TYPE_CHECKING:
    from ..models.nimbus_sts import NimbusSTS


def plot_latent_trajectory(
    clf: "NimbusSTS",
    X: np.ndarray,
    y: np.ndarray,
    figsize: tuple[float, float] = (12, 6),
    title: Optional[str] = None,
):
    """Plot latent state evolution over time.
    
    Parameters
    ----------
    clf : NimbusSTS
        Fitted classifier.
    X : np.ndarray of shape (n_samples, n_features)
        Sequential data.
    y : np.ndarray of shape (n_samples,)
        True labels.
    figsize : tuple of float, default=(12, 6)
        Figure size.
    title : str, optional
        Plot title.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    
    Examples
    --------
    >>> from nimbus_bci import NimbusSTS
    >>> from nimbus_bci.utils.state_diagnostics import plot_latent_trajectory
    >>> 
    >>> clf = NimbusSTS(num_steps=50)
    >>> clf.fit(X_train, y_train)
    >>> 
    >>> fig = plot_latent_trajectory(clf, X_train, y_train)
    >>> fig.savefig("latent_trajectory.png")
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for plotting. "
            "Install with: pip install matplotlib"
        )
    
    from ..models.nimbus_sts.inference import run_filter
    
    if not hasattr(clf, "model_"):
        raise ValueError("Classifier must be fitted before plotting")
    
    params = clf.model_.params
    state_dim = int(params["state_dim"])
    
    # Run filter to get state trajectory
    y_encoded = np.asarray(y)
    if clf._label_encoder is not None:
        y_encoded = np.array([clf._label_encoder.get(yi, yi) for yi in y])
    
    z_means, z_covs = run_filter(
        X, y_encoded,
        params["z_mean_init"], params["z_cov_init"],
        params["A"], params["Q"],
        params["W"], params["H"], params["b"], params["R"]
    )
    
    # Create subplots
    fig, axes = plt.subplots(
        state_dim, 1,
        figsize=figsize,
        sharex=True,
        squeeze=False
    )
    axes = axes.flatten()
    
    if title is not None:
        fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # Get unique classes for coloring
    unique_classes = np.unique(y)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_classes)))
    class_to_color = {c: colors[i] for i, c in enumerate(unique_classes)}
    
    for dim in range(state_dim):
        ax = axes[dim]
        
        # Plot mean trajectory
        time_steps = np.arange(len(z_means))
        ax.plot(
            time_steps, z_means[:, dim],
            linewidth=2, color='darkblue',
            label=f'State z[{dim}]'
        )
        
        # Plot uncertainty bands (±2σ)
        std = np.sqrt(z_covs[:, dim, dim])
        ax.fill_between(
            time_steps,
            z_means[:, dim] - 2 * std,
            z_means[:, dim] + 2 * std,
            alpha=0.3, color='blue',
            label='±2σ uncertainty'
        )
        
        # Color background by true class
        for t in range(len(y)):
            ax.axvspan(
                t, t + 1,
                alpha=0.15,
                color=class_to_color[y[t]],
                linewidth=0
            )
        
        ax.set_ylabel(f'z[{dim}]', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper right', fontsize=9)
        
        # Add zero reference line
        ax.axhline(0, color='black', linestyle=':', alpha=0.3, linewidth=1)
    
    axes[-1].set_xlabel('Time (trials)', fontsize=11, fontweight='bold')
    
    # Add class legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=class_to_color[c], alpha=0.3, label=f'Class {c}')
        for c in unique_classes
    ]
    axes[0].legend(
        handles=legend_elements,
        loc='upper left',
        fontsize=9,
        title='True Classes'
    )
    
    plt.tight_layout()
    return fig


def analyze_state_stability(
    clf: "NimbusSTS",
    X: np.ndarray,
    y: np.ndarray,
) -> dict:
    """Analyze stability of latent state over time.
    
    Computes metrics to assess how stable the latent state is,
    useful for detecting excessive drift or instability.
    
    Parameters
    ----------
    clf : NimbusSTS
        Fitted classifier.
    X : np.ndarray of shape (n_samples, n_features)
        Sequential data.
    y : np.ndarray of shape (n_samples,)
        True labels.
    
    Returns
    -------
    metrics : dict
        Dictionary containing:
        - 'mean_state_change': Mean L2 norm of state changes
        - 'max_state_change': Maximum L2 norm of state change
        - 'state_variance': Variance of each state dimension
        - 'uncertainty_growth': Mean growth rate of uncertainty
    
    Examples
    --------
    >>> metrics = analyze_state_stability(clf, X_train, y_train)
    >>> print(f"Mean state change: {metrics['mean_state_change']:.4f}")
    >>> print(f"Uncertainty growth: {metrics['uncertainty_growth']:.4f}")
    """
    from ..models.nimbus_sts.inference import run_filter
    
    if not hasattr(clf, "model_"):
        raise ValueError("Classifier must be fitted before analysis")
    
    params = clf.model_.params
    
    # Run filter to get state trajectory
    y_encoded = np.asarray(y)
    if clf._label_encoder is not None:
        y_encoded = np.array([clf._label_encoder.get(yi, yi) for yi in y])
    
    z_means, z_covs = run_filter(
        X, y_encoded,
        params["z_mean_init"], params["z_cov_init"],
        params["A"], params["Q"],
        params["W"], params["H"], params["b"], params["R"]
    )
    
    # Compute state changes
    state_changes = np.diff(z_means, axis=0)
    state_change_norms = np.linalg.norm(state_changes, axis=1)
    
    # Compute uncertainty (trace of covariance)
    uncertainties = np.array([np.trace(P) for P in z_covs])
    uncertainty_changes = np.diff(uncertainties)
    
    # Compute state variance over time
    state_variance = np.var(z_means, axis=0)
    
    metrics = {
        'mean_state_change': float(np.mean(state_change_norms)),
        'max_state_change': float(np.max(state_change_norms)),
        'state_variance': state_variance,
        'uncertainty_growth': float(np.mean(uncertainty_changes)),
        'final_uncertainty': float(uncertainties[-1]),
        'initial_uncertainty': float(uncertainties[0]),
    }
    
    return metrics


def diagnose_convergence(
    clf: "NimbusSTS",
    X: np.ndarray,
    y: np.ndarray,
    window_size: int = 10,
) -> dict:
    """Diagnose convergence issues in NimbusSTS training.
    
    Parameters
    ----------
    clf : NimbusSTS
        Fitted classifier.
    X : np.ndarray
        Training data.
    y : np.ndarray
        Training labels.
    window_size : int, default=10
        Window size for smoothing accuracy.
    
    Returns
    -------
    diagnostics : dict
        Dictionary containing:
        - 'training_accuracy': Final training accuracy
        - 'state_stability': State stability metrics
        - 'recommendations': List of recommendations
    """
    from ..models.nimbus_sts.inference import run_filter, softmax
    
    if not hasattr(clf, "model_"):
        raise ValueError("Classifier must be fitted before diagnosis")
    
    params = clf.model_.params
    
    # Compute training accuracy
    preds = clf.predict(X)
    training_accuracy = float(np.mean(preds == y))
    
    # Analyze state stability
    stability_metrics = analyze_state_stability(clf, X, y)
    
    # Generate recommendations
    recommendations = []
    
    if training_accuracy < 0.6:
        recommendations.append(
            "Low training accuracy. Consider increasing num_steps or learning_rate."
        )
    
    if stability_metrics['mean_state_change'] < 0.01:
        recommendations.append(
            "Very low state changes. Consider increasing transition_cov "
            "to allow more temporal adaptation."
        )
    
    if stability_metrics['mean_state_change'] > 1.0:
        recommendations.append(
            "Large state changes detected. Consider decreasing transition_cov "
            "or learning_rate for more stability."
        )
    
    if stability_metrics['uncertainty_growth'] > 0.1:
        recommendations.append(
            "Uncertainty is growing rapidly. This is normal for propagate_state(), "
            "but concerning during training. Check observation_cov parameter."
        )
    
    if not recommendations:
        recommendations.append("Model appears to be converging well!")
    
    diagnostics = {
        'training_accuracy': training_accuracy,
        'state_stability': stability_metrics,
        'recommendations': recommendations,
    }
    
    return diagnostics

