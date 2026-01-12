# 🧬 gs2txt

> LLM-powered biological process annotation for gene sets

[![PyPI version](https://badge.fury.io/py/geneset-annotator.svg)](https://badge.fury.io/py/geneset-annotator)
[![Tests](https://github.com/yourusername/geneset-annotator/workflows/tests/badge.svg)](https://github.com/yourusername/geneset-annotator/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**geneset-annotator** uses large language models to generate concise, biologically meaningful descriptions of gene sets. It intelligently combines gene functions with pathway enrichment results to infer the dominant biological process.

---

## ✨ Features

- 🤖 **Multiple LLM providers**: OpenAI, Anthropic Claude, LiteLLM, or custom
- 🧪 **Flexible enrichment**: Built-in pathway enrichment or bring your own
- 🔧 **Customizable prompts**: Tailor prompts for specific domains or output formats
- 📊 **Batch processing**: Process multiple gene sets from CSV files
- 🐍 **Simple API**: One-line annotation or full programmatic control
- 🧪 **Well tested**: Comprehensive test suite with >90% coverage

---

## 🚀 Quick Start

### Installation

```bash
pip install gs2txt
```

### Basic Usage

```python
import pandas as pd
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider

# Your differential expression results
deg_df = pd.DataFrame({
    "gene": ["TP53", "MYC", "BRCA1", "EGFR", "KRAS"],
    "logFC": [2.3, 1.8, -1.5, 2.1, 1.9]
})

# Setup LLM provider
provider = OpenAIProvider(
    api_key="your-openai-key",
    model_id="gpt-4"
)

# Create annotator
annotator = GeneSetAnnotator(provider)

# Generate annotation
result = annotator.annotate(deg_df)
print(result)
```

**Output:**

```
Process: DNA damage response and cell cycle regulation

This gene set is enriched for critical tumor suppressors (TP53, BRCA1) 
and oncogenes (MYC, EGFR, KRAS) that collectively regulate cell cycle 
checkpoints and apoptotic responses to genomic stress.
```

---

## 📖 Usage Examples

### Example 1: Use Anthropic Claude

```python
from gs2txt.llm import AnthropicProvider

provider = AnthropicProvider(
    api_key="your-anthropic-key",
    model_id="claude-sonnet-4-20250514"
)

annotator = GeneSetAnnotator(provider)
result = annotator.annotate(deg_df)
```

### Example 2: Skip enrichment with pre-computed pathways

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

### Example 3: Add PPI or other context

```python
ppi_context = """
PPI Network Analysis:
- Hub genes: TP53, MYC, EGFR
- Main module: DNA damage response
"""

result = annotator.annotate(
    deg_df,
    additional_context=ppi_context
)
```

### Example 4: Batch process CSV

```python
from gs2txt.batch import run_batch_annotation

run_batch_annotation(
    provider=provider,
    input_csv="all_clusters_degs.csv",  # has 'cluster' and 'gene' columns
    output_csv="annotated_clusters.csv",
    group_col="cluster"
)
```

### Example 5: Custom prompt template

```python
from gs2txt.prompts.builder import PromptBuilder

custom_builder = PromptBuilder(
    system_template="You are a cancer genomics expert...",
    user_template="Identify the cancer hallmark: {genes}..."
)

annotator = GeneSetAnnotator(
    llm_provider=provider,
    prompt_builder=custom_builder
)
```

---

## 🔧 Advanced Configuration

### Custom LLM Provider

Implement your own LLM provider:

```python
from gs2txt.llm.base import BaseLLMProvider

class MyCustomProvider(BaseLLMProvider):
    def generate(self, messages):
        # Your custom LLM call
        return response_text
  
    def validate_config(self):
        return True

provider = MyCustomProvider(model_id="my-model")
annotator = GeneSetAnnotator(provider)
```

### Custom Enrichment Method

```python
from gs2txt.enrichment import BaseEnrichment

class MyEnrichment(BaseEnrichment):
    def enrich(self, genes, **kwargs):
        # Your enrichment logic
        return pd.DataFrame({
            "Term": [...],
            "Adjusted P-value": [...]
        })

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=MyEnrichment()
)
```

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=gs2txt --cov-report=html
```

---

## 📚 Documentation

- [Quick Start Guide](docs/quickstart.md)
- [API Reference](docs/api_reference.md)
- [Advanced Usage](docs/advanced_usage.md)
- [Custom Providers](docs/custom_providers.md)

---

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

### Development Setup

```bash
git clone https://github.com/yourusername/geneset-annotator.git
cd geneset-annotator
pip install -e ".[dev]"
pre-commit install
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Inspired by the need for interpretable functional genomics
- Built on top of excellent tools: GSEApy
- Thanks to the single-cell genomics community

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/geneset-annotator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/geneset-annotator/discussions)
- **Email**: 80359555@qq.com

---

## ⭐ Citation

If you use geneset-annotator in your research, please cite:

```bibtex
@software{gs2txt,
  title = {gs2txt: LLM-powered gene set annotation},
  author = {Yushuai Wu},
  year = {2025},
  url = {https://github.com/wuys13/gs2txt}
}
```
