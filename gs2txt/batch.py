"""
Batch processing utilities for gs2txt.
"""

import pandas as pd
from typing import Optional
from tqdm import tqdm

from .core import GeneSetAnnotator
from .io import CSVReader, CSVWriter


class BatchProcessor:
    """Process multiple gene sets in batch with progress tracking."""

    def __init__(self, annotator: GeneSetAnnotator):
        """
        Initialize with a GeneSetAnnotator instance.

        Parameters
        ----------
        annotator : GeneSetAnnotator
            Configured annotator for gene set annotation
        """
        self.annotator = annotator

    def process_grouped_data(
        self,
        df: pd.DataFrame,
        group_column: str,
        **annotate_kwargs
    ) -> pd.DataFrame:
        """
        Process dataframe grouped by a column.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with gene and group columns
        group_column : str
            Column to group by (e.g., 'cluster', 'celltype')
        **annotate_kwargs
            Parameters passed to annotate() method

        Returns
        -------
        pd.DataFrame
            Original data + 'annotation' column with LLM results
        """
        # Get unique groups
        groups = df[group_column].unique()

        # Process each group with progress bar
        annotations = {}
        for group in tqdm(groups, desc="Processing gene sets"):
            # Get genes for this group
            group_df = df[df[group_column] == group]

            # Annotate
            try:
                annotation = self.annotator.annotate(group_df, **annotate_kwargs)
                annotations[group] = annotation
            except Exception as e:
                print(f"Warning: Failed to annotate {group}: {e}")
                annotations[group] = f"Process: Failed - {str(e)}"

        # Create annotation column by mapping group to annotation
        df_result = df.copy()
        df_result["annotation"] = df_result[group_column].map(annotations)

        return df_result

    def process_single_geneset(
        self,
        df: pd.DataFrame,
        **annotate_kwargs
    ) -> pd.DataFrame:
        """
        Process a single gene set.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with gene column
        **annotate_kwargs
            Parameters passed to annotate() method

        Returns
        -------
        pd.DataFrame
            Original data + 'annotation' column with LLM results
        """
        # Annotate the entire dataset as one gene set
        try:
            annotation = self.annotator.annotate(df, **annotate_kwargs)
        except Exception as e:
            print(f"Warning: Annotation failed: {e}")
            annotation = f"Process: Failed - {str(e)}"

        # Add annotation column to all rows
        df_result = df.copy()
        df_result["annotation"] = annotation

        return df_result

    def process_single_file(
        self,
        input_path: str,
        output_path: str,
        group_column: Optional[str] = None,
        **annotate_kwargs
    ):
        """
        Process entire CSV file and save results.

        Parameters
        ----------
        input_path : str
            Input CSV file path
        output_path : str
            Output CSV file path
        group_column : str, optional
            Column to group by. If None, treats all genes as single set.
        **annotate_kwargs
            Parameters passed to annotate() method
        """
        # Read CSV
        print(f"Reading input file: {input_path}")
        df = CSVReader.read_gene_file(input_path, group_column)

        # Process (grouped or single)
        if group_column:
            print(f"Processing {len(df[group_column].unique())} gene sets grouped by '{group_column}'...")
            results = self.process_grouped_data(df, group_column, **annotate_kwargs)
        else:
            print(f"Processing single gene set with {len(df)} genes...")
            results = self.process_single_geneset(df, **annotate_kwargs)

        # Write results
        print(f"Writing results to: {output_path}")
        CSVWriter.write_results(results, output_path)
        print("Done!")
