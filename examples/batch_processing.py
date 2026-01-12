"""
Batch processing example for gs2txt.
"""

import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm.base import OpenAIProvider


def example_batch_processing():
    """Process multiple gene sets."""

    # Simulate multiple gene sets (e.g., from clustering)
    gene_sets = {
        "cluster_1": pd.DataFrame({"gene": ["TP53", "MYC", "BRCA1"]}),
        "cluster_2": pd.DataFrame({"gene": ["CD4", "CD8A", "IL2"]}),
        "cluster_3": pd.DataFrame({"gene": ["EGFR", "KRAS", "BRAF"]}),
    }

    # Setup provider
    provider = OpenAIProvider(api_key="your-openai-key", model_id="gpt-4", temperature=0.0)

    # Create annotator
    annotator = GeneSetAnnotator(llm_provider=provider, enrichment_method="pathway")

    # Process each gene set
    results = {}
    for name, df in gene_sets.items():
        print(f"Annotating {name}...")
        result = annotator.annotate(df, max_gene_num=50)
        results[name] = result
        print(f"{name}: {result}\n")

    return results


def example_csv_batch_processing():
    """Process gene sets from CSV file."""

    # Load CSV with 'cluster' and 'gene' columns
    # Example format:
    # cluster,gene,logFC
    # cluster_1,TP53,2.3
    # cluster_1,MYC,1.8
    # cluster_2,CD4,1.5
    # ...

    # For this example, we'll create sample data
    all_degs = pd.DataFrame(
        {
            "cluster": ["cluster_1", "cluster_1", "cluster_2", "cluster_2"],
            "gene": ["TP53", "MYC", "CD4", "CD8A"],
            "logFC": [2.3, 1.8, 1.5, 1.2],
        }
    )

    # Setup provider
    provider = OpenAIProvider(api_key="your-openai-key", model_id="gpt-4", temperature=0.0)
    annotator = GeneSetAnnotator(llm_provider=provider, enrichment_method="pathway")

    # Group by cluster and annotate each
    results = []
    for cluster, group_df in all_degs.groupby("cluster"):
        print(f"Annotating {cluster}...")
        annotation = annotator.annotate(group_df, max_gene_num=60)
        results.append({"cluster": cluster, "annotation": annotation})

    # Create results dataframe
    results_df = pd.DataFrame(results)
    print("\nResults:")
    print(results_df)

    # Save to CSV
    # results_df.to_csv("annotated_clusters.csv", index=False)

    return results_df


if __name__ == "__main__":
    print("=== Example: Batch Processing ===")
    example_batch_processing()

    print("\n=== Example: CSV Batch Processing ===")
    example_csv_batch_processing()
