"""Simple test for train_data tool."""

import sys
sys.path.insert(0, './hidennsim')

from hidennsim.tools.train_data import execute_train_data

# Test with sample parameters
result = execute_train_data(
    input_col=[0, 1, 2],
    output_col=[3],
    data_train= r"C:\Users\lesp9\Downloads\vibe\pyinn_als\data\1s2p_1o_coupled_nd_train.csv",
    data_test = r"C:\Users\lesp9\Downloads\vibe\pyinn_als\data\1s2p_1o_coupled_nd_test.csv",
    interp_method="MLP",
    num_epochs_MLP=100,
    bool_save_model=True,
    bool_plot=True
)
print(result)
