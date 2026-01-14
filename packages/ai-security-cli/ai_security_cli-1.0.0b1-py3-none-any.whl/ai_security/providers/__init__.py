"""LLM Provider implementations for live model testing"""

from typing import Dict, Type, List

from .base_provider import (
    BaseProvider,
    LLMResponse,
    ProviderError,
    AuthenticationError,
    RateLimitError,
)
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .bedrock_provider import BedrockProvider
from .vertex_provider import VertexProvider
from .azure_provider import AzureProvider
from .custom_provider import CustomProvider


# Provider name to class mapping
PROVIDER_MAP: Dict[str, Type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
    "bedrock": BedrockProvider,
    "vertex": VertexProvider,
    "azure": AzureProvider,
    "custom": CustomProvider,
}


def get_provider(provider_name: str, **kwargs) -> BaseProvider:
    """
    Factory function to create a provider instance.

    Args:
        provider_name: Name of the provider (openai, anthropic, etc.)
        **kwargs: Provider-specific configuration

    Returns:
        Configured provider instance

    Raises:
        ValueError: If provider name is unknown
    """
    provider_name = provider_name.lower()
    if provider_name not in PROVIDER_MAP:
        available = ", ".join(PROVIDER_MAP.keys())
        raise ValueError(
            f"Unknown provider: {provider_name}. Available: {available}"
        )

    provider_class = PROVIDER_MAP[provider_name]
    return provider_class(**kwargs)


def get_available_providers() -> List[str]:
    """Return list of available provider names."""
    return list(PROVIDER_MAP.keys())


__all__ = [
    # Base classes
    "BaseProvider",
    "LLMResponse",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    # Provider implementations
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "BedrockProvider",
    "VertexProvider",
    "AzureProvider",
    "CustomProvider",
    # Factory functions
    "get_provider",
    "get_available_providers",
    "PROVIDER_MAP",
]
