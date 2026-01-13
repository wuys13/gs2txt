# BatchProcessor

Process multiple gene set files in batch mode.

## Overview

`BatchProcessor` enables efficient processing of multiple DEG files with automatic output generation.

## Class Reference

::: gs2txt.batch.BatchProcessor
    options:
      show_source: true
      heading_level: 3

## Constructor

```python
BatchProcessor(
    llm_provider: BaseLLMProvider,
    enrichment_method: Optional[str] = "pathway",
    prompt_builder: Optional[PromptBuilder] = None
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_provider` | `BaseLLMProvider` | Required | LLM provider instance |
| `enrichment_method` | `str` or `None` | `"pathway"` | Enrichment method |
| `prompt_builder` | `PromptBuilder` | `None` | Custom prompt builder |

## Methods

### process_directory()

Process all CSV files in a directory.

```python
def process_directory(
    self,
    input_dir: str,
    output_dir: str,
    max_gene_num: int = 60,
    max_pathway_num: int = 10,
    pvalue_threshold: float = 0.05,
    log2fc_threshold: float = 1.0
) -> Dict[str, str]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_dir` | `str` | Required | Directory with DEG CSV files |
| `output_dir` | `str` | Required | Output directory |
| `max_gene_num` | `int` | `60` | Maximum genes per file |
| `max_pathway_num` | `int` | `10` | Maximum pathways |
| `pvalue_threshold` | `float` | `0.05` | P-value filter |
| `log2fc_threshold` | `float` | `1.0` | Log2FC filter |

#### Returns

`Dict[str, str]` - Mapping of input filename to annotation result

#### Example

```python
from gs2txt.batch import BatchProcessor
from gs2txt.llm import OpenAIProvider

provider = OpenAIProvider(api_key="...", model_id="gpt-4")
processor = BatchProcessor(llm_provider=provider)

results = processor.process_directory(
    input_dir="data/deg/",
    output_dir="results/",
    max_gene_num=100,
    pvalue_threshold=0.01
)

for filename, annotation in results.items():
    print(f"{filename}: {annotation[:100]}...")
```

### process_file()

Process a single DEG file.

```python
def process_file(
    self,
    input_file: str,
    output_file: Optional[str] = None,
    **kwargs
) -> str
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_file` | `str` | Required | Path to DEG CSV file |
| `output_file` | `str` | `None` | Output path (optional) |
| `**kwargs` | | | Same as `process_directory()` |

#### Returns

`str` - Annotation result

#### Example

```python
result = processor.process_file(
    input_file="data/sample1.csv",
    output_file="results/sample1_annotation.txt"
)
```

## Input File Format

CSV files must have a `gene` column. Optional columns:

| Column | Description |
|--------|-------------|
| `gene` | Gene symbols (required) |
| `pvalue` | P-values for filtering |
| `logFC` | Log2 fold change |

### Example

```csv
gene,pvalue,logFC
TP53,0.001,2.5
BRCA1,0.002,2.3
MYC,0.003,-1.8
```

## Output Format

### Directory Processing

Creates one output file per input file:

```
results/
├── sample1_annotation.csv
├── sample2_annotation.csv
└── sample3_annotation.csv
```

Each output file contains:

```csv
gene_set,annotation
sample1,"This gene set is primarily involved in..."
```

### Single File Processing

Returns annotation as string, optionally saves to file.

## Error Handling

```python
try:
    results = processor.process_directory(
        input_dir="data/",
        output_dir="results/"
    )
except FileNotFoundError as e:
    print(f"Directory not found: {e}")
except ValueError as e:
    print(f"Invalid file format: {e}")
```

## Thread Safety

`BatchProcessor` processes files sequentially by default. For parallel processing, create separate instances:

```python
from concurrent.futures import ThreadPoolExecutor

def process_single(filepath):
    processor = BatchProcessor(llm_provider=provider)
    return processor.process_file(filepath)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_single, file_list))
```
