"""
Basic usage examples for geneset-annotator.
"""

import pandas as pd
from geneset_annotator import GeneSetAnnotator
from geneset_annotator.llm import OpenAIProvider, AnthropicProvider, LiteLLMProvider
from geneset_annotator.enrichment import PathwayEnrichment, CustomEnrichment


# ============================================
# Example 1: Basic usage with OpenAI
# ============================================

def example_basic_openai():
    """Basic annotation with OpenAI GPT-4."""
    
    # Prepare gene data
    deg_df = pd.DataFrame({
        "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
        "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]
    })
    
    # Setup LLM provider
    provider = OpenAIProvider(
        api_key="your-openai-key",
        model_id="gpt-4",
        temperature=0.0
    )
    
    # Create annotator
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method="pathway"  # Auto enrichment
    )
    
    # Annotate
    result = annotator.annotate(deg_df, max_gene_num=50)
    print(result)


# ============================================
# Example 2: Using Anthropic Claude
# ============================================

def example_anthropic():
    """Annotation with Claude."""
    
    deg_df = pd.read_csv("your_degs.csv")
    
    provider = AnthropicProvider(
        api_key="your-anthropic-key",
        model_id="claude-sonnet-4-20250514",
        temperature=0.0
    )
    
    annotator = GeneSetAnnotator(provider)
    result = annotator.annotate(deg_df)
    print(result)


# ============================================
# Example 3: Pre-computed pathways
# ============================================

def example_precomputed_pathways():
    """Skip enrichment by providing pathways directly."""
    
    deg_df = pd.DataFrame({
        "gene": ["CD4", "CD8A", "IL2", "IFNG", "TNF"]
    })
    
    # Pre-computed enrichment results
    pathways = [
        "T cell activation",
        "Immune response",
        "Cytokine signaling"
    ]
    
    provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4")
    annotator = GeneSetAnnotator(provider, enrichment_method=None)
    
    result = annotator.annotate(
        deg_df,
        pathways=pathways,
        compute_enrichment=False
    )
    print(result)


# ============================================
# Example 4: Custom enrichment method
# ============================================

def example_custom_enrichment():
    """Use custom enrichment analyzer."""
    
    deg_df = pd.DataFrame({"gene": ["GENE1", "GENE2", "GENE3"]})
    
    # Custom enrichment (e.g., from your own analysis)
    custom_terms = [
        "Cell cycle regulation",
        "DNA repair",
        "Chromatin remodeling"
    ]
    enrichment = CustomEnrichment(terms=custom_terms)
    
    provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4")
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=enrichment
    )
    
    result = annotator.annotate(deg_df)
    print(result)


# ============================================
# Example 5: Additional context (PPI, etc.)
# ============================================

def example_with_ppi_context():
    """Include PPI network information in prompt."""
    
    deg_df = pd.read_csv("degs.csv")
    
    # Additional context from PPI analysis
    ppi_context = """
    PPI Network Analysis:
    - Hub genes: TP53, MYC, EGFR
    - Network density: 0.45
    - Main module: DNA damage response
    """
    
    provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4")
    annotator = GeneSetAnnotator(provider)
    
    result = annotator.annotate(
        deg_df,
        additional_context=ppi_context
    )
    print(result)


# ============================================
# Example 6: Custom prompt builder
# ============================================

def example_custom_prompt():
    """Use custom prompt template."""
    
    from geneset_annotator.prompts.builder import PromptBuilder
    
    deg_df = pd.DataFrame({"gene": ["A", "B", "C"]})
    
    # Custom prompt for cancer-specific annotation
    custom_builder = PromptBuilder(
        system_template=(
            "You are an expert in cancer genomics. "
            "Focus on oncogenic processes and tumor biology."
        ),
        user_template=(
            "Identify the cancer hallmark represented by:\n"
            "[Genes] {genes}\n"
            "{pathways_section}\n"
            "Format: Hallmark: <name>\nExplanation: <text>"
        )
    )
    
    provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4")
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        prompt_builder=custom_builder
    )
    
    result = annotator.annotate(deg_df)
    print(result)


# ============================================
# Example 7: Batch processing
# ============================================

def example_batch():
    """Process multiple gene sets from CSV."""
    
    from geneset_annotator.batch import run_batch_annotation
    
    # Input: CSV with 'group' and 'gene' columns
    # Output: CSV with 'group' and 'llm_process_annotation' columns
    
    provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4")
    
    run_batch_annotation(
        provider=provider,
        input_csv="all_degs.csv",
        output_csv="annotated_results.csv",
        group_col="cluster",
        max_gene_num=60,
        sleep_time=1.0  # Rate limiting
    )


# ============================================
# Example 8: Legacy function (backwards compat)
# ============================================

def example_legacy():
    """Use legacy function for simple cases."""
    
    from geneset_annotator import annotate_gene_set_with_llm
    
    deg_df = pd.DataFrame({"gene": ["TP53", "MYC"]})
    
    result = annotate_gene_set_with_llm(
        deg_df=deg_df,
        model_id="gpt-4",
        api_key="sk-...",
        max_gene_num=50
    )
    print(result)


if __name__ == "__main__":
    # Run examples
    example_basic_openai()
