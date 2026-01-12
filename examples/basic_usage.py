"""
Basic usage example for gs2txt.
"""

import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm.base import OpenAIProvider


def main():
    """Basic annotation with OpenAI GPT-4."""

    # Prepare gene data
    deg_df = pd.DataFrame(
        {"gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"], "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]}
    )

    # Setup LLM provider
    provider = OpenAIProvider(api_key="your-openai-key", model_id="gpt-4", temperature=0.0)

    # Create annotator with automatic pathway enrichment
    annotator = GeneSetAnnotator(
        llm_provider=provider, enrichment_method="pathway"  # Auto enrichment
    )

    # Annotate
    result = annotator.annotate(deg_df, max_gene_num=50)
    print(result)


if __name__ == "__main__":
    main()
