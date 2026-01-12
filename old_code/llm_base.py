"""
LLM Provider abstraction for geneset-annotator.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_id: str, temperature: float = 0.0, **kwargs):
        """
        Initialize LLM provider.
        
        Parameters
        ----------
        model_id : str
            Model identifier
        temperature : float
            Sampling temperature
        **kwargs
            Additional provider-specific parameters
        """
        self.model_id = model_id
        self.temperature = temperature
        self.config = kwargs
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response from messages.
        
        Parameters
        ----------
        messages : List[Dict[str, str]]
            List of message dicts with 'role' and 'content'
            
        Returns
        -------
        str
            Generated response text
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str = None, base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        from openai import OpenAI
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()
    
    def validate_config(self) -> bool:
        return self.client.api_key is not None


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        from anthropic import Anthropic
        
        self.client = Anthropic(api_key=api_key)
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        # Anthropic API 需要分离 system message
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        
        response = self.client.messages.create(
            model=self.model_id,
            system=system_msg,
            messages=user_messages,
            temperature=self.temperature,
            max_tokens=2048,
        )
        return response.content[0].text.strip()
    
    def validate_config(self) -> bool:
        return self.client.api_key is not None


class LiteLLMProvider(BaseLLMProvider):
    """LiteLLM unified provider (supports multiple backends)."""
    
    def __init__(self, api_key: str = None, base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        from openai import OpenAI
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or "https://litellm.thesaisai.com/"
        )
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()
    
    def validate_config(self) -> bool:
        return True  # LiteLLM handles validation internally
