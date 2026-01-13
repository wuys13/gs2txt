# Two-Stage Pipeline

The `TwoStagePipeline` class separates data preprocessing from LLM annotation.

## Overview

```
Stage 1 (Preprocess)          Stage 2 (Annotate)
--------------------          ------------------
DEG files ─────┐               intermediate.csv
               │                      │
Pathway files ─┼──► intermediate.csv ──► LLM ──► final_output.csv
               │
Config file ───┘
```

## Class Reference

::: gs2txt.pipeline.TwoStagePipeline
    options:
      show_source: true
      heading_level: 3

## Methods

### preprocess_batch()

Batch preprocess multiple DEG files with multiple pathway sources.

```python
@staticmethod
def preprocess_batch(
    config_file: str,
    output_file: str = "intermediate.csv",
    ppi_context: Optional[Dict[str, str]] = None
) -> pd.DataFrame
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_file` | `str` | Required | Path to YAML config |
| `output_file` | `str` | `"intermediate.csv"` | Output path |
| `ppi_context` | `Dict[str, str]` | `None` | PPI context per gene set |

#### Example

```python
from gs2txt.pipeline import TwoStagePipeline

TwoStagePipeline.preprocess_batch(
    config_file="config.yaml",
    output_file="intermediate.csv",
    ppi_context={
        "sample1": "Hub genes: TP53, BRCA1",
        "sample2": "Hub genes: CD4, IL2"
    }
)
```

### preprocess()

Preprocess a single DEG file with grouped clusters.

```python
@staticmethod
def preprocess(
    deg_file: str,
    enrichment_dir: str,
    output_file: str,
    config_file: Optional[str] = None,
    group_column: str = "cluster",
    ppi_context: Optional[Dict[str, str]] = None
) -> pd.DataFrame
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deg_file` | `str` | Required | Path to DEG CSV |
| `enrichment_dir` | `str` | Required | Path to enrichment directory |
| `output_file` | `str` | Required | Output path |
| `config_file` | `str` | `None` | Path to config (optional) |
| `group_column` | `str` | `"cluster"` | Column for grouping |
| `ppi_context` | `Dict[str, str]` | `None` | PPI context per cluster |

#### Example

```python
TwoStagePipeline.preprocess(
    deg_file="deg.csv",
    enrichment_dir="enrichment/",
    output_file="intermediate.csv",
    config_file="config.yaml",
    group_column="cluster"
)
```

### annotate()

Generate annotations using LLM.

```python
@staticmethod
def annotate(
    intermediate_file: str,
    output_file: str,
    config_file: Optional[str] = None
) -> pd.DataFrame
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `intermediate_file` | `str` | Required | Path to intermediate CSV |
| `output_file` | `str` | Required | Output path |
| `config_file` | `str` | `None` | Path to config |

#### Example

```python
TwoStagePipeline.annotate(
    intermediate_file="intermediate.csv",
    output_file="final_output.csv",
    config_file="config.yaml"
)
```

## Configuration

### YAML Config Structure

```yaml
# Input paths (for batch mode)
input:
  deg_dir: "./data/deg/"
  pathway_dirs:
    - "./data/GO/"
    - "./data/KEGG/"

# Gene filtering
gene_filter:
  pvalue_threshold: 0.05
  log2fc_threshold: 1.0
  pvalue_column: "pvalue"
  log2fc_column: "logFC"
  max_gene_num: 60

# Pathway filtering
pathway_filter:
  pvalue_threshold: 0.05
  pvalue_column: "Adjusted P-value"
  term_column: "Term"
  max_pathway_num: 10

# LLM configuration
llm:
  provider: "litellm"
  model_id: "gpt-4"
  temperature: 0.0
  base_url: "https://your-server.com/"
  api_key_env: "LITELLM_API_KEY"
```

### PipelineConfig Class

```python
from gs2txt.config_loader import PipelineConfig

# Load from YAML
config = PipelineConfig.from_yaml("config.yaml")

# Use defaults
config = PipelineConfig.default()

# Save config
config.save_yaml("config_backup.yaml")

# Access attributes
print(config.max_gene_num)
print(config.llm_provider)
```

## File Formats

### DEG File (Input)

```csv
gene,pvalue,logFC
TP53,0.001,2.5
BRCA1,0.002,2.3
```

### Pathway File (Input)

```csv
Term,Adjusted P-value,Genes
DNA damage response,0.0001,"TP53,BRCA1"
Cell cycle,0.0005,"CDKN1A,RB1"
```

### Intermediate File (Stage 1 Output)

```csv
gs,genes,pathways,ppis,final_prompt
sample1,"TP53,BRCA1","DNA damage,Cell cycle","Hub: TP53","Your task..."
```

### Final Output (Stage 2 Output)

```csv
gs,annotation,pathways,PPIs,Final_prompt
sample1,"This gene set is involved in...","DNA damage","Hub: TP53","Your task..."
```

## Workflow Examples

### Batch Processing

```python
# Stage 1: Preprocess all samples
TwoStagePipeline.preprocess_batch(
    config_file="config.yaml",
    output_file="intermediate.csv"
)

# Review intermediate.csv here

# Stage 2: Annotate
TwoStagePipeline.annotate(
    intermediate_file="intermediate.csv",
    output_file="final_output.csv",
    config_file="config.yaml"
)
```

### Single File Processing

```python
# Stage 1
TwoStagePipeline.preprocess(
    deg_file="clustered_deg.csv",
    enrichment_dir="enrichment/",
    output_file="intermediate.csv",
    group_column="cluster"
)

# Stage 2
TwoStagePipeline.annotate(
    intermediate_file="intermediate.csv",
    output_file="final_output.csv"
)
```

## Error Handling

```python
try:
    TwoStagePipeline.preprocess_batch(
        config_file="config.yaml",
        output_file="intermediate.csv"
    )
except FileNotFoundError as e:
    print(f"Missing file: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

Common errors:

- `FileNotFoundError`: DEG directory or config file not found
- `ValueError`: Missing required columns or invalid configuration
- LLM errors during annotation stage
