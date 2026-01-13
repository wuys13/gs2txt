# Advanced Usage

Extend gs2txt for custom use cases.

## Topics

### [Custom LLM Providers](custom-providers.md)

Create providers for any LLM service:

- Local models (Ollama, vLLM)
- Custom API endpoints
- Retry logic and caching
- Logging and monitoring

### [Custom Prompts](custom-prompts.md)

Customize prompts for specific domains:

- Cancer genomics
- Immunology
- Drug response
- Multi-language support
- Structured output

### [Custom Enrichment](custom-enrichment.md)

Implement custom enrichment methods:

- External APIs (DAVID, Enrichr)
- Local databases
- Combined sources
- Pre-computed results

## Quick Examples

### Custom Provider

```python
from gs2txt.llm.base import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    def generate(self, messages):
        # Your implementation
        return response_text
```

### Custom Prompt

```python
from gs2txt.prompts.builder import PromptBuilder

builder = PromptBuilder(
    system_template="You are a cancer expert...",
    user_template="Analyze: {genes}"
)
```

### Custom Enrichment

```python
from gs2txt.enrichment import BaseEnrichment

class MyEnrichment(BaseEnrichment):
    def enrich(self, genes, **kwargs):
        # Your implementation
        return pd.DataFrame({
            "Term": [...],
            "Adjusted P-value": [...]
        })
```
