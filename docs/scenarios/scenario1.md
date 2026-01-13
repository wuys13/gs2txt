# Scenario 1: Batch CSV Processing

Process CSV files directly and output results to new CSV files.

## When to Use

- You have CSV files with gene expression data
- You want a simple file-in, file-out workflow
- You're processing single or grouped gene sets

## Quick Start

```bash
cd examples
export LITELLM_API_KEY=your-api-key
python scenario1_batch_csv.py
```

## Input Format

### Single Gene Set

```csv
gene,logFC,pvalue
TP53,2.3,0.001
MYC,1.8,0.002
BRCA1,-1.5,0.003
```

### Multiple Clusters

```csv
cluster,gene,logFC,pvalue
cluster_1,TP53,2.3,0.001
cluster_1,MYC,1.8,0.002
cluster_2,CD4,1.5,0.003
cluster_2,CD8A,1.2,0.004
```

## Output Format

```csv
gs,annotation
sample_input,"This gene set is enriched for tumor suppressors..."
cluster_1,"DNA damage response pathway is the dominant process..."
cluster_2,"T cell activation and immune response..."
```

## Code Examples

### Process Single File

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider
from gs2txt.batch import BatchProcessor

# Setup
provider = LiteLLMProvider(
    api_key="your-api-key",
    model_id="gpt-4",
    base_url="https://your-litellm-server.com/"
)
annotator = GeneSetAnnotator(llm_provider=provider)
processor = BatchProcessor(annotator)

# Process
processor.process_single_file(
    input_path="genes.csv",
    output_path="output.csv",
    group_column=None,          # Single gene set
    max_gene_num=60,
    pvalue_threshold=0.05,
    log2fc_threshold=1.0
)
```

### Process Grouped Data

```python
processor.process_single_file(
    input_path="clustered_genes.csv",
    output_path="output.csv",
    group_column="cluster",     # Group by cluster column
    max_gene_num=50,
    max_pathway_num=10,
    pvalue_threshold=0.05
)
```

### Skip Enrichment Analysis

```python
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=None      # Skip enrichment
)
processor = BatchProcessor(annotator)

processor.process_single_file(
    input_path="genes.csv",
    output_path="output.csv",
    compute_enrichment=False
)
```

### Add Context Information

```python
# Manual processing with context
df = pd.read_csv("genes.csv")

ppi_context = """
PPI Network Analysis:
- Hub genes: TP53, MYC
- Network density: 0.45
"""

annotation = annotator.annotate(
    df,
    additional_context=ppi_context
)

# Save result
result_df = pd.DataFrame([{
    "gs": "sample",
    "annotation": annotation
}])
result_df.to_csv("output.csv", index=False)
```

## Full Example Script

See [`examples/scenario1_batch_csv.py`](https://github.com/wuys13/gs2txt/blob/main/examples/scenario1_batch_csv.py) for a complete example with multiple use cases.

## Tips

1. **Gene column is required**: Your CSV must have a `gene` column
2. **P-value and logFC are optional**: Used for filtering if present
3. **Group column is optional**: Use for processing multiple gene sets
4. **Output has two columns**: `gs` (gene set name) and `annotation` (LLM result)
