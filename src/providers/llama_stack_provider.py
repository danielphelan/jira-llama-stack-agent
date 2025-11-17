"""
Llama Stack provider implementation.
"""

import logging
from typing import List, Dict, Any, Optional, AsyncIterator

from llama_stack_client import LlamaStackClient

from .base import BaseModelProvider, ModelResponse, ChatMessage

logger = logging.getLogger(__name__)


class LlamaStackProvider(BaseModelProvider):
    """
    Provider for Llama Stack models.

    Llama Stack is Meta's official framework for building LLM applications.
    Default URL: http://localhost:5000
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Llama Stack provider.

        Args:
            config: Configuration dictionary with keys:
                - model_name: Model identifier (e.g., "meta-llama/Llama-3.3-70B-Instruct")
                - base_url: Llama Stack server URL (default: http://localhost:5000)
                - api_key: Optional API key
                - temperature: Default temperature
                - max_tokens: Default max tokens
        """
        super().__init__(config)
        self.base_url = self.base_url or "http://localhost:5000"

        # Initialize Llama Stack client
        client_kwargs = {"base_url": self.base_url}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key

        self.client = LlamaStackClient(**client_kwargs)

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a chat completion using Llama Stack.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Llama Stack-specific parameters

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

            response = await self.client.inference.chat_completion(**params)

            # Extract content from response
            # Llama Stack response format: response.content is a list of content blocks
            content = ""
            if hasattr(response, "content") and response.content:
                # Handle different content formats
                if isinstance(response.content, list):
                    for content_block in response.content:
                        if hasattr(content_block, "text"):
                            content += content_block.text
                        elif isinstance(content_block, dict) and "text" in content_block:
                            content += content_block["text"]
                elif hasattr(response.content, "text"):
                    content = response.content.text
                else:
                    content = str(response.content)

            # Extract usage information if available
            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                }

            return ModelResponse(
                content=content,
                model=self.model_name,
                finish_reason=getattr(response, "stop_reason", None),
                usage=usage,
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"Llama Stack API error: {e}")
            raise RuntimeError(f"Failed to get completion from Llama Stack: {e}")

    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion using Llama Stack.

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
            }

            if "top_p" in kwargs:
                params["top_p"] = kwargs["top_p"]

            # Llama Stack streaming
            async for chunk in self.client.inference.chat_completion_stream(**params):
                if hasattr(chunk, "delta"):
                    if hasattr(chunk.delta, "text"):
                        yield chunk.delta.text
                    elif isinstance(chunk.delta, dict) and "text" in chunk.delta:
                        yield chunk.delta["text"]

        except Exception as e:
            logger.error(f"Llama Stack streaming error: {e}")
            raise RuntimeError(f"Failed to stream from Llama Stack: {e}")

    async def list_models(self) -> List[str]:
        """
        List available models from Llama Stack.

        Returns:
            List of model names
        """
        try:
            # Llama Stack models endpoint
            models = await self.client.models.list()
            if isinstance(models, list):
                return [
                    model.identifier if hasattr(model, "identifier") else str(model)
                    for model in models
                ]
            return []
        except Exception as e:
            logger.error(f"Failed to list Llama Stack models: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if Llama Stack server is accessible.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Try to list models as a health check
            await self.list_models()
            return True
        except Exception as e:
            logger.warning(f"Llama Stack health check failed: {e}")
            return False
