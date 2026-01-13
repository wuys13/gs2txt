# Installation

## Requirements

- Python 3.9 or higher
- pip package manager

## Basic Installation

Install gs2txt from PyPI:

```bash
pip install gs2txt
```

## Installation with Optional Dependencies

### With Enrichment Support

For built-in pathway enrichment using GSEApy:

```bash
pip install gs2txt[enrichment]
```

### With All Features

```bash
pip install gs2txt[all]
```

### For Development

```bash
pip install gs2txt[dev]
```

## Development Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/wuys13/gs2txt.git
cd gs2txt
pip install -e ".[dev]"
```

## Verify Installation

```python
import gs2txt
from gs2txt import GeneSetAnnotator
from gs2txt.llm import OpenAIProvider, AnthropicProvider, LiteLLMProvider

print("gs2txt installed successfully!")
```

## API Keys

gs2txt requires an API key for the LLM provider you choose:

### OpenAI

```bash
export OPENAI_API_KEY=sk-xxx
```

### Anthropic

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
```

### LiteLLM (Recommended)

```bash
export LITELLM_API_KEY=your-api-key
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration Options](configuration.md)
