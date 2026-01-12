"""
Core annotation API for gs2txt.
"""

import pandas as pd
from typing import List, Optional, Union
from .llm.base import BaseLLMProvider
from .enrichment.base import BaseEnrichment
from .enrichment import create_enrichment
from .prompts.builder import PromptBuilder


class GeneSetAnnotator:
    """Main class for gene set annotation using LLMs."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        enrichment_method: Optional[Union[str, BaseEnrichment]] = "pathway",
        prompt_builder: Optional[PromptBuilder] = None,
        **enrichment_kwargs
    ):
        """
        Initialize annotator.

        Parameters
        ----------
        llm_provider : BaseLLMProvider
            LLM provider instance
        enrichment_method : str or BaseEnrichment
            Enrichment method or instance
        prompt_builder : PromptBuilder, optional
            Custom prompt builder
        **enrichment_kwargs
            Additional parameters for enrichment

        Examples
        --------
        >>> from gs2txt import GeneSetAnnotator
        >>> from gs2txt.llm.base import OpenAIProvider
        >>>
        >>> provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4")
        >>> annotator = GeneSetAnnotator(llm_provider=provider)
        >>> result = annotator.annotate(deg_df)
        """
        self.llm_provider = llm_provider

        # Setup enrichment
        if isinstance(enrichment_method, str):
            self.enrichment = create_enrichment(enrichment_method, **enrichment_kwargs)
        elif isinstance(enrichment_method, BaseEnrichment):
            self.enrichment = enrichment_method
        else:
            self.enrichment = None

        # Setup prompt builder
        self.prompt_builder = prompt_builder or PromptBuilder()

    def annotate(
        self,
        deg_df: pd.DataFrame,
        max_gene_num: int = 60,
        max_pathway_num: int = 10,
        pathways: Optional[List[str]] = None,
        compute_enrichment: bool = True,
        additional_context: Optional[str] = None,
    ) -> str:
        """
        Annotate a gene set with biological process description.

        Parameters
        ----------
        deg_df : pd.DataFrame
            DataFrame with at least a 'gene' column
        max_gene_num : int
            Maximum genes to use
        max_pathway_num : int
            Maximum pathways to use
        pathways : List[str], optional
            Pre-computed pathway terms (skip enrichment if provided)
        compute_enrichment : bool
            Whether to compute enrichment if pathways not provided
        additional_context : str, optional
            Additional context to include in prompt (e.g., PPI info)

        Returns
        -------
        str
            LLM-generated biological process annotation

        Raises
        ------
        ValueError
            If deg_df doesn't contain 'gene' column

        Examples
        --------
        >>> # Basic usage
        >>> result = annotator.annotate(deg_df)

        >>> # With pre-computed pathways
        >>> result = annotator.annotate(
        ...     deg_df,
        ...     pathways=["Inflammatory response", "Apoptosis"]
        ... )

        >>> # With additional context
        >>> ppi_info = "Hub genes: TP53, MYC"
        >>> result = annotator.annotate(deg_df, additional_context=ppi_info)
        """
        # Validate input
        if deg_df is None or len(deg_df) == 0:
            return "Process: Unresolved functional program\nNo genes provided."

        if "gene" not in deg_df.columns:
            raise ValueError("deg_df must contain a 'gene' column")

        # Extract genes
        genes = deg_df["gene"].dropna().astype(str).tolist()[:max_gene_num]

        # Get pathways
        pathway_terms = None
        if pathways is not None:
            pathway_terms = pathways[:max_pathway_num]
        elif compute_enrichment and self.enrichment is not None:
            try:
                enr_results = self.enrichment.enrich(genes)
                if enr_results is not None and len(enr_results) > 0:
                    enr_results = enr_results.sort_values("Adjusted P-value")
                    pathway_terms = (
                        enr_results["Term"].astype(str).tolist()[:max_pathway_num]
                    )
            except Exception as e:
                print(f"Warning: Enrichment failed: {e}")

        # Build prompt
        messages = self.prompt_builder.build(
            genes=genes, pathways=pathway_terms, additional_context=additional_context
        )

        # Generate annotation
        try:
            return self.llm_provider.generate(messages)
        except Exception as e:
            return f"Process: Failed\nError: {str(e)}"


# Convenience function for backwards compatibility
def annotate_gene_set_with_llm(
    deg_df: pd.DataFrame,
    max_gene_num: int = 60,
    max_pathway_num: int = 10,
    pathways: Optional[List[str]] = None,
    compute_pathway_if_missing: bool = True,
    geneset_file=None,
    model_id: str = "gpt-4",
    temperature: float = 0.0,
    api_key: str = None,
    base_url: str = None,
) -> str:
    """
    Legacy function for direct annotation (backwards compatible).

    This is a convenience wrapper around GeneSetAnnotator for users
    who want a simple function call without explicit provider setup.
    """
    from .llm.openai_provider import OpenAIProvider

    provider = OpenAIProvider(
        api_key=api_key, base_url=base_url, model_id=model_id, temperature=temperature
    )

    enrichment_kwargs = {}
    if geneset_file is not None:
        enrichment_kwargs["gene_sets"] = geneset_file

    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway" if compute_pathway_if_missing else None,
        **enrichment_kwargs
    )

    return annotator.annotate(
        deg_df=deg_df,
        max_gene_num=max_gene_num,
        max_pathway_num=max_pathway_num,
        pathways=pathways,
        compute_enrichment=compute_pathway_if_missing,
    )
