"""
Configuration management for gs2txt.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for gs2txt CLI."""

    # LLM settings
    provider: str = "openai"  # openai, anthropic, litellm
    api_key: Optional[str] = None
    model_id: str = "gpt-4"
    temperature: float = 0.0
    base_url: Optional[str] = None

    # Annotation settings
    max_gene_num: int = 60
    max_pathway_num: int = 10
    enrichment_method: str = "pathway"
    compute_enrichment: bool = True

    # Differential gene filtering settings
    pvalue_threshold: float = 0.05
    log2fc_threshold: float = 1.0
    pvalue_column: str = "pvalue"
    log2fc_column: str = "logFC"

    # File I/O
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    group_column: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

        Environment variables:
        - GS2TXT_API_KEY: API key for LLM provider
        - GS2TXT_PROVIDER: LLM provider (openai, anthropic, litellm)
        - GS2TXT_MODEL: Model ID

        Returns
        -------
        Config
            Configuration instance with values from environment
        """
        return cls(
            api_key=os.getenv("GS2TXT_API_KEY"),
            provider=os.getenv("GS2TXT_PROVIDER", "openai"),
            model_id=os.getenv("GS2TXT_MODEL", "gpt-4"),
        )

    def merge_with_args(self, args):
        """
        Merge CLI arguments with config (args override env vars).

        Parameters
        ----------
        args : argparse.Namespace
            Parsed command-line arguments
        """
        # File I/O
        if hasattr(args, "input") and args.input:
            self.input_file = args.input
        if hasattr(args, "output") and args.output:
            self.output_file = args.output
        if hasattr(args, "group_by") and args.group_by:
            self.group_column = args.group_by

        # LLM settings
        if hasattr(args, "provider") and args.provider:
            self.provider = args.provider
        if hasattr(args, "api_key") and args.api_key:
            self.api_key = args.api_key
        if hasattr(args, "model") and args.model:
            self.model_id = args.model
        if hasattr(args, "temperature") and args.temperature is not None:
            self.temperature = args.temperature

        # Annotation settings
        if hasattr(args, "max_genes") and args.max_genes:
            self.max_gene_num = args.max_genes
        if hasattr(args, "max_pathways") and args.max_pathways:
            self.max_pathway_num = args.max_pathways
        if hasattr(args, "enrichment") and args.enrichment:
            if args.enrichment == "none":
                self.enrichment_method = None
                self.compute_enrichment = False
            else:
                self.enrichment_method = args.enrichment
                self.compute_enrichment = True

        # Differential gene filtering settings
        if hasattr(args, "pvalue_threshold") and args.pvalue_threshold is not None:
            self.pvalue_threshold = args.pvalue_threshold
        if hasattr(args, "log2fc_threshold") and args.log2fc_threshold is not None:
            self.log2fc_threshold = args.log2fc_threshold
        if hasattr(args, "pvalue_column") and args.pvalue_column:
            self.pvalue_column = args.pvalue_column
        if hasattr(args, "log2fc_column") and args.log2fc_column:
            self.log2fc_column = args.log2fc_column
