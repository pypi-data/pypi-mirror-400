"""Base classes and protocols for AI providers.

This module defines the abstract interface that all AI providers must implement,
ensuring consistent behavior across different translation backends.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderConfig:
    """Configuration for an AI provider.

    Attributes:
        api_key: API key for authentication (None for local providers like Ollama)
        model: Model name to use for translation
        base_url: Optional base URL override for API endpoint
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts on failure
        extra: Additional provider-specific configuration
    """

    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None
    timeout: float = 60.0
    max_retries: int = 3
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(
        cls,
        env_var: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> "ProviderConfig":
        """Create config from environment variable.

        Args:
            env_var: Environment variable name for API key
            model: Model name to use
            **kwargs: Additional configuration options

        Returns:
            ProviderConfig instance
        """
        api_key = os.getenv(env_var) if env_var else None
        return cls(api_key=api_key, model=model, **kwargs)


@dataclass
class TranslationRequest:
    """Request for translation.

    Attributes:
        text: Text to translate
        source_lang: Source language code (e.g., 'en', 'ko')
        target_lang: Target language code (e.g., 'ja', 'zh')
        context: Optional context to improve translation quality
    """

    text: str
    source_lang: str
    target_lang: str
    context: str | None = None


@dataclass
class TranslationResponse:
    """Response from translation.

    Attributes:
        translated_text: The translated text
        source_lang: Source language code
        target_lang: Target language code
        model: Model used for translation
        provider: Provider name
        usage: Token usage information (if available)
    """

    translated_text: str
    source_lang: str
    target_lang: str
    model: str
    provider: str
    usage: dict[str, int] | None = None


class AIProvider(ABC):
    """Abstract base class for AI translation providers.

    All AI providers must inherit from this class and implement
    the required abstract methods.

    Example:
        class MyProvider(AIProvider):
            name = "my_provider"
            env_var = "MY_API_KEY"
            default_model = "my-model-v1"

            async def translate(self, request: TranslationRequest) -> TranslationResponse:
                # Implementation here
                pass
    """

    # Class attributes to be overridden by subclasses
    name: str = ""
    display_name: str = ""
    env_var: str | None = None
    default_model: str = ""
    supported_models: list[str] = []

    def __init__(self, config: ProviderConfig | None = None) -> None:
        """Initialize the provider.

        Args:
            config: Provider configuration. If None, will attempt to
                   create from environment variables.
        """
        if config is None:
            config = ProviderConfig.from_env(
                env_var=self.env_var,
                model=self.default_model,
            )
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate provider configuration.

        Override this method in subclasses for provider-specific validation.

        Raises:
            APIKeyNotFoundError: If required API key is missing
        """
        from truthound_dashboard.translate.exceptions import APIKeyNotFoundError

        if self.requires_api_key and not self.config.api_key:
            raise APIKeyNotFoundError(self.name, self.env_var or "API_KEY")

    @property
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key.

        Override this in subclasses that don't require API keys (e.g., Ollama).
        """
        return True

    @property
    def model(self) -> str:
        """Get the model to use for translation."""
        return self.config.model or self.default_model

    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using this provider.

        Args:
            request: Translation request containing text and language info

        Returns:
            TranslationResponse with translated text

        Raises:
            TranslationAPIError: If API call fails
        """
        pass

    async def translate_batch(
        self,
        requests: list[TranslationRequest],
    ) -> list[TranslationResponse]:
        """Translate multiple texts.

        Default implementation calls translate() for each request.
        Override this in subclasses for more efficient batch processing.

        Args:
            requests: List of translation requests

        Returns:
            List of translation responses
        """
        import asyncio

        return await asyncio.gather(*[self.translate(req) for req in requests])

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available and configured.

        Returns:
            True if the provider can be used, False otherwise
        """
        pass

    def get_translation_prompt(self, request: TranslationRequest) -> str:
        """Generate the translation prompt.

        Override this method to customize the prompt for specific providers.

        Args:
            request: Translation request

        Returns:
            Formatted prompt string
        """
        context_part = ""
        if request.context:
            context_part = f"\n\nContext: {request.context}"

        return f"""Translate the following text from {request.source_lang} to {request.target_lang}.
Only output the translated text, nothing else.
Do not add any explanations, notes, or additional formatting.{context_part}

Text to translate:
{request.text}"""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"
