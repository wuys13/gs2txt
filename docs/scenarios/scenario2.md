# Scenario 2: Python API

Integrate gs2txt directly into your Python code and get annotation results as strings.

## When to Use

- You're building a data analysis pipeline
- You need programmatic control over the process
- You want to process results in memory
- You're building a web application or service

## Quick Start

```bash
cd examples
export LITELLM_API_KEY=your-api-key
python scenario2_api.py
```

## Basic Usage

```python
import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import LiteLLMProvider

# Prepare data
deg_df = pd.DataFrame({
    "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
    "logFC": [2.3, 1.8, -1.5, 2.1, 1.9],
    "pvalue": [0.001, 0.002, 0.003, 0.001, 0.002]
})

# Setup provider
provider = LiteLLMProvider(
    api_key="your-api-key",
    model_id="gpt-4",
    temperature=0.0,
    base_url="https://your-litellm-server.com/"
)

# Create annotator
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method="pathway"  # or None to skip
)

# Get annotation
result = annotator.annotate(deg_df)
print(result)  # String output
```

## All Parameters

```python
result = annotator.annotate(
    deg_df,                          # DataFrame with 'gene' column
    max_gene_num=60,                 # Max genes to include
    max_pathway_num=10,              # Max pathways to include
    pathways=None,                   # Pre-computed pathway list
    compute_enrichment=True,         # Run enrichment analysis
    additional_context=None,         # Extra context string
    pvalue_threshold=0.05,           # P-value filter
    log2fc_threshold=1.0             # Log2FC filter
)
```

## Code Examples

### Use Pre-computed Pathways

```python
pathways = [
    "T cell activation",
    "Immune response",
    "Cytokine signaling"
]

result = annotator.annotate(
    deg_df,
    pathways=pathways,
    compute_enrichment=False
)
```

### Add PPI Context

```python
ppi_context = """
PPI Network Analysis:
- Hub genes: TP53, MYC, EGFR
- Network density: 0.45
- Main module: DNA damage response
"""

result = annotator.annotate(
    deg_df,
    additional_context=ppi_context
)
```

### Process Multiple Gene Sets

```python
gene_sets = {
    "cluster_1": pd.DataFrame({"gene": ["TP53", "MYC", "BRCA1"]}),
    "cluster_2": pd.DataFrame({"gene": ["CD4", "CD8A", "IL2"]}),
    "cluster_3": pd.DataFrame({"gene": ["EGFR", "KRAS", "BRAF"]}),
}

results = {}
for name, df in gene_sets.items():
    results[name] = annotator.annotate(df)
    print(f"{name}: {results[name]}")

# Save to CSV
result_df = pd.DataFrame([
    {"gs": name, "annotation": ann}
    for name, ann in results.items()
])
result_df.to_csv("results.csv", index=False)
```

### Use Different Providers

#### OpenAI

```python
from gs2txt.llm import OpenAIProvider

provider = OpenAIProvider(
    api_key="sk-xxx",
    model_id="gpt-4",
    temperature=0.0
)
```

#### Anthropic Claude

```python
from gs2txt.llm import AnthropicProvider

provider = AnthropicProvider(
    api_key="sk-ant-xxx",
    model_id="claude-sonnet-4-20250514",
    temperature=0.0
)
```

### Skip Enrichment (Faster)

```python
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=None
)

result = annotator.annotate(
    deg_df,
    compute_enrichment=False
)
```

## Output Format

The `annotate()` method returns a string:

```
This gene set is enriched for critical tumor suppressors (TP53, BRCA1)
and oncogenes (MYC, EGFR, KRAS) that collectively regulate cell cycle
checkpoints and apoptotic responses to genomic stress.
```

- 2-4 sentences describing the biological process
- No labels like "Process:" or "Summary:"
- Focuses on functional meaning and biological interpretation

## Full Example Script

See [`examples/scenario2_api.py`](https://github.com/wuys13/gs2txt/blob/main/examples/scenario2_api.py) for a complete example with 9 different use cases.

## Tips

1. **Return type is string**: `annotate()` returns text directly
2. **Filtering is built-in**: P-value and log2FC filtering happen automatically
3. **Enrichment is optional**: Set `enrichment_method=None` for faster processing
4. **Context improves results**: Add PPI or other analysis results via `additional_context`
