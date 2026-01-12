"""
Enrichment analysis utilities for geneset-annotator.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd


class BaseEnrichment(ABC):
    """Abstract base class for enrichment analysis."""
    
    @abstractmethod
    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        """
        Perform enrichment analysis.
        
        Parameters
        ----------
        genes : List[str]
            Gene list
        **kwargs
            Additional parameters
            
        Returns
        -------
        pd.DataFrame
            Enrichment results with 'Term' and 'Adjusted P-value' columns
        """
        pass


class PathwayEnrichment(BaseEnrichment):
    """Pathway enrichment using GSEApy."""
    
    def __init__(
        self, 
        gene_sets: List[str] = None,
        organism: str = "Human",
        cutoff: float = 0.05
    ):
        """
        Initialize pathway enrichment.
        
        Parameters
        ----------
        gene_sets : List[str]
            Gene set databases (e.g., ['MSigDB_Hallmark_2020', 'KEGG_2021_Human'])
        organism : str
            Organism name
        cutoff : float
            P-value cutoff
        """
        self.gene_sets = gene_sets or [
            "MSigDB_Hallmark_2020", 
            "KEGG_2021_Human", 
            "GO_Biological_Process_2025"
        ]
        self.organism = organism
        self.cutoff = cutoff
    
    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        import gseapy as gp
        
        enr = gp.enrichr(
            gene_list=genes,
            gene_sets=self.gene_sets,
            organism=self.organism,
            cutoff=self.cutoff
        )
        return enr.results


class CustomEnrichment(BaseEnrichment):
    """Custom enrichment from user-provided results."""
    
    def __init__(self, terms: List[str]):
        """
        Initialize with pre-computed enrichment terms.
        
        Parameters
        ----------
        terms : List[str]
            List of enriched pathway/GO terms
        """
        self.terms = terms
    
    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        # Return as DataFrame for consistency
        return pd.DataFrame({
            "Term": self.terms,
            "Adjusted P-value": [0.01] * len(self.terms)
        })


class PPIEnrichment(BaseEnrichment):
    """PPI network-based enrichment (future implementation)."""
    
    def __init__(self, confidence_cutoff: float = 0.7):
        self.confidence_cutoff = confidence_cutoff
    
    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        # Placeholder for STRING DB or similar
        raise NotImplementedError(
            "PPI enrichment not yet implemented. "
            "Consider using STRING DB API or local network data."
        )


def create_enrichment(
    method: str = "pathway",
    **kwargs
) -> BaseEnrichment:
    """
    Factory function to create enrichment analyzer.
    
    Parameters
    ----------
    method : str
        Enrichment method: 'pathway', 'custom', 'ppi'
    **kwargs
        Method-specific parameters
        
    Returns
    -------
    BaseEnrichment
        Enrichment analyzer instance
    """
    if method == "pathway":
        return PathwayEnrichment(**kwargs)
    elif method == "custom":
        return CustomEnrichment(**kwargs)
    elif method == "ppi":
        return PPIEnrichment(**kwargs)
    else:
        raise ValueError(f"Unknown enrichment method: {method}")
