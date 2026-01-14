"""Train data configuration and training tool - Cython-compiled module."""

import os
import sys
import io
from typing import Any, Optional
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError as e:
    raise ImportError(
        "PyYAML is not installed. Install it with: pip install pyyaml"
    ) from e

from .pyinn.main import train_model


# Define required fields that must be provided by the user
REQUIRED_FIELDS = {
    "DATA_PARAM": ["input_col", "output_col", "data_train"]
}

# Output directories (relative to tools folder)
def _get_tools_dir() -> Path:
    """Get the tools directory path."""
    return Path(__file__).parent

def _get_model_save_dir() -> Path:
    """Get the directory for saving models."""
    save_dir = _get_tools_dir() / "pyinn" / "model_saved"
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir

def _get_plots_dir() -> Path:
    """Get the directory for saving plots."""
    plots_dir = _get_tools_dir() / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    return plots_dir

def _get_logs_dir() -> Path:
    """Get the directory for saving logs."""
    logs_dir = _get_tools_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


class LogCapture:
    """Context manager to capture stdout and save to log file."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.captured = io.StringIO()
        self.original_stdout = None

    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.captured
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        # Save captured output to file
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(self.captured.getvalue())
        return False

    def get_logs(self) -> str:
        """Get the captured log content."""
        return self.captured.getvalue()


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
    data_train: Optional[str] = None,
    data_val: Optional[str] = None,
    data_test: Optional[str] = None,
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
    # Training execution parameters
    run_type: str = "regression",
    gpu_idx: int = 0,
) -> dict:
    """
    Create a training configuration and execute model training.

    This tool:
    1. Creates a configuration dictionary from reference config and user inputs
    2. Combines data file paths into data_filenames list
    3. Validates that required fields are provided
    4. Executes the training pipeline
    5. Saves model to tools/pyinn/model_saved/ and plots to tools/plots/

    Args:
        input_col: (REQUIRED) List of integers. Input columns of the data.
        output_col: (REQUIRED) List of integers. Output columns of the data.
        data_train: (REQUIRED) Full file path to training data CSV file.
        data_val: (Optional) Full file path to validation data CSV file.
        data_test: (Optional) Full file path to test data CSV file.
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
        run_type: Problem type - 'regression' or 'classification'
        gpu_idx: GPU device index (default: 0)

    Returns:
        Dictionary with training results including:
        - config: The complete configuration used
        - model_save_path: Path where model was saved (if bool_save_model=True)
        - plots_path: Path where plots were saved (if bool_plot=True)
        - training_completed: Boolean indicating success

    Raises:
        ValueError: If required fields are missing
        FileNotFoundError: If reference config file not found
    """
    # Load reference configuration
    config = _load_reference_config()

    # Combine data file paths into data_filenames list
    # Order: [train] or [train, val] or [train, test] or [train, val, test]
    data_filenames = None
    if data_train is not None:
        data_filenames = [data_train]
        if data_val is not None and data_test is not None:
            # All three provided: [train, val, test]
            data_filenames = [data_train, data_val, data_test]
        elif data_val is not None:
            # Train and val: [train, val]
            data_filenames = [data_train, data_val]
        elif data_test is not None:
            # Train and test: [train, test]
            data_filenames = [data_train, data_test]

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
    if data_train is not None:
        # Store data_train for validation purposes
        data_updates["data_train"] = data_train
    if data_filenames is not None:
        # Store combined data_filenames for the training pipeline
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

    # Set output directories in config
    model_save_dir = _get_model_save_dir()
    plots_dir = _get_plots_dir()
    logs_dir = _get_logs_dir()

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    interp_name = interp_method if interp_method else config["MODEL_PARAM"]["interp_method"]
    log_filename = f"training_{interp_name}_{timestamp}.log"
    log_path = logs_dir / log_filename

    # Add output paths to config for the training pipeline
    if "OUTPUT" not in config:
        config["OUTPUT"] = {}
    config["OUTPUT"]["model_save_dir"] = str(model_save_dir)
    config["OUTPUT"]["plots_dir"] = str(plots_dir)
    config["OUTPUT"]["logs_dir"] = str(logs_dir)

    # Execute training with log capture
    import time as time_module
    train_rmse = None
    val_rmse = None
    test_rmse = None
    training_time = None

    with LogCapture(log_path) as log_capture:
        print(f"\n{'='*60}")
        print("Starting Training Pipeline")
        print(f"{'='*60}")
        print(f"Model save directory: {model_save_dir}")
        print(f"Plots directory: {plots_dir}")
        print(f"Log file: {log_path}")
        print(f"{'='*60}\n")

        try:
            start_time = time_module.time()
            model = train_model(
                config=config,
                run_type=run_type,
                gpu_idx=gpu_idx,
            )
            training_time = time_module.time() - start_time
            training_completed = True

            # Extract metrics from trained model
            if hasattr(model, 'errors_train') and model.errors_train:
                train_rmse = model.errors_train[-1]
            if hasattr(model, 'errors_val') and model.errors_val:
                val_rmse = model.errors_val[-1]
            if hasattr(model, 'error_test'):
                test_rmse = model.error_test

            print("\nTraining completed successfully!")
            print(f"Total training time: {training_time:.2f} seconds")
        except Exception as e:
            training_completed = False
            print(f"\nTraining failed with error: {e}")
            raise

    # Return results
    return {
        "config": config,
        "model_save_path": str(model_save_dir) if config.get("TRAIN_PARAM", {}).get("bool_save_model", False) else None,
        "plots_path": str(plots_dir) if config.get("PLOT", {}).get("bool_plot", False) else None,
        "log_path": str(log_path),
        "training_completed": training_completed,
        "interp_method": config["MODEL_PARAM"]["interp_method"],
        "run_type": run_type,
        "train_rmse": train_rmse,
        "val_rmse": val_rmse,
        "test_rmse": test_rmse,
        "training_time_seconds": training_time,
    }
