"""
Enrichment analysis methods for gs2txt.
"""

from .base import BaseEnrichment
from .custom import CustomEnrichment
from .pathway import PathwayEnrichment
from .ppi import PPIEnrichment


def create_enrichment(method: str = "pathway", **kwargs) -> BaseEnrichment:
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

    Raises
    ------
    ValueError
        If method is not recognized
    """
    if method == "pathway":
        return PathwayEnrichment(**kwargs)
    elif method == "custom":
        return CustomEnrichment(**kwargs)
    elif method == "ppi":
        return PPIEnrichment(**kwargs)
    else:
        raise ValueError(f"Unknown enrichment method: {method}")


__all__ = [
    "BaseEnrichment",
    "PathwayEnrichment",
    "CustomEnrichment",
    "PPIEnrichment",
    "create_enrichment",
]
