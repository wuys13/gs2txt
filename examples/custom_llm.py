"""
Custom LLM provider examples for gs2txt.
"""

import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm.base import AnthropicProvider, BaseLLMProvider


def example_anthropic():
    """Annotation with Anthropic Claude."""

    deg_df = pd.DataFrame(
        {"gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"], "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]}
    )

    provider = AnthropicProvider(
        api_key="your-anthropic-key", model_id="claude-sonnet-4-20250514", temperature=0.0
    )

    annotator = GeneSetAnnotator(llm_provider=provider)
    result = annotator.annotate(deg_df)
    print(result)


def example_custom_provider():
    """Use a custom LLM provider."""

    # Define custom provider
    class MyCustomProvider(BaseLLMProvider):
        def generate(self, messages):
            # Your custom LLM call
            return "Process: Custom response\nCustom implementation."

        def validate_config(self):
            return True

    deg_df = pd.DataFrame({"gene": ["TP53", "MYC", "BRCA1"]})

    provider = MyCustomProvider(model_id="my-model", temperature=0.0)
    annotator = GeneSetAnnotator(llm_provider=provider, enrichment_method=None)

    result = annotator.annotate(deg_df, compute_enrichment=False)
    print(result)


if __name__ == "__main__":
    print("=== Example: Anthropic Claude ===")
    example_anthropic()

    print("\n=== Example: Custom Provider ===")
    example_custom_provider()
