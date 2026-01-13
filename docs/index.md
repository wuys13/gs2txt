# gs2txt

> LLM-powered biological process annotation for gene sets

**gs2txt** uses large language models to generate concise, biologically meaningful descriptions of gene sets. It intelligently combines gene functions with pathway enrichment results to infer the dominant biological process.

## Features

- **Multiple LLM Providers**: OpenAI, Anthropic Claude, LiteLLM, or custom
- **Flexible Enrichment**: Built-in pathway enrichment or bring your own
- **Customizable Prompts**: Tailor prompts for specific domains or output formats
- **Batch Processing**: Process multiple gene sets from CSV files
- **Two-Stage Pipeline**: Separate preprocessing from API calls for large-scale analysis
- **Simple API**: One-line annotation or full programmatic control

## Quick Example

```python
import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

# Your differential expression results
deg_df = pd.DataFrame({
    "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
    "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]
})

# Setup and annotate
provider = OpenAIProvider(api_key="your-key", model_id="gpt-4")
annotator = GeneSetAnnotator(llm_provider=provider)
result = annotator.annotate(deg_df)

print(result)
# Output: "This gene set is enriched for critical tumor suppressors and oncogenes
# that collectively regulate cell cycle checkpoints and apoptotic responses..."
```

## Installation

```bash
pip install gs2txt
```

## Usage Scenarios

gs2txt provides three usage scenarios for different needs:

| Scenario | Best For | API Required |
|----------|----------|--------------|
| [Batch CSV](scenarios/scenario1.md) | Process CSV files, output to CSV | Yes |
| [Python API](scenarios/scenario2.md) | Code integration, get text results | Yes |
| [Two-Stage Pipeline](scenarios/scenario3.md) | Large-scale analysis, review before API | Stage 1: No, Stage 2: Yes |

## Getting Started

1. [Installation Guide](getting-started/installation.md)
2. [Quick Start Tutorial](getting-started/quickstart.md)
3. [Configuration Options](getting-started/configuration.md)

## Links

- [GitHub Repository](https://github.com/wuys13/gs2txt)
- [PyPI Package](https://pypi.org/project/gs2txt/)
- [Issue Tracker](https://github.com/wuys13/gs2txt/issues)
