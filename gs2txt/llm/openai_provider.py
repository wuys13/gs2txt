"""
OpenAI API provider for gs2txt.
"""

from typing import List, Dict
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str = None, base_url: str = None, **kwargs):
        """
        Initialize OpenAI provider.

        Parameters
        ----------
        api_key : str, optional
            OpenAI API key
        base_url : str, optional
            Custom API base URL (for OpenAI-compatible endpoints)
        **kwargs
            Additional parameters (model_id, temperature, etc.)
        """
        super().__init__(**kwargs)
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using OpenAI API.

        Parameters
        ----------
        messages : List[Dict[str, str]]
            Message list with 'role' and 'content' keys

        Returns
        -------
        str
            Generated response text
        """
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return self.client.api_key is not None
