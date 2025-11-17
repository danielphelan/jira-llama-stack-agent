"""
Ollama provider implementation.
"""

import logging
from typing import List, Dict, Any, Optional, AsyncIterator
import aiohttp
import json

from .base import BaseModelProvider, ModelResponse, ChatMessage

logger = logging.getLogger(__name__)


class OllamaProvider(BaseModelProvider):
    """
    Provider for Ollama models.

    Ollama provides a simple API for running LLMs locally.
    Default URL: http://localhost:11434
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.

        Args:
            config: Configuration dictionary with keys:
                - model_name: Model identifier (e.g., "llama3.3:70b")
                - base_url: Ollama server URL (default: http://localhost:11434)
                - temperature: Default temperature
                - max_tokens: Default max tokens (mapped to num_predict)
        """
        super().__init__(config)
        self.base_url = self.base_url or "http://localhost:11434"
        self.api_url = f"{self.base_url}/api"

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a chat completion using Ollama.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (mapped to num_predict)
            **kwargs: Additional Ollama-specific options

        Returns:
            ModelResponse with generated content
        """
        url = f"{self.api_url}/chat"

        # Build options
        options = {
            "temperature": self._get_temperature(temperature),
            "num_predict": self._get_max_tokens(max_tokens),
        }

        # Add any additional options from kwargs
        if "top_p" in kwargs:
            options["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            options["top_k"] = kwargs["top_k"]

        payload = {
            "model": self.model_name,
            "messages": self._messages_to_dicts(messages),
            "stream": False,
            "options": options,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()

            content = data.get("message", {}).get("content", "")

            # Extract usage information if available
            usage = None
            if "prompt_eval_count" in data or "eval_count" in data:
                usage = {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                }

            return ModelResponse(
                content=content,
                model=data.get("model", self.model_name),
                finish_reason=data.get("done_reason"),
                usage=usage,
                raw_response=data,
            )

        except aiohttp.ClientError as e:
            logger.error(f"Ollama API error: {e}")
            raise RuntimeError(f"Failed to get completion from Ollama: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama chat completion: {e}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion using Ollama.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional options

        Yields:
            Chunks of generated content
        """
        url = f"{self.api_url}/chat"

        options = {
            "temperature": self._get_temperature(temperature),
            "num_predict": self._get_max_tokens(max_tokens),
        }

        if "top_p" in kwargs:
            options["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            options["top_k"] = kwargs["top_k"]

        payload = {
            "model": self.model_name,
            "messages": self._messages_to_dicts(messages),
            "stream": True,
            "options": options,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode("utf-8"))
                                if "message" in data:
                                    chunk = data["message"].get("content", "")
                                    if chunk:
                                        yield chunk
                            except json.JSONDecodeError:
                                continue

        except aiohttp.ClientError as e:
            logger.error(f"Ollama streaming error: {e}")
            raise RuntimeError(f"Failed to stream from Ollama: {e}")

    async def list_models(self) -> List[str]:
        """
        List available models from Ollama.

        Returns:
            List of model names
        """
        url = f"{self.api_url}/tags"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

            models = data.get("models", [])
            return [model.get("name", "") for model in models if "name" in model]

        except aiohttp.ClientError as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if Ollama server is accessible.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    async def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Pull/download a model to Ollama.

        Args:
            model_name: Model to pull (uses configured model if not specified)

        Returns:
            True if successful, False otherwise
        """
        model = model_name or self.model_name
        url = f"{self.api_url}/pull"

        payload = {"name": model, "stream": False}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    logger.info(f"Successfully pulled model: {model}")
                    return True
        except aiohttp.ClientError as e:
            logger.error(f"Failed to pull model {model}: {e}")
            return False
