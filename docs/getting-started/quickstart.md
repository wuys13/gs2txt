# Quick Start

This guide will help you get started with gs2txt in 5 minutes.

## Step 1: Set Up API Key

```bash
# Choose one provider
export OPENAI_API_KEY=sk-xxx           # OpenAI
export ANTHROPIC_API_KEY=sk-ant-xxx    # Anthropic
export LITELLM_API_KEY=your-key        # LiteLLM (recommended)
```

## Step 2: Prepare Your Data

Create a CSV file with a `gene` column:

```csv
gene,logFC,pvalue
TP53,2.3,0.001
MYC,1.8,0.002
BRCA1,-1.5,0.003
EGFR,2.1,0.001
KRAS,1.9,0.002
```

## Step 3: Run Annotation

### Option A: Command Line

```bash
gs2txt --input genes.csv --output results.csv --api-key $OPENAI_API_KEY
```

### Option B: Python API

```python
import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

# Load data
deg_df = pd.read_csv("genes.csv")

# Setup provider
provider = OpenAIProvider(
    api_key="your-api-key",
    model_id="gpt-4",
    temperature=0.0
)

# Create annotator and run
annotator = GeneSetAnnotator(llm_provider=provider)
result = annotator.annotate(deg_df)

print(result)
```

## Step 4: View Results

The output is a concise biological process description:

```
This gene set is enriched for critical tumor suppressors (TP53, BRCA1)
and oncogenes (MYC, EGFR, KRAS) that collectively regulate cell cycle
checkpoints and apoptotic responses to genomic stress.
```

## Common Use Cases

### Process Multiple Clusters

```python
from gs2txt.batch import BatchProcessor

processor = BatchProcessor(annotator)
processor.process_single_file(
    input_path="clustered_genes.csv",
    output_path="results.csv",
    group_column="cluster"
)
```

### Use Pre-computed Pathways

```python
pathways = ["T cell activation", "Immune response", "Cytokine signaling"]
result = annotator.annotate(deg_df, pathways=pathways)
```

### Add PPI Context

```python
ppi_context = "Hub genes: TP53, MYC. Network density: 0.45"
result = annotator.annotate(deg_df, additional_context=ppi_context)
```

## Next Steps

- [Usage Scenarios](../scenarios/index.md) - Choose the right approach for your use case
- [Configuration](configuration.md) - Customize filtering and LLM parameters
- [API Reference](../api/annotator.md) - Full API documentation
