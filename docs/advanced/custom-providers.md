# Custom LLM Providers

Create custom providers for any LLM service.

## Base Class

All providers must implement `BaseLLMProvider`:

```python
from gs2txt.llm.base import BaseLLMProvider
from typing import List, Dict

class BaseLLMProvider:
    def generate(self, messages: List[Dict]) -> str:
        """Generate response from messages."""
        raise NotImplementedError

    def validate_config(self) -> bool:
        """Validate provider configuration."""
        return True
```

## Creating a Custom Provider

### Basic Implementation

```python
from gs2txt.llm.base import BaseLLMProvider
from typing import List, Dict
import requests

class MyCustomProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        model_id: str,
        temperature: float = 0.0,
        base_url: str = "https://api.myservice.com"
    ):
        self.api_key = api_key
        self.model_id = model_id
        self.temperature = temperature
        self.base_url = base_url

    def generate(self, messages: List[Dict]) -> str:
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model_id,
                "messages": messages,
                "temperature": self.temperature
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def validate_config(self) -> bool:
        return bool(self.api_key and self.model_id)
```

### Usage

```python
from gs2txt import GeneSetAnnotator

provider = MyCustomProvider(
    api_key="my-api-key",
    model_id="my-model",
    base_url="https://my-llm-server.com"
)

annotator = GeneSetAnnotator(llm_provider=provider)
result = annotator.annotate(deg_df)
```

## Advanced Examples

### Provider with Retry Logic

```python
import time
from typing import List, Dict

class RetryProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_id: str, max_retries: int = 3):
        self.api_key = api_key
        self.model_id = model_id
        self.max_retries = max_retries

    def generate(self, messages: List[Dict]) -> str:
        for attempt in range(self.max_retries):
            try:
                return self._call_api(messages)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

    def _call_api(self, messages: List[Dict]) -> str:
        # Your API call implementation
        pass
```

### Provider with Caching

```python
import hashlib
import json
from functools import lru_cache

class CachedProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_id: str, cache_size: int = 100):
        self.api_key = api_key
        self.model_id = model_id
        self._cache = {}
        self._cache_size = cache_size

    def generate(self, messages: List[Dict]) -> str:
        cache_key = self._make_key(messages)

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self._call_api(messages)

        if len(self._cache) >= self._cache_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))

        self._cache[cache_key] = result
        return result

    def _make_key(self, messages: List[Dict]) -> str:
        return hashlib.md5(
            json.dumps(messages, sort_keys=True).encode()
        ).hexdigest()

    def _call_api(self, messages: List[Dict]) -> str:
        # Your API call implementation
        pass
```

### Provider with Logging

```python
import logging
from datetime import datetime

class LoggingProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_id: str, log_file: str = "llm.log"):
        self.api_key = api_key
        self.model_id = model_id
        self.logger = logging.getLogger("llm_provider")
        handler = logging.FileHandler(log_file)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def generate(self, messages: List[Dict]) -> str:
        start_time = datetime.now()
        self.logger.info(f"Request: {len(messages)} messages")

        try:
            result = self._call_api(messages)
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Response: {len(result)} chars in {elapsed:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"Error: {e}")
            raise

    def _call_api(self, messages: List[Dict]) -> str:
        # Your API call implementation
        pass
```

## Provider with Local Models

### Using Ollama

```python
import requests

class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        model_id: str = "llama2",
        base_url: str = "http://localhost:11434"
    ):
        self.model_id = model_id
        self.base_url = base_url

    def generate(self, messages: List[Dict]) -> str:
        # Convert to Ollama format
        prompt = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_id,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
```

### Using vLLM

```python
from openai import OpenAI

class VLLMProvider(BaseLLMProvider):
    def __init__(
        self,
        model_id: str,
        base_url: str = "http://localhost:8000/v1"
    ):
        self.model_id = model_id
        self.client = OpenAI(
            base_url=base_url,
            api_key="not-needed"
        )

    def generate(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages
        )
        return response.choices[0].message.content
```

## Message Format

All providers receive messages in the standard format:

```python
messages = [
    {
        "role": "system",
        "content": "You are a genomics expert..."
    },
    {
        "role": "user",
        "content": "Analyze these genes: TP53, MYC, BRCA1..."
    }
]
```

## Best Practices

1. **Always implement `validate_config()`** to catch configuration errors early
2. **Handle rate limiting** with exponential backoff
3. **Log requests and responses** for debugging
4. **Consider caching** for repeated queries
5. **Implement timeouts** to avoid hanging requests

```python
def generate(self, messages: List[Dict]) -> str:
    response = requests.post(
        self.endpoint,
        json={"messages": messages},
        timeout=60  # 60 second timeout
    )
    response.raise_for_status()
    return response.json()["content"]
```
