# Usage Scenarios

gs2txt provides three usage scenarios to fit different workflows and requirements.

## Overview

| Scenario | Best For | API Required | Output Format |
|----------|----------|--------------|---------------|
| [Scenario 1: Batch CSV](scenario1.md) | Process CSV files directly | Yes | CSV file |
| [Scenario 2: Python API](scenario2.md) | Code integration | Yes | String |
| [Scenario 3: Two-Stage](scenario3.md) | Large-scale analysis | Stage 1: No, Stage 2: Yes | CSV files |

## Which Scenario Should I Use?

### Use Scenario 1 (Batch CSV) if:

- You have one or more CSV files to process
- You want simple file-in, file-out workflow
- You don't need to inspect intermediate results

### Use Scenario 2 (Python API) if:

- You're integrating gs2txt into your analysis pipeline
- You need programmatic control over the annotation process
- You want to process results in memory

### Use Scenario 3 (Two-Stage Pipeline) if:

- You have large-scale data (many gene sets)
- You want to review data before calling the LLM API
- You need to merge pathways from multiple sources (GO, KEGG, Reactome)
- You want to separate data preparation from API usage (cost control)

## Quick Comparison

### Scenario 1: Simple and Direct

```python
from gs2txt.batch import BatchProcessor

processor = BatchProcessor(annotator)
processor.process_single_file("input.csv", "output.csv")
```

### Scenario 2: Flexible and Programmable

```python
result = annotator.annotate(deg_df)
# Do something with the string result
```

### Scenario 3: Scalable and Reviewable

```bash
# Stage 1: No API needed
python scenario3_two_stage.py batch

# Review intermediate.csv

# Stage 2: API needed
python scenario3_two_stage.py annotate
```

## Example Scripts

All scenarios have complete example scripts in the `examples/` directory:

- `examples/scenario1_batch_csv.py`
- `examples/scenario2_api.py`
- `examples/scenario3_two_stage.py`

Run them with:

```bash
cd examples
export LITELLM_API_KEY=your-api-key
python scenario1_batch_csv.py
```
