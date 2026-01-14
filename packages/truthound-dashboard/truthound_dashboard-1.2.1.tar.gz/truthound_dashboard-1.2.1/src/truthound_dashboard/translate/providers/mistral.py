"""Mistral provider for translation.

This module implements the Mistral AI translation provider.
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


class MistralProvider(AIProvider):
    """Mistral AI translation provider.

    Uses Mistral AI's models for translation.

    Environment:
        MISTRAL_API_KEY: API key for authentication

    Example:
        provider = MistralProvider()
        response = await provider.translate(
            TranslationRequest(text="Hello", source_lang="en", target_lang="ja")
        )
    """

    name = "mistral"
    display_name = "Mistral AI"
    env_var = "MISTRAL_API_KEY"
    default_model = "mistral-small-latest"
    supported_models = [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest",
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
    ]

    DEFAULT_BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self, config: ProviderConfig | None = None) -> None:
        super().__init__(config)
        self.base_url = self.config.base_url or self.DEFAULT_BASE_URL

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using Mistral API.

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
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a professional translator. "
                                    "Translate the given text accurately and naturally. "
                                    "Only output the translated text, nothing else."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
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
                translated_text = data["choices"][0]["message"]["content"].strip()

                usage = None
                if "usage" in data:
                    usage = {
                        "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                        "completion_tokens": data["usage"].get("completion_tokens", 0),
                        "total_tokens": data["usage"].get("total_tokens", 0),
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
        """Check if Mistral API is available.

        Returns:
            True if API key is set
        """
        return bool(self.config.api_key)
