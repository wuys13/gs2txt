"""
Pathway enrichment using GSEApy for gs2txt.
"""


import pandas as pd

from .base import BaseEnrichment


class PathwayEnrichment(BaseEnrichment):
    """Pathway enrichment using GSEApy."""

    def __init__(
        self, gene_sets: list[str] = None, organism: str = "Human", cutoff: float = 0.05
    ):
        """
        Initialize pathway enrichment.

        Parameters
        ----------
        gene_sets : List[str], optional
            Gene set databases (e.g., ['MSigDB_Hallmark_2020', 'KEGG_2021_Human'])
        organism : str
            Organism name (default: "Human")
        cutoff : float
            P-value cutoff (default: 0.05)
        """
        self.gene_sets = gene_sets or [
            "MSigDB_Hallmark_2020",
            "KEGG_2021_Human",
            "GO_Biological_Process_2025",
        ]
        self.organism = organism
        self.cutoff = cutoff

    def enrich(self, genes: list[str], **kwargs) -> pd.DataFrame:
        """
        Perform pathway enrichment using GSEApy.

        Parameters
        ----------
        genes : List[str]
            Gene list
        **kwargs
            Additional GSEApy parameters

        Returns
        -------
        pd.DataFrame
            Enrichment results with 'Term' and 'Adjusted P-value' columns
        """
        import gseapy as gp

        enr = gp.enrichr(
            gene_list=genes,
            gene_sets=self.gene_sets,
            organism=self.organism,
            cutoff=self.cutoff,
        )
        return enr.results
