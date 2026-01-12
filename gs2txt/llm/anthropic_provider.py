"""
Anthropic Claude API provider for gs2txt.
"""

from typing import List, Dict
from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str = None, **kwargs):
        """
        Initialize Anthropic provider.

        Parameters
        ----------
        api_key : str, optional
            Anthropic API key
        **kwargs
            Additional parameters (model_id, temperature, etc.)
        """
        super().__init__(**kwargs)
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using Anthropic API.

        Parameters
        ----------
        messages : List[Dict[str, str]]
            Message list with 'role' and 'content' keys

        Returns
        -------
        str
            Generated response text
        """
        # Anthropic API requires system message separation
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
        """Validate Anthropic configuration."""
        return self.client.api_key is not None
