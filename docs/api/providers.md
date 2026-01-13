# LLM Providers

gs2txt supports multiple LLM providers through a pluggable architecture.

## Available Providers

| Provider | Class | Models |
|----------|-------|--------|
| OpenAI | `OpenAIProvider` | GPT-4, GPT-3.5-turbo |
| Anthropic | `AnthropicProvider` | Claude 3.5, Claude 3 |
| LiteLLM | `LiteLLMProvider` | Any LiteLLM-supported model |

## OpenAIProvider

```python
from gs2txt.llm import OpenAIProvider

provider = OpenAIProvider(
    api_key="sk-xxx",
    model_id="gpt-4",
    temperature=0.0,
    base_url=None  # Optional: custom endpoint
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | Required | OpenAI API key |
| `model_id` | `str` | `"gpt-4"` | Model identifier |
| `temperature` | `float` | `0.0` | Sampling temperature |
| `base_url` | `str` | `None` | Custom API endpoint |

### Supported Models

- `gpt-4`
- `gpt-4-turbo`
- `gpt-4-turbo-preview`
- `gpt-3.5-turbo`

## AnthropicProvider

```python
from gs2txt.llm import AnthropicProvider

provider = AnthropicProvider(
    api_key="sk-ant-xxx",
    model_id="claude-sonnet-4-20250514",
    temperature=0.0
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | Required | Anthropic API key |
| `model_id` | `str` | Required | Model identifier |
| `temperature` | `float` | `0.0` | Sampling temperature |

### Supported Models

- `claude-sonnet-4-20250514`
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

## LiteLLMProvider

LiteLLM provides a unified interface for multiple LLM backends.

```python
from gs2txt.llm import LiteLLMProvider

provider = LiteLLMProvider(
    api_key="your-api-key",
    model_id="gpt-4",
    temperature=0.0,
    base_url="https://your-litellm-server.com/"
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | Required | API key |
| `model_id` | `str` | Required | Model identifier |
| `temperature` | `float` | `0.0` | Sampling temperature |
| `base_url` | `str` | `None` | LiteLLM server URL |

### Benefits

- Unified API for multiple providers
- Load balancing and fallbacks
- Cost tracking
- Rate limiting

## Base Provider Interface

All providers implement `BaseLLMProvider`:

```python
from gs2txt.llm.base import BaseLLMProvider

class BaseLLMProvider:
    def generate(self, messages: List[Dict]) -> str:
        """Generate response from messages."""
        raise NotImplementedError

    def validate_config(self) -> bool:
        """Validate provider configuration."""
        return True
```

### Message Format

```python
messages = [
    {"role": "system", "content": "You are a genomics expert..."},
    {"role": "user", "content": "Analyze these genes: TP53, MYC..."}
]
```

## Creating Custom Providers

Implement your own provider:

```python
from gs2txt.llm.base import BaseLLMProvider

class MyCustomProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_id: str, **kwargs):
        self.api_key = api_key
        self.model_id = model_id
        self.kwargs = kwargs

    def generate(self, messages: List[Dict]) -> str:
        # Your custom LLM call
        response = my_llm_call(
            messages=messages,
            api_key=self.api_key,
            model=self.model_id
        )
        return response.text

    def validate_config(self) -> bool:
        return bool(self.api_key and self.model_id)
```

### Usage

```python
provider = MyCustomProvider(
    api_key="...",
    model_id="my-model"
)
annotator = GeneSetAnnotator(llm_provider=provider)
```

## Environment Variables

| Variable | Provider | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | OpenAI | API key |
| `ANTHROPIC_API_KEY` | Anthropic | API key |
| `LITELLM_API_KEY` | LiteLLM | API key |

## Error Handling

```python
from gs2txt.llm import OpenAIProvider

provider = OpenAIProvider(api_key="invalid")

try:
    result = annotator.annotate(deg_df)
except Exception as e:
    print(f"LLM error: {e}")
```

Common errors:

- Invalid API key
- Rate limiting
- Model not found
- Network timeout
