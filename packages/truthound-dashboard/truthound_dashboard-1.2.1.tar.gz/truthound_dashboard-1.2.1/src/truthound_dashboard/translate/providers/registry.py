"""Provider registry for managing AI translation providers.

This module provides a central registry for AI providers, enabling
dynamic provider discovery and auto-detection based on environment.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from truthound_dashboard.translate.providers.base import AIProvider, ProviderConfig


class ProviderRegistry:
    """Registry for AI translation providers.

    This class manages provider registration and lookup, supporting
    both explicit selection and auto-detection.

    Example:
        registry = ProviderRegistry()
        registry.register("openai", OpenAIProvider)

        # Get specific provider
        provider = registry.get("openai")

        # Auto-detect based on environment
        provider = registry.detect()
    """

    _providers: dict[str, type["AIProvider"]] = {}
    _instances: dict[str, "AIProvider"] = {}

    @classmethod
    def register(cls, name: str, provider_class: type["AIProvider"]) -> None:
        """Register a provider class.

        Args:
            name: Provider name (e.g., 'openai', 'anthropic')
            provider_class: Provider class to register
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def get(
        cls,
        name: str,
        config: "ProviderConfig | None" = None,
    ) -> "AIProvider":
        """Get a provider instance by name.

        Args:
            name: Provider name
            config: Optional configuration override

        Returns:
            Provider instance

        Raises:
            ProviderNotFoundError: If provider is not registered
        """
        from truthound_dashboard.translate.exceptions import ProviderNotFoundError

        name_lower = name.lower()
        if name_lower not in cls._providers:
            raise ProviderNotFoundError(name, list(cls._providers.keys()))

        # Create new instance with config
        provider_class = cls._providers[name_lower]
        return provider_class(config)

    @classmethod
    def detect(cls, config: "ProviderConfig | None" = None) -> "AIProvider":
        """Auto-detect and return an available provider.

        Detection priority:
        1. Anthropic (ANTHROPIC_API_KEY)
        2. OpenAI (OPENAI_API_KEY)
        3. Mistral (MISTRAL_API_KEY)
        4. Ollama (if running locally)

        Args:
            config: Optional configuration override

        Returns:
            First available provider instance

        Raises:
            ProviderNotFoundError: If no provider is available
        """
        from truthound_dashboard.translate.exceptions import ProviderNotFoundError

        # Priority order for detection
        detection_order = [
            ("anthropic", "ANTHROPIC_API_KEY"),
            ("openai", "OPENAI_API_KEY"),
            ("mistral", "MISTRAL_API_KEY"),
            ("ollama", None),  # Ollama doesn't need API key
        ]

        for provider_name, env_var in detection_order:
            if provider_name not in cls._providers:
                continue

            # Check if API key is available (or not needed)
            if env_var is None or os.getenv(env_var):
                try:
                    provider = cls.get(provider_name, config)
                    return provider
                except Exception:
                    continue

        raise ProviderNotFoundError(
            "auto",
            list(cls._providers.keys()),
        )

    @classmethod
    def list_available(cls) -> list[dict[str, str]]:
        """List all registered providers with their status.

        Returns:
            List of dicts with provider info and availability status
        """
        result = []
        for name, provider_class in cls._providers.items():
            env_var = provider_class.env_var
            has_key = (
                env_var is None  # Doesn't need key
                or bool(os.getenv(env_var))
            )
            result.append({
                "name": name,
                "display_name": provider_class.display_name or name.title(),
                "env_var": env_var or "N/A",
                "available": has_key,
                "default_model": provider_class.default_model,
            })
        return result

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers. Mainly for testing."""
        cls._providers.clear()
        cls._instances.clear()


def register_provider(name: str, provider_class: type["AIProvider"]) -> None:
    """Register a provider class with the global registry.

    Args:
        name: Provider name
        provider_class: Provider class to register
    """
    ProviderRegistry.register(name, provider_class)


def get_provider(
    name: str,
    config: "ProviderConfig | None" = None,
) -> "AIProvider":
    """Get a provider instance by name.

    Args:
        name: Provider name (e.g., 'openai', 'anthropic')
        config: Optional configuration override

    Returns:
        Provider instance

    Raises:
        ProviderNotFoundError: If provider not found
    """
    return ProviderRegistry.get(name, config)


def detect_provider(config: "ProviderConfig | None" = None) -> "AIProvider":
    """Auto-detect and return an available provider.

    Args:
        config: Optional configuration override

    Returns:
        First available provider

    Raises:
        ProviderNotFoundError: If no provider available
    """
    return ProviderRegistry.detect(config)


def list_available_providers() -> list[dict[str, str]]:
    """List all registered providers with availability status.

    Returns:
        List of provider info dicts
    """
    return ProviderRegistry.list_available()


# Auto-register built-in providers on module import
def _register_builtin_providers() -> None:
    """Register all built-in providers."""
    from truthound_dashboard.translate.providers.openai import OpenAIProvider
    from truthound_dashboard.translate.providers.anthropic import AnthropicProvider
    from truthound_dashboard.translate.providers.ollama import OllamaProvider
    from truthound_dashboard.translate.providers.mistral import MistralProvider

    register_provider("openai", OpenAIProvider)
    register_provider("anthropic", AnthropicProvider)
    register_provider("ollama", OllamaProvider)
    register_provider("mistral", MistralProvider)


_register_builtin_providers()
