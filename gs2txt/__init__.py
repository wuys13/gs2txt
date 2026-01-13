"""
gs2txt: LLM-powered biological process annotation for gene sets.
"""

__version__ = "0.1.2"

from .core import GeneSetAnnotator, annotate_gene_set_with_llm
from .enrichment import create_enrichment
from .enrichment.base import BaseEnrichment
from .enrichment.custom import CustomEnrichment
from .enrichment.pathway import PathwayEnrichment
from .llm.anthropic_provider import AnthropicProvider
from .llm.base import BaseLLMProvider
from .llm.litellm_provider import LiteLLMProvider
from .llm.openai_provider import OpenAIProvider
from .prompts.builder import PromptBuilder

__all__ = [
    "GeneSetAnnotator",
    "annotate_gene_set_with_llm",
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LiteLLMProvider",
    "BaseEnrichment",
    "PathwayEnrichment",
    "CustomEnrichment",
    "create_enrichment",
    "PromptBuilder",
]
