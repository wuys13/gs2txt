"""
Enrichment analysis base class for gs2txt.
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseEnrichment(ABC):
    """Abstract base class for enrichment analysis."""

    @abstractmethod
    def enrich(self, genes: list[str], **kwargs) -> pd.DataFrame:
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
