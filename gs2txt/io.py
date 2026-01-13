"""
CSV input/output handlers for gs2txt.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


class CSVReader:
    """Read and validate input CSV files."""

    @staticmethod
    def read_gene_file(file_path: str, group_column: Optional[str] = None) -> pd.DataFrame:
        """
        Read CSV file with gene data.

        Parameters
        ----------
        file_path : str
            Path to input CSV file
        group_column : str, optional
            Column name for grouping (e.g., 'cluster', 'celltype')

        Returns
        -------
        pd.DataFrame
            Validated DataFrame with 'gene' column

        Raises
        ------
        FileNotFoundError
            If file doesn't exist
        ValueError
            If 'gene' column is missing or if group_column specified but not found
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        # Read CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}") from e

        # Validate 'gene' column exists
        if "gene" not in df.columns:
            raise ValueError(
                f"Input CSV must contain a 'gene' column. "
                f"Found columns: {', '.join(df.columns)}"
            )

        # Validate group column if specified
        if group_column and group_column not in df.columns:
            raise ValueError(
                f"Group column '{group_column}' not found in CSV. "
                f"Available columns: {', '.join(df.columns)}"
            )

        return df


class CSVWriter:
    """Write annotation results to CSV."""

    @staticmethod
    def write_results(results: pd.DataFrame, output_path: str):
        """
        Save annotated results to CSV file.

        Parameters
        ----------
        results : pd.DataFrame
            DataFrame with annotation results
        output_path : str
            Output CSV file path

        Raises
        ------
        ValueError
            If results DataFrame is empty or invalid
        IOError
            If file cannot be written
        """
        if results is None or len(results) == 0:
            raise ValueError("Cannot write empty results to CSV")

        # Create parent directory if it doesn't exist
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to CSV
        try:
            results.to_csv(output_path, index=False)
        except Exception as e:
            raise OSError(f"Error writing results to {output_path}: {e}") from e
