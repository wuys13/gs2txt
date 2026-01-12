"""
Command-line interface for gs2txt.
"""

import argparse
import sys

from .config import Config
from .batch import BatchProcessor
from .core import GeneSetAnnotator
from .llm import OpenAIProvider, AnthropicProvider, LiteLLMProvider


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="gs2txt",
        description="LLM-powered biological process annotation for gene sets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  gs2txt --input genes.csv --output results.csv --api-key sk-xxx

  # Process multiple clusters
  gs2txt --input data.csv --output results.csv --api-key sk-xxx --group-by cluster

  # Use Anthropic Claude
  gs2txt --input genes.csv --output results.csv --provider anthropic --api-key sk-ant-xxx

  # Use environment variables
  export GS2TXT_API_KEY=sk-xxx
  gs2txt --input genes.csv --output results.csv

For more information, visit: https://github.com/wuys13/gs2txt
        """
    )

    # Required arguments
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input CSV file with gene data (must contain 'gene' column)"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output CSV file path"
    )

    # LLM configuration
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "litellm"],
        default="openai",
        help="LLM provider (default: openai)"
    )
    parser.add_argument(
        "--api-key",
        help="API key (or set GS2TXT_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model ID (default: gpt-4)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (default: 0.0)"
    )

    # Annotation parameters
    parser.add_argument(
        "--max-genes",
        type=int,
        default=60,
        help="Maximum genes to use (default: 60)"
    )
    parser.add_argument(
        "--max-pathways",
        type=int,
        default=10,
        help="Maximum pathways to use (default: 10)"
    )
    parser.add_argument(
        "--enrichment",
        choices=["pathway", "none"],
        default="pathway",
        help="Enrichment method (default: pathway)"
    )
    parser.add_argument(
        "--group-by",
        help="Column name to group by (e.g., 'cluster', 'celltype')"
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Load configuration from environment
    config = Config.from_env()

    # Override with CLI arguments
    config.merge_with_args(args)

    # Validate API key
    if not config.api_key:
        print("Error: API key required (use --api-key or GS2TXT_API_KEY env var)", file=sys.stderr)
        sys.exit(1)

    # Validate input file
    if not config.input_file:
        print("Error: Input file required (use --input)", file=sys.stderr)
        sys.exit(1)

    # Validate output file
    if not config.output_file:
        print("Error: Output file required (use --output)", file=sys.stderr)
        sys.exit(1)

    # Create LLM provider
    print(f"Initializing {config.provider} provider with model {config.model_id}...")
    try:
        if config.provider == "openai":
            provider = OpenAIProvider(
                api_key=config.api_key,
                model_id=config.model_id,
                temperature=config.temperature
            )
        elif config.provider == "anthropic":
            provider = AnthropicProvider(
                api_key=config.api_key,
                model_id=config.model_id,
                temperature=config.temperature
            )
        else:  # litellm
            provider = LiteLLMProvider(
                api_key=config.api_key,
                model_id=config.model_id,
                temperature=config.temperature
            )
    except Exception as e:
        print(f"Error: Failed to initialize LLM provider: {e}", file=sys.stderr)
        sys.exit(1)

    # Create annotator
    enrichment = config.enrichment_method if config.compute_enrichment else None
    annotator = GeneSetAnnotator(
        llm_provider=provider,
        enrichment_method=enrichment
    )

    # Process file
    processor = BatchProcessor(annotator)

    try:
        processor.process_single_file(
            input_path=config.input_file,
            output_path=config.output_file,
            group_column=config.group_column,
            max_gene_num=config.max_gene_num,
            max_pathway_num=config.max_pathway_num
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error during processing: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
