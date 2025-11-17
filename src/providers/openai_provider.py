"""
OpenAI provider implementation.
"""

import logging
from typing import List, Dict, Any, Optional, AsyncIterator

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import BaseModelProvider, ModelResponse, ChatMessage

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseModelProvider):
    """
    Provider for OpenAI models (GPT-4, GPT-3.5, etc.).

    Also compatible with OpenAI-compatible APIs like Azure OpenAI,
    Together AI, etc.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.

        Args:
            config: Configuration dictionary with keys:
                - model_name: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
                - api_key: OpenAI API key (required)
                - base_url: Optional base URL for OpenAI-compatible APIs
                - organization: Optional organization ID
                - temperature: Default temperature
                - max_tokens: Default max tokens
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI provider requires the 'openai' package. "
                "Install it with: pip install openai>=1.0.0"
            )

        super().__init__(config)

        if not self.api_key:
            raise ValueError("OpenAI provider requires an API key")

        # Initialize OpenAI client
        client_kwargs = {"api_key": self.api_key}

        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        if "organization" in config:
            client_kwargs["organization"] = config["organization"]

        self.client = AsyncOpenAI(**client_kwargs)

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a chat completion using OpenAI.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            ModelResponse with generated content
        """
        try:
            # Convert messages to dict format
            message_dicts = self._messages_to_dicts(messages)

            # Build request parameters
            params = {
                "model": self.model_name,
                "messages": message_dicts,
                "temperature": self._get_temperature(temperature),
                "max_tokens": self._get_max_tokens(max_tokens),
            }

            # Add optional parameters
            if "top_p" in kwargs:
                params["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                params["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                params["presence_penalty"] = kwargs["presence_penalty"]
            if "response_format" in kwargs:
                params["response_format"] = kwargs["response_format"]

            response = await self.client.chat.completions.create(**params)

            # Extract content
            content = response.choices[0].message.content or ""

            # Extract usage information
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return ModelResponse(
                content=content,
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                usage=usage,
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to get completion from OpenAI: {e}")

    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion using OpenAI.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional options

        Yields:
            Chunks of generated content
        """
        try:
            message_dicts = self._messages_to_dicts(messages)

            params = {
                "model": self.model_name,
                "messages": message_dicts,
                "temperature": self._get_temperature(temperature),
                "max_tokens": self._get_max_tokens(max_tokens),
                "stream": True,
            }

            if "top_p" in kwargs:
                params["top_p"] = kwargs["top_p"]

            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise RuntimeError(f"Failed to stream from OpenAI: {e}")

    async def list_models(self) -> List[str]:
        """
        List available models from OpenAI.

        Returns:
            List of model names
        """
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to list OpenAI models: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Try to list models as a health check
            await self.list_models()
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
