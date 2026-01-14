"""
INN Plotting Utilities
----------------------------------------------------------------------------------
Simple plotting functions for training loss visualization.

Copyright (C) 2024  Chanwook Park
Northwestern University, Evanston, Illinois, US, chanwookpark2024@u.northwestern.edu
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os


def plot_loss(model, data_name, interp_method, save_dir='plots'):
    """
    Plot training and validation loss vs epoch.

    Args:
        model: Trained model with loss_history or errors_train/errors_val attributes
        data_name: Name of the dataset (for filename)
        interp_method: Method name (for filename)
        save_dir: Directory to save plots (default: 'plots')
    """
    # Create plots directory if needed
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Get loss history from model (support both old and new attribute names)
    if hasattr(model, 'loss_history') and model.loss_history:
        train_loss = model.loss_history
        epochs = list(range(1, len(train_loss) + 1))
        val_loss = getattr(model, 'val_loss_history', None)
    elif hasattr(model, 'errors_train') and model.errors_train:
        train_loss = model.errors_train
        val_loss = getattr(model, 'errors_val', None)
        epochs = getattr(model, 'errors_epoch', list(range(1, len(train_loss) + 1)))
    else:
        print("Warning: No loss history found in model")
        return

    # Create figure
    fig = plt.figure(figsize=(8, 6))
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])

    # Plot training loss
    ax.plot(epochs, train_loss, '-', color='#2563eb', linewidth=2, label='Training loss')

    # Plot validation loss if available
    if val_loss is not None and len(val_loss) > 0:
        # Handle case where val_loss may have different length than epochs
        if len(val_loss) == len(epochs):
            ax.plot(epochs, val_loss, '--', color='#dc2626', linewidth=2, label='Validation loss')
        else:
            # Validation computed at different intervals
            val_epochs = np.linspace(epochs[0], epochs[-1], len(val_loss))
            ax.plot(val_epochs, val_loss, '--', color='#dc2626', linewidth=2, label='Validation loss')

    # Formatting
    ax.set_xlabel('Epoch', fontsize=14)
    ax.set_ylabel('Loss', fontsize=14)
    ax.tick_params(axis='both', labelsize=12)
    ax.set_xlim(0, epochs[-1])
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)

    # Set reasonable y-limits
    all_losses = list(train_loss)
    if val_loss is not None:
        all_losses.extend(val_loss)
    min_loss = min(all_losses) if all_losses else 1e-4
    max_loss = max(all_losses) if all_losses else 1e0

    y_min = max(min_loss * 0.5, 1e-8)
    y_max = min(max_loss * 2, 1e2)
    ax.set_ylim(y_min, y_max)

    ax.legend(shadow=True, borderpad=1, fontsize=12, loc='best')
    ax.set_title(f'{data_name} - {interp_method}', fontsize=14)
    plt.tight_layout()

    # Save figure
    n_epochs = epochs[-1]
    filename = f"{data_name}_{interp_method}_loss_{n_epochs}epoch.png"
    filepath = os.path.join(save_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Loss plot saved to: {filepath}")

    # plt.show()
    plt.close()


def plot_regression(model, cls_data, config):
    """
    Plot results for regression models.
    Plots training loss vs epoch and spatial comparison if plot_in_axis is specified.

    Args:
        model: Trained regression model
        cls_data: Data object with data_name attribute
        config: Configuration dictionary with PLOT settings
    """
    bool_plot = config.get('PLOT', {}).get('bool_plot', True)

    if bool_plot:
        data_name = getattr(cls_data, 'data_name', config.get('data_name', 'unknown'))
        interp_method = getattr(model, 'interp_method', config.get('interp_method', 'unknown'))
        save_dir = config.get('OUTPUT', {}).get('plots_dir', 'plots')
        plot_loss(model, data_name, interp_method, save_dir=save_dir)

        # Plot spatial comparison if plot_in_axis is specified
        if config.get('PLOT', {}).get('plot_in_axis'):
            plot_spatial_comparison(model, cls_data, config)
    else:
        print("\nPlotting deactivated\n")


def plot_classification(model, cls_data, config):
    """
    Plot results for classification models.
    Only plots training loss vs epoch.

    Args:
        model: Trained classification model
        cls_data: Data object with data_name attribute
        config: Configuration dictionary with PLOT settings
    """
    bool_plot = config.get('PLOT', {}).get('bool_plot', True)

    if bool_plot:
        data_name = getattr(cls_data, 'data_name', config.get('data_name', 'unknown'))
        interp_method = getattr(model, 'interp_method', config.get('interp_method', 'unknown'))
        save_dir = config.get('OUTPUT', {}).get('plots_dir', 'plots')
        plot_loss(model, data_name, interp_method, save_dir=save_dir)
    else:
        print("\nPlotting deactivated\n")


# Legacy alias for backward compatibility
plot_loss_landscape = plot_loss


def plot_spatial_comparison(model, cls_data, config, save_dir='plots'):
    """
    Plot original data vs prediction in de-normalized input-output space.

    Automatically detects spatial dimensions (x1, x2, ...) vs parametric dimensions (p1, p2, ...)
    from plot_in_axis config and calls appropriate plotting function.

    Args:
        model: Trained model with forward/v_forward methods and params
        cls_data: Data object with test data and normalization bounds
        config: Configuration dictionary with PLOT settings
        save_dir: Directory to save plots (default: 'plots')
    """
    import jax.numpy as jnp

    # Check if plotting is enabled
    plot_config = config.get('PLOT', {})
    if not plot_config.get('bool_plot', True):
        print("\nSpatial comparison plotting deactivated\n")
        return

    # Get plot configuration
    plot_in_axis = plot_config.get('plot_in_axis', [])
    plot_out_axis = plot_config.get('plot_out_axis', [0])
    plot_params_number = plot_config.get('plot_params_number', 2)

    if not plot_in_axis:
        print("Warning: plot_in_axis not specified in config")
        return

    # Count spatial coordinates (those starting with 'x')
    spatial_indices = [i for i, name in enumerate(plot_in_axis) if name.startswith('x')]
    param_indices = [i for i, name in enumerate(plot_in_axis) if not name.startswith('x')]
    n_spatial = len(spatial_indices)

    print(f"\nPlotting spatial comparison:")
    print(f"  Spatial dimensions: {n_spatial} ({[plot_in_axis[i] for i in spatial_indices]})")
    print(f"  Parametric dimensions: {len(param_indices)} ({[plot_in_axis[i] for i in param_indices]})")
    print(f"  Output axis: {plot_out_axis}")
    print(f"  Number of parameter sets: {plot_params_number}")

    # Call appropriate plotting function based on spatial dimensions
    if n_spatial == 2:
        plot_spatial_2d(model, cls_data, config, spatial_indices, param_indices,
                       plot_out_axis, plot_params_number, save_dir)
    elif n_spatial == 1:
        plot_spatial_1d(model, cls_data, config, spatial_indices, param_indices,
                       plot_out_axis, plot_params_number, save_dir)
    elif n_spatial == 3:
        plot_spatial_3d(model, cls_data, config, spatial_indices, param_indices,
                       plot_out_axis, plot_params_number, save_dir)
    else:
        print(f"Warning: {n_spatial}D spatial plotting not implemented")


def plot_spatial_2d(model, cls_data, config, spatial_indices, param_indices,
                    plot_out_axis, plot_params_number, save_dir='plots'):
    """
    Plot 2D spatial comparison (original vs predicted) for multiple parameter sets.

    Creates a figure with:
    - Rows: different parameter sets from test data
    - Columns: [Original data, Predicted data]
    - Color: output value specified by plot_out_axis

    Args:
        model: Trained model
        cls_data: Data object with test data
        config: Configuration dictionary
        spatial_indices: Indices of spatial coordinates (e.g., [0, 1] for x1, x2)
        param_indices: Indices of parametric coordinates
        plot_out_axis: Which output(s) to plot as color
        plot_params_number: Number of parameter sets to plot
        save_dir: Directory to save plots
    """
    import jax.numpy as jnp

    # Create plots directory if needed
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Get test data
    x_test = cls_data.x_data_test  # Normalized test input
    u_test = cls_data.u_data_test  # Normalized test output

    # Get predictions
    x_test_jax = jnp.array(x_test)
    u_pred = model.v_forward(model.params, x_test_jax)
    u_pred = np.array(u_pred)

    # De-normalize data
    x_test_denorm = denormalize(x_test, cls_data.x_data_minmax)
    u_test_denorm = denormalize(np.array(u_test), cls_data.u_data_minmax)
    u_pred_denorm = denormalize(u_pred, cls_data.u_data_minmax)

    # Find unique parameter combinations in test data
    if len(param_indices) > 0:
        param_values = x_test_denorm[:, param_indices]
        # Round to avoid floating point issues
        param_rounded = np.round(param_values, decimals=6)
        unique_params, unique_indices = np.unique(param_rounded, axis=0, return_inverse=True)

        # Select parameter sets to plot (evenly spaced through unique params)
        n_unique = len(unique_params)
        if n_unique >= plot_params_number:
            selected_param_indices = np.linspace(0, n_unique - 1, plot_params_number, dtype=int)
        else:
            selected_param_indices = np.arange(n_unique)
            plot_params_number = n_unique
    else:
        # No parametric dimensions, plot all data as one set
        unique_indices = np.zeros(len(x_test), dtype=int)
        selected_param_indices = [0]
        plot_params_number = 1
        unique_params = np.array([[]])

    # Get output index to plot
    out_idx = plot_out_axis[0] if isinstance(plot_out_axis, list) else plot_out_axis

    # Get axis labels
    plot_in_axis = config.get('PLOT', {}).get('plot_in_axis', [])
    x_label = plot_in_axis[spatial_indices[0]] if len(plot_in_axis) > spatial_indices[0] else 'x1'
    y_label = plot_in_axis[spatial_indices[1]] if len(plot_in_axis) > spatial_indices[1] else 'x2'

    # Create figure
    fig, axes = plt.subplots(plot_params_number, 2, figsize=(12, 5 * plot_params_number))

    # Handle single row case
    if plot_params_number == 1:
        axes = axes.reshape(1, -1)

    # Global color limits for consistency
    all_u_test = u_test_denorm[:, out_idx]
    all_u_pred = u_pred_denorm[:, out_idx]
    vmin = min(np.min(all_u_test), np.min(all_u_pred))
    vmax = max(np.max(all_u_test), np.max(all_u_pred))

    for row, param_idx in enumerate(selected_param_indices):
        # Get data points for this parameter set
        mask = unique_indices == param_idx

        x_spatial = x_test_denorm[mask][:, spatial_indices]
        u_original = u_test_denorm[mask, out_idx]
        u_predicted = u_pred_denorm[mask, out_idx]

        # Get parameter values for title
        if len(param_indices) > 0:
            param_vals = unique_params[param_idx]
            param_names = [plot_in_axis[i] for i in param_indices]
            param_str = ', '.join([f'{n}={v:.3g}' for n, v in zip(param_names, param_vals)])
        else:
            param_str = 'All data'

        # Plot original data (left column)
        ax_orig = axes[row, 0]
        sc_orig = ax_orig.scatter(x_spatial[:, 0], x_spatial[:, 1], c=u_original,
                                   cmap='viridis', vmin=vmin, vmax=vmax, s=20, alpha=0.8)
        ax_orig.set_xlabel(x_label, fontsize=12)
        ax_orig.set_ylabel(y_label, fontsize=12)
        ax_orig.set_title(f'Original: {param_str}', fontsize=11)
        ax_orig.set_aspect('equal', adjustable='box')
        plt.colorbar(sc_orig, ax=ax_orig, label=f'Output[{out_idx}]')

        # Plot predicted data (right column)
        ax_pred = axes[row, 1]
        sc_pred = ax_pred.scatter(x_spatial[:, 0], x_spatial[:, 1], c=u_predicted,
                                   cmap='viridis', vmin=vmin, vmax=vmax, s=20, alpha=0.8)
        ax_pred.set_xlabel(x_label, fontsize=12)
        ax_pred.set_ylabel(y_label, fontsize=12)
        ax_pred.set_title(f'Predicted: {param_str}', fontsize=11)
        ax_pred.set_aspect('equal', adjustable='box')
        plt.colorbar(sc_pred, ax=ax_pred, label=f'Output[{out_idx}]')

        # Compute and display RMSE for this parameter set
        rmse = np.sqrt(np.mean((u_original - u_predicted) ** 2))
        ax_pred.text(0.02, 0.98, f'RMSE: {rmse:.4e}', transform=ax_pred.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Add overall title
    data_name = config.get('data_name', 'unknown')
    interp_method = config.get('interp_method', 'unknown')
    fig.suptitle(f'{data_name} - {interp_method}: Original vs Predicted', fontsize=14, y=1.02)

    plt.tight_layout()

    # Save figure
    filename = f"{data_name}_{interp_method}_spatial_comparison.png"
    filepath = os.path.join(save_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Spatial comparison plot saved to: {filepath}")

    # plt.show()
    plt.close()


def plot_spatial_1d(model, cls_data, config, spatial_indices, param_indices,
                    plot_out_axis, plot_params_number, save_dir='plots'):
    """
    Plot 1D spatial comparison (original vs predicted) for multiple parameter sets.

    Args:
        model: Trained model
        cls_data: Data object with test data
        config: Configuration dictionary
        spatial_indices: Indices of spatial coordinates
        param_indices: Indices of parametric coordinates
        plot_out_axis: Which output(s) to plot
        plot_params_number: Number of parameter sets to plot
        save_dir: Directory to save plots
    """
    import jax.numpy as jnp

    # Create plots directory if needed
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Get test data
    x_test = cls_data.x_data_test
    u_test = cls_data.u_data_test

    # Get predictions
    x_test_jax = jnp.array(x_test)
    u_pred = model.v_forward(model.params, x_test_jax)
    u_pred = np.array(u_pred)

    # De-normalize data
    x_test_denorm = denormalize(x_test, cls_data.x_data_minmax)
    u_test_denorm = denormalize(np.array(u_test), cls_data.u_data_minmax)
    u_pred_denorm = denormalize(u_pred, cls_data.u_data_minmax)

    # Find unique parameter combinations
    if len(param_indices) > 0:
        param_values = x_test_denorm[:, param_indices]
        param_rounded = np.round(param_values, decimals=6)
        unique_params, unique_indices = np.unique(param_rounded, axis=0, return_inverse=True)
        n_unique = len(unique_params)
        if n_unique >= plot_params_number:
            selected_param_indices = np.linspace(0, n_unique - 1, plot_params_number, dtype=int)
        else:
            selected_param_indices = np.arange(n_unique)
            plot_params_number = n_unique
    else:
        unique_indices = np.zeros(len(x_test), dtype=int)
        selected_param_indices = [0]
        plot_params_number = 1
        unique_params = np.array([[]])

    out_idx = plot_out_axis[0] if isinstance(plot_out_axis, list) else plot_out_axis
    plot_in_axis = config.get('PLOT', {}).get('plot_in_axis', [])
    x_label = plot_in_axis[spatial_indices[0]] if len(plot_in_axis) > spatial_indices[0] else 'x'

    # Create figure
    fig, axes = plt.subplots(plot_params_number, 1, figsize=(10, 4 * plot_params_number))

    if plot_params_number == 1:
        axes = [axes]

    for row, param_idx in enumerate(selected_param_indices):
        mask = unique_indices == param_idx

        x_spatial = x_test_denorm[mask][:, spatial_indices[0]]
        u_original = u_test_denorm[mask, out_idx]
        u_predicted = u_pred_denorm[mask, out_idx]

        # Sort by x for proper line plotting
        sort_idx = np.argsort(x_spatial)
        x_spatial = x_spatial[sort_idx]
        u_original = u_original[sort_idx]
        u_predicted = u_predicted[sort_idx]

        if len(param_indices) > 0:
            param_vals = unique_params[param_idx]
            param_names = [plot_in_axis[i] for i in param_indices]
            param_str = ', '.join([f'{n}={v:.3g}' for n, v in zip(param_names, param_vals)])
        else:
            param_str = 'All data'

        ax = axes[row]
        ax.plot(x_spatial, u_original, 'b-', linewidth=2, label='Original', alpha=0.8)
        ax.plot(x_spatial, u_predicted, 'r--', linewidth=2, label='Predicted', alpha=0.8)
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(f'Output[{out_idx}]', fontsize=12)
        ax.set_title(param_str, fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)

        rmse = np.sqrt(np.mean((u_original - u_predicted) ** 2))
        ax.text(0.02, 0.98, f'RMSE: {rmse:.4e}', transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    data_name = config.get('data_name', 'unknown')
    interp_method = config.get('interp_method', 'unknown')
    fig.suptitle(f'{data_name} - {interp_method}: Original vs Predicted', fontsize=14)

    plt.tight_layout()

    filename = f"{data_name}_{interp_method}_spatial_comparison.png"
    filepath = os.path.join(save_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Spatial comparison plot saved to: {filepath}")

    # plt.show()
    plt.close()


def plot_spatial_3d(model, cls_data, config, spatial_indices, param_indices,
                    plot_out_axis, plot_params_number, save_dir='plots'):
    """
    Plot 3D spatial comparison (original vs predicted) for multiple parameter sets.
    Uses 3D scatter plots with color representing the output value.
    """
    import jax.numpy as jnp
    from mpl_toolkits.mplot3d import Axes3D

    # Create plots directory if needed
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Get test data and predictions
    x_test = cls_data.x_data_test
    u_test = cls_data.u_data_test

    x_test_jax = jnp.array(x_test)
    u_pred = model.v_forward(model.params, x_test_jax)
    u_pred = np.array(u_pred)

    # De-normalize
    x_test_denorm = denormalize(x_test, cls_data.x_data_minmax)
    u_test_denorm = denormalize(np.array(u_test), cls_data.u_data_minmax)
    u_pred_denorm = denormalize(u_pred, cls_data.u_data_minmax)

    # Find unique parameter combinations
    if len(param_indices) > 0:
        param_values = x_test_denorm[:, param_indices]
        param_rounded = np.round(param_values, decimals=6)
        unique_params, unique_indices = np.unique(param_rounded, axis=0, return_inverse=True)
        n_unique = len(unique_params)
        if n_unique >= plot_params_number:
            selected_param_indices = np.linspace(0, n_unique - 1, plot_params_number, dtype=int)
        else:
            selected_param_indices = np.arange(n_unique)
            plot_params_number = n_unique
    else:
        unique_indices = np.zeros(len(x_test), dtype=int)
        selected_param_indices = [0]
        plot_params_number = 1
        unique_params = np.array([[]])

    out_idx = plot_out_axis[0] if isinstance(plot_out_axis, list) else plot_out_axis
    plot_in_axis = config.get('PLOT', {}).get('plot_in_axis', [])

    # Create figure
    fig = plt.figure(figsize=(14, 6 * plot_params_number))

    vmin = min(np.min(u_test_denorm[:, out_idx]), np.min(u_pred_denorm[:, out_idx]))
    vmax = max(np.max(u_test_denorm[:, out_idx]), np.max(u_pred_denorm[:, out_idx]))

    for row, param_idx in enumerate(selected_param_indices):
        mask = unique_indices == param_idx

        x_spatial = x_test_denorm[mask][:, spatial_indices]
        u_original = u_test_denorm[mask, out_idx]
        u_predicted = u_pred_denorm[mask, out_idx]

        if len(param_indices) > 0:
            param_vals = unique_params[param_idx]
            param_names = [plot_in_axis[i] for i in param_indices]
            param_str = ', '.join([f'{n}={v:.3g}' for n, v in zip(param_names, param_vals)])
        else:
            param_str = 'All data'

        # Original (left)
        ax_orig = fig.add_subplot(plot_params_number, 2, 2*row + 1, projection='3d')
        sc_orig = ax_orig.scatter(x_spatial[:, 0], x_spatial[:, 1], x_spatial[:, 2],
                                   c=u_original, cmap='viridis', vmin=vmin, vmax=vmax, s=10)
        ax_orig.set_xlabel(plot_in_axis[spatial_indices[0]])
        ax_orig.set_ylabel(plot_in_axis[spatial_indices[1]])
        ax_orig.set_zlabel(plot_in_axis[spatial_indices[2]])
        ax_orig.set_title(f'Original: {param_str}', fontsize=10)

        # Predicted (right)
        ax_pred = fig.add_subplot(plot_params_number, 2, 2*row + 2, projection='3d')
        sc_pred = ax_pred.scatter(x_spatial[:, 0], x_spatial[:, 1], x_spatial[:, 2],
                                   c=u_predicted, cmap='viridis', vmin=vmin, vmax=vmax, s=10)
        ax_pred.set_xlabel(plot_in_axis[spatial_indices[0]])
        ax_pred.set_ylabel(plot_in_axis[spatial_indices[1]])
        ax_pred.set_zlabel(plot_in_axis[spatial_indices[2]])
        ax_pred.set_title(f'Predicted: {param_str}', fontsize=10)

        rmse = np.sqrt(np.mean((u_original - u_predicted) ** 2))
        ax_pred.text2D(0.02, 0.98, f'RMSE: {rmse:.4e}', transform=ax_pred.transAxes,
                      fontsize=9, verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    data_name = config.get('data_name', 'unknown')
    interp_method = config.get('interp_method', 'unknown')
    fig.suptitle(f'{data_name} - {interp_method}: Original vs Predicted', fontsize=14)

    plt.tight_layout()

    filename = f"{data_name}_{interp_method}_spatial_comparison.png"
    filepath = os.path.join(save_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Spatial comparison plot saved to: {filepath}")

    # plt.show()
    plt.close()


def denormalize(data, minmax):
    """
    De-normalize data from [0, 1] back to original range.

    Args:
        data: Normalized data array
        minmax: Dictionary with 'min' and 'max' arrays

    Returns:
        De-normalized data array
    """
    return data * (minmax["max"] - minmax["min"]) + minmax["min"]
