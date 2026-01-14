"""
INN Data Module - Regression
----------------------------------------------------------------------------------
Data loading and preprocessing for regression tasks.
Uses NumPy arrays for efficient CPU-to-GPU transfer with JAX.

Copyright (C) 2024  Chanwook Park
Northwestern University, Evanston, Illinois, US, chanwookpark2024@u.northwestern.edu
"""

import jax
import jax.numpy as jnp
import numpy as np
import os
import sys
import pandas as pd
from typing import Sequence
from scipy.stats import qmc


class Data_regression:
    """
    Data container for regression tasks.

    Stores data as NumPy arrays for efficient batch transfer to JAX/GPU.
    No PyTorch dependencies - pure NumPy/JAX workflow.
    """

    def __init__(self, config: dict, *args: list) -> None:
        """
        Initialize data container.

        Args:
            config: Configuration dictionary from YAML file
            *args[0]: Optional list of pre-loaded datasets
        """
        if not os.path.exists('data'):
            os.makedirs('data')

        self.data_dir = 'data/'
        self.input_col = config['DATA_PARAM']['input_col']
        self.output_col = config['DATA_PARAM']['output_col']
        self.dim = len(self.input_col)
        self.var = len(self.output_col)
        self.bool_normalize = config['DATA_PARAM']['bool_normalize']
        self.bool_shuffle = config['DATA_PARAM']['bool_shuffle']
        self.bool_data_generation = config['DATA_PARAM']['bool_data_generation']
        self.batch_size = config['TRAIN_PARAM']['batch_size']

        # Load and split data
        data_train, data_val, data_test, data, ndata = self._load_data(config, args)

        # Divide into input and output
        x_data_org = data[:, self.input_col]
        u_data_org = data[:, self.output_col]
        x_data_train_org = data_train[:, self.input_col]
        u_data_train_org = data_train[:, self.output_col]
        x_data_val_org = data_val[:, self.input_col]
        u_data_val_org = data_val[:, self.output_col]
        x_data_test_org = data_test[:, self.input_col]
        u_data_test_org = data_test[:, self.output_col]

        # Compute normalization bounds
        # self.x_data_minmax = {"min": x_data_org.min(axis=0), "max": x_data_org.max(axis=0)}
        # self.u_data_minmax = {"min": u_data_org.min(axis=0), "max": u_data_org.max(axis=0)}
        self.x_data_minmax = {"min": x_data_train_org.min(axis=0), "max": x_data_train_org.max(axis=0)}
        self.u_data_minmax = {"min": u_data_train_org.min(axis=0), "max": u_data_train_org.max(axis=0)}

        # Normalize if requested
        if self.bool_normalize:
            self.x_data_train = self._normalize(x_data_train_org, self.x_data_minmax)
            self.u_data_train = self._normalize(u_data_train_org, self.u_data_minmax)
            self.x_data_val = self._normalize(x_data_val_org, self.x_data_minmax)
            self.u_data_val = self._normalize(u_data_val_org, self.u_data_minmax)
            self.x_data_test = self._normalize(x_data_test_org, self.x_data_minmax)
            self.u_data_test = self._normalize(u_data_test_org, self.u_data_minmax)
        else:
            self.x_data_train = x_data_train_org.astype(np.float32)
            self.u_data_train = u_data_train_org.astype(np.float32)
            self.x_data_val = x_data_val_org.astype(np.float32)
            self.u_data_val = u_data_val_org.astype(np.float32)
            self.x_data_test = x_data_test_org.astype(np.float32)
            self.u_data_test = u_data_test_org.astype(np.float32)

        # Store sizes
        self.n_train = len(self.x_data_train)
        self.n_val = len(self.x_data_val)
        self.n_test = len(self.x_data_test)

        print(f'Loaded {ndata} datapoints from the data files')
        print(f'  Train: {self.n_train}, Val: {self.n_val}, Test: {self.n_test}')

    def _normalize(self, data, minmax):
        """Normalize data to [0, 1] range."""
        return ((data - minmax["min"]) / (minmax["max"] - minmax["min"])).astype(np.float32)

    def _load_data(self, config, args):
        """Load and split data based on configuration."""

        if self.bool_data_generation:
            
            print("Data generation is not implemented yet.")
            sys.exit()

        elif not self.bool_data_generation and 'data_filenames' in config['DATA_PARAM']:
            # Load from files
            filenames = config['DATA_PARAM']['data_filenames']
            data, data_train, data_val, data_test, ndata = self._load_from_files(filenames, config)

        else:
            # Directly imported data
            data_list = args[0]
            data, data_train, data_val, data_test, ndata = self._load_from_args(data_list, config)

        return data_train, data_val, data_test, data, ndata

    def _split_data(self, data, config):
        """Split data according to split_ratio."""
        ndata = len(data)
        split_ratio = config['DATA_PARAM']['split_ratio']

        if len(split_ratio) == 2:
            train_end = int(split_ratio[0] * ndata)
            return data[:train_end], data[train_end:], data[train_end:]
        elif len(split_ratio) == 3:
            train_end = int(split_ratio[0] * ndata)
            val_end = train_end + int(split_ratio[1] * ndata)
            return data[:train_end], data[train_end:val_end], data[val_end:]
        elif len(split_ratio) == 1 and split_ratio[0] == 1.0:
            return data, data, data
        else:
            print("Error: Invalid split ratio")
            sys.exit()

    def _load_from_files(self, filenames, config):
        """Load data from CSV files."""
        def load_csv(filepath):
            if not os.path.isabs(filepath):
                filepath = self.data_dir + filepath
            df = pd.read_csv(filepath)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            return df[numeric_cols].values.astype(np.float32)

        if len(filenames) == 1:
            data = load_csv(filenames[0])
            self.data = data  # Store for turbulence plotting
            ndata = len(data)
            if self.bool_shuffle:
                np.random.shuffle(data)
            data_train, data_val, data_test = self._split_data(data, config)

        elif len(filenames) == 2:
            data_train = load_csv(filenames[0])
            data_test = load_csv(filenames[1])
            data_val = data_test
            data = np.concatenate([data_train, data_val], axis=0)
            ndata = len(data)

        elif len(filenames) == 3:
            data_train = load_csv(filenames[0])
            data_val = load_csv(filenames[1])
            data_test = load_csv(filenames[2])
            data = np.concatenate([data_train, data_val, data_test], axis=0)
            ndata = len(data)

        return data, data_train, data_val, data_test, ndata

    def _load_from_args(self, data_list, config):
        """Load data from directly passed arrays."""
        if len(data_list) == 1:
            data = data_list[0]
            ndata = len(data)
            if self.bool_shuffle:
                np.random.shuffle(data)
            data_train, data_val, data_test = self._split_data(data, config)

        elif len(data_list) == 2:
            data_train = data_list[0]
            data_val = data_list[1]
            data_test = data_list[1]
            data = np.concatenate([data_train, data_val], axis=0)
            ndata = len(data)

        elif len(data_list) == 3:
            data_train = data_list[0]
            data_val = data_list[1]
            data_test = data_list[2]
            data = np.concatenate([data_train, data_val, data_test], axis=0)
            ndata = len(data)

        return data, data_train, data_val, data_test, ndata

    def __len__(self):
        return self.n_train + self.n_val + self.n_test

    def normalize(self, x_data=None, u_data=None):
        """Normalize data to [0, 1] range."""
        result = []
        if x_data is not None:
            x_norm = (x_data - self.x_data_minmax["min"]) / (self.x_data_minmax["max"] - self.x_data_minmax["min"])
            result.append(x_norm)
        if u_data is not None:
            u_norm = (u_data - self.u_data_minmax["min"]) / (self.u_data_minmax["max"] - self.u_data_minmax["min"])
            result.append(u_norm)
        return result

    def denormalize(self, x_data=None, u_data=None):
        """Denormalize data from [0, 1] range to original scale."""
        result = []
        if x_data is not None:
            x_org = (self.x_data_minmax["max"] - self.x_data_minmax["min"]) * x_data + self.x_data_minmax["min"]
            result.append(x_org)
        if u_data is not None:
            u_org = (self.u_data_minmax["max"] - self.u_data_minmax["min"]) * u_data + self.u_data_minmax["min"]
            result.append(u_org)
        return result

