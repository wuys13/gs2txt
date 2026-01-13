"""
LLM Provider abstraction for gs2txt.
"""

from abc import ABC, abstractmethod


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
    def generate(self, messages: list[dict[str, str]]) -> str:
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
