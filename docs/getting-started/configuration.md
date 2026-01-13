# Configuration

gs2txt provides flexible configuration options for gene filtering, pathway filtering, and LLM settings.

## Gene Filtering Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_gene_num` | 60 | Maximum number of genes to include |
| `pvalue_threshold` | 0.05 | P-value cutoff (genes with pvalue <= threshold) |
| `log2fc_threshold` | 1.0 | Log2FC cutoff (genes with \|log2FC\| >= threshold) |

### Example

```python
result = annotator.annotate(
    deg_df,
    max_gene_num=100,
    pvalue_threshold=0.01,
    log2fc_threshold=1.5
)
```

## Pathway Filtering Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_pathway_num` | 10 | Maximum number of pathways to include |
| `compute_enrichment` | True | Whether to run enrichment analysis |

### Example

```python
result = annotator.annotate(
    deg_df,
    max_pathway_num=15,
    compute_enrichment=True
)
```

## LLM Provider Configuration

### OpenAI

```python
from gs2txt.llm import OpenAIProvider

provider = OpenAIProvider(
    api_key="sk-xxx",
    model_id="gpt-4",           # or "gpt-4-turbo", "gpt-3.5-turbo"
    temperature=0.0,            # 0.0 = deterministic, 1.0 = creative
    base_url=None               # Optional: custom endpoint
)
```

### Anthropic

```python
from gs2txt.llm import AnthropicProvider

provider = AnthropicProvider(
    api_key="sk-ant-xxx",
    model_id="claude-sonnet-4-20250514",
    temperature=0.0
)
```

### LiteLLM (Recommended)

```python
from gs2txt.llm import LiteLLMProvider

provider = LiteLLMProvider(
    api_key="your-api-key",
    model_id="gpt-4",
    temperature=0.0,
    base_url="https://your-litellm-server.com/"
)
```

## YAML Configuration (Two-Stage Pipeline)

For the two-stage pipeline, use a YAML configuration file:

```yaml
# config.yaml

# Input paths (for batch mode)
input:
  deg_dir: "./data/deg/"
  pathway_dirs:
    - "./data/GO/"
    - "./data/KEGG/"
    - "./data/Reactome/"

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
  base_url: "https://your-litellm-server.com/"
  api_key_env: "LITELLM_API_KEY"  # Read from environment variable
```

### Using YAML Config

```python
from gs2txt.pipeline import TwoStagePipeline

# Stage 1: Preprocess
TwoStagePipeline.preprocess_batch(
    config_file="config.yaml",
    output_file="intermediate.csv"
)

# Stage 2: Annotate
TwoStagePipeline.annotate(
    intermediate_file="intermediate.csv",
    output_file="final_output.csv",
    config_file="config.yaml"
)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GS2TXT_API_KEY` | Default API key for CLI |
| `GS2TXT_PROVIDER` | Default LLM provider |
| `GS2TXT_MODEL` | Default model ID |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `LITELLM_API_KEY` | LiteLLM API key |

## Column Name Mapping

gs2txt supports common column name variations:

### Gene Columns

- `gene`, `Gene`, `GENE`, `symbol`, `Symbol`

### P-value Columns

- `pvalue`, `p_value`, `p-value`, `PValue`, `padj`, `FDR`

### Log2FC Columns

- `logFC`, `log2FC`, `log2FoldChange`, `Log2FC`

### Pathway Term Columns

- `Term`, `term`, `Pathway`, `pathway`, `Name`, `name`
