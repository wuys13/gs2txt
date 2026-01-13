"""
Batch processing utilities for gs2txt.
"""

from typing import Optional

import pandas as pd
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
            Summary data with columns: gs, annotation, pathways, PPIs, Final_prompt
        """
        # Get unique groups
        groups = df[group_column].unique()

        # Process each group with progress bar
        results = []
        for group in tqdm(groups, desc="Processing gene sets"):
            # Get genes for this group
            group_df = df[df[group_column] == group]

            # Annotate with detailed info
            try:
                detailed = self.annotator.annotate_detailed(group_df, **annotate_kwargs)
                results.append({
                    "gs": group,
                    "annotation": detailed["annotation"],
                    "pathways": detailed["pathways"],
                    "PPIs": detailed["ppis"],
                    "Final_prompt": detailed["final_prompt"],
                })
            except Exception as e:
                print(f"Warning: Failed to annotate {group}: {e}")
                results.append({
                    "gs": group,
                    "annotation": "",
                    "pathways": "",
                    "PPIs": "",
                    "Final_prompt": "",
                })

        return pd.DataFrame(results)

    def process_single_geneset(
        self,
        df: pd.DataFrame,
        gs_name: str = "gene_set",
        **annotate_kwargs
    ) -> pd.DataFrame:
        """
        Process a single gene set.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with gene column
        gs_name : str
            Name for this gene set (used in output 'gs' column)
        **annotate_kwargs
            Parameters passed to annotate() method

        Returns
        -------
        pd.DataFrame
            Summary data with columns: gs, annotation, pathways, PPIs, Final_prompt
        """
        # Annotate the entire dataset as one gene set with detailed info
        try:
            detailed = self.annotator.annotate_detailed(df, **annotate_kwargs)
            return pd.DataFrame([{
                "gs": gs_name,
                "annotation": detailed["annotation"],
                "pathways": detailed["pathways"],
                "PPIs": detailed["ppis"],
                "Final_prompt": detailed["final_prompt"]
            }])
        except Exception as e:
            print(f"Warning: Annotation failed: {e}")
            return pd.DataFrame([{
                "gs": gs_name,
                "annotation": "",
                "pathways": "",
                "PPIs": "",
                "Final_prompt": ""
            }])

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
        from pathlib import Path

        # Read CSV
        print(f"Reading input file: {input_path}")
        df = CSVReader.read_gene_file(input_path, group_column)

        # Process (grouped or single)
        if group_column:
            print(f"Processing {len(df[group_column].unique())} gene sets grouped by '{group_column}'...")
            results = self.process_grouped_data(df, group_column, **annotate_kwargs)
        else:
            # Use input filename (without extension) as gs name
            gs_name = Path(input_path).stem
            print(f"Processing single gene set '{gs_name}' with {len(df)} genes...")
            results = self.process_single_geneset(df, gs_name=gs_name, **annotate_kwargs)

        # Write results
        print(f"Writing results to: {output_path}")
        CSVWriter.write_results(results, output_path)
        print("Done!")
