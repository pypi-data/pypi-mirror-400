"""Train data configuration tool - Cython-compiled module."""

import os
from typing import Any, Optional
from pathlib import Path

try:
    import yaml
except ImportError as e:
    raise ImportError(
        "PyYAML is not installed. Install it with: pip install pyyaml"
    ) from e


# Define required fields that must be provided by the user
REQUIRED_FIELDS = {
    "DATA_PARAM": ["input_col", "output_col", "data_filenames"]
}


def _get_config_ref_path() -> Path:
    """Get the path to the reference config file."""
    return Path(__file__).parent / "config" / "config_ref.yaml"


def _load_reference_config() -> dict:
    """Load the reference configuration from YAML file."""
    config_path = _get_config_ref_path()
    if not config_path.exists():
        raise FileNotFoundError(
            f"Reference config file not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _validate_required_fields(user_config: dict) -> list[str]:
    """
    Check if all required fields are provided.

    Returns:
        List of missing required field paths (e.g., ["DATA_PARAM.input_col"])
    """
    missing = []

    for section, fields in REQUIRED_FIELDS.items():
        if section not in user_config:
            # All fields in this section are missing
            for field in fields:
                missing.append(f"{section}.{field}")
        else:
            for field in fields:
                if field not in user_config[section]:
                    missing.append(f"{section}.{field}")

    return missing


def _deep_update(base: dict, updates: dict) -> dict:
    """
    Recursively update a nested dictionary.

    Args:
        base: The base dictionary to update
        updates: The dictionary with updates to apply

    Returns:
        Updated dictionary
    """
    result = base.copy()

    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_update(result[key], value)
        else:
            result[key] = value

    return result


def execute_train_data(
    input_col: Optional[list[int]] = None,
    output_col: Optional[list[int]] = None,
    data_filenames: Optional[list[str]] = None,
    interp_method: Optional[str] = None,
    nmode: Optional[int] = None,
    nseg: Optional[int] = None,
    s_patch: Optional[int] = None,
    alpha_dil: Optional[float] = None,
    p_order: Optional[int] = None,
    radial_basis: Optional[str] = None,
    INNactivation: Optional[str] = None,
    sigma_factor: Optional[float] = None,
    nlayers: Optional[int] = None,
    nneurons: Optional[int] = None,
    activation: Optional[str] = None,
    hidden_dim: Optional[int] = None,
    grid_size: Optional[int] = None,
    spline_order: Optional[int] = None,
    num_layers: Optional[int] = None,
    modes: Optional[int] = None,
    split_ratio: Optional[list[float]] = None,
    bool_data_generation: Optional[bool] = None,
    bool_normalize: Optional[bool] = None,
    bool_shuffle: Optional[bool] = None,
    num_epochs_INN: Optional[int] = None,
    num_epochs_MLP: Optional[int] = None,
    num_epochs_KAN: Optional[int] = None,
    num_epochs_FNO: Optional[int] = None,
    batch_size: Optional[int] = None,
    learning_rate: Optional[float] = None,
    validation_period: Optional[int] = None,
    bool_denormalize: Optional[bool] = None,
    patience: Optional[int] = None,
    stopping_loss_train: Optional[float] = None,
    bool_save_model: Optional[bool] = None,
    bool_plot: Optional[bool] = None,
    plot_in_axis: Optional[list[str]] = None,
    plot_out_axis: Optional[list[int]] = None,
    plot_params_number: Optional[int] = None,
) -> dict:
    """
    Create a training configuration dictionary based on reference config.

    Reads the reference config file and updates components from user input.
    Required fields (input_col, output_col, data_filenames) must be provided.
    Optional fields use reference defaults if not specified.

    Args:
        input_col: (REQUIRED) List of integers. Input columns of the data.
        output_col: (REQUIRED) List of integers. Output columns of the data.
        data_filenames: (REQUIRED) List of file paths for train/val/test data.
        interp_method: Interpolation method ("linear", "nonlinear", "gaussian", "MLP", "KAN", "FNO")
        nmode: Number of CP tensor decomposition modes
        nseg: Number of segments in each dimension
        s_patch: Size of patch for nonlinear INN
        alpha_dil: Dilatation factor for nonlinear INN
        p_order: Polynomial order for nonlinear INN
        radial_basis: Radial basis function for nonlinear INN
        INNactivation: Activation function for nonlinear INN
        sigma_factor: Sigma factor for Gaussian INN
        nlayers: Number of layers for MLP
        nneurons: Number of neurons for MLP
        activation: Activation function for MLP
        hidden_dim: Hidden dimensions for KAN
        grid_size: Grid size for KAN
        spline_order: B-spline order for KAN
        num_layers: Number of layers for FNO
        modes: Number of modes for FNO
        split_ratio: Train/val/test split ratio
        bool_data_generation: Whether to generate data
        bool_normalize: Whether to normalize training data
        bool_shuffle: Whether to shuffle training data
        num_epochs_INN: Number of epochs for INN
        num_epochs_MLP: Number of epochs for MLP
        num_epochs_KAN: Number of epochs for KAN
        num_epochs_FNO: Number of epochs for FNO
        batch_size: Batch size for training
        learning_rate: Learning rate
        validation_period: Period for validation
        bool_denormalize: Whether to denormalize predictions
        patience: Training patience
        stopping_loss_train: Stopping loss threshold
        bool_save_model: Whether to save the model
        bool_plot: Whether to plot results
        plot_in_axis: Input variable types for plotting
        plot_out_axis: Output variable indices for plotting
        plot_params_number: Number of parameter sets to plot

    Returns:
        Complete configuration dictionary with all parameters

    Raises:
        ValueError: If required fields are missing
        FileNotFoundError: If reference config file not found
    """
    # Load reference configuration
    config = _load_reference_config()

    # Build user updates dictionary
    user_updates = {}

    # MODEL_PARAM updates
    model_updates = {}
    if interp_method is not None:
        model_updates["interp_method"] = interp_method
    if nmode is not None:
        model_updates["nmode"] = nmode
    if nseg is not None:
        model_updates["nseg"] = nseg
    if s_patch is not None:
        model_updates["s_patch"] = s_patch
    if alpha_dil is not None:
        model_updates["alpha_dil"] = alpha_dil
    if p_order is not None:
        model_updates["p_order"] = p_order
    if radial_basis is not None:
        model_updates["radial_basis"] = radial_basis
    if INNactivation is not None:
        model_updates["INNactivation"] = INNactivation
    if sigma_factor is not None:
        model_updates["sigma_factor"] = sigma_factor
    if nlayers is not None:
        model_updates["nlayers"] = nlayers
    if nneurons is not None:
        model_updates["nneurons"] = nneurons
    if activation is not None:
        model_updates["activation"] = activation
    if hidden_dim is not None:
        model_updates["hidden_dim"] = hidden_dim
    if grid_size is not None:
        model_updates["grid_size"] = grid_size
    if spline_order is not None:
        model_updates["spline_order"] = spline_order
    if num_layers is not None:
        model_updates["num_layers"] = num_layers
    if modes is not None:
        model_updates["modes"] = modes

    if model_updates:
        user_updates["MODEL_PARAM"] = model_updates

    # DATA_PARAM updates
    data_updates = {}
    if input_col is not None:
        data_updates["input_col"] = input_col
    if output_col is not None:
        data_updates["output_col"] = output_col
    if data_filenames is not None:
        data_updates["data_filenames"] = data_filenames
    if split_ratio is not None:
        data_updates["split_ratio"] = split_ratio
    if bool_data_generation is not None:
        data_updates["bool_data_generation"] = bool_data_generation
    if bool_normalize is not None:
        data_updates["bool_normalize"] = bool_normalize
    if bool_shuffle is not None:
        data_updates["bool_shuffle"] = bool_shuffle

    if data_updates:
        user_updates["DATA_PARAM"] = data_updates

    # TRAIN_PARAM updates
    train_updates = {}
    if num_epochs_INN is not None:
        train_updates["num_epochs_INN"] = num_epochs_INN
    if num_epochs_MLP is not None:
        train_updates["num_epochs_MLP"] = num_epochs_MLP
    if num_epochs_KAN is not None:
        train_updates["num_epochs_KAN"] = num_epochs_KAN
    if num_epochs_FNO is not None:
        train_updates["num_epochs_FNO"] = num_epochs_FNO
    if batch_size is not None:
        train_updates["batch_size"] = batch_size
    if learning_rate is not None:
        train_updates["learning_rate"] = learning_rate
    if validation_period is not None:
        train_updates["validation_period"] = validation_period
    if bool_denormalize is not None:
        train_updates["bool_denormalize"] = bool_denormalize
    if patience is not None:
        train_updates["patience"] = patience
    if stopping_loss_train is not None:
        train_updates["stopping_loss_train"] = stopping_loss_train
    if bool_save_model is not None:
        train_updates["bool_save_model"] = bool_save_model

    if train_updates:
        user_updates["TRAIN_PARAM"] = train_updates

    # PLOT updates
    plot_updates = {}
    if bool_plot is not None:
        plot_updates["bool_plot"] = bool_plot
    if plot_in_axis is not None:
        plot_updates["plot_in_axis"] = plot_in_axis
    if plot_out_axis is not None:
        plot_updates["plot_out_axis"] = plot_out_axis
    if plot_params_number is not None:
        plot_updates["plot_params_number"] = plot_params_number

    if plot_updates:
        user_updates["PLOT"] = plot_updates

    # Apply user updates to config
    config = _deep_update(config, user_updates)

    # Validate required fields
    missing_fields = _validate_required_fields(user_updates)
    if missing_fields:
        raise ValueError(
            f"Missing required fields: {', '.join(missing_fields)}. "
            "These fields must be provided by the user."
        )

    return config
