"""
Custom enrichment examples for gs2txt.
"""

import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm.base import OpenAIProvider
from gs2txt.enrichment.custom import CustomEnrichment


def example_precomputed_pathways():
    """Skip enrichment by providing pathways directly."""

    deg_df = pd.DataFrame({"gene": ["CD4", "CD8A", "IL2", "IFNG", "TNF"]})

    # Pre-computed enrichment results
    pathways = ["T cell activation", "Immune response", "Cytokine signaling"]

    provider = OpenAIProvider(api_key="your-openai-key", model_id="gpt-4", temperature=0.0)
    annotator = GeneSetAnnotator(llm_provider=provider, enrichment_method=None)

    result = annotator.annotate(deg_df, pathways=pathways, compute_enrichment=False)
    print(result)


def example_custom_enrichment():
    """Use custom enrichment analyzer."""

    deg_df = pd.DataFrame({"gene": ["GENE1", "GENE2", "GENE3"]})

    # Custom enrichment (e.g., from your own analysis)
    custom_terms = ["Cell cycle regulation", "DNA repair", "Chromatin remodeling"]
    enrichment = CustomEnrichment(terms=custom_terms)

    provider = OpenAIProvider(api_key="your-openai-key", model_id="gpt-4", temperature=0.0)
    annotator = GeneSetAnnotator(llm_provider=provider, enrichment_method=enrichment)

    result = annotator.annotate(deg_df)
    print(result)


def example_with_additional_context():
    """Include PPI network information in prompt."""

    deg_df = pd.DataFrame(
        {"gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"], "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]}
    )

    # Additional context from PPI analysis
    ppi_context = """
    PPI Network Analysis:
    - Hub genes: TP53, MYC, EGFR
    - Network density: 0.45
    - Main module: DNA damage response
    """

    provider = OpenAIProvider(api_key="your-openai-key", model_id="gpt-4", temperature=0.0)
    annotator = GeneSetAnnotator(llm_provider=provider)

    result = annotator.annotate(deg_df, additional_context=ppi_context)
    print(result)


if __name__ == "__main__":
    print("=== Example: Pre-computed Pathways ===")
    example_precomputed_pathways()

    print("\n=== Example: Custom Enrichment ===")
    example_custom_enrichment()

    print("\n=== Example: With Additional Context ===")
    example_with_additional_context()
