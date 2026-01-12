# gs2txt Development Framework

## Project Structure

```
gs2txt/
├── gs2txt/                          # Main package directory
│   ├── __init__.py                  # Package initialization, exports main APIs
│   ├── core.py                      # Core annotation logic (GeneSetAnnotator)
│   ├── llm/
│   │   ├── __init__.py              # Export LLM providers
│   │   ├── base.py                  # BaseLLMProvider abstract class
│   │   ├── openai_provider.py      # OpenAI implementation
│   │   ├── anthropic_provider.py   # Anthropic Claude implementation
│   │   └── litellm_provider.py     # LiteLLM implementation
│   ├── enrichment/
│   │   ├── __init__.py              # Export enrichment classes
│   │   ├── base.py                  # BaseEnrichment abstract class
│   │   ├── pathway.py               # Pathway enrichment (GSEApy)
│   │   ├── custom.py                # Custom enrichment adapter
│   │   └── ppi.py                   # PPI network analysis (future)
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── templates.py             # Prompt templates
│   │   └── builder.py               # PromptBuilder class
│   └── utils.py                     # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_core.py                 # Test core annotation logic
│   ├── test_llm_providers.py        # Test LLM providers
│   ├── test_enrichment.py           # Test enrichment methods
│   ├── test_prompts.py              # Test prompt building
│   └── fixtures/
│       ├── sample_degs.csv          # Sample DEG data
│       └── sample_pathways.json     # Sample pathway results
├── examples/
│   ├── basic_usage.py               # Basic annotation example
│   ├── custom_llm.py                # Custom LLM provider example
│   ├── custom_enrichment.py         # Custom enrichment example
│   ├── batch_processing.py          # Batch processing example
│   └── notebooks/
│       └── tutorial.ipynb           # Tutorial notebook
├── docs/
│   ├── quickstart.md                # Quick start guide
│   ├── api_reference.md             # API reference
│   ├── advanced_usage.md            # Advanced usage guide
│   └── custom_providers.md          # Custom provider guide
├── data/                            # Sample datasets
│   └── pathways/
├── pyproject.toml                   # Project configuration (PEP 517/518)
├── setup.py                         # Backwards compatibility setup
├── README.md                        # Project README
├── CLAUDE.md                        # Claude Code guidance
├── LICENSE                          # MIT License
└── CHANGELOG.md                     # Version history
```

## Key Design Principles

### 1. Modular Architecture
- **LLM providers**: Abstract base class with pluggable implementations
- **Enrichment methods**: Support built-in (GSEApy) or custom enrichment
- **Prompt building**: Customizable templates for different use cases

### 2. Flexible Configuration
- Users can choose any LLM provider (OpenAI, Anthropic, LiteLLM, custom)
- Enrichment can be skipped, use built-in methods, or provide pre-computed results
- Additional context (PPI, cell type info) can be added to prompts

### 3. Simple API
- Main entry point: `GeneSetAnnotator` class
- One-line annotation: `annotator.annotate(deg_df)`
- Sensible defaults with full customization options

## Dependencies

### Core Dependencies
```toml
pandas >= 1.5.0          # DataFrame operations
openai >= 1.0.0          # OpenAI API client
anthropic >= 0.18.0      # Anthropic Claude API client
```

### Optional Dependencies
```toml
gseapy >= 1.0.0          # Pathway enrichment (optional)
```

### Development Dependencies
```toml
pytest >= 7.0.0          # Testing framework
pytest-cov >= 4.0.0      # Coverage reporting
black >= 23.0.0          # Code formatting
ruff >= 0.1.0            # Linting
mypy >= 1.0.0            # Type checking
pre-commit >= 3.0.0      # Git hooks
```

## Module Descriptions

### `core.py`
- `GeneSetAnnotator`: Main class orchestrating the annotation workflow
  - Accepts LLM provider, enrichment method, and prompt builder
  - `annotate()` method: main API for generating annotations
  - Handles input validation, gene extraction, pathway computation, LLM invocation

### `llm/base.py`
- `BaseLLMProvider`: Abstract base class defining the LLM interface
  - `generate(messages)`: Generate response from message list
  - `validate_config()`: Validate provider configuration

### `llm/openai_provider.py`
- `OpenAIProvider`: OpenAI API implementation
- Supports custom base_url for compatible endpoints

### `llm/anthropic_provider.py`
- `AnthropicProvider`: Anthropic Claude API implementation
- Handles system message separation required by Claude API

### `llm/litellm_provider.py`
- `LiteLLMProvider`: Unified interface for multiple backends
- Supports OpenAI-compatible APIs through LiteLLM

### `enrichment/base.py`
- `BaseEnrichment`: Abstract base class for enrichment analysis
  - `enrich(genes)`: Returns DataFrame with 'Term' and 'Adjusted P-value'

### `enrichment/pathway.py`
- `PathwayEnrichment`: GSEApy-based pathway enrichment
- Supports MSigDB, KEGG, GO databases

### `enrichment/custom.py`
- `CustomEnrichment`: Adapter for pre-computed enrichment results
- Accepts pathway term list or full enrichment DataFrame

### `prompts/builder.py`
- `PromptBuilder`: Constructs LLM prompts from templates
- Supports custom system and user prompt templates
- Handles gene list, pathway list, and additional context formatting

## Implementation Notes

### Import Structure
The package should support these import patterns:
```python
# Main API
from gs2txt import GeneSetAnnotator

# LLM providers
from gs2txt.llm.base import OpenAIProvider, AnthropicProvider, LiteLLMProvider

# Enrichment methods
from gs2txt.enrichment.base import BaseEnrichment
from gs2txt.enrichment.pathway import PathwayEnrichment
from gs2txt.enrichment.custom import CustomEnrichment

# Prompt building
from gs2txt.prompts.builder import PromptBuilder
```

### Configuration Pattern
```python
# Minimal configuration (uses defaults)
annotator = GeneSetAnnotator(llm_provider=provider)

# Full configuration
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method="pathway",  # or instance of BaseEnrichment
    prompt_builder=PromptBuilder(),
    # Additional enrichment kwargs
    gene_sets=["MSigDB_Hallmark_2020"],
    cutoff=0.05
)
```

### Error Handling
- Input validation: Check for required 'gene' column
- Enrichment failures: Log warning and continue without pathways
- LLM failures: Return error message with "Process: Failed" prefix
- Empty gene lists: Return "Process: Unresolved functional program"
