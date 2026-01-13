# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-13

### Added

- **Core Features**
  - `GeneSetAnnotator` - Main annotation engine for gene set analysis
  - Built-in gene filtering by p-value and log2FC thresholds
  - Automatic pathway enrichment using GSEApy
  - Customizable prompt templates for domain-specific use cases

- **LLM Providers**
  - `OpenAIProvider` - OpenAI API integration (GPT-4, GPT-3.5)
  - `AnthropicProvider` - Anthropic Claude integration
  - `LiteLLMProvider` - Unified interface for multiple LLM backends

- **Enrichment Methods**
  - `PathwayEnrichment` - GSEApy-based enrichment (MSigDB, KEGG, GO)
  - `CustomEnrichment` - Adapter for pre-computed results

- **Batch Processing**
  - `BatchProcessor` - Process multiple gene sets from CSV files
  - Support for grouped data (e.g., by cluster)
  - Automatic output formatting (gs, annotation columns)

- **Two-Stage Pipeline** (New in 0.1.0)
  - `TwoStagePipeline.preprocess()` - Single file preprocessing
  - `TwoStagePipeline.preprocess_batch()` - Batch preprocessing from folders
  - `TwoStagePipeline.annotate()` - LLM annotation stage
  - YAML configuration support
  - Multiple pathway source merging (GO, KEGG, Reactome)

- **CLI Interface**
  - `gs2txt` command for processing CSV files
  - Support for multiple providers and models
  - Configurable filtering parameters

- **Documentation**
  - Three usage scenarios with example scripts
  - Comprehensive README with API examples
  - MkDocs documentation site

### Example Scripts

- `scenario1_batch_csv.py` - Batch CSV processing
- `scenario2_api.py` - Python API integration
- `scenario3_two_stage.py` - Two-stage pipeline processing

---

[Unreleased]: https://github.com/wuys13/gs2txt/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/wuys13/gs2txt/releases/tag/v0.1.0
