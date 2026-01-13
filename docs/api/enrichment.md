# Enrichment Methods

gs2txt supports flexible pathway enrichment analysis.

## Overview

| Method | Description | Use Case |
|--------|-------------|----------|
| `PathwayEnrichment` | GSEApy-based enrichment | Automatic pathway discovery |
| `CustomEnrichment` | Pre-computed results | External enrichment tools |
| `None` | Skip enrichment | Gene-only analysis |

## PathwayEnrichment

Default enrichment using GSEApy.

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method="pathway"  # Default
)
```

### Supported Databases

- MSigDB (Molecular Signatures Database)
- KEGG (Kyoto Encyclopedia of Genes and Genomes)
- GO (Gene Ontology)

### Requirements

```bash
pip install gs2txt[enrichment]
# or
pip install gseapy
```

## CustomEnrichment

Use pre-computed enrichment results.

```python
from gs2txt.enrichment.custom import CustomEnrichment

# Pre-computed pathways
pathways = [
    "T cell activation",
    "Immune response",
    "Cytokine signaling"
]

custom_enrichment = CustomEnrichment(terms=pathways)

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=custom_enrichment
)
```

### Alternative: Pass Pathways Directly

```python
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=None
)

result = annotator.annotate(
    deg_df,
    pathways=["T cell activation", "Immune response"],
    compute_enrichment=False
)
```

## Skip Enrichment

For gene-only analysis without pathway context.

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

## Custom Enrichment Class

Implement your own enrichment method:

```python
from gs2txt.enrichment import BaseEnrichment
import pandas as pd

class MyEnrichment(BaseEnrichment):
    def __init__(self, database: str = "GO"):
        self.database = database

    def enrich(
        self,
        genes: List[str],
        **kwargs
    ) -> pd.DataFrame:
        # Your enrichment logic
        results = my_enrichment_api(
            genes=genes,
            database=self.database
        )

        # Return DataFrame with required columns
        return pd.DataFrame({
            "Term": results["pathway_names"],
            "Adjusted P-value": results["pvalues"]
        })
```

### Required Output Format

The `enrich()` method must return a DataFrame with:

| Column | Type | Description |
|--------|------|-------------|
| `Term` | `str` | Pathway/term name |
| `Adjusted P-value` | `float` | Statistical significance |

### Usage

```python
my_enrichment = MyEnrichment(database="Reactome")

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=my_enrichment
)
```

## Enrichment Parameters

Control enrichment behavior:

```python
result = annotator.annotate(
    deg_df,
    max_pathway_num=15,        # Max pathways to include
    compute_enrichment=True    # Enable/disable enrichment
)
```

## Two-Stage Pipeline Enrichment

For the two-stage pipeline, enrichment files are provided externally:

```yaml
# config.yaml
input:
  pathway_dirs:
    - "./data/GO/"
    - "./data/KEGG/"
    - "./data/Reactome/"

pathway_filter:
  pvalue_threshold: 0.05
  pvalue_column: "Adjusted P-value"
  term_column: "Term"
  max_pathway_num: 10
```

### Pathway File Format

```csv
Term,Adjusted P-value,Genes
DNA damage response,0.0001,"TP53,BRCA1,ATM"
Cell cycle checkpoint,0.0005,"CDKN1A,RB1"
Apoptotic process,0.001,"BAX,BCL2,TP53"
```

### Multiple Source Merging

When using multiple pathway directories:

1. Files are matched by name (e.g., `sample1.csv`)
2. Pathways from all sources are merged
3. Duplicates are removed
4. Results are sorted by p-value
5. Top N pathways are selected

## Performance Tips

1. **Skip enrichment for speed**: Use `compute_enrichment=False` with pre-computed pathways
2. **Limit pathway count**: Use `max_pathway_num` to reduce prompt size
3. **Use two-stage pipeline**: Pre-compute enrichment once, re-run annotation as needed
