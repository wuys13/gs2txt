# Scenario 3: Two-Stage Pipeline

Separate data preprocessing from LLM API calls for large-scale analysis.

## When to Use

- You have large-scale data (many gene sets)
- You want to review data before calling the API
- You need to merge pathways from multiple sources (GO, KEGG, Reactome)
- You want to separate data preparation from API usage
- You're working in an environment where API access is restricted

## Key Benefits

1. **Stage 1 (Preprocess)**: No API needed - can run offline
2. **Review intermediate results** before spending API credits
3. **Merge pathways** from multiple databases
4. **Resume annotation** if interrupted
5. **Re-run annotation** with different models without re-preprocessing

## Quick Start

```bash
cd examples

# Stage 1: Preprocess (no API needed)
python scenario3_two_stage.py batch

# Review intermediate results
python scenario3_two_stage.py check

# Stage 2: Annotate (API needed)
export LITELLM_API_KEY=your-api-key
python scenario3_two_stage.py annotate
```

## Input Structure

### DEG Files (one per gene set)

```
data/deg/
├── sample1.csv
├── sample2.csv
└── sample3.csv
```

Each file contains:
```csv
gene,pvalue,logFC
TP53,0.001,2.5
BRCA1,0.002,2.3
CDKN1A,0.003,2.1
```

### Pathway Files (multiple sources)

```
data/GO/
├── sample1.csv
├── sample2.csv
└── sample3.csv

data/KEGG/
├── sample1.csv
├── sample2.csv
└── sample3.csv

data/Reactome/
├── sample1.csv
└── sample3.csv
```

Each file contains:
```csv
Term,Adjusted P-value,Genes
DNA damage response,0.0001,"TP53,BRCA1,ATM"
Cell cycle checkpoint,0.0005,"CDKN1A,RB1"
```

## Configuration File

Create `config.yaml`:

```yaml
# Input paths
input:
  deg_dir: "../data/deg/"
  pathway_dirs:
    - "../data/GO/"
    - "../data/KEGG/"
    - "../data/Reactome/"

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
  api_key_env: "LITELLM_API_KEY"
```

## Code Examples

### Stage 1: Batch Preprocess

```python
from gs2txt.pipeline import TwoStagePipeline

# Preprocess all DEG files
TwoStagePipeline.preprocess_batch(
    config_file="config.yaml",
    output_file="intermediate.csv",
    ppi_context={
        "sample1": "Hub genes: TP53, BRCA1",
        "sample2": "Hub genes: CD4, IL2"
    }
)
```

### Stage 2: Annotate

```python
TwoStagePipeline.annotate(
    intermediate_file="intermediate.csv",
    output_file="final_output.csv",
    config_file="config.yaml"
)
```

### Single File Mode (Alternative)

For processing a single DEG file with one enrichment directory:

```python
TwoStagePipeline.preprocess(
    deg_file="sample_deg.csv",
    enrichment_dir="enrichment/",
    output_file="intermediate.csv",
    config_file="config.yaml",
    group_column="cluster"
)
```

## Output Format

### Intermediate Results (`intermediate.csv`)

```csv
gs,genes,pathways,ppis,final_prompt
sample1,"TP53,BRCA1,CDKN1A","DNA damage response,p53 signaling","Hub: TP53","Your task..."
sample2,"CD4,CD8A,IL2","T cell activation,Immune response","Hub: CD4","Your task..."
```

### Final Results (`final_output.csv`)

```csv
gs,annotation,pathways,PPIs,Final_prompt
sample1,"This gene set is involved in DNA damage response...",DNA damage response,"Hub: TP53","Your task..."
sample2,"T cell activation and immune signaling...",T cell activation,"Hub: CD4","Your task..."
```

## Pathway Merging

When using multiple pathway directories, gs2txt:

1. Searches each directory for matching files (same filename)
2. Merges all pathways from all sources
3. Removes duplicates
4. Sorts by p-value
5. Takes top N pathways (configured by `max_pathway_num`)

Example: For `sample1.csv`:
- Finds `GO/sample1.csv`, `KEGG/sample1.csv`, `Reactome/sample1.csv`
- Merges all pathways, removes duplicates
- Sorts by p-value, takes top 10

## CLI Commands

```bash
# Batch preprocess (recommended)
python scenario3_two_stage.py batch

# Single file preprocess
python scenario3_two_stage.py preprocess

# Check intermediate results
python scenario3_two_stage.py check

# Run annotation
python scenario3_two_stage.py annotate

# Run both stages
python scenario3_two_stage.py batch-all
```

## Full Example Script

See [`examples/scenario3_two_stage.py`](https://github.com/wuys13/gs2txt/blob/main/examples/scenario3_two_stage.py) for a complete example.

## Tips

1. **Always check intermediate results** before running annotation
2. **File names must match**: DEG file `sample1.csv` matches pathway `sample1.csv`
3. **Pathway directories are optional**: Missing files are skipped with a warning
4. **PPI context is optional**: Adds extra information to the prompt
5. **Re-run annotation safely**: Intermediate file is preserved
