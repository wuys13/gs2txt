# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

gs2txt is a Python package that uses Large Language Models (LLMs) to automatically generate concise, biologically meaningful descriptions of gene sets. It combines gene functions with pathway enrichment results to infer the dominant biological process, designed for functional genomics researchers working with differential gene expression (DEG) analysis.

## Core Architecture

### Main Components

1. **GeneSetAnnotator** (`core.py`): Main annotation engine that orchestrates the workflow
   - Accepts LLM provider, enrichment method, and prompt builder
   - Main API: `annotate(deg_df)` method
   - Handles input validation, gene extraction, pathway computation, LLM invocation

2. **LLM Providers** (`llm/`): Pluggable abstraction for different LLM services
   - `BaseLLMProvider`: Abstract base class defining the interface
   - `OpenAIProvider`: OpenAI API implementation
   - `AnthropicProvider`: Anthropic Claude implementation
   - `LiteLLMProvider`: Unified interface for multiple backends

3. **Enrichment Analysis** (`enrichment/`): Flexible pathway enrichment
   - `BaseEnrichment`: Abstract base class
   - `PathwayEnrichment`: GSEApy-based enrichment (MSigDB, KEGG, GO)
   - `CustomEnrichment`: Adapter for pre-computed results

4. **Prompt Building** (`prompts/builder.py`): Customizable templates
   - `PromptBuilder`: Constructs LLM prompts with customizable templates
   - Supports custom system/user prompts for domain-specific use cases

## Development Commands

### Installation

```bash
# Install package in development mode
pip install -e .

# Install with all dependencies (including enrichment tools)
pip install -e ".[all]"

# Install development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=gs2txt --cov-report=term-missing

# Run specific test file
pytest tests/test_core.py

# Run tests excluding integration tests
pytest -m "not integration"

# Run tests excluding slow tests
pytest -m "not slow"
```

### Code Quality

```bash
# Format code with black
black gs2txt/ tests/

# Lint with ruff
ruff check gs2txt/ tests/

# Type check with mypy
mypy gs2txt/
```

## Project Structure

```
gs2txt/
├── gs2txt/                    # Main package
│   ├── __init__.py           # Package initialization
│   ├── core.py               # GeneSetAnnotator class
│   ├── llm/                  # LLM provider implementations
│   ├── enrichment/           # Enrichment methods
│   ├── prompts/              # Prompt templates
│   └── utils.py              # Utilities
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── old_code/                 # Reference implementation
├── pyproject.toml            # Package configuration
└── readme.md                 # User documentation
```

## Key API Patterns

### Basic Usage

```python
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider
import pandas as pd

# Setup
provider = OpenAIProvider(api_key="sk-...", model_id="gpt-4", temperature=0.0)
annotator = GeneSetAnnotator(llm_provider=provider)

# Annotate
deg_df = pd.DataFrame({"gene": ["TP53", "MYC", "BRCA1"]})
result = annotator.annotate(deg_df)
```

### With Custom Enrichment

```python
from gs2txt.enrichment.custom import CustomEnrichment

pathways = ["T cell activation", "Immune response"]
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=CustomEnrichment(terms=pathways)
)
```

### With Custom Prompts

```python
from gs2txt.prompts.builder import PromptBuilder

builder = PromptBuilder(
    system_template="You are a cancer genomics expert...",
    user_template="Identify the cancer hallmark: {genes}..."
)
annotator = GeneSetAnnotator(
    llm_provider=provider,
    prompt_builder=builder
)
```

## Code Migration Status

The project is migrating from `/old_code/` (reference implementation) to the proper package structure in `/gs2txt/`.

**Current State:**
- Reference code exists in `/old_code/` with 6 Python files
- Target structure defined in `development.md`
- `pyproject.toml` configured for modern Python packaging

**When Working on This Codebase:**
1. Use `/old_code/` as reference for behavior and API design
2. Implement code in `/gs2txt/` following the structure in `development.md`
3. Maintain API compatibility with examples in `readme.md`
4. Target >90% test coverage for all new code
5. Follow the import patterns: `from gs2txt.llm import OpenAIProvider`

## Design Principles

1. **Modular Architecture**: LLM providers, enrichment methods, and prompts are pluggable
2. **Flexible Configuration**: Users can skip enrichment, use built-in methods, or provide pre-computed results
3. **Simple API**: One-line annotation with sensible defaults, full customization available
4. **Type Safety**: Use type hints throughout for better IDE support and error detection