"""Translation module for truthound-dashboard.

This module provides AI-powered translation capabilities for Intlayer content files.
It supports multiple AI providers and can automatically detect available providers
based on environment variables.

Example:
    # CLI usage
    truthound translate -l ja,zh,de -p openai

    # Auto-detect provider
    truthound translate -l ja,zh

Supported Providers:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude 3)
    - Ollama (local LLM, no API key required)
    - Mistral
"""

from truthound_dashboard.translate.providers import (
    AIProvider,
    ProviderConfig,
    ProviderRegistry,
    get_provider,
    detect_provider,
    list_available_providers,
)
from truthound_dashboard.translate.translator import (
    ContentTranslator,
    TranslationResult,
)
from truthound_dashboard.translate.config_updater import (
    IntlayerConfigUpdater,
)
from truthound_dashboard.translate.exceptions import (
    TranslationError,
    ProviderNotFoundError,
    APIKeyNotFoundError,
    TranslationAPIError,
)

__all__ = [
    # Providers
    "AIProvider",
    "ProviderConfig",
    "ProviderRegistry",
    "get_provider",
    "detect_provider",
    "list_available_providers",
    # Translator
    "ContentTranslator",
    "TranslationResult",
    # Config
    "IntlayerConfigUpdater",
    # Exceptions
    "TranslationError",
    "ProviderNotFoundError",
    "APIKeyNotFoundError",
    "TranslationAPIError",
]
