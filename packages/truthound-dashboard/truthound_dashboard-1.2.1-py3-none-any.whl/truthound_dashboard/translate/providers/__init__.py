"""AI provider abstraction layer for translation.

This module provides a unified interface for multiple AI providers,
enabling seamless switching between different translation backends.

Example:
    from truthound_dashboard.translate.providers import get_provider, detect_provider

    # Explicit provider selection
    provider = get_provider("openai")

    # Auto-detection based on environment
    provider = detect_provider()

    # Translate text
    result = await provider.translate(
        text="Hello, world!",
        source_lang="en",
        target_lang="ja",
    )
"""

from truthound_dashboard.translate.providers.base import (
    AIProvider,
    ProviderConfig,
    TranslationRequest,
    TranslationResponse,
)
from truthound_dashboard.translate.providers.registry import (
    ProviderRegistry,
    get_provider,
    detect_provider,
    list_available_providers,
    register_provider,
)

__all__ = [
    # Base classes
    "AIProvider",
    "ProviderConfig",
    "TranslationRequest",
    "TranslationResponse",
    # Registry functions
    "ProviderRegistry",
    "get_provider",
    "detect_provider",
    "list_available_providers",
    "register_provider",
]
