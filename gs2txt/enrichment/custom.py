"""
Custom enrichment from user-provided results for gs2txt.
"""

from typing import List
import pandas as pd
from .base import BaseEnrichment


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
        """
        Return pre-computed enrichment terms as DataFrame.

        Parameters
        ----------
        genes : List[str]
            Gene list (not used, for interface compatibility)
        **kwargs
            Additional parameters (not used)

        Returns
        -------
        pd.DataFrame
            Enrichment results with 'Term' and 'Adjusted P-value' columns
        """
        # Return as DataFrame for consistency
        return pd.DataFrame(
            {"Term": self.terms, "Adjusted P-value": [0.01] * len(self.terms)}
        )
