# 🧬 gs2txt

> LLM-powered biological process annotation for gene sets

[![PyPI version](https://badge.fury.io/py/gs2txt.svg)](https://badge.fury.io/py/gs2txt)
[![Tests](https://github.com/wuys13/gs2txt/workflows/tests/badge.svg)](https://github.com/wuys13/gs2txt/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**gs2txt** uses large language models to generate concise, biologically meaningful descriptions of gene sets. It intelligently combines gene functions with pathway enrichment results to infer the dominant biological process.

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
    model_id="gpt-4",
    temperature=0.0
)

# Create annotator
annotator = GeneSetAnnotator(llm_provider=provider)

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
    model_id="claude-sonnet-4-20250514",
    temperature=0.0
)

annotator = GeneSetAnnotator(llm_provider=provider)
result = annotator.annotate(deg_df)
```

### Example 2: Use pre-computed pathways

```python
pathways = [
    "T cell activation",
    "Immune response",
    "Cytokine signaling"
]

# Pathways will be used directly, enrichment will be skipped
result = annotator.annotate(
    deg_df,
    pathways=pathways
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

### Example 4: Batch process multiple gene sets

```python
# Process multiple gene sets
gene_sets = {
    "cluster_1": deg_df_1,
    "cluster_2": deg_df_2,
    "cluster_3": deg_df_3
}

results = {}
for name, df in gene_sets.items():
    results[name] = annotator.annotate(df)
    print(f"{name}: {results[name]}")
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
import pandas as pd

class MyEnrichment(BaseEnrichment):
    def enrich(self, genes: list, **kwargs) -> pd.DataFrame:
        # Your enrichment logic
        # Return DataFrame with 'Term' and 'Adjusted P-value' columns
        return pd.DataFrame({
            "Term": ["pathway1", "pathway2"],
            "Adjusted P-value": [0.01, 0.02]
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
git clone https://github.com/wuys13/gs2txt.git
cd gs2txt
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

- **Issues**: [GitHub Issues](https://github.com/wuys13/gs2txt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wuys13/gs2txt/discussions)
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
