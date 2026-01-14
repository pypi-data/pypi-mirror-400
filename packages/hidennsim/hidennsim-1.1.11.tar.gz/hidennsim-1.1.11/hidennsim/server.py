"""MCP Server for HIDENNSIM - Cython-compiled module."""

import asyncio
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from . import __version__
from .tools.add_jax import execute_add_jax
from .tools.subtract_jax import execute_subtract_jax
from .tools.multiply_jax import execute_multiply_jax
from .tools.csv_dimensions import execute_csv_dimensions
from .tools.train_data import execute_train_data


class HIDENNSIMServer:
    """MCP server with JAX-based numerical tools."""

    def __init__(self):
        self.server = Server("hidennsim")
        self._setup_handlers()

    def _setup_handlers(self):
        """Register MCP handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools. 
            [VERY IMPORTANT] MCP Server advertises tools via this function. """
            return [
                types.Tool(
                    name="add_jax",
                    description="Perform floating-point addition using JAX",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "number",
                                "description": "First operand"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second operand"
                            }
                        },
                        "required": ["a", "b"]
                    },
                ),
                types.Tool(
                    name="subtract_jax",
                    description="Perform floating-point subtraction using JAX (a - b)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "number",
                                "description": "Minuend (number to subtract from)"
                            },
                            "b": {
                                "type": "number",
                                "description": "Subtrahend (number to subtract)"
                            }
                        },
                        "required": ["a", "b"]
                    },
                ),
                types.Tool(
                    name="multiply_jax",
                    description="Perform floating-point multiplication using JAX (a * b)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "number",
                                "description": "First multiplicand"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second multiplicand"
                            }
                        },
                        "required": ["a", "b"]
                    },
                ),
                types.Tool(
                    name="csv_dimensions",
                    description="Get the dimensions (rows, columns) of a CSV file. Provide either a file path or CSV content directly (from attachment).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to CSV file on disk (optional if csv_content provided)"
                            },
                            "csv_content": {
                                "type": "string",
                                "description": "CSV content as string (optional if file_path provided, use this for attachments)"
                            }
                        },
                        "required": []
                    },
                ),
                types.Tool(
                    name="train_data",
                    description="Train a machine learning model using HIDENNSIM. Creates configuration and automatically executes training. REQUIRED: input_col, output_col, data_train. Supports INN (linear/nonlinear/gaussian), MLP, KAN, and FNO models. Models saved to tools/pyinn/model_saved/, plots to tools/plots/.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_col": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "(REQUIRED) Input columns of the data, e.g., [0,1,2]"
                            },
                            "output_col": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "(REQUIRED) Output columns of the data, e.g., [3]"
                            },
                            "data_train": {
                                "type": "string",
                                "description": "(REQUIRED) Full file path to training data CSV file"
                            },
                            "data_val": {
                                "type": "string",
                                "description": "(Optional) Full file path to validation data CSV file"
                            },
                            "data_test": {
                                "type": "string",
                                "description": "(Optional) Full file path to test data CSV file"
                            },
                            "interp_method": {
                                "type": "string",
                                "description": "Interpolation method: 'linear', 'nonlinear', 'gaussian', 'MLP', 'KAN', or 'FNO'"
                            },
                            "nmode": {
                                "type": "integer",
                                "description": "Number of CP tensor decomposition modes (INN linear)"
                            },
                            "nseg": {
                                "type": "integer",
                                "description": "Number of segments in each dimension (INN linear)"
                            },
                            "nlayers": {
                                "type": "integer",
                                "description": "Number of layers (MLP)"
                            },
                            "nneurons": {
                                "type": "integer",
                                "description": "Number of neurons (MLP)"
                            },
                            "activation": {
                                "type": "string",
                                "description": "Activation function (MLP)"
                            },
                            "hidden_dim": {
                                "type": "integer",
                                "description": "Hidden dimensions (KAN)"
                            },
                            "grid_size": {
                                "type": "integer",
                                "description": "Grid size (KAN)"
                            },
                            "num_layers": {
                                "type": "integer",
                                "description": "Number of layers (FNO)"
                            },
                            "modes": {
                                "type": "integer",
                                "description": "Number of modes (FNO)"
                            },
                            "split_ratio": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Train/val/test split ratio, e.g., [0.8, 0.1, 0.1]"
                            },
                            "bool_normalize": {
                                "type": "boolean",
                                "description": "Whether to normalize training data"
                            },
                            "num_epochs_INN": {
                                "type": "integer",
                                "description": "Number of epochs for INN model"
                            },
                            "num_epochs_MLP": {
                                "type": "integer",
                                "description": "Number of epochs for MLP model"
                            },
                            "batch_size": {
                                "type": "integer",
                                "description": "Batch size for training"
                            },
                            "learning_rate": {
                                "type": "number",
                                "description": "Learning rate"
                            },
                            "bool_save_model": {
                                "type": "boolean",
                                "description": "Whether to save the model"
                            },
                            "bool_plot": {
                                "type": "boolean",
                                "description": "Whether to plot results"
                            },
                            "run_type": {
                                "type": "string",
                                "description": "Problem type: 'regression' or 'classification' (default: 'regression')"
                            },
                            "gpu_idx": {
                                "type": "integer",
                                "description": "GPU device index (default: 0)"
                            },
                            "TD_type": {
                                "type": "string",
                                "description": "Tensor decomposition type: 'CP' or 'Tucker' (default: 'CP')"
                            }
                        },
                        "required": ["input_col", "output_col", "data_train"]
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict[str, Any]
        ) -> list[types.TextContent]:
            """Handle tool calls."""
            if name == "add_jax":
                result = execute_add_jax(arguments["a"], arguments["b"])
                return [
                    types.TextContent(
                        type="text",
                        text=f"Result: {result}"
                    )
                ]
            elif name == "subtract_jax":
                result = execute_subtract_jax(arguments["a"], arguments["b"])
                return [
                    types.TextContent(
                        type="text",
                        text=f"Result: {result}"
                    )
                ]
            elif name == "multiply_jax":
                result = execute_multiply_jax(arguments["a"], arguments["b"])
                return [
                    types.TextContent(
                        type="text",
                        text=f"Result: {result}"
                    )
                ]
            elif name == "csv_dimensions":
                result = execute_csv_dimensions(
                    file_path=arguments.get("file_path"),
                    csv_content=arguments.get("csv_content")
                )
                return [
                    types.TextContent(
                        type="text",
                        text=f"Dimensions: {result['rows']} rows x {result['columns']} columns\nColumns: {result['column_names']}"
                    )
                ]
            elif name == "train_data":
                result = execute_train_data(
                    input_col=arguments.get("input_col"),
                    output_col=arguments.get("output_col"),
                    data_train=arguments.get("data_train"),
                    data_val=arguments.get("data_val"),
                    data_test=arguments.get("data_test"),
                    interp_method=arguments.get("interp_method"),
                    nmode=arguments.get("nmode"),
                    nseg=arguments.get("nseg"),
                    s_patch=arguments.get("s_patch"),
                    alpha_dil=arguments.get("alpha_dil"),
                    p_order=arguments.get("p_order"),
                    radial_basis=arguments.get("radial_basis"),
                    INNactivation=arguments.get("INNactivation"),
                    sigma_factor=arguments.get("sigma_factor"),
                    nlayers=arguments.get("nlayers"),
                    nneurons=arguments.get("nneurons"),
                    activation=arguments.get("activation"),
                    hidden_dim=arguments.get("hidden_dim"),
                    grid_size=arguments.get("grid_size"),
                    spline_order=arguments.get("spline_order"),
                    num_layers=arguments.get("num_layers"),
                    modes=arguments.get("modes"),
                    split_ratio=arguments.get("split_ratio"),
                    bool_data_generation=arguments.get("bool_data_generation"),
                    bool_normalize=arguments.get("bool_normalize"),
                    bool_shuffle=arguments.get("bool_shuffle"),
                    num_epochs_INN=arguments.get("num_epochs_INN"),
                    num_epochs_MLP=arguments.get("num_epochs_MLP"),
                    num_epochs_KAN=arguments.get("num_epochs_KAN"),
                    num_epochs_FNO=arguments.get("num_epochs_FNO"),
                    batch_size=arguments.get("batch_size"),
                    learning_rate=arguments.get("learning_rate"),
                    validation_period=arguments.get("validation_period"),
                    bool_denormalize=arguments.get("bool_denormalize"),
                    patience=arguments.get("patience"),
                    stopping_loss_train=arguments.get("stopping_loss_train"),
                    bool_save_model=arguments.get("bool_save_model"),
                    bool_plot=arguments.get("bool_plot"),
                    plot_in_axis=arguments.get("plot_in_axis"),
                    plot_out_axis=arguments.get("plot_out_axis"),
                    plot_params_number=arguments.get("plot_params_number"),
                    run_type=arguments.get("run_type", "regression"),
                    gpu_idx=arguments.get("gpu_idx", 0),
                    TD_type=arguments.get("TD_type", "CP"),
                )
                # Format response based on training result
                status = "✅ Training completed successfully" if result.get("training_completed") else "❌ Training failed"
                response_parts = [
                    status,
                    f"Method: {result.get('interp_method', 'unknown')}",
                    f"Run type: {result.get('run_type', 'unknown')}",
                ]
                # Add training metrics
                if result.get("train_rmse") is not None:
                    response_parts.append(f"Train RMSE: {result['train_rmse']:.4e}")
                if result.get("val_rmse") is not None:
                    response_parts.append(f"Validation RMSE: {result['val_rmse']:.4e}")
                if result.get("test_rmse") is not None:
                    response_parts.append(f"Test RMSE: {result['test_rmse']:.4e}")
                if result.get("training_time_seconds") is not None:
                    response_parts.append(f"Training time: {result['training_time_seconds']:.2f} seconds")
                # Add output paths
                if result.get("model_save_path"):
                    response_parts.append(f"Model saved: {result['model_save_path']}")
                if result.get("plots_path"):
                    response_parts.append(f"Plots saved: {result['plots_path']}")
                if result.get("log_path"):
                    response_parts.append(f"Training log: {result['log_path']}")

                return [
                    types.TextContent(
                        type="text",
                        text="\n".join(response_parts)
                    )
                ]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="hidennsim",
                    server_version=__version__,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    """Entry point for the MCP server."""
    server = HIDENNSIMServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
