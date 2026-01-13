# GeneSetAnnotator

The main annotation engine for gene set analysis.

## Overview

`GeneSetAnnotator` is the core class that orchestrates:

1. Gene filtering by p-value and log2FC
2. Pathway enrichment analysis
3. Prompt construction
4. LLM invocation

## Basic Usage

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

provider = OpenAIProvider(api_key="...", model_id="gpt-4")
annotator = GeneSetAnnotator(llm_provider=provider)

result = annotator.annotate(deg_df)
```

## Class Reference

::: gs2txt.core.GeneSetAnnotator
    options:
      show_source: true
      heading_level: 3

## Constructor

```python
GeneSetAnnotator(
    llm_provider: BaseLLMProvider,
    enrichment_method: Optional[str] = "pathway",
    prompt_builder: Optional[PromptBuilder] = None
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_provider` | `BaseLLMProvider` | Required | LLM provider instance |
| `enrichment_method` | `str` or `None` | `"pathway"` | Enrichment method: `"pathway"`, `"custom"`, or `None` |
| `prompt_builder` | `PromptBuilder` | `None` | Custom prompt builder |

### Example

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider
from gs2txt.prompts.builder import PromptBuilder

# Basic setup
annotator = GeneSetAnnotator(
    llm_provider=OpenAIProvider(api_key="...", model_id="gpt-4")
)

# With custom prompt
custom_builder = PromptBuilder(
    system_template="You are a cancer genomics expert...",
    user_template="Analyze these cancer genes: {genes}"
)
annotator = GeneSetAnnotator(
    llm_provider=provider,
    prompt_builder=custom_builder
)

# Without enrichment
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=None
)
```

## Methods

### annotate()

Main method to generate annotation for a gene set.

```python
def annotate(
    self,
    deg_df: pd.DataFrame,
    max_gene_num: int = 60,
    max_pathway_num: int = 10,
    pathways: Optional[List[str]] = None,
    compute_enrichment: bool = True,
    additional_context: Optional[str] = None,
    pvalue_threshold: float = 0.05,
    log2fc_threshold: float = 1.0
) -> str
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deg_df` | `pd.DataFrame` | Required | DataFrame with 'gene' column |
| `max_gene_num` | `int` | `60` | Maximum genes to include |
| `max_pathway_num` | `int` | `10` | Maximum pathways to include |
| `pathways` | `List[str]` | `None` | Pre-computed pathway list |
| `compute_enrichment` | `bool` | `True` | Whether to run enrichment |
| `additional_context` | `str` | `None` | Extra context (e.g., PPI) |
| `pvalue_threshold` | `float` | `0.05` | P-value filter threshold |
| `log2fc_threshold` | `float` | `1.0` | Log2FC filter threshold |

#### Returns

`str` - LLM-generated annotation text

#### Example

```python
result = annotator.annotate(
    deg_df,
    max_gene_num=100,
    pvalue_threshold=0.01,
    additional_context="PPI hub genes: TP53, MYC"
)
```

### annotate_detailed()

Returns detailed results including intermediate data.

```python
def annotate_detailed(
    self,
    deg_df: pd.DataFrame,
    **kwargs
) -> dict
```

#### Returns

```python
{
    "annotation": str,      # LLM result
    "genes": List[str],     # Filtered genes
    "pathways": List[str],  # Enriched pathways
    "prompt": str           # Final prompt sent to LLM
}
```

## Input DataFrame Format

The input DataFrame must have a `gene` column. Optional columns:

| Column | Description |
|--------|-------------|
| `gene` | Gene symbols (required) |
| `pvalue` | P-values for filtering |
| `logFC` | Log2 fold change for filtering |

### Example

```python
import pandas as pd

deg_df = pd.DataFrame({
    "gene": ["TP53", "MYC", "BRCA1"],
    "pvalue": [0.001, 0.002, 0.003],
    "logFC": [2.3, 1.8, -1.5]
})
```

## Error Handling

```python
try:
    result = annotator.annotate(deg_df)
except ValueError as e:
    # Missing 'gene' column
    print(f"Invalid input: {e}")
except Exception as e:
    # LLM API error
    print(f"LLM error: {e}")
```

## Thread Safety

`GeneSetAnnotator` instances are thread-safe for read operations. However, creating separate instances per thread is recommended for parallel processing.

```python
from concurrent.futures import ThreadPoolExecutor

def process_geneset(name, df):
    annotator = GeneSetAnnotator(llm_provider=provider)
    return annotator.annotate(df)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(
        lambda x: process_geneset(x[0], x[1]),
        gene_sets.items()
    )
```
