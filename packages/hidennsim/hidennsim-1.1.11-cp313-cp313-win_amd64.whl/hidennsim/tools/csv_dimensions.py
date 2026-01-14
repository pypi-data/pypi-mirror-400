"""CSV dimensions tool - Cython-compiled module."""

from typing import Optional
import io

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "pandas is not installed. Install it with: pip install pandas"
    ) from e


def execute_csv_dimensions(
    file_path: Optional[str] = None,
    csv_content: Optional[str] = None
) -> dict:
    """
    Get the dimensions (rows, columns) of a CSV file.

    Accepts either a file path to read from disk, or CSV content as a string
    (useful when content is provided via Claude Desktop attachment).

    Args:
        file_path: Path to the CSV file on disk (optional)
        csv_content: CSV content as a string (optional)

    Returns:
        Dictionary with 'rows', 'columns', and 'column_names' keys

    Raises:
        ValueError: If neither file_path nor csv_content is provided
        FileNotFoundError: If file_path doesn't exist
        pd.errors.EmptyDataError: If CSV is empty
    """
    # Validate inputs
    if file_path is None and csv_content is None:
        raise ValueError(
            "Either 'file_path' or 'csv_content' must be provided"
        )

    if file_path is not None and csv_content is not None:
        raise ValueError(
            "Provide only one of 'file_path' or 'csv_content', not both"
        )

    # Read CSV from appropriate source
    if file_path is not None:
        if not isinstance(file_path, str):
            raise TypeError(
                f"file_path must be a string, got {type(file_path).__name__}"
            )
        df = pd.read_csv(file_path)
    else:
        if not isinstance(csv_content, str):
            raise TypeError(
                f"csv_content must be a string, got {type(csv_content).__name__}"
            )
        df = pd.read_csv(io.StringIO(csv_content))

    # Get dimensions
    rows, columns = df.shape
    column_names = df.columns.tolist()

    return {
        "rows": rows,
        "columns": columns,
        "column_names": column_names
    }
