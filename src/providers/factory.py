"""
Factory for creating model provider instances.
"""

import logging
from typing import Dict, Any, Optional

from .base import BaseModelProvider
from .ollama_provider import OllamaProvider
from .llama_stack_provider import LlamaStackProvider
from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ProviderType:
    """Supported provider types."""
    OLLAMA = "ollama"
    LLAMA_STACK = "llama_stack"
    OPENAI = "openai"

    @classmethod
    def all(cls) -> list:
        """Get all supported provider types."""
        return [cls.OLLAMA, cls.LLAMA_STACK, cls.OPENAI]


class ModelProviderFactory:
    """
    Factory for creating model provider instances.

    Usage:
        config = {
            "provider": "ollama",
            "model_name": "llama3.3:70b",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
            "max_tokens": 4096,
        }
        provider = ModelProviderFactory.create(config)
        response = await provider.chat_completion(messages)
    """

    _provider_classes = {
        ProviderType.OLLAMA: OllamaProvider,
        ProviderType.LLAMA_STACK: LlamaStackProvider,
        ProviderType.OPENAI: OpenAIProvider,
    }

    @classmethod
    def create(cls, config: Dict[str, Any]) -> BaseModelProvider:
        """
        Create a model provider based on configuration.

        Args:
            config: Provider configuration with at least a "provider" key

        Returns:
            Instance of the appropriate provider

        Raises:
            ValueError: If provider type is unsupported or missing
            ImportError: If required dependencies are not installed
        """
        provider_type = config.get("provider")

        if not provider_type:
            raise ValueError(
                "Provider configuration must include 'provider' key. "
                f"Supported providers: {ProviderType.all()}"
            )

        provider_type = provider_type.lower()

        if provider_type not in cls._provider_classes:
            raise ValueError(
                f"Unsupported provider type: {provider_type}. "
                f"Supported providers: {ProviderType.all()}"
            )

        provider_class = cls._provider_classes[provider_type]

        try:
            logger.info(f"Creating {provider_type} provider with model: {config.get('model_name', 'default')}")
            return provider_class(config)
        except ImportError as e:
            logger.error(f"Failed to import {provider_type} provider: {e}")
            raise ImportError(
                f"Required dependencies for {provider_type} provider are not installed. "
                f"Error: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to create {provider_type} provider: {e}")
            raise

    @classmethod
    def create_from_env(cls, provider_type: Optional[str] = None) -> BaseModelProvider:
        """
        Create a provider from environment variables.

        This is a convenience method for simple setups. For more complex
        configurations, use create() with explicit config.

        Args:
            provider_type: Override the provider type (defaults to OLLAMA)

        Returns:
            Instance of the appropriate provider

        Environment variables:
            - MODEL_PROVIDER: Provider type (ollama, llama_stack, openai)
            - MODEL_NAME: Model name
            - MODEL_BASE_URL: Provider base URL
            - MODEL_API_KEY: API key (if required)
            - MODEL_TEMPERATURE: Default temperature
            - MODEL_MAX_TOKENS: Default max tokens
        """
        import os

        provider = provider_type or os.getenv("MODEL_PROVIDER", ProviderType.OLLAMA)

        config = {
            "provider": provider,
            "model_name": os.getenv("MODEL_NAME", "llama3.3:70b"),
            "base_url": os.getenv("MODEL_BASE_URL"),
            "api_key": os.getenv("MODEL_API_KEY"),
            "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "4096")),
        }

        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}

        return cls.create(config)

    @classmethod
    def supported_providers(cls) -> list:
        """Get list of supported provider types."""
        return ProviderType.all()

    @classmethod
    def register_provider(
        cls,
        provider_type: str,
        provider_class: type
    ) -> None:
        """
        Register a custom provider.

        This allows extending the factory with custom provider implementations.

        Args:
            provider_type: Identifier for the provider
            provider_class: Provider class (must inherit from BaseModelProvider)
        """
        if not issubclass(provider_class, BaseModelProvider):
            raise ValueError(
                f"Provider class must inherit from BaseModelProvider, "
                f"got {provider_class}"
            )

        cls._provider_classes[provider_type.lower()] = provider_class
        logger.info(f"Registered custom provider: {provider_type}")
