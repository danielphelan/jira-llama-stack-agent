"""
Base provider interface for model providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum


class MessageRole(str, Enum):
    """Message roles in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """A message in a chat conversation."""
    role: MessageRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclass
class ModelResponse:
    """Response from a model provider."""
    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    raw_response: Optional[Any] = None

    def __str__(self) -> str:
        return self.content


class BaseModelProvider(ABC):
    """
    Abstract base class for model providers.

    All model providers must implement this interface to ensure
    consistent behavior across different backends.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration.

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.model_name = config.get("model_name", "")
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        self.default_temperature = config.get("temperature", 0.7)
        self.default_max_tokens = config.get("max_tokens", 4096)

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a chat completion.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            ModelResponse containing the generated content
        """
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated content
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        List available models from the provider.

        Returns:
            List of model names/identifiers
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        pass

    def get_model_name(self) -> str:
        """Get the configured model name."""
        return self.model_name

    def _get_temperature(self, temperature: Optional[float]) -> float:
        """Get temperature value, using default if not specified."""
        return temperature if temperature is not None else self.default_temperature

    def _get_max_tokens(self, max_tokens: Optional[int]) -> int:
        """Get max_tokens value, using default if not specified."""
        return max_tokens if max_tokens is not None else self.default_max_tokens

    def _messages_to_dicts(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Convert ChatMessage objects to dictionaries."""
        return [msg.to_dict() for msg in messages]
