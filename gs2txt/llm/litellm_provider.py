"""
LiteLLM unified provider for gs2txt.
"""

from typing import List, Dict
from .base import BaseLLMProvider


class LiteLLMProvider(BaseLLMProvider):
    """LiteLLM unified provider (supports multiple backends)."""

    def __init__(self, api_key: str = None, base_url: str = None, **kwargs):
        """
        Initialize LiteLLM provider.

        Parameters
        ----------
        api_key : str, optional
            API key for the LiteLLM service
        base_url : str, optional
            LiteLLM base URL (default: https://litellm.thesaisai.com/)
        **kwargs
            Additional parameters (model_id, temperature, etc.)
        """
        super().__init__(**kwargs)
        from openai import OpenAI

        self.client = OpenAI(
            api_key=api_key, base_url=base_url or "https://litellm.thesaisai.com/"
        )

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using LiteLLM API.

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
        """Validate LiteLLM configuration."""
        return True  # LiteLLM handles validation internally
