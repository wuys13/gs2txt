"""
PPI network-based enrichment (placeholder) for gs2txt.
"""

from typing import List
import pandas as pd
from .base import BaseEnrichment


class PPIEnrichment(BaseEnrichment):
    """PPI network-based enrichment (future implementation)."""

    def __init__(self, confidence_cutoff: float = 0.7):
        """
        Initialize PPI enrichment.

        Parameters
        ----------
        confidence_cutoff : float
            Confidence score cutoff for PPI interactions (default: 0.7)
        """
        self.confidence_cutoff = confidence_cutoff

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        """
        Perform PPI-based enrichment (not yet implemented).

        Parameters
        ----------
        genes : List[str]
            Gene list
        **kwargs
            Additional parameters

        Returns
        -------
        pd.DataFrame
            Enrichment results

        Raises
        ------
        NotImplementedError
            This feature is not yet implemented
        """
        raise NotImplementedError(
            "PPI enrichment not yet implemented. "
            "Consider using STRING DB API or local network data."
        )
