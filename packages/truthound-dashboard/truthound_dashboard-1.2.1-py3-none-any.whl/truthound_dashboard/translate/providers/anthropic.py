"""Anthropic provider for translation.

This module implements the Anthropic translation provider using
Claude models.
"""

from __future__ import annotations

import httpx

from truthound_dashboard.translate.exceptions import TranslationAPIError
from truthound_dashboard.translate.providers.base import (
    AIProvider,
    ProviderConfig,
    TranslationRequest,
    TranslationResponse,
)


class AnthropicProvider(AIProvider):
    """Anthropic translation provider.

    Uses Anthropic's Claude models for translation.

    Environment:
        ANTHROPIC_API_KEY: API key for authentication

    Example:
        provider = AnthropicProvider()
        response = await provider.translate(
            TranslationRequest(text="Hello", source_lang="en", target_lang="ja")
        )
    """

    name = "anthropic"
    display_name = "Anthropic"
    env_var = "ANTHROPIC_API_KEY"
    default_model = "claude-sonnet-4-20250514"
    supported_models = [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    DEFAULT_BASE_URL = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"

    def __init__(self, config: ProviderConfig | None = None) -> None:
        super().__init__(config)
        self.base_url = self.config.base_url or self.DEFAULT_BASE_URL

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using Anthropic API.

        Args:
            request: Translation request

        Returns:
            Translation response with translated text

        Raises:
            TranslationAPIError: If API call fails
        """
        prompt = self.get_translation_prompt(request)

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers={
                        "x-api-key": self.config.api_key,
                        "anthropic-version": self.API_VERSION,
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 4096,
                        "system": (
                            "You are a professional translator. "
                            "Translate the given text accurately and naturally. "
                            "Only output the translated text, nothing else."
                        ),
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                if response.status_code != 200:
                    raise TranslationAPIError(
                        provider_name=self.name,
                        message=f"API request failed: {response.text}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                data = response.json()
                translated_text = data["content"][0]["text"].strip()

                usage = None
                if "usage" in data:
                    usage = {
                        "input_tokens": data["usage"].get("input_tokens", 0),
                        "output_tokens": data["usage"].get("output_tokens", 0),
                    }

                return TranslationResponse(
                    translated_text=translated_text,
                    source_lang=request.source_lang,
                    target_lang=request.target_lang,
                    model=self.model,
                    provider=self.name,
                    usage=usage,
                )

            except httpx.TimeoutException as e:
                raise TranslationAPIError(
                    provider_name=self.name,
                    message=f"Request timed out after {self.config.timeout}s",
                ) from e
            except httpx.RequestError as e:
                raise TranslationAPIError(
                    provider_name=self.name,
                    message=f"Request failed: {e}",
                ) from e

    async def is_available(self) -> bool:
        """Check if Anthropic API is available.

        Returns:
            True if API key is set
        """
        return bool(self.config.api_key)
